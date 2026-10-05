/* Capturas documentales en un perfil aislado, sin datos del usuario. */
const { chromium } = require('playwright');
const fs = require('node:fs');
const path = require('node:path');
const output = path.resolve(__dirname, '..', 'tmp', 'entrega3-evidencias');
const base = 'https://santycp.github.io/PoliTechNews/';
(async () => {
  fs.mkdirSync(output, { recursive: true });
  const chrome = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
  const browser = await chromium.launch({ headless: true, ...(fs.existsSync(chrome) ? { executablePath: chrome } : {}) });
  try {
    const context = await browser.newContext({ viewport: { width: 1440, height: 1000 } });
    const page = await context.newPage();
    const routes = [['01-inicio', '', 'home'], ['02-noticias', 'noticias', 'news'], ['03-detalle', 'noticias/ia-aulas', 'detail'], ['04-favoritos', 'favoritos', 'favorites'], ['05-gestion', 'gestion', 'admin'], ['06-contacto', 'contacto', 'contact']];
    for (const [name, route, component] of routes) {
      await page.goto(`${base}#/${route}`);
      await page.locator(`app-${component} h1`).waitFor();
      await page.evaluate(() => document.fonts.ready);
      await page.evaluate(async () => Promise.all([...document.images].map(img => img.decode().catch(() => {}))));
      await page.screenshot({ path: path.join(output, `${name}.png`) });
      if (component === 'detail') {
        await page.getByRole('button', { name: /Agregar a favoritos/ }).click();
        await page.getByRole('button', { name: /Quitar de favoritos/ }).waitFor();
      }
    }
    await page.setViewportSize({ width: 390, height: 844 });
    await page.goto(base);
    await page.locator('app-home h1').waitFor();
    await page.evaluate(() => document.fonts.ready);
    await page.screenshot({ path: path.join(output, '07-movil.png') });
    console.log('CAPTURAS_PUBLICAS_OK');
  } finally { await browser.close(); }
})().catch(error => { console.error(error); process.exit(1); });
