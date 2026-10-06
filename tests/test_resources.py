"""Resource lifecycle regression checks with HA collection doubles."""
import asyncio
import importlib.util
from pathlib import Path
import sys
from types import ModuleType, SimpleNamespace
import unittest
from unittest.mock import AsyncMock

ROOT = Path(__file__).resolve().parents[1]

def module(name, **values):
    obj = ModuleType(name)
    obj.__dict__.update(values)
    sys.modules[name] = obj
    return obj

for name in ['homeassistant', 'homeassistant.components', 'homeassistant.components.lovelace']:
    module(name)
module('homeassistant.components.lovelace.const', LOVELACE_DATA='lovelace', MODE_STORAGE='storage')
module('homeassistant.core', HomeAssistant=object)
loader = module('homeassistant.loader', async_get_integration=AsyncMock(return_value=SimpleNamespace(version='1.2.9')))
module('emby_metadata', __path__=[])
module('emby_metadata.const', DOMAIN='emby_metadata')
spec = importlib.util.spec_from_file_location('emby_metadata.frontend', ROOT/'custom_components/emby_metadata/frontend.py')
frontend = importlib.util.module_from_spec(spec)
spec.loader.exec_module(frontend)

class Resources:
    def __init__(self, items=()):
        self.saved = [dict(item) for item in items]
        self.loaded = False
        self.writes = []
    async def async_get_info(self):
        self.loaded = True
        return {'resources':len(self.saved)}
    def async_items(self):
        assert self.loaded, 'Must load before checking existing entries'
        return list(self.saved)
    async def async_create_item(self, data):
        assert set(data)=={'url','res_type'}
        self.writes.append('create')
        self.saved.append({'id':'new','url':data['url'],'type':data['res_type']})
    async def async_update_item(self, id, data):
        assert set(data)=={'url','res_type'}
        self.writes.append('update')
        next(x for x in self.saved if x['id']==id).update(url=data['url'],type=data['res_type'])
    async def async_delete_item(self, id):
        self.writes.append('delete')
        self.saved=[x for x in self.saved if x['id']!=id]

def hass(resources, mode='storage'):
    return SimpleNamespace(data={'lovelace':SimpleNamespace(resources=resources, resource_mode=mode)})

class Tests(unittest.IsolatedAsyncioTestCase):
    async def test_first_install_and_repeat(self):
        r=Resources();h=hass(r)
        await frontend.async_register_card(h)
        await frontend.async_register_card(h)
        self.assertEqual(r.writes,['create'])
        self.assertEqual(r.saved[0]['url'],frontend.CARD_URL+'?v=1.2.9')
    async def test_restart_and_upgrade_preserve_id(self):
        r=Resources([{'id':'manual','url':frontend.CARD_URL+'?v=1.2.8','type':'js'}])
        await frontend.async_register_card(hass(r))
        self.assertEqual(r.saved,[{'id':'manual','url':frontend.CARD_URL+'?v=1.2.9','type':'module'}])
        r.loaded=False
        await frontend.async_register_card(hass(r))
        self.assertEqual(r.writes,['update'])
    async def test_unversioned_manual_resource(self):
        r=Resources([{'id':'manual','url':frontend.CARD_URL,'type':'module'}])
        await frontend.async_register_card(hass(r))
        self.assertEqual(r.writes,['update'])
    async def test_duplicates_and_unrelated_entries(self):
        unrelated=[{'id':str(i),'url':url,'type':'module'} for i,url in enumerate([
            '/local/emby-metadata-card.js','https://example.org'+frontend.CARD_URL,
            '//example.org'+frontend.CARD_URL,'/other.js'])]
        r=Resources(unrelated+[
            {'id':'one','url':frontend.CARD_URL+'?v=old','type':'module'},
            {'id':'two','url':frontend.CARD_URL,'type':'module'}])
        await frontend.async_register_card(hass(r))
        self.assertEqual(r.saved[:4],unrelated)
        self.assertEqual(len(r.saved),5)
        self.assertEqual(r.writes,['update','delete'])
    async def test_yaml_is_untouched_and_instructed(self):
        r=Resources()
        with self.assertLogs(frontend._LOGGER,level='INFO') as log:
            await frontend.async_register_card(hass(r,'yaml'))
        self.assertFalse(r.loaded)
        self.assertFalse(r.writes)
        self.assertIn('?v=1.2.9',str(log.output))
    async def test_failure_does_not_block_integration_and_retry(self):
        r=Resources();load=r.async_get_info
        r.async_get_info=AsyncMock(side_effect=OSError('disk error'))
        with self.assertLogs(frontend._LOGGER,level='ERROR'):
            await frontend.async_register_card(hass(r))
        self.assertFalse(r.writes)
        r.async_get_info=load
        await frontend.async_register_card(hass(r))
        self.assertEqual(r.writes,['create'])
    async def test_registration_once_per_integration_not_per_client(self):
        # Exercise actual integration setup and two client setups/unloads.
        module('homeassistant.components.http', StaticPathConfig=lambda *a:a)
        module('homeassistant.config_entries',ConfigEntry=object)
        sys.modules['emby_metadata.const'].PLATFORMS=['image','sensor']
        module('emby_metadata.coordinator',EmbyCoordinator=lambda *a:SimpleNamespace(async_config_entry_first_refresh=AsyncMock()))
        sys.modules['emby_metadata.frontend']=frontend
        spec=importlib.util.spec_from_file_location('emby_metadata',ROOT/'custom_components/emby_metadata/__init__.py')
        integration=importlib.util.module_from_spec(spec);spec.loader.exec_module(integration)
        r=Resources();h=hass(r)
        h.http=SimpleNamespace(async_register_static_paths=AsyncMock())
        h.config_entries=SimpleNamespace(async_forward_entry_setups=AsyncMock(),async_unload_platforms=AsyncMock(return_value=True))
        await integration.async_setup(h,{})
        for _ in range(2):
            entry=SimpleNamespace()
            await integration.async_setup_entry(h,entry)
            await integration.async_unload_entry(h,entry)
        self.assertEqual(r.writes,['create'])
        h.http.async_register_static_paths.assert_awaited_once()

if __name__=='__main__':
    unittest.main(verbosity=2)
