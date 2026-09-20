const { chromium } = require("playwright");
const assert = require("node:assert/strict");
const path = require("node:path");

const BASE = "http://localhost:8000";
const CHROME = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe";

(async () => {
  const browser = await chromium.launch({ headless: true, executablePath: CHROME });
  const context = await browser.newContext({ viewport: { width: 1440, height: 900 } });
  const page = await context.newPage();
  const errors = [];
  page.on("pageerror", (error) => errors.push(error.message));

  await page.goto(BASE);
  await page.locator(".news-card").first().waitFor();
  assert.equal(await page.locator(".news-card").count(), 3);
  await page.screenshot({ path: path.join("tmp", "home-qa.png"), fullPage: true });

  await page.goto(`${BASE}/noticias.html`);
  await page.locator(".news-card").first().waitFor();
  assert.equal(await page.locator(".news-card").count(), 6);
  await page.getByRole("button", { name: "Cloud", exact: true }).click();
  assert.equal(await page.locator(".news-card").count(), 2);
  await page.getByRole("button", { name: "Todas", exact: true }).click();
  await page.locator("#news-query").fill("identidad digital");
  await page.getByRole("button", { name: "Buscar", exact: true }).click();
  assert.equal(await page.locator(".news-card").count(), 1);
  await page.screenshot({ path: path.join("tmp", "noticias-qa.png"), fullPage: true });

  await page.goto(`${BASE}/detalle.html?id=ia-aulas`);
  await page.getByRole("button", { name: "Agregar a favoritos" }).click();
  await page.goto(`${BASE}/favoritos.html`);
  await page.locator(".favorite-card").first().waitFor();
  assert.equal(await page.locator(".favorite-card").count(), 1);
  await page.reload();
  assert.equal(await page.locator(".favorite-card").count(), 1);

  await page.goto(`${BASE}/gestion.html`);
  await page.locator("#article-title").fill("Nueva noticia de prueba académica");
  await page.locator("#article-category").selectOption("Datos");
  await page.locator("#article-summary").fill("Este artículo de prueba verifica el flujo de creación en el navegador.");
  await page.locator("#article-content").fill("Este es un texto de prueba suficientemente extenso para validar el formulario de creación de noticias. Explica de manera simple cómo se registra una nueva publicación y cómo aparece posteriormente en el catálogo de PoliTechNews.");
  await page.getByRole("button", { name: "Publicar noticia" }).click();
  await page.getByRole("row", { name: /Nueva noticia de prueba académica/ }).waitFor();
  await page.screenshot({ path: path.join("tmp", "gestion-qa.png"), fullPage: true });
  await page.goto(`${BASE}/noticias.html`);
  assert.ok((await page.locator(".news-card").allTextContents()).some((text) => text.includes("Nueva noticia de prueba académica")));
  await page.goto(`${BASE}/gestion.html`);
  page.once("dialog", (dialog) => dialog.accept());
  await page.getByRole("row", { name: /Nueva noticia de prueba académica/ }).getByRole("button", { name: /Eliminar/ }).click();
  await page.waitForTimeout(200);
  assert.equal(await page.getByRole("row", { name: /Nueva noticia de prueba académica/ }).count(), 0);

  await page.locator("#article-title").fill("Borrador de prueba para PoliTechNews");
  await page.locator("#article-category").selectOption("Cloud");
  await page.locator("#article-summary").fill("Descripción de prueba para verificar que el borrador no se publique en el catálogo.");
  await page.locator("#article-content").fill("Este es otro texto académico de prueba suficientemente largo para validar el formulario. El contenido se guarda como borrador en el navegador y debe permanecer fuera del listado público de noticias hasta que se publique.");
  await page.getByRole("button", { name: "Guardar borrador" }).click();
  await page.getByRole("row", { name: /Borrador de prueba para PoliTechNews/ }).waitFor();
  await page.goto(`${BASE}/noticias.html`);
  assert.ok(!(await page.locator(".news-card").allTextContents()).some((text) => text.includes("Borrador de prueba para PoliTechNews")));

  await page.goto(`${BASE}/contacto.html`);
  await page.locator("#contact-name").fill("Santiago Calvo Patiño");
  await page.locator("#contact-email").fill("santiago@example.com");
  await page.locator("#contact-subject").selectOption("Consulta general");
  await page.locator("#contact-message").fill("Este mensaje académico verifica las validaciones del formulario de contacto.");
  await page.locator('input[name="privacy"]').check();
  await page.screenshot({ path: path.join("tmp", "contacto-qa.png"), fullPage: true });
  await page.getByRole("button", { name: /Enviar mensaje/ }).click();
  await page.getByText(/Mensaje validado correctamente/).waitFor();

  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto(BASE);
  await page.locator(".news-card").first().waitFor();
  await page.getByRole("button", { name: "Abrir menú" }).click();
  assert.ok(await page.locator("#main-nav").isVisible());
  await page.getByRole("button", { name: "Cerrar menú" }).click();
  assert.ok(!(await page.locator("#main-nav").isVisible()));
  const scrollWidth = await page.evaluate(() => document.documentElement.scrollWidth);
  assert.ok(scrollWidth <= 390, `Desbordamiento horizontal: ${scrollWidth}px`);
  await page.screenshot({ path: path.join("tmp", "home-mobile-qa.png"), fullPage: true });

  assert.deepEqual(errors, []);
  console.log("SMOKE_OK: inicio, catálogo, búsqueda, filtros, detalle, favoritos, CRUD, contacto y móvil");
  await browser.close();
})().catch((error) => { console.error(error); process.exit(1); });
