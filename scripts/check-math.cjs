// Load every rendered page in a browser and inspect the completed MathJax output.
const { chromium } = require('playwright');
const fs = require('node:fs');
const path = require('node:path');
const http = require('node:http');
const root = path.resolve(__dirname, '..');
const site = path.join(root, '_site');
const types = {'.html':'text/html', '.js':'text/javascript', '.css':'text/css', '.json':'application/json', '.svg':'image/svg+xml', '.png':'image/png', '.gif':'image/gif', '.woff':'font/woff', '.woff2':'font/woff2'};
const server = http.createServer((req, res) => {
  const pathname = decodeURIComponent(new URL(req.url, 'http://localhost').pathname);
  let file = path.resolve(site, '.' + pathname);
  if (!file.startsWith(site + path.sep)) { res.writeHead(403).end(); return; }
  if (fs.existsSync(file) && fs.statSync(file).isDirectory()) file = path.join(file, 'index.html');
  if (!fs.existsSync(file) && !path.extname(file)) file += '.html';
  if (!fs.existsSync(file)) { res.writeHead(404).end(); return; }
  res.setHeader('Content-Type', types[path.extname(file)] || 'application/octet-stream');
  fs.createReadStream(file).pipe(res);
});
(async () => {
  let browser;
  const errors = [];
  await new Promise(resolve => server.listen(0, '127.0.0.1', resolve));
  const base = `http://127.0.0.1:${server.address().port}/`;
  try {
    browser = await chromium.launch({headless: true, ...(process.env.OTWIKI_BROWSER ? {executablePath: process.env.OTWIKI_BROWSER} : {})});
    const files = fs.readdirSync(root).filter(f => f.endsWith('.qmd')).sort();
    let next = 0;
    async function worker() {
      const page = await browser.newPage({viewport: {width: 1440, height: 1000}});
      while (next < files.length) {
        const file = files[next++].replace(/\.qmd$/, '.html');
        try {
          await page.goto(base + encodeURIComponent(file), {waitUntil: 'networkidle', timeout: 45000});
          const results = await page.evaluate(async () => {
            const main = document.querySelector('main');
            const math = main.querySelectorAll('.math');
            if (math.length) {
              if (!window.MathJax?.startup?.promise) return ['MathJax did not load'];
              await window.MathJax.startup.promise;
            }
            const failures = [];
            for (const node of main.querySelectorAll('mjx-merror, [data-mjx-error], .katex-error, mjx-mtext[style*="color: red"]')) {
              const letters = [...node.querySelectorAll('mjx-c')].map(el => {
                const code = [...el.classList].find(c => /^mjx-c[0-9A-F]+$/.test(c));
                return code ? String.fromCodePoint(parseInt(code.slice(5), 16)) : '';
              }).join('');
              failures.push(node.getAttribute('data-mjx-error') || node.textContent || letters || 'formula error');
            }
            for (const el of math) if (!el.querySelector('mjx-container')) failures.push('Formula was not typeset: ' + el.textContent.slice(0, 120));
            for (const img of main.querySelectorAll('img')) if (!img.complete || !img.naturalWidth) failures.push('Image did not load: ' + img.getAttribute('src'));
            for (const a of main.querySelectorAll('a[href^="#"]')) {
              const id = decodeURIComponent(a.getAttribute('href').slice(1));
              if (id && !document.getElementById(id)) failures.push('Missing rendered anchor: ' + id);
            }
            return failures;
          });
          for (const failure of results) errors.push(`${file}: ${failure}`);
        } catch (error) { errors.push(`${file}: ${error.message}`); }
      }
      await page.close();
    }
    await Promise.all([worker(), worker(), worker()]);
    if (errors.length) throw new Error(errors.join('\n'));
    console.log(`Passed: math rendering, images, and rendered anchors on all ${files.length} pages.`);
  } finally {
    if (browser) await browser.close();
    await new Promise(resolve => server.close(resolve));
  }
})().catch(error => { console.error(error.message); process.exitCode = 1; });
