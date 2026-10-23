const {chromium}=require('playwright');
const fs=require('fs');
(async()=>{
 const browser=await chromium.launch({executablePath:process.env.BROWSER_EXECUTABLE,headless:true});
 try {
  const page=await browser.newPage({viewport:{width:1400,height:1100}});
  await page.setContent('<body style="background:#20272c;color:white;font-family:Arial"><p id="result"></p><main id="host" style="width:1100px"></main></body>');
  await page.addScriptTag({path:'custom_components/emby_metadata/static/emby-metadata-card.js'});
  await page.addScriptTag({path:'tests/player-browser.js'});
  await page.waitForFunction(()=>window.testResult);
  const result=await page.evaluate(()=>window.testResult);
  if(!result.passed)throw Error(result.error);
  console.log(result.checks.length+' player browser checks passed');
 } finally {await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
