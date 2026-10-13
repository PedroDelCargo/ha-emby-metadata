"""Polling, sharing and options regression tests with HA boundary doubles."""
import asyncio
import importlib
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import AsyncMock, Mock

from test_backend import (
    ENTRY, Response, Session, coordinator, make_coordinator, module,
)

ROOT = Path(__file__).resolve().parents[1]


class Flow:
    def __init_subclass__(cls, **kwargs): pass
    def async_show_form(self, **kwargs): return {"type": "form", **kwargs}
    def async_create_entry(self, **kwargs): return {"type": "create_entry", **kwargs}


module('homeassistant.config_entries', ConfigEntry=object, ConfigFlow=Flow, OptionsFlow=Flow)
flow = importlib.import_module('emby_metadata.config_flow')
module('homeassistant.components.http', StaticPathConfig=object)
module('homeassistant.helpers.config_validation', config_entry_only_config_schema=lambda domain: domain)
module('emby_metadata.frontend', CARD_URL='/card', async_register_card=AsyncMock())
spec = importlib.util.spec_from_file_location('emby_metadata.setup', ROOT/'custom_components/emby_metadata/__init__.py')
setup = importlib.util.module_from_spec(spec)
setup.__package__ = 'emby_metadata'
spec.loader.exec_module(setup)


def entry(id='one', options=None, **data):
    return SimpleNamespace(entry_id=id, options=options or {}, data=ENTRY.data | data)


