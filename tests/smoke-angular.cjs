/* Prueba de aceptación sobre la compilación real. No modifica datos del usuario. */
const { chromium } = require('playwright');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const http = require('node:http');

const root = path.resolve(__dirname, '..');
const output = path.join(root, 'tmp', 'entrega3-qa');
const configuredBase = process.env.BASE_URL;
const buildDirectory = path.join(root, 'dist', 'politechnews', 'browser');
const buildPrefix = configuredBase ? '/' : (fs.readFileSync(path.join(buildDirectory, 'index.html'), 'utf8').match(/<base href="([^"]+)"/)?.[1] || '/');
const base = (configuredBase || `http://127.0.0.1:4300${buildPrefix}`).replace(/\/?$/, '/');

// El servidor de la prueba solo sirve la carpeta dist; no expone el repositorio.
function previewServer() {
  const directory = buildDirectory;
  const mime = { '.html': 'text/html', '.js': 'text/javascript', '.css': 'text/css', '.json': 'application/json', '.png': 'image/png' };
  return http.createServer((req, res) => {
    const pathname = decodeURIComponent(new URL(req.url, base).pathname);
    if (!pathname.startsWith(buildPrefix)) { res.writeHead(404); res.end(); return; }
    const relativePath = pathname.slice(buildPrefix.length) || 'index.html';
    const file = path.resolve(directory, relativePath);
    if (!file.startsWith(directory + path.sep) || !fs.existsSync(file) || !fs.statSync(file).isFile()) { res.writeHead(404); res.end(); return; }
    res.setHeader('Content-Type', mime[path.extname(file)] || 'application/octet-stream');
    fs.createReadStream(file).pipe(res);
  });
}

