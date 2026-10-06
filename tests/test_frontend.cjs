const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');
const assert = require('assert/strict');
const cardPath = path.resolve('custom_components/emby_metadata/static/emby-metadata-card.js');
(async () => {
  fs.mkdirSync('test-results',{recursive:true});
  const browser = await chromium.launch({executablePath:process.env.BROWSER_EXECUTABLE,headless:true});
  const page = await browser.newPage({viewport:{width:1400,height:1100}});
  const errors=[]; page.on('pageerror',e=>errors.push(String(e)));
  await page.setContent('<body style="margin:20px;background:#20232a;font-family:Arial"><main id="host" style="width:1100px"></main></body>');
  await page.addScriptTag({path:cardPath});
  await page.evaluate(() => {
    const svg=(w,h,color)=>'data:image/svg+xml,'+encodeURIComponent(`<svg xmlns="http://www.w3.org/2000/svg" width="${w}" height="${h}"><defs><linearGradient id="g"><stop stop-color="${color}"/><stop offset="1" stop-color="#b88745"/></linearGradient></defs><rect width="100%" height="100%" fill="url(#g)"/><circle cx="70%" cy="40%" r="100" fill="#d6c9a0" opacity=".5"/></svg>`);
    window.data={language:'fr',states:{'sensor.emby':{state:'Le départ',attributes:{playing:true,emby_item_id:'e1',media_type:'Episode',title:'Le départ',series_title:'Les horizons',season_number:0,episode_number:2,production_year:2026,genres:['Aventure','Drame'],overview:'Un équipage part à la découverte d’un monde inconnu. '.repeat(35),community_rating:6.4,runtime_minutes:49,video_width:3840,video_height:2160,video_codec:'hevc',video_hdr:'None',audio_codec:'EAC3',audio_channels:6,poster_entity:'image.poster',backdrop_entity:'image.backdrop',logo_entity:'image.logo',director:{name:'Camille Martin',image_entity:'image.director'},actors:Array.from({length:5},(_,i)=>({name:`Interprète ${i+1}`,role:`Personnage ${i+1}`,image_entity:'image.actor'}))}},'image.poster':{state:'v1',attributes:{entity_picture:svg(400,600,'#243044')}},'image.backdrop':{state:'v1',attributes:{entity_picture:svg(1600,900,'#326779')}},'image.director':{state:'v1',attributes:{entity_picture:svg(200,300,'#4c6570')}},'image.actor':{state:'v1',attributes:{entity_picture:svg(200,300,'#4c6570')}}}};
    window.card=document.createElement('emby-metadata-card');
    card.setConfig({entity:'sensor.emby'}); card.hass=data;
    document.querySelector('#host').append(card);
  });
  // Data URLs cannot take HA's cache-busting query. Intercept helper in fixtures only.
  await page.evaluate(()=>{
    const original=card._imageUrl;
    card._imageUrl=function(id){const url=data.states[id]?.attributes?.entity_picture;return url?.startsWith('data:')?url:original.call(this,id)};
    card._lastSignature=null;card.hass=data;
  });
  await page.waitForTimeout(100);
  const layout = ()=>page.evaluate(()=>{
    const root=card.shadowRoot, q=s=>root.querySelector(s), rect=e=>({x:e.getBoundingClientRect().x,width:e.getBoundingClientRect().width,height:e.getBoundingClientRect().height});
    return {card:rect(q('.card')),layout:rect(q('.layout')),content:rect(q('.content')),backdrop:rect(q('.backdrop')),poster:q('.poster-column')?getComputedStyle(q('.poster-column')).display:null,columns:getComputedStyle(q('.people-grid')).gridTemplateColumns.split(' ').length,text:root.textContent,overflow:q('.card').scrollWidth>q('.card').clientWidth};
  });
  let result=await layout();
  assert(result.backdrop.height>500,'horizontal backdrop has height');
  assert(Math.abs(result.backdrop.width/result.backdrop.height-16/9)<.01,'proportional backdrop');
  assert.equal(result.poster,'flex'); assert.equal(result.columns,6); assert(!result.overflow);
  assert(result.text.includes('S00E02 · Le départ')); assert(result.text.includes('★ 6,4')); assert(!result.text.includes('>None<'));
  await page.screenshot({path:'test-results/horizontal.png',fullPage:true});
  await page.evaluate(()=>card.setConfig({entity:'sensor.emby',show_poster:false}));
  result=await layout(); assert.equal(result.poster,null); assert.equal(result.content.width,result.layout.width-32);
  await page.evaluate(()=>window.before=card.shadowRoot.querySelector('.card'));
  await page.evaluate(()=>{card.hass=structuredClone(data);card.setConfig({entity:'sensor.emby',show_poster:false});});
  assert(await page.evaluate(()=>before===card.shadowRoot.querySelector('.card')),'same data/config must preserve DOM');
  await page.evaluate(()=>data.states['sensor.emby'].attributes.position=500);
  await page.evaluate(()=>card.hass=data);
  assert(await page.evaluate(()=>before===card.shadowRoot.querySelector('.card')),'playback position does not rebuild DOM');
  const h0=await page.locator('.synopsis-text').evaluate(e=>e.clientHeight);
  await page.locator('.synopsis-toggle').click();
  await page.waitForTimeout(110);
  const mid=await page.locator('.synopsis-text').evaluate(e=>e.clientHeight);
  await page.waitForTimeout(250);
  const h1=await page.locator('.synopsis-text').evaluate(e=>e.clientHeight);
  assert(mid>h0 && mid<h1,'expansion has intermediate height');
  await page.locator('.synopsis-toggle').click(); await page.waitForTimeout(350);
  assert.equal(await page.locator('.synopsis-text').evaluate(e=>e.clientHeight),h0);
  for(const [width,cols,poster] of [[390,3,'none'],[600,3,'none'],[767,3,'none'],[768,6,'flex'],[1100,6,'flex']]){
    await page.evaluate(w=>{document.querySelector('#host').style.width=`${w}px`;card.setConfig({entity:'sensor.emby'});},width);
    await page.waitForTimeout(70);result=await layout();
    assert.equal(result.columns,cols);assert.equal(result.poster,poster);assert(!result.overflow,`overflow at ${width}`);
    if(width===390)await page.screenshot({path:'test-results/vertical.png',fullPage:true});
  }
  const pure=await page.evaluate(()=>{
    const C=customElements.get('emby-metadata-card'), f=C.getConfigForm();
    f.assertConfig({});f.assertConfig({entity:''});
    let rejected=false;try{f.assertConfig({show_video:'false'})}catch{rejected=true}
    return {rejected,group:f.schema.find(v=>v.name==='technical'),hdr:['None','none',' NONE ',null,'SDR'].map(v=>card._hdr(v)),rating:card._formatRating(null)};
  });
  assert(pure.rejected);assert(pure.group.flatten);assert.equal(pure.group.schema.length,3);assert(pure.hdr.every(v=>v===null));assert.equal(pure.rating,null);
  // The synopsis spans both columns and begins below the visible poster.
  for (const width of [768,1100]) {
    await page.evaluate(w=>document.querySelector('#host').style.width=`${w}px`,width);
    await page.waitForTimeout(80);
    const rects=await page.evaluate(()=>{
      const q=s=>card.shadowRoot.querySelector(s).getBoundingClientRect();
      const p=q('.poster'),s=q('.synopsis'),l=q('.layout');
      return {below:s.top>=p.bottom,width:s.width,available:l.width-32,left:s.left-l.left};
    });
    assert(rects.below);assert.equal(rects.width,rects.available);assert.equal(rects.left,16);
  }
  // New disclosure and portrait behavior.
  assert.equal(await page.locator('.section-toggle').count(),2);
  assert.deepEqual(await page.locator('.section-toggle').evaluateAll(items=>items.map(e=>e.getAttribute('aria-expanded'))),['false','false']);
  const people=page.locator('.people-section .section-body');
  assert.equal(await people.evaluate(e=>e.getBoundingClientRect().height),0);
  await page.locator('.people-section .section-toggle').focus();
  await page.keyboard.press('Enter');
  await page.waitForTimeout(100);
  const peopleMid=await people.evaluate(e=>e.getBoundingClientRect().height);
  await page.waitForTimeout(230);
  const peopleFull=await people.evaluate(e=>e.getBoundingClientRect().height);
  assert(peopleMid>0 && peopleMid<peopleFull,'cast expands smoothly');
  const geometry=await page.evaluate(()=>{
    const root=card.shadowRoot,photo=root.querySelector('.person-photo-wrap'),caption=root.querySelector('.person-caption');
    const r=photo.getBoundingClientRect(),c=caption.getBoundingClientRect();
    const duration=root.querySelector('.runtime-rating').getBoundingClientRect();
    const synopsis=root.querySelector('.synopsis').getBoundingClientRect();
    const top=root.querySelector('.heading').getBoundingClientRect();
    const layout=root.querySelector('.layout').getBoundingClientRect();
    return {width:r.width,captionWidth:c.width,bottom:Math.abs(r.bottom-c.bottom),background:getComputedStyle(caption).backgroundColor,fallback:getComputedStyle(photo).backgroundImage,space:synopsis.top-duration.bottom,top:top.top-layout.top};
  });
  assert(geometry.width<=150);assert.equal(geometry.width,geometry.captionWidth);assert(geometry.bottom<1);
  assert.equal(geometry.background,'rgba(0, 0, 0, 0.6)');assert(geometry.fallback.includes('data:image/svg+xml'));
  assert.equal(geometry.space,16);assert.equal(geometry.top,16);
  await page.evaluate(()=>{data.states['sensor.emby'].attributes.community_rating=7.2;card.hass=data;});
  assert.equal(await page.locator('.people-section .section-toggle').getAttribute('aria-expanded'),'true');
  await page.locator('.technical .section-toggle').click();await page.waitForTimeout(320);
  assert.equal(await page.locator('.technical .section-toggle').getAttribute('aria-expanded'),'true');
  await page.locator('.people-section .section-toggle').click();
  await page.waitForTimeout(320);
  await page.evaluate(()=>{data.states['image.actor'].attributes.entity_picture='data:image/png;base64,invalid';card.hass=data;});
  await page.waitForTimeout(100);
  assert(await page.locator('.person-photo').last().evaluate(e=>e.hidden));
  assert(await page.locator('.person-caption').last().isVisible());
  await page.screenshot({path:'test-results/card124-open.png',fullPage:true});
  await page.evaluate(()=>{data.states['sensor.emby'].attributes.emby_item_id='new-item';card.hass=data;});
  assert.deepEqual(await page.locator('.section-toggle').evaluateAll(items=>items.map(e=>e.getAttribute('aria-expanded'))),['false','false']);
  // Every opening closes the other two, including rapid transitions and rerenders.
  for (const width of [390,1100]) {
    await page.evaluate(w=>document.querySelector('#host').style.width=`${w}px`,width);
    for (const active of ['synopsis','technical','people','technical','synopsis','people']) {
      const selector=active==='synopsis'?'.synopsis-toggle':`[data-section="${active}"] .section-toggle`;
      await page.locator(selector).evaluate(e=>e.click());
      const state=await page.evaluate(()=>({synopsis:!!card._expanded,...card._sections}));
      assert.deepEqual(state,{synopsis:active==='synopsis',technical:active==='technical',people:active==='people'});
      assert.equal(await page.locator('[aria-expanded="true"]').count(),1);
      await page.evaluate(()=>{data.states['sensor.emby'].attributes.community_rating+=0.01;card.hass=data;});
      assert.equal(await page.locator('[aria-expanded="true"]').count(),1);
    }
    await page.locator('.people-section .section-toggle').evaluate(e=>e.click());
    assert.equal(await page.locator('[aria-expanded="true"]').count(),0);
  }
  // Error fallbacks for all image classes.
  await page.evaluate(()=>{
    data.states['image.logo']={state:'v1',attributes:{entity_picture:'data:image/png;base64,invalid'}};
    data.states['image.backdrop'].attributes.entity_picture='data:image/png;base64,invalid';
    card.hass=data;
  });
  await page.waitForTimeout(100);
  assert.equal(await page.locator('.title-text').textContent(),'Les horizons');
  assert(await page.locator('.backdrop').evaluate(e=>e.naturalWidth>0));
  const versions=await page.evaluate(()=>{
    card._imageUrl=Object.getPrototypeOf(card)._imageUrl;
    const image=data.states['image.poster'];image.attributes.entity_picture='/api/image_proxy/image.poster?token=first';
    const first=card._signature(data.states['sensor.emby']);
    image.attributes.entity_picture='/api/image_proxy/image.poster?token=second';
    const token=card._signature(data.states['sensor.emby']);
    image.state='changed-image';
    const changed=card._signature(data.states['sensor.emby']);
    return {same:first===token,changed:changed!==token,url:card._imageUrl('image.poster')};
  });
  assert(versions.same,'HA token rotation does not rebuild the card');
  assert(versions.changed,'new image timestamp invalidates displayed image');
  assert(versions.url.includes('v=changed-image'));
  assert.equal(errors.length,0,errors.join('\n'));
  fs.writeFileSync('test-results/frontend-results.json',JSON.stringify({passed:true,checks:['horizontal backdrop and proportions','poster false full width','episode title and decimal rating','stable DOM on identical data/config and playback position','animated synopsis expansion/collapse','responsive widths 390/600/767/768/1100','3/6 people columns','form validation and flattened technical options','HDR sentinel filtering','missing rating','broken logo/backdrop fallbacks'],errors},null,2));
  console.log('Browser regression checks passed');
  await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
