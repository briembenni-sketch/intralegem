const { chromium } = require(require('child_process').execSync('npm root -g').toString().trim() + '/playwright');
const fs=require('fs');
(async()=>{
  const [file,w,out]=process.argv.slice(2);
  const svg=fs.readFileSync(file,'utf8');
  const vb=svg.match(/viewBox="([^"]+)"/)[1].split(' ').map(Number);
  const W=+w, H=Math.round(W*vb[3]/vb[2]);
  const b=await chromium.launch();const p=await b.newPage({viewport:{width:W,height:H}});
  await p.setContent(`<body style="margin:0;background:#000;color:#fff">${svg.replace('<svg ',`<svg width="${W}" height="${H}" `)}</body>`);
  await p.screenshot({path:out}); await b.close();
})();
