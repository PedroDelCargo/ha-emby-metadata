"""Regression checks with HA/aiohttp boundary doubles; no live server required."""
import asyncio
import ast
import importlib
import json
from pathlib import Path
import sys
import types
import unittest

ROOT = Path('custom_components/emby_metadata').resolve()

def module(name, **attrs):
    obj = types.ModuleType(name)
    obj.__dict__.update(attrs)
    sys.modules[name] = obj
    return obj

class Coordinator:
    def __class_getitem__(cls, item): return cls
    def __init__(self, *args, **kwargs):
        self.data = {}
        self.last_update_success = True
        self.options = kwargs

class Entity:
    def __class_getitem__(cls, item): return cls
    def __init__(self, coordinator): self.coordinator = coordinator
    @property
    def available(self): return self.coordinator.last_update_success
    def _handle_coordinator_update(self): pass

class Image:
    def __init__(self, hass): pass

for name in ['homeassistant','homeassistant.helpers','homeassistant.components']:
    module(name)
module('homeassistant.config_entries', ConfigEntry=object)
module('homeassistant.core', HomeAssistant=object)
module('homeassistant.const', Platform=types.SimpleNamespace(SENSOR='sensor', IMAGE='image'))
module('homeassistant.helpers.aiohttp_client', async_get_clientsession=lambda hass: hass)
module('homeassistant.helpers.update_coordinator', DataUpdateCoordinator=Coordinator, CoordinatorEntity=Entity, UpdateFailed=RuntimeError)
module('homeassistant.helpers.device_registry', DeviceInfo=dict)
module('homeassistant.helpers.entity_platform', AddEntitiesCallback=object)
module('homeassistant.helpers.entity_registry', async_get=lambda hass: hass)
module('homeassistant.components.sensor', SensorEntity=type('SensorEntity',(),{}))
module('homeassistant.components.image', ImageEntity=Image)
module('aiohttp', ClientError=ConnectionError, ClientTimeout=lambda **kw: kw)
package=module('emby_metadata'); package.__path__=[str(ROOT)]
metadata=importlib.import_module('emby_metadata.metadata')
coordinator=importlib.import_module('emby_metadata.coordinator')
sensor=importlib.import_module('emby_metadata.sensor')
image=importlib.import_module('emby_metadata.image')

DIRECTOR={'Id':'d','Name':'Director','Type':'Director'}
ACTOR={'Id':'a','Name':'Actor','Type':'Actor','Role':'Pilot','PrimaryImageTag':'face'}
EPISODE={'Id':'e1','Type':'Episode','Name':'Arrival','SeriesId':'series','SeasonId':'season','ParentIndexNumber':0,'IndexNumber':1,'Overview':'Episode overview','ImageTags':{'Primary':'still'},'People':[DIRECTOR]}
SERIES={'Id':'series','Name':'The Series','Overview':'Series overview','ImageTags':{'Primary':'poster','Logo':'logo'},'BackdropImageTags':['background'],'People':[ACTOR]}
ENTRY=types.SimpleNamespace(entry_id='test',data={'protocol':'http','host':'server','port':8096,'api_key':'secret','device_id':'device','device_name':'Shield'})

class Response:
    def __init__(self, status=200, data=None): self.status,self.data=status,data
    async def __aenter__(self): return self
    async def __aexit__(self,*args): pass
    async def json(self): return self.data

class Session:
    def __init__(self, responses): self.responses=list(responses); self.calls=[]
    def get(self,url,**kw):
        self.calls.append((url,kw))
        if not self.responses: raise AssertionError('Unexpected request '+url)
        return self.responses.pop(0)

