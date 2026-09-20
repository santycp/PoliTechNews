/* PoliTechNews - Entrega 2. Sin bibliotecas externas. */
(() => {
  "use strict";

  const page = document.body.dataset.page || "inicio";
  const root = document.querySelector("#app");
  const CATEGORIES = ["Todas", "Inteligencia Artificial", "Desarrollo", "Cloud", "Datos", "Ciberseguridad", "Innovación"];
  const DEFAULT_IMAGE = "assets/images/innovacion.png";
  const KEY = {
    favorites: "politechnews:favorites:v1",
    custom: "politechnews:custom:v1",
    deleted: "politechnews:deleted:v1"
  };
  const state = { base: [], custom: [], deleted: [], favorites: [], category: "Todas", query: "", page: 1, order: "newest", adminQuery: "", adminStatus: "Todas", adminPage: 1 };

  // El almacenamiento local conserva favoritos y cambios editoriales entre recargas.
  // Si el navegador bloquea o corrompe un valor, la aplicación vuelve a una lista segura.
  function read(key, fallback) {
    try {
      const value = JSON.parse(localStorage.getItem(key));
      return Array.isArray(value) ? value : fallback;
    } catch {
      return fallback;
    }
  }

  function save(key, value) {
    try {
      localStorage.setItem(key, JSON.stringify(value));
      return true;
    } catch {
      announce("No hay espacio disponible en este navegador para guardar los cambios.", "error");
      return false;
    }
  }

  // Escapa contenido editable antes de insertarlo en plantillas HTML.
  function esc(value) {
    return String(value ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);
  }

  function plain(value) {
    return String(value ?? "").trim();
  }

  function dateLabel(value) {
    const date = new Date(`${value}T12:00:00Z`);
    return Number.isNaN(date.getTime()) ? value : new Intl.DateTimeFormat("es-CO", { day: "numeric", month: "short", year: "numeric", timeZone: "UTC" }).format(date);
  }

  // Combina el JSON inicial con las noticias creadas y oculta las eliminadas.
  function allArticles() {
    return [...state.custom, ...state.base].filter((item) => !state.deleted.includes(item.id));
  }

  function published() {
    return allArticles().filter((item) => item.status !== "draft").sort((a, b) => b.date.localeCompare(a.date));
  }

  function getArticle(id) {
    return allArticles().find((item) => item.id === id);
  }

  function href(id) {
    return `detalle.html?id=${encodeURIComponent(id)}`;
  }

  function categoryClass(category) {
    return `tag-${({ "Inteligencia Artificial": "ia", Desarrollo: "dev", Cloud: "cloud", Datos: "data", Ciberseguridad: "security", Innovación: "innovation" })[category] || "innovation"}`;
  }

  function imageSrc(article) {
    const value = String(article.image || "");
    return value.startsWith("assets/images/") || value.startsWith("data:image/") ? value : DEFAULT_IMAGE;
  }

  function nav() {
    const links = [
      ["inicio", "Inicio", "index.html"], ["noticias", "Noticias", "noticias.html"],
      ["favoritos", "Favoritos", "favoritos.html"], ["gestion", "Gestionar", "gestion.html"],
      ["contacto", "Contacto", "contacto.html"]
    ];
    return `<a class="skip-link" href="#contenido">Saltar al contenido</a>
      <header class="site-header"><div class="container nav-wrap">
        <a class="brand" href="index.html" aria-label="PoliTechNews, ir al inicio"><img src="assets/images/logo.png" alt="" width="44" height="44"><span>PoliTech<span class="brand-accent">News</span></span></a>
        <button class="menu-toggle" type="button" aria-label="Abrir menú" aria-expanded="false" aria-controls="main-nav"><span></span><span></span><span></span></button>
        <nav class="main-nav" id="main-nav" aria-label="Navegación principal">${links.map(([key, label, target]) => `<a href="${target}" ${page === key || (page === "detalle" && key === "noticias") ? 'aria-current="page"' : ""}>${label}</a>`).join("")}</nav>
        <a class="button button-navy nav-cta" href="noticias.html">Explorar noticias</a>
      </div></header>`;
  }

  function footer() {
    return `<footer class="site-footer"><div class="container footer-grid">
      <div><a class="footer-brand" href="index.html">PoliTech<span>News</span></a><p>Conectando conocimiento, tecnología y futuro.</p></div>
      <div><strong>Navegación</strong><p><a href="index.html">Inicio</a> · <a href="noticias.html">Noticias</a> · <a href="favoritos.html">Favoritos</a></p><p><a href="gestion.html">Gestión</a> · <a href="contacto.html">Contacto</a></p></div>
      <div><strong>Proyecto académico</strong><p>Politécnico Grancolombiano</p><p>© 2026 PoliTechNews</p></div>
    </div></footer><div id="toast" class="toast" role="status" aria-live="polite"></div>`;
  }

  function shell(main) {
    root.innerHTML = `${nav()}<main id="contenido">${main}</main>${footer()}`;
  }

  function announce(message, kind = "success") {
    const toast = document.querySelector("#toast");
    if (!toast) return;
    toast.textContent = message;
    toast.className = `toast show ${kind}`;
    clearTimeout(announce.timer);
    announce.timer = setTimeout(() => { toast.className = "toast"; }, 4200);
  }

  function banner(eyebrow, title, description, extra = "") {
    return `<section class="banner container"><div class="banner-copy"><span class="eyebrow">${esc(eyebrow)}</span><h1>${esc(title)}</h1><p>${esc(description)}</p>${extra}</div><div class="banner-mark" aria-hidden="true"><span></span><span></span><span></span></div></section>`;
  }

  function card(article) {
    return `<article class="news-card"><a class="card-image" href="${href(article.id)}" aria-label="Leer ${esc(article.title)}"><img src="${esc(imageSrc(article))}" alt="Ilustración de ${esc(article.category)}"></a>
      <div class="card-content"><span class="category-tag ${categoryClass(article.category)}">${esc(article.category)}</span><h3><a href="${href(article.id)}">${esc(article.title)}</a></h3><p>${esc(article.summary)}</p>
      <div class="card-bottom"><span>${esc(dateLabel(article.date))} · ${esc(article.minutes)} min</span><a href="${href(article.id)}">Leer más <span aria-hidden="true">→</span></a></div></div></article>`;
  }

  function emptyState(title, description, action = "") {
    return `<div class="empty-state"><div class="empty-symbol" aria-hidden="true">○</div><h3>${esc(title)}</h3><p>${esc(description)}</p>${action}</div>`;
  }

  // Las vistas comparten cabecera, pie y tarjetas para mantener consistencia visual.
  function renderHome() {
    const featured = published().slice(0, 3);
    shell(`<div class="home-main">
      <section class="home-hero container"><div class="hero-copy"><span class="hero-pill">● &nbsp; PERIÓDICO UNIVERSITARIO</span><h1>Tecnología que<br>transforma el futuro.</h1><p>Noticias, análisis y tendencias sobre inteligencia artificial, desarrollo, datos, nube y ciberseguridad.</p><div class="hero-actions"><a class="button button-teal" href="noticias.html">Explorar noticias <span aria-hidden="true">→</span></a><a class="button button-outline-light" href="contacto.html">Conócenos</a></div><small>CONTENIDO ACADÉMICO · ACTUALIZADO EN 2026</small></div><div class="hero-art"><img src="assets/images/hero-illustration.png" alt="Ilustración de panel de tecnología con gráficas e indicadores"></div></section>
      <section class="container section featured-section"><div class="section-top"><div><span class="eyebrow dark">LO MÁS RECIENTE</span><h2>Noticias destacadas</h2><p>Una selección para entender las ideas que están moviendo el mundo digital.</p></div><a class="text-link" href="noticias.html">Ver todas <span aria-hidden="true">→</span></a></div><div class="news-grid">${featured.map(card).join("")}</div></section>
      <section class="category-section"><div class="container"><h2>Explora por categorías</h2><p>Encuentra el tema que necesitas para aprender, investigar o inspirarte.</p><div class="category-row">${CATEGORIES.slice(1, 6).map((c) => `<a class="category-pill ${categoryClass(c)}" href="noticias.html?categoria=${encodeURIComponent(c)}">${esc(c)}</a>`).join("")}</div></div></section>
      <section class="community-section"><div class="container community-card"><div><span class="eyebrow">COMUNIDAD POLITÉCNICA</span><h2>Información tecnológica<br>en un solo lugar.</h2><p>Contenido claro, relevante y conectado con la vida universitaria.</p></div><a class="button button-teal" href="contacto.html">Descubrir PoliTechNews <span aria-hidden="true">→</span></a></div></section>
    </div>`);
  }

  function filteredNews() {
    const q = state.query.toLocaleLowerCase("es");
    return published().filter((article) => (state.category === "Todas" || article.category === state.category) && (!q || `${article.title} ${article.summary} ${article.category}`.toLocaleLowerCase("es").includes(q)));
  }

  function pagination(total, current, action) {
    if (total <= 1) return "";
    return `<nav class="pagination" aria-label="Paginación"><button data-action="${action}" data-page="${current - 1}" ${current === 1 ? "disabled" : ""} aria-label="Página anterior">‹</button>${Array.from({ length: total }, (_, i) => `<button data-action="${action}" data-page="${i + 1}" ${current === i + 1 ? 'aria-current="page"' : ""}>${i + 1}</button>`).join("")}<button data-action="${action}" data-page="${current + 1}" ${current === total ? "disabled" : ""} aria-label="Página siguiente">›</button></nav>`;
  }

  function newsResults() {
    const items = filteredNews();
    const perPage = 6;
    const pages = Math.max(1, Math.ceil(items.length / perPage));
    state.page = Math.min(state.page, pages);
    const shown = items.slice((state.page - 1) * perPage, state.page * perPage);
    return `<div class="section-top results-heading"><div><h2>Últimas publicaciones</h2><p>${items.length} ${items.length === 1 ? "noticia encontrada" : "noticias encontradas"}</p></div><span class="muted">Mostrando ${shown.length} de ${items.length}</span></div>
      ${shown.length ? `<div class="news-grid">${shown.map(card).join("")}</div>${pagination(pages, state.page, "news-page")}` : emptyState("No encontramos noticias", "Prueba otra palabra clave o cambia la categoría.", '<button type="button" class="button button-navy" data-action="clear-filters">Ver todas las noticias</button>')}`;
  }

  function renderNews() {
    const fromUrl = new URLSearchParams(location.search).get("categoria");
    if (fromUrl && CATEGORIES.includes(fromUrl)) state.category = fromUrl;
    shell(`${banner("ACTUALIDAD TECNOLÓGICA", "Todas las noticias", "Explora novedades, análisis y tendencias que conectan la tecnología con nuestra comunidad universitaria.", `<div class="banner-counter"><strong>${published().length}</strong><span>artículos disponibles</span></div>`)}
      <section class="container section"><form id="news-search" class="filter-panel" role="search"><div class="filter-row"><label class="visually-hidden" for="news-query">Buscar noticias</label><input id="news-query" name="query" type="search" placeholder="Buscar por título, categoría o palabra clave..." value="${esc(state.query)}"><button type="submit" class="button button-navy">Buscar</button></div><div class="chip-row" aria-label="Filtrar por categoría">${CATEGORIES.map((c) => `<button type="button" class="filter-chip ${state.category === c ? "selected" : ""}" data-action="category" data-category="${esc(c)}" aria-pressed="${state.category === c}">${esc(c)}</button>`).join("")}</div></form><div id="news-results">${newsResults()}</div></section>`);
  }

  function renderDetail() {
    const id = new URLSearchParams(location.search).get("id") || published()[0]?.id;
    const article = getArticle(id);
    if (!article || article.status === "draft") {
      shell(`<section class="container section">${emptyState("Noticia no disponible", "Es posible que la publicación haya sido eliminada.", '<a class="button button-navy" href="noticias.html">Volver a noticias</a>')}</section>`);
      return;
    }
    document.title = `${article.title} | PoliTechNews`;
    const related = published().filter((item) => item.id !== article.id).sort((a, b) => Number(b.category === article.category) - Number(a.category === article.category)).slice(0, 3);
    const favorite = state.favorites.includes(article.id);
    shell(`<article class="container article-page"><div class="breadcrumbs"><a href="index.html">Inicio</a> / <a href="noticias.html">Noticias</a> / ${esc(article.category)}</div><span class="category-tag ${categoryClass(article.category)}">${esc(article.category)}</span><h1>${esc(article.title)}</h1><p class="article-lead">${esc(article.summary)}</p>
      <div class="article-meta"><div class="author-avatar" aria-hidden="true">${esc(article.author.split(" ").map((s) => s[0]).join("").slice(0, 2))}</div><div><strong>${esc(article.author)}</strong><small>Redacción PoliTechNews</small></div><span class="meta-divider"></span><span>${esc(dateLabel(article.date))}<br><small>Lectura de ${esc(article.minutes)} minutos</small></span><div class="article-actions"><button class="button button-navy" data-action="favorite" data-id="${esc(article.id)}" aria-pressed="${favorite}">${favorite ? "♥ Quitar de favoritos" : "♡ Agregar a favoritos"}</button><button class="icon-button" data-action="share" aria-label="Compartir noticia">↗</button></div></div>
      <img class="article-image" src="${esc(imageSrc(article))}" alt="Ilustración de ${esc(article.category)}">
      <div class="article-layout"><div class="article-body"><h2>Una nueva mirada para la comunidad</h2>${article.content.map((paragraph) => `<p>${esc(paragraph)}</p>`).join("")}<blockquote>“La tecnología es más valiosa cuando ayuda a formular mejores preguntas, no solamente cuando entrega respuestas rápidas.”</blockquote><h2>Tres oportunidades para la comunidad</h2><ol><li>Aprendizaje personalizado con apoyo de herramientas digitales.</li><li>Investigación más ágil y colaboración entre disciplinas.</li><li>Nuevas formas de crear, compartir y evaluar ideas.</li></ol><a class="text-link" href="noticias.html">← Volver a noticias</a></div>
      <aside class="article-aside"><div class="aside-box"><h3>En resumen</h3><ul><li>${esc(article.summary)}</li><li>Contenido para la comunidad universitaria.</li><li>Lectura de ${esc(article.minutes)} minutos.</li></ul></div><h3>Noticias relacionadas</h3>${related.map((item) => `<a class="related-card" href="${href(item.id)}"><img src="${esc(imageSrc(item))}" alt=""><span><small>${esc(item.category)}</small><strong>${esc(item.title)}</strong><small>${esc(item.minutes)} min · Leer más →</small></span></a>`).join("")}</aside></div>
      <div class="article-cta"><div><h2>¿Quieres recibir las próximas historias?</h2><p>Mantente conectado con la actualidad tecnológica universitaria.</p></div><a class="button button-teal" href="noticias.html">Explorar más noticias →</a></div></article>`);
  }

  function renderFavorites() {
    let items = state.favorites.map(getArticle).filter((item) => item && item.status !== "draft");
    if (state.order === "oldest") items = items.reverse();
    shell(`${banner("TU BIBLIOTECA PERSONAL", "Noticias favoritas", "Guarda las historias que quieres consultar nuevamente y mantenlas disponibles en un solo lugar.", `<div class="banner-counter"><strong>${items.length}</strong><span>${items.length === 1 ? "guardada" : "guardadas"}</span></div>`)}
      <section class="container section"><div class="section-top"><div><h2>Tu selección</h2><p>${items.length} ${items.length === 1 ? "artículo guardado" : "artículos guardados"}</p></div><div class="toolbar"><label class="visually-hidden" for="favorites-sort">Ordenar favoritos</label><select id="favorites-sort"><option value="newest" ${state.order === "newest" ? "selected" : ""}>Más recientes</option><option value="oldest" ${state.order === "oldest" ? "selected" : ""}>Más antiguos</option></select><button class="button button-soft" data-action="clear-favorites" ${!items.length ? "disabled" : ""}>Limpiar</button></div></div>
      ${items.length ? `<div class="favorite-list">${items.map((a) => `<article class="favorite-card"><a href="${href(a.id)}" class="favorite-image"><img src="${esc(imageSrc(a))}" alt="Ilustración de ${esc(a.category)}"></a><div class="favorite-body"><span class="category-tag ${categoryClass(a.category)}">${esc(a.category)}</span><h3><a href="${href(a.id)}">${esc(a.title)}</a></h3><p>${esc(a.summary)}</p><div class="favorite-foot"><small>${esc(dateLabel(a.date))} · ${esc(a.minutes)} min de lectura</small><a href="${href(a.id)}">Leer noticia →</a></div></div><button class="remove-favorite" data-action="favorite" data-id="${esc(a.id)}" aria-label="Quitar ${esc(a.title)} de favoritos">×</button></article>`).join("")}</div>` : emptyState("Tu lista está vacía", "Selecciona el corazón en cualquier noticia para guardarla aquí.", '<a class="button button-navy" href="noticias.html">Explorar noticias</a>')}
      <div class="tip-panel"><div><strong>Guarda lo que te inspira</strong><p>Selecciona el corazón en cualquier noticia para encontrarla después en esta sección.</p></div><a class="button button-navy" href="noticias.html">Explorar noticias →</a></div></section>`);
  }

  function adminResults() {
    const q = state.adminQuery.toLocaleLowerCase("es");
    const items = allArticles().filter((a) => (!q || `${a.title} ${a.category}`.toLocaleLowerCase("es").includes(q)) && (state.adminStatus === "Todas" || (state.adminStatus === "Publicadas" ? a.status !== "draft" : a.status === "draft"))).sort((a, b) => b.date.localeCompare(a.date));
    const pages = Math.max(1, Math.ceil(items.length / 6));
    state.adminPage = Math.min(state.adminPage, pages);
    const shown = items.slice((state.adminPage - 1) * 6, state.adminPage * 6);
    return `<div class="table-wrap"><table class="admin-table"><thead><tr><th>Noticia</th><th>Estado</th><th>Fecha</th><th>Acciones</th></tr></thead><tbody>${shown.map((a) => `<tr><td><div class="table-news"><img src="${esc(imageSrc(a))}" alt=""><span><strong>${esc(a.title)}</strong><small>${esc(a.category)}</small></span></div></td><td><span class="status ${a.status === "draft" ? "draft" : "published"}">${a.status === "draft" ? "Borrador" : "Publicada"}</span></td><td>${esc(dateLabel(a.date))}</td><td><div class="table-actions"><a href="${href(a.id)}" ${a.status === "draft" ? 'aria-disabled="true" tabindex="-1"' : ""} title="Ver noticia">Ver</a><button data-action="delete" data-id="${esc(a.id)}" aria-label="Eliminar ${esc(a.title)}">Eliminar</button></div></td></tr>`).join("")}</tbody></table>${!shown.length ? `<div class="empty-admin">No hay noticias para estos filtros.</div>` : ""}</div><div class="table-footer"><small>Mostrando ${shown.length} de ${items.length} noticias</small>${pagination(pages, state.adminPage, "admin-page")}</div>`;
  }

  function renderAdmin() {
    const items = allArticles();
    const publishedCount = items.filter((a) => a.status !== "draft").length;
    const drafts = items.length - publishedCount;
    shell(`${banner("PANEL EDITORIAL", "Gestionar noticias", "Crea, organiza y administra el contenido de PoliTechNews.")}
      <section class="container section admin-section"><div class="stats-grid"><div class="stat"><span class="stat-symbol blue" aria-hidden="true">▣</span><span>Noticias totales<strong>${items.length}</strong></span></div><div class="stat"><span class="stat-symbol teal" aria-hidden="true">✓</span><span>Publicadas<strong>${publishedCount}</strong></span></div><div class="stat"><span class="stat-symbol orange" aria-hidden="true">▤</span><span>Borradores<strong>${drafts}</strong></span></div><div class="stat"><span class="stat-symbol violet" aria-hidden="true">♡</span><span>Guardadas<strong>${state.favorites.length}</strong></span></div></div>
      <div class="admin-grid"><section class="panel"><h2>Crear nueva noticia</h2><p>Completa la información principal del artículo.</p><form id="admin-form" class="stacked-form"><label for="article-title">Título de la noticia <span>*</span></label><input id="article-title" name="title" required minlength="8" maxlength="120" placeholder="Escribe un título claro y atractivo">
      <label for="article-category">Categoría <span>*</span></label><select id="article-category" name="category" required><option value="">Seleccionar categoría</option>${CATEGORIES.slice(1).map((c) => `<option value="${esc(c)}">${esc(c)}</option>`).join("")}</select>
      <label for="article-summary">Descripción corta <span>*</span></label><textarea id="article-summary" name="summary" required minlength="20" maxlength="160" rows="3" placeholder="Resume la noticia en máximo 160 caracteres..."></textarea>
      <label for="article-content">Contenido <span>*</span></label><textarea id="article-content" name="content" required minlength="80" rows="9" placeholder="Desarrolla aquí el contenido completo..."></textarea>
      <label for="article-image">Imagen destacada <small>(opcional, PNG o JPG, hasta 1 MB)</small></label><input id="article-image" name="image" type="file" accept="image/png,image/jpeg,image/webp"><p class="form-hint">Si no agregas una imagen, se usará la ilustración de la categoría.</p>
      <div class="form-buttons"><button class="button button-navy" type="submit" name="mode" value="publish">Publicar noticia</button><button class="button button-outline" type="submit" name="mode" value="draft">Guardar borrador</button></div></form></section>
      <section class="panel registered"><h2>Noticias registradas</h2><p>Administra los artículos existentes.</p><form id="admin-search" class="admin-search"><label class="visually-hidden" for="admin-query">Buscar noticia</label><input id="admin-query" type="search" placeholder="Buscar noticia..." value="${esc(state.adminQuery)}"><label class="visually-hidden" for="admin-status">Filtrar por estado</label><select id="admin-status"><option ${state.adminStatus === "Todas" ? "selected" : ""}>Todas</option><option ${state.adminStatus === "Publicadas" ? "selected" : ""}>Publicadas</option><option ${state.adminStatus === "Borradores" ? "selected" : ""}>Borradores</option></select><button class="button button-navy" type="submit">Filtrar</button></form><div id="admin-results">${adminResults()}</div></section></div></section>`);
  }

  function renderContact() {
    shell(`${banner("HABLEMOS", "Conecta con PoliTechNews", "¿Tienes una idea, una historia o una sugerencia? Nuestro equipo quiere escucharte.", '<div class="banner-badges"><span>◷ Respuesta en 24–48 h</span><span>◷ Lunes a viernes · 8–5</span></div>')}
      <section class="container section"><div class="contact-grid"><aside class="contact-info"><h2>Estamos cerca</h2><p>Elige el canal que mejor se adapte a ti.</p><dl><dt>Correo de ejemplo</dt><dd>contacto@politechnews.edu.co</dd><dt>Ubicación</dt><dd>Medellín, Colombia</dd><dt>Horario de atención</dt><dd>Lunes a viernes, 8:00 a. m. – 5:00 p. m.</dd></dl><div class="student-note"><strong>¿Eres estudiante?</strong><p>También puedes proponer temas y participar como colaborador.</p></div></aside>
      <section class="panel contact-form-panel"><h2>Envíanos un mensaje</h2><p>Todos los campos marcados con * son obligatorios.</p><form id="contact-form" class="stacked-form"><div class="form-two"><div><label for="contact-name">Nombre completo <span>*</span></label><input id="contact-name" name="name" autocomplete="name" required minlength="3" maxlength="80" placeholder="Tu nombre"></div><div><label for="contact-email">Correo electrónico <span>*</span></label><input id="contact-email" name="email" type="email" autocomplete="email" required placeholder="nombre@correo.com"></div></div>
      <label for="contact-subject">Asunto <span>*</span></label><select id="contact-subject" name="subject" required><option value="">Selecciona una opción</option><option>Sugerencia de tema</option><option>Corrección de contenido</option><option>Colaboración</option><option>Consulta general</option></select>
      <label for="contact-message">Mensaje <span>*</span></label><textarea id="contact-message" name="message" required minlength="20" maxlength="500" rows="7" placeholder="Cuéntanos cómo podemos ayudarte..."></textarea><small id="message-count" class="form-hint">0 / 500 caracteres</small>
      <label class="check-label"><input name="privacy" type="checkbox" required><span>Acepto el tratamiento de mis datos para responder esta solicitud.</span></label><div class="form-buttons"><button class="button button-navy" type="submit">Enviar mensaje →</button><span class="form-hint">Verás una confirmación al enviar. Este prototipo no envía correos.</span></div><div id="contact-result" role="status" aria-live="polite"></div></form></section></div>
      <div class="faq"><h2>Preguntas frecuentes</h2><div class="faq-grid"><article><strong>¿Puedo proponer una noticia?</strong><p>Sí, envíanos el tema y una breve descripción.</p></article><article><strong>¿Cuándo recibiré respuesta?</strong><p>La respuesta real dependerá de la implementación del servicio de correo.</p></article><article><strong>¿Puedo solicitar una corrección?</strong><p>Claro. Indica el artículo y el dato que debemos revisar.</p></article></div></div></section>`);
  }

  // Las imágenes pequeñas se convierten a data URL para que el prototipo no requiera servidor.
  async function imageForForm(file, category) {
    if (!file) return ({ "Inteligencia Artificial": "assets/images/ia.png", Desarrollo: "assets/images/desarrollo.png", Cloud: "assets/images/cloud.png", Datos: "assets/images/datos.png", Ciberseguridad: "assets/images/ciberseguridad.png", Innovación: "assets/images/innovacion.png" })[category] || DEFAULT_IMAGE;
    if (!["image/png", "image/jpeg", "image/webp"].includes(file.type) || file.size > 1024 * 1024) throw new Error("La imagen debe ser PNG, JPG o WebP y pesar menos de 1 MB.");
    return await new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve(reader.result);
      reader.onerror = () => reject(new Error("No se pudo leer la imagen."));
      reader.readAsDataURL(file);
    });
  }

  // Crea un registro publicado o borrador y vuelve a renderizar las vistas dependientes.
  async function createArticle(form, mode) {
    if (!form.reportValidity()) return;
    const fields = new FormData(form);
    try {
      const image = await imageForForm(form.elements.image.files[0], fields.get("category"));
      const content = plain(fields.get("content")).split(/\n\s*\n/).map(plain).filter(Boolean);
      const article = {
        id: `user-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`,
        title: plain(fields.get("title")), category: plain(fields.get("category")),
        summary: plain(fields.get("summary")), content, image,
        author: "Redacción PoliTechNews", date: new Date().toISOString().slice(0, 10),
        minutes: Math.max(1, Math.ceil(plain(fields.get("content")).split(/\s+/).length / 200)),
        status: mode === "draft" ? "draft" : "published"
      };
      const next = [article, ...state.custom];
      if (!save(KEY.custom, next)) return;
      state.custom = next;
      renderAdmin();
      announce(mode === "draft" ? "Borrador guardado en este navegador." : "Noticia publicada en este navegador.");
    } catch (error) {
      announce(error.message, "error");
    }
  }

  function toggleFavorite(id) {
    if (state.favorites.includes(id)) state.favorites = state.favorites.filter((value) => value !== id);
    else state.favorites.unshift(id);
    save(KEY.favorites, state.favorites);
    if (page === "favoritos") renderFavorites();
    else if (page === "detalle") renderDetail();
    announce(state.favorites.includes(id) ? "Noticia agregada a favoritos." : "Noticia eliminada de favoritos.");
  }

  // Delegación de eventos: también cubre tarjetas y filas generadas después del primer render.
  function onClick(event) {
    const target = event.target.closest("[data-action]");
    if (!target) return;
    const action = target.dataset.action;
    if (action === "category") {
      state.category = target.dataset.category;
      state.page = 1;
      history.replaceState(null, "", state.category === "Todas" ? "noticias.html" : `noticias.html?categoria=${encodeURIComponent(state.category)}`);
      renderNews();
    } else if (action === "news-page") {
      state.page = Number(target.dataset.page);
      document.querySelector("#news-results").innerHTML = newsResults();
      document.querySelector("#news-results").scrollIntoView({ behavior: "smooth", block: "start" });
    } else if (action === "clear-filters") {
      state.category = "Todas";
      state.query = "";
      state.page = 1;
      history.replaceState(null, "", "noticias.html");
      renderNews();
    } else if (action === "favorite") {
      toggleFavorite(target.dataset.id);
    } else if (action === "clear-favorites") {
      if (confirm("¿Quitar todas las noticias de favoritos?")) {
        state.favorites = [];
        save(KEY.favorites, state.favorites);
        renderFavorites();
        announce("La lista de favoritos quedó vacía.");
      }
    } else if (action === "delete") {
      const article = getArticle(target.dataset.id);
      if (article && confirm(`¿Eliminar la noticia «${article.title}»?`)) {
        if (state.custom.some((item) => item.id === article.id)) {
          state.custom = state.custom.filter((item) => item.id !== article.id);
          save(KEY.custom, state.custom);
        } else {
          state.deleted.push(article.id);
          save(KEY.deleted, state.deleted);
        }
        state.favorites = state.favorites.filter((id) => id !== article.id);
        save(KEY.favorites, state.favorites);
        renderAdmin();
        announce("Noticia eliminada de este navegador.");
      }
    } else if (action === "admin-page") {
      state.adminPage = Number(target.dataset.page);
      document.querySelector("#admin-results").innerHTML = adminResults();
    } else if (action === "share") {
      if (navigator.share) navigator.share({ title: document.title, url: location.href }).catch(() => {});
      else navigator.clipboard?.writeText(location.href).then(() => announce("Enlace copiado al portapapeles.")).catch(() => announce("Copia la dirección de la barra del navegador."));
    }
  }

  function onSubmit(event) {
    const form = event.target;
    if (form.id === "news-search") {
      event.preventDefault();
      state.query = plain(form.elements.query.value);
      state.page = 1;
      document.querySelector("#news-results").innerHTML = newsResults();
    } else if (form.id === "admin-search") {
      event.preventDefault();
      state.adminQuery = plain(document.querySelector("#admin-query").value);
      state.adminStatus = document.querySelector("#admin-status").value;
      state.adminPage = 1;
      document.querySelector("#admin-results").innerHTML = adminResults();
    } else if (form.id === "admin-form") {
      event.preventDefault();
      createArticle(form, event.submitter?.value || "publish");
    } else if (form.id === "contact-form") {
      event.preventDefault();
      if (!form.reportValidity()) return;
      document.querySelector("#contact-result").innerHTML = '<p class="form-success">Mensaje validado correctamente. Este prototipo académico no envía correos ni guarda tus datos.</p>';
      form.reset();
      document.querySelector("#message-count").textContent = "0 / 500 caracteres";
      announce("Formulario validado. Envío simulado correctamente.");
    }
  }

  function bindEvents() {
    document.addEventListener("click", onClick);
    document.addEventListener("submit", onSubmit);
    document.addEventListener("change", (event) => {
      if (event.target.id === "favorites-sort") {
        state.order = event.target.value;
        renderFavorites();
      }
    });
    document.addEventListener("input", (event) => {
      if (event.target.id === "contact-message") document.querySelector("#message-count").textContent = `${event.target.value.length} / 500 caracteres`;
    });
    document.addEventListener("click", (event) => {
      const toggle = event.target.closest(".menu-toggle");
      if (!toggle) return;
      const open = toggle.getAttribute("aria-expanded") !== "true";
      toggle.setAttribute("aria-expanded", String(open));
      toggle.setAttribute("aria-label", open ? "Cerrar menú" : "Abrir menú");
      document.querySelector("#main-nav").classList.toggle("open", open);
    });
  }

  // El JSON es la fuente inicial; los cambios locales se fusionan al iniciar cada página.
  async function init() {
    state.favorites = read(KEY.favorites, []);
    state.custom = read(KEY.custom, []);
    state.deleted = read(KEY.deleted, []);
    root.innerHTML = '<div class="loading" role="status">Cargando PoliTechNews…</div>';
    try {
      const response = await fetch("data/noticias.json");
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const data = await response.json();
      if (!Array.isArray(data)) throw new Error("Formato JSON incorrecto");
      state.base = data;
      bindEvents();
      ({ inicio: renderHome, noticias: renderNews, detalle: renderDetail, favoritos: renderFavorites, gestion: renderAdmin, contacto: renderContact }[page] || renderHome)();
    } catch (error) {
      root.innerHTML = `<div class="load-error"><h1>No se pudieron cargar las noticias</h1><p>Abre el proyecto mediante un servidor local. Por ejemplo: <code>python -m http.server 8000</code> y visita <code>http://localhost:8000</code>.</p><p class="muted">${esc(error.message)}</p></div>`;
    }
  }

  init();
})();