class Tests(unittest.IsolatedAsyncioTestCase):
    async def test_setup_unload_and_setup_failure_cleanup(self):
        http = Session([Response(data=[{'DeviceId': 'device'}, {'DeviceId': 'other'}])])
        http.data = {}
        http.config_entries = SimpleNamespace(
            async_forward_entry_setups=AsyncMock(),
            async_unload_platforms=AsyncMock(return_value=True))
        a, b = entry(), entry('two', device_id='other')
        for e in (a, b):
            e.async_on_unload = Mock()
            e.add_update_listener = Mock()
        await asyncio.gather(setup.async_setup_entry(http, a), setup.async_setup_entry(http, b))
        self.assertIs(a.runtime_data.sessions, b.runtime_data.sessions)
        self.assertEqual(len(http.calls), 1)
        await setup.async_unload_entry(http, a)
        self.assertEqual(len(b.runtime_data.sessions.listeners), 1)
        await setup.async_unload_entry(http, b)
        self.assertEqual(http.data['emby_metadata'], {})
        http.responses = [Response(500)]
        with self.assertRaises(Exception): await setup.async_setup_entry(http, a)
        self.assertEqual(http.data['emby_metadata'], {})

    async def test_options_during_outage_do_not_publish_stale_success(self):
        a = entry()
        c = make_coordinator(Session([]), a)
        a.runtime_data = c
        c.sessions.last_update_success = False
        c.sessions.async_request_refresh = AsyncMock()
        c.sessions.async_set_updated_data = Mock()
        await setup._async_options_updated(None, a)
        c.sessions.async_set_updated_data.assert_not_called()
        c.sessions.async_request_refresh.assert_awaited_once()

    async def test_states_options_and_shared_minimum(self):
        a = entry(options={'idle_interval': 7, 'playing_interval': 12, 'absent_interval': 50})
        b = entry('two', {'idle_interval': 9}, device_id='other')
        source = coordinator.EmbySessionsCoordinator(Session([]), a)
        source.clients = {'one': a}
        for sessions, expected in [([], 50), ([{'DeviceId': 'device'}], 7),
                                   ([{'DeviceId': 'device', 'NowPlayingItem': {'Id': 'movie'}}], 12)]:
            source.select_interval(sessions)
            self.assertEqual(source.update_interval.total_seconds(), expected)
        source.clients['two'] = b
        source.select_interval([{'DeviceId': 'other'}])
        self.assertEqual(source.update_interval.total_seconds(), 9)

    async def test_default_connected_idle_is_five_seconds(self):
        c = make_coordinator(Session([Response(data=[{'DeviceId': 'device'}])]))
        await c.sessions.async_refresh()
        self.assertEqual(c.sessions.update_interval.total_seconds(), 5)
        self.assertIsNone((await c._async_update_data())['NowPlayingItem'])

    async def test_concurrent_setup_and_clients_use_one_request(self):
        class SlowResponse(Response):
            async def json(self):
                await asyncio.sleep(0)
                return self.data
        http = Session([SlowResponse(data=[{'DeviceId': 'device'}, {'DeviceId': 'other'}])])
        a = make_coordinator(http, entry())
        b = make_coordinator(http, entry('two', device_id='other'), a.sessions)
        await asyncio.gather(a.sessions.async_ensure_data(), b.sessions.async_ensure_data())
        await asyncio.gather(a._async_update_data(), b._async_update_data())
        self.assertEqual(len(http.calls), 1)
        self.assertIsNone(a.update_interval)
        self.assertIsNone(b.update_interval)

    async def test_unchanged_metadata_does_not_notify_entities(self):
        c = make_coordinator(Session([]))
        listener = Mock()
        c.async_add_listener(listener)
        for position in (1, 99):
            c.sessions.data = [{'DeviceId': 'device', 'PlayState': {'PositionTicks': position}}]
            await c.async_refresh()
        listener.assert_called_once()

    async def test_bad_sessions_are_rejected(self):
        for response in (Response(401), Response(data={}), Response(data=[None])):
            source = coordinator.EmbySessionsCoordinator(Session([response]), ENTRY)
            await source.async_refresh()
            self.assertFalse(source.last_update_success)
            self.assertEqual(source.update_interval.total_seconds(), 30)

    async def test_failure_backoff_and_recovery(self):
        http = Session([Response(500), Response(data=[{'DeviceId': 'device'}])])
        c = make_coordinator(http)
        with self.assertRaises(Exception): await c.sessions.async_ensure_data()
        self.assertFalse(c.sessions.last_update_success)
        self.assertEqual(c.sessions.update_interval.total_seconds(), 30)
        with self.assertRaises(RuntimeError): await c._async_update_data()
        await c.sessions.async_ensure_data()
        self.assertEqual(c.sessions.update_interval.total_seconds(), 5)
        self.assertIsNone((await c._async_update_data())['NowPlayingItem'])

    async def test_snapshot_changed_during_enrichment_is_not_lost(self):
        c = make_coordinator(Session([]))
        started, finish = asyncio.Event(), asyncio.Event()
        snapshots = []
        async def refresh():
            snapshots.append(c.sessions.data)
            if len(snapshots) == 1:
                started.set()
                await finish.wait()
        c.async_refresh = refresh
        c.async_start()
        c.sessions.async_set_updated_data(['old'])
        await started.wait()
        c.sessions.async_set_updated_data(['new'])
        finish.set()
        await c._refresh_task
        self.assertEqual(snapshots, [['old'], ['new']])
        await c.async_stop()
        self.assertEqual(c.sessions.listeners, [])

    async def test_unload_cancels_enrichment(self):
        c = make_coordinator(Session([]))
        started = asyncio.Event()
        async def refresh():
            started.set()
            await asyncio.Event().wait()
        c.async_refresh = refresh
        c.async_start()
        c.sessions.async_set_updated_data([])
        await started.wait()
        await c.async_stop()
        self.assertTrue(c._refresh_task.cancelled())
        self.assertEqual(c.sessions.listeners, [])

    async def test_options_apply_without_reload_and_unload_retains_other_client(self):
        a, b = entry(), entry('two', device_id='other')
        c = make_coordinator(Session([]), a)
        source = c.sessions
        source.clients['two'] = b
        source.data = [{'DeviceId': 'device'}]
        a.runtime_data = c
        a.options = {'idle_interval': 8}
        hass = SimpleNamespace(data={'emby_metadata': {setup._server_key(a): source}})
        await setup._async_options_updated(hass, a)
        self.assertEqual(source.update_interval.total_seconds(), 8)
        source.async_shutdown = AsyncMock()
        await setup._release_server(hass, a)
        source.async_shutdown.assert_not_awaited()
        self.assertEqual(source.update_interval.total_seconds(), 30)
        await setup._release_server(hass, b)
        source.async_shutdown.assert_awaited_once()
        self.assertEqual(hass.data['emby_metadata'], {})

    def test_credentials_are_isolated(self):
        self.assertNotEqual(setup._server_key(entry()), setup._server_key(entry(api_key='different')))
        self.assertNotEqual(setup._server_key(entry()), setup._server_key(entry(host='other')))

    async def test_options_validation_and_saved_defaults(self):
        handler = flow.OptionsFlow()
        handler.config_entry = entry(options={'idle_interval': 8})
        form = await handler.async_step_init()
        self.assertEqual(form['data_schema']({}), {'idle_interval': 8, 'playing_interval': 5, 'absent_interval': 30})
        for value in [0, 4, 301, 5.5, True, '5']:
            result = await handler.async_step_init({'idle_interval': value})
            self.assertEqual(result['errors'], {'base': 'invalid_interval'})
        result = await handler.async_step_init({'idle_interval': 5, 'playing_interval': 10, 'absent_interval': 300})
        self.assertEqual(result['type'], 'create_entry')
        self.assertEqual(result['data']['absent_interval'], 300)

    def test_options_translations_have_same_keys(self):
        root = ROOT/'custom_components/emby_metadata'
        english = json.loads((root/'strings.json').read_text(encoding='utf-8'))['options']
        for locale in ['en', 'fr', 'de', 'es']:
            translated = json.loads((root/'translations'/f'{locale}.json').read_text(encoding='utf-8'))['options']
            self.assertEqual(set(english['step']['init']['data']), set(translated['step']['init']['data']))
            self.assertEqual(set(english['error']), set(translated['error']))


if __name__ == '__main__': unittest.main(verbosity=2)