class Tests(unittest.IsolatedAsyncioTestCase):
    def test_syntax_and_json(self):
        for f in ROOT.rglob('*.py'): ast.parse(f.read_text(encoding='utf-8'),filename=str(f))
        for f in ROOT.rglob('*.json'): json.loads(f.read_text(encoding='utf-8'))

    def test_episode_metadata_and_images(self):
        item=metadata.normalize_item(EPISODE,series=SERIES)
        self.assertEqual(item['Overview'],'Episode overview')
        self.assertEqual(item['SeriesName'],'The Series')
        self.assertEqual(metadata.image_source(item,'poster'),('series','Primary','poster'))
        self.assertEqual(metadata.image_source(item,'backdrop'),('series','Backdrop','background'))
        self.assertEqual(metadata.image_source(item,'logo'),('series','Logo','logo'))
        self.assertEqual(metadata.image_source(item,'director'),('d','Primary',None))
        self.assertEqual(metadata.image_source(item,'actor_1'),('a','Primary','face'))

    def test_season_poster_and_parent_backdrop(self):
        item=metadata.normalize_item(EPISODE | {'ParentBackdropItemId':'parent','ParentBackdropImageTags':['inherited']}, series=SERIES,season={'Id':'season','ImageTags':{'Primary':'season-poster'}})
        self.assertEqual(metadata.image_source(item,'poster'),('season','Primary','season-poster'))
        self.assertEqual(metadata.image_source(item,'backdrop'),('parent','Backdrop','inherited'))

    def test_series_fallback_and_no_wrong_rating(self):
        item=metadata.normalize_item(EPISODE | {'Overview':None},series=SERIES | {'CommunityRating':9})
        self.assertEqual(item['Overview'],'Series overview')
        self.assertNotIn('CommunityRating',item)

    def test_people_slots_skip_nameless_deduplicate_and_guest(self):
        item=metadata.normalize_item({'People':[{'Id':'bad','Type':'Actor'},ACTOR,ACTOR,{'Name':'Guest','Id':'g','Type':'GuestStar'}]})
        self.assertEqual(len(item['People']),2)
        self.assertEqual(metadata.image_source(item,'actor_1')[0],'a')
        self.assertEqual(metadata.image_source(item,'actor_2')[0],'g')
        self.assertEqual([p['name'] for p in sensor.people_metadata(item)[1]],['Actor','Guest'])

    def test_selected_streams_disabled_and_defaults(self):
        item={'MediaStreams':[{'Type':'Subtitle','Index':1},{'Type':'Subtitle','Index':3,'IsDefault':True}]}
        self.assertEqual(sensor.selected_stream(item,'Subtitle',-1),{})
        self.assertEqual(sensor.selected_stream(item,'Subtitle',1)['Index'],1)
        self.assertEqual(sensor.selected_stream(item,'Subtitle')['Index'],3)
        self.assertEqual(sensor.selected_stream({'MediaStreams':[{'Type':'Subtitle','Index':1}]},'Subtitle'),{})

    def test_hdr_none_and_sdr_filtered(self):
        for value in ['None','none',' NONE ',None,'SDR','Unknown',0]:
            self.assertIsNone(metadata.hdr_value({'ExtendedVideoType':value}))
        self.assertEqual(metadata.hdr_value({'ExtendedVideoType':'None','VideoRange':'HDR10'}),'HDR10')

    def test_volatile_fields_excluded(self):
        a=metadata.normalize_item(EPISODE | {'UserData':{'PlaybackPositionTicks':1}})
        b=metadata.normalize_item(EPISODE | {'UserData':{'PlaybackPositionTicks':999}})
        self.assertEqual(a,b)

    def test_stream_version(self):
        item=metadata.normalize_item({'MediaSources':[{'Id':'v1','MediaStreams':[{'Codec':'h264'}]},{'Id':'v2','MediaStreams':[{'Codec':'hevc'}]}]},media_source_id='v2')
        self.assertEqual(item['MediaStreams'][0]['Codec'],'hevc')
        self.assertNotIn('MediaSources',item)

    async def test_documented_endpoint_and_cache(self):
        session=Session([Response(data=EPISODE)])
        c=coordinator.EmbyCoordinator(session,ENTRY)
        self.assertEqual(await c._item_details('e1','u'),EPISODE)
        self.assertEqual(await c._item_details('e1','u'),EPISODE)
        self.assertEqual(len(session.calls),1)
        self.assertTrue(session.calls[0][0].endswith('/Users/u/Items/e1'))
        self.assertEqual(session.calls[0][1]['headers'],{'X-Emby-Token':'secret'})

    async def test_list_endpoint_fallback(self):
        session=Session([Response(404),Response(data={'Items':[EPISODE]})])
        c=coordinator.EmbyCoordinator(session,ENTRY)
        self.assertEqual(await c._item_details('e1','u'),EPISODE)
        self.assertTrue(session.calls[1][0].endswith('/Items'))
        self.assertEqual(session.calls[1][1]['params']['Ids'],'e1')

    async def test_transient_detail_failure_preserves_data(self):
        session=Session([Response(500),Response(500)])
        c=coordinator.EmbyCoordinator(session,ENTRY)
        c._details_cache[('u','e1')]=(0,EPISODE)
        self.assertEqual(await c._item_details('e1','u'),EPISODE)

    async def test_poll_equality_and_enrichment(self):
        active={'DeviceId':'device','UserId':'u','NowPlayingItem':EPISODE,'PlayState':{'PositionTicks':1,'SubtitleStreamIndex':-1}}
        session=Session([Response(data=[active]),Response(data=EPISODE),Response(data=SERIES),Response(data={'Id':'season'}),Response(data=[active | {'PlayState':{'PositionTicks':999,'SubtitleStreamIndex':-1}}])])
        c=coordinator.EmbyCoordinator(session,ENTRY)
        first=await c._async_update_data(); second=await c._async_update_data()
        self.assertEqual(first,second)
        self.assertEqual(first['NowPlayingItem']['SeriesName'],'The Series')
        self.assertEqual(c.update_interval.total_seconds(),5)
        self.assertFalse(c.options['always_update'])

    async def test_idle_interval_and_disconnect(self):
        c=coordinator.EmbyCoordinator(Session([Response(data=[])]),ENTRY)
        self.assertIsNone((await c._async_update_data())['NowPlayingItem'])
        self.assertEqual(c.update_interval.total_seconds(),30)

    def test_sensor_registry_and_episode_attributes(self):
        c=Coordinator(); c.data={'NowPlayingItem':metadata.normalize_item(EPISODE,series=SERIES)}
        entity=sensor.EmbyNowPlayingSensor(c,ENTRY)
        entity.hass=types.SimpleNamespace(async_get_entity_id=lambda domain,platform,uid:'image.renamed_'+uid)
        attrs=entity.extra_state_attributes
        self.assertEqual(attrs['series_title'],'The Series')
        self.assertEqual(attrs['season_number'],0)
        self.assertEqual(attrs['actors'][0]['image_entity'],'image.renamed_test_actor_1')

    async def test_image_cache_changes_only_with_source(self):
        c=Coordinator(); c.data={'NowPlayingItem':metadata.normalize_item(EPISODE,series=SERIES)}
        calls=[]
        async def fetch(*args): calls.append(args); return b'picture','image/png'
        c.async_fetch_image=fetch
        entity=image.EmbyImageEntity(None,c,ENTRY,'poster','Poster')
        stamp=entity._attr_image_last_updated
        self.assertTrue(entity.available)
        self.assertEqual(await entity.async_image(),b'picture')
        entity._handle_coordinator_update()
        self.assertEqual(await entity.async_image(),b'picture')
        self.assertEqual(len(calls),1)
        self.assertEqual(entity._attr_image_last_updated,stamp)
        c.data={'NowPlayingItem':metadata.normalize_item({'Id':'movie','ImageTags':{'Primary':'new'}})}
        entity._handle_coordinator_update()
        await entity.async_image()
        self.assertEqual(calls[-1],('movie','Primary','new'))
        c.data={'NowPlayingItem':None}
        entity._handle_coordinator_update()
        self.assertFalse(entity.available)
        self.assertIsNone(await entity.async_image())

if __name__=='__main__': unittest.main(verbosity=2)
