const {chromium}=require('playwright');
const assert=require('assert/strict');
(async()=>{
 const browser=await chromium.launch({executablePath:process.env.BROWSER_EXECUTABLE,headless:true});
 const page=await browser.newPage();
 await page.setContent('<main></main>');
 await page.addScriptTag({path:'custom_components/emby_metadata/static/emby-metadata-card.js'});
 const result=await page.evaluate(()=>{
  const C=customElements.get('emby-metadata-card'),card=new C();
  card.setConfig({entity:'sensor.test'});document.querySelector('main').append(card);
  const states={'sensor.test':{state:'Film',attributes:{title:'Original title',overview:'Original synopsis',playing:true,community_rating:6.4,director:{name:'Person',role:'Réalisateur'},subtitle_language:'fre',subtitle_forced:true,subtitle_hearing_impaired:true}}};
  card.hass={states};
  const en=card.shadowRoot.textContent;
  const englishLanguage=card._language('fre');
  const form=C.getConfigForm();
  const contexts=['en','fr','fr-CA','de','de-DE','es','es-MX',''].map(language=>{
    const ctx={hass:{language}};
    let error='';try{form.assertConfig.call(ctx,{show_video:'no'})}catch(e){error=e.message}
    return {language,label:form.computeLabel.call(ctx,{name:'technical'}),entity:form.computeLabel.call(ctx,{name:'entity'}),error};
  });
  card.hass={states,locale:{language:'fr-CA'}};
  const fr=card.shadowRoot.textContent;
  const same=card.shadowRoot.querySelector('.card');card.hass={states,locale:{language:'fr-CA'}};
  const unchanged=same===card.shadowRoot.querySelector('.card');
  card.hass={states:{},language:'en'};const missingEn=card.shadowRoot.textContent;
  card.hass={states:{},language:'fr'};const missingFr=card.shadowRoot.textContent;
  card.hass={states:{'sensor.test':{state:'Idle',attributes:{playing:false}}},language:'en'};
  const idleEn=card.shadowRoot.textContent;
  const keys=Object.keys(EMBY_CARD_TRANSLATIONS.en).sort();
  return {en,fr,englishLanguage,contexts,unchanged,missingEn,missingFr,idleEn,keysEqual:JSON.stringify(keys)===JSON.stringify(Object.keys(EMBY_CARD_TRANSLATIONS.fr).sort()),fallback:embyCardText('show_more','xx'),missingKey:embyCardText('missing_key','fr'),description:window.customCards[0].description};
 });
 assert(result.en.includes('Cast and crew'));assert(result.en.includes('Director'));assert(result.en.includes('Subtitles'));assert(result.en.includes('Forced'));assert(result.en.includes('SDH'));assert(result.en.includes('★ 6.4'));
 assert.equal(result.englishLanguage,'French');
 assert(result.fr.includes('Distribution'));assert(result.fr.includes('Réalisateur'));assert(result.fr.includes('Sous-titres'));assert(result.fr.includes('★ 6,4'));
 assert(result.fr.includes('Original title'));assert(result.fr.includes('Original synopsis'));
 assert(result.unchanged);assert(result.keysEqual);assert.equal(result.fallback,'Show more');
 assert(result.missingEn.includes('Entity not found'));assert(result.missingFr.includes('Entité introuvable'));assert(result.idleEn.includes('Nothing playing'));
 for(const context of result.contexts){
   const language=context.language.split('-')[0];
   const expected={fr:['Informations techniques','Entité Emby','booléen'],de:['Technische Informationen','Emby-Entität','boolescher'],es:['Información técnica','Entidad de Emby','booleano']}[language]||['Technical information','Emby entity','boolean'];
   assert.equal(context.label,expected[0]);assert.equal(context.entity,expected[1]);assert(context.error.includes(expected[2]));
 }
 const translations=await page.evaluate(()=>['de-DE','es-MX'].map(language=>({language,cast:embyCardText('cast',language),more:embyCardText('show_more',language),director:embyCardText('director',language)})));
 assert.deepEqual(translations,[{language:'de-DE',cast:'Besetzung und Mitwirkende',more:'Mehr anzeigen',director:'Regie'},{language:'es-MX',cast:'Reparto y equipo',more:'Mostrar más',director:'Dirección'}]);
 console.log('Localization checks passed: English default, French/regional variants, fallback, editor labels/errors, locale switching, stable DOM, rating and track languages.');
 await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