(async () => {
  fs.mkdirSync(output, { recursive: true });
  const server = configuredBase ? undefined : previewServer();
  if (server) await new Promise(resolve => server.listen(4300, '127.0.0.1', resolve));
  const localChrome = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
  const browser = await chromium.launch({ headless: true, ...(fs.existsSync(localChrome) ? { executablePath: localChrome } : {}) });
  try {
    const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });
    const page = await context.newPage();
    const errors = [];
    page.on('pageerror', error => errors.push(error.message));
    const visit = async route => {
      await page.goto(`${base}#/${route}`);
      const component = route.startsWith('noticias/') ? 'detail' : ({ noticias: 'news', favoritos: 'favorites', gestion: 'admin', contacto: 'contact' }[route] || 'home');
      await page.locator(`app-${component}`).waitFor();
    };
    const shot = async name => page.screenshot({ path: path.join(output, `${name}.png`), fullPage: true });
    const count = async (selector, expected) => { await page.waitForFunction(({ selector, expected }) => document.querySelectorAll(selector).length === expected, { selector, expected }); };
    const fillArticle = async title => {
      await page.locator('#article-title').fill(title);
      await page.locator('#article-category').selectOption('Datos');
      await page.locator('#article-summary').fill('Noticia académica que verifica la publicación y la persistencia del contenido.');
      await page.locator('#article-content').fill('Texto académico para verificar el formulario Angular y la creación de una noticia. Contiene una extensión suficiente para comprobar las validaciones del contenido y su visualización posterior.\n\nSegundo párrafo de la noticia de prueba.');
    };
    await visit(''); await count('.news-card', 3); await shot('01-inicio');
    assert.match(await page.locator('app-root').getAttribute('ng-version'), /^22\./);
    // Navegación SPA, historial y enlaces profundos.
    await page.locator('#main-nav').getByRole('link', { name: 'Noticias', exact: true }).click();
    await count('.news-card', 6);
    await page.getByRole('button', { name: 'Página siguiente' }).click(); await count('.news-card', 6);
    await page.getByRole('button', { name: 'Cloud', exact: true }).click(); await count('.news-card', 2);
    assert.ok(page.url().includes('categoria=Cloud'));
    await page.reload(); await count('.news-card', 2);
    await page.getByRole('button', { name: 'Todas', exact: true }).click(); await count('.news-card', 6);
    await page.locator('#news-query').fill('identidad digital'); await page.getByRole('button', { name: 'Buscar', exact: true }).click(); await count('.news-card', 1);
    await page.reload(); await count('.news-card', 1);
    await page.locator('#news-query').fill('zzzzzz'); await page.getByRole('button', { name: 'Buscar', exact: true }).click(); await page.getByText('No encontramos noticias').waitFor();
    await page.getByRole('button', { name: 'Ver todas las noticias' }).click(); await count('.news-card', 6); await shot('02-noticias');
    await visit('noticias/ia-aulas'); await page.getByRole('heading', { name: 'La IA transforma los procesos de aprendizaje', exact: true }).waitFor(); await shot('03-detalle');
    await page.getByRole('button', { name: /Agregar a favoritos/ }).click();
    await page.locator('#main-nav').getByRole('link', { name: 'Favoritos', exact: true }).click(); await count('.favorite-card', 1);
    await page.reload(); await count('.favorite-card', 1); await shot('04-favoritos');
    await visit('noticias/campus-nube'); await page.getByRole('button', { name: /Agregar a favoritos/ }).click();
    await visit('favoritos'); await count('.favorite-card', 2);
    const newest = await page.locator('.favorite-card h3').first().textContent();
    assert.match(newest, /IA transforma/);
    await page.locator('#favorites-sort').selectOption('oldest'); assert.match(await page.locator('.favorite-card h3').first().textContent(), /nube/);
    // Formularios inválidos, imagen incompatible y una publicación válida.
    await visit('gestion'); await page.getByRole('button', { name: 'Publicar noticia', exact: true }).click();
    await page.getByText('Escribe un título de 8 a 120 caracteres.').waitFor();
    await fillArticle('Nueva noticia de prueba académica');
    await page.locator('#article-image').setInputFiles({ name: 'archivo.txt', mimeType: 'text/plain', buffer: Buffer.from('texto') });
    await page.getByRole('button', { name: 'Publicar noticia', exact: true }).click();
    await page.getByRole('alert').filter({ hasText: 'La imagen debe ser' }).waitFor();
    await page.locator('#article-image').setInputFiles([]);
    await page.getByRole('button', { name: 'Publicar noticia', exact: true }).click();
    await page.getByRole('row', { name: /Nueva noticia de prueba académica/ }).waitFor(); await shot('05-gestion');
    await visit('noticias'); await page.getByRole('heading', { name: 'Nueva noticia de prueba académica', exact: true }).waitFor();
    await page.reload(); await page.getByRole('heading', { name: 'Nueva noticia de prueba académica', exact: true }).waitFor();
    await visit('gestion'); await fillArticle('Borrador académico de PoliTechNews'); await page.getByRole('button', { name: 'Guardar borrador' }).click();
    await page.getByRole('row', { name: /Borrador académico/ }).waitFor();
    await visit('noticias'); assert.equal(await page.getByRole('heading', { name: 'Borrador académico de PoliTechNews', exact: true }).count(), 0);
    await visit('gestion'); await page.getByRole('row', { name: /Borrador académico/ }).getByRole('button', { name: /Publicar/ }).click();
    await visit('noticias'); await page.getByRole('heading', { name: 'Borrador académico de PoliTechNews', exact: true }).waitFor();
    await visit('gestion'); page.once('dialog', d => d.accept()); await page.getByRole('row', { name: /Nueva noticia de prueba académica/ }).getByRole('button', { name: /Eliminar/ }).click();
    await page.getByRole('row', { name: /Nueva noticia de prueba académica/ }).waitFor({ state: 'hidden' });
    // Interpolación segura: el texto editable no crea nodos HTML.
    await fillArticle('<img src=x onerror=alert(1)> Noticia'); await page.getByRole('button', { name: 'Publicar noticia', exact: true }).click();
    await visit('noticias'); await page.getByRole('heading', { name: '<img src=x onerror=alert(1)> Noticia', exact: true }).waitFor();
    assert.equal(await page.locator('img[src="x"]').count(), 0);
    await visit('noticias/no-existe'); await page.getByText('Noticia no disponible', { exact: true }).waitFor();
    await visit('contacto'); await page.getByRole('button', { name: /Enviar mensaje/ }).click();
    await page.getByText('Escribe un correo electrónico válido.').waitFor();
    assert.equal(await page.locator('.form-success').count(), 0);
    await page.locator('#contact-name').fill('Santiago Calvo Patiño'); await page.locator('#contact-email').fill('santiago@example.com');
    await page.locator('#contact-subject').selectOption('Consulta general'); await page.locator('#contact-message').fill('Este mensaje académico verifica las validaciones del formulario de contacto.');
    await page.locator('input[name="privacy"]').check(); await shot('06-contacto');
    await page.getByRole('button', { name: /Enviar mensaje/ }).click(); await page.getByText(/Mensaje validado correctamente/).waitFor();
    // Menú y todas las vistas sin desbordamiento a 390 px.
    await page.setViewportSize({ width: 390, height: 844 });
    await visit(''); await page.getByRole('button', { name: 'Abrir menú' }).click(); await page.locator('#main-nav').waitFor({ state: 'visible' });
    await page.getByRole('button', { name: 'Cerrar menú' }).click(); await page.locator('#main-nav').waitFor({ state: 'hidden' });
    await shot('07-inicio-movil');
    for (const route of ['', 'noticias', 'noticias/ia-aulas', 'favoritos', 'gestion', 'contacto']) {
      await visit(route); await page.locator('main h1').waitFor();
      assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth), `Desbordamiento en ${route}`);
    }
    // Un almacenamiento corrupto o una cuota bloqueada no debe romper la aplicación.
    const broken = await browser.newContext();
    await broken.addInitScript(() => {
      localStorage.setItem('politechnews:custom:v1', '{invalido');
      localStorage.setItem('politechnews:favorites:v1', '[null,{},3]');
      const original = Storage.prototype.setItem;
      Storage.prototype.setItem = function (key, value) { if (window.blockStorage) throw new DOMException('Cuota', 'QuotaExceededError'); return original.call(this, key, value); };
    });
    const p2 = await broken.newPage(); await p2.goto(`${base}#/noticias/ia-aulas`);
    await p2.getByRole('button', { name: /Agregar a favoritos/ }).waitFor();
    await p2.evaluate(() => { window.blockStorage = true; });
    await p2.getByRole('button', { name: /Agregar a favoritos/ }).click();
    await p2.getByText(/No se pudieron guardar los cambios/).waitFor();
    assert.equal(await p2.getByRole('button', { name: /Agregar a favoritos/ }).getAttribute('aria-pressed'), 'false');
    await broken.close();
    // Error de red explícito y recuperación con Reintentar.
    const retry = await browser.newContext(); const p3 = await retry.newPage();
    await p3.route('**/data/noticias.json', route => route.fulfill({ status: 503, body: 'no disponible' }));
    await p3.goto(base); await p3.getByRole('button', { name: 'Reintentar' }).waitFor();
    await p3.unroute('**/data/noticias.json'); await p3.getByRole('button', { name: 'Reintentar' }).click();
    await p3.locator('.news-card').first().waitFor(); await retry.close();
    assert.deepEqual(errors, []);
    fs.writeFileSync(path.join(output, 'resultados.json'), JSON.stringify({ date: new Date().toISOString(), base, angular: '22.2.1', result: 'PASS', coverage: ['navegación SPA', 'JSON', 'búsqueda', 'filtros', 'paginación', 'recarga de rutas', 'favoritos', 'orden', 'validaciones', 'archivos', 'publicación', 'borradores', 'eliminación', 'escape HTML', 'contacto', 'móvil', 'Storage corrupto', 'cuota', 'error de red y reintento'], errors }, null, 2));
    console.log('ANGULAR_SMOKE_OK: navegación, JSON, filtros, favoritos, formularios, CRUD, persistencia, errores y móvil.');
  } finally { await browser.close(); if (server) await new Promise(resolve => server.close(resolve)); }
})().catch(error => { console.error(error); process.exit(1); });
