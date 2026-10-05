# PoliTechNews - Entrega 3

Aplicación Angular 22 para consultar noticias tecnológicas universitarias. Conserva la identidad visual de los mockups y las funcionalidades de la Entrega 2. Las vistas están organizadas en componentes standalone, con rutas, binding, formularios reactivos y servicios compartidos.

## Ejecutar Angular

Requisitos: Node.js 24.15 o posterior de la rama 24, y npm.

```bash
npm ci
npm start
```

Abre [http://127.0.0.1:4200](http://127.0.0.1:4200). Para compilar y probar la versión de producción:

```bash
npm run build
npm test
```

La prueba usa Chrome si está instalado en la ruta predeterminada de Windows. En otros entornos ejecuta antes `npx playwright install chromium`.

## Arquitectura Angular

```text
src/main.ts                  Arranque de la aplicación
src/app/app.config.ts        HttpClient, Router e inicialización
src/app/app.routes.ts        Seis rutas con carga diferida
src/app/app.component.*      Encabezado, menú, pie y avisos
src/app/core/                Modelo, datos, Storage y validadores
src/app/shared/              Tarjetas, banners, paginación y estados vacíos
src/app/pages/               Inicio, Noticias, Detalle, Favoritos, Gestión y Contacto
data/noticias.json           Catálogo inicial compartido con la Entrega 2
assets/images/              Recursos originales del diseño
tests/smoke-angular.cjs      Prueba de aceptación sobre dist
.github/workflows/pages.yml  Compilación, pruebas y despliegue
```

`NewsService` carga y valida el JSON con HttpClient. Las señales (`signal`) y valores derivados (`computed`) mantienen las vistas sincronizadas con favoritos, publicaciones y eliminaciones. `StorageService` conserva las claves de la versión anterior y valida su contenido al leerlo. Las plantillas usan interpolación `{{ }}`, propiedades `[disabled]`, eventos `(click)` y formularios `[formGroup]`; la búsqueda y el orden usan `ngModel`.

Los formularios rechazan entradas vacías, correo inválido, longitudes incorrectas e imágenes incompatibles o mayores de 1 MB. Un borrador puede publicarse desde Gestión. Los favoritos se ordenan por fecha de publicación. No se usan cadenas HTML editables ni `innerHTML` en el nuevo código.

Los favoritos y cambios editoriales siguen siendo locales al navegador. Contacto valida y muestra confirmación; no envía correos. La guía permite este alcance con JSON y Web Storage.

## Publicación

Destino: [PoliTechNews en GitHub Pages](https://santycp.github.io/PoliTechNews/).

El flujo `pages.yml` ejecuta `npm ci`, compila con `--base-href /PoliTechNews/`, prueba la aplicación bajo ese prefijo y publica el resultado. El origen de Pages se configura como **GitHub Actions**. Las rutas usan hash (`#/noticias/ia-aulas`) para que las recargas funcionen en alojamiento estático. Los pushes que solo cambian documentos no reconstruyen el sitio; se puede ejecutar el flujo manualmente.

El despliegue público y el recorrido automatizado se verificaron el **5 de octubre de 2026**. La prueba cubre diecinueve áreas: rutas, JSON, búsqueda, filtros, paginación, favoritos, formularios, publicaciones, persistencia, fallos y móvil.

### Entregables finales

- [Informe APA de la Entrega 3 en PDF](output/pdf/PoliTechNews_Entrega_3.pdf).
- [Informe editable en Word](output/docx/PoliTechNews_Entrega_3.docx).
- [Arquitectura](docs/Arquitectura_Entrega_3.md).
- [Guion de video de 2 minutos y 50 segundos](docs/Guion_Video_Entrega_3.md).

Fecha límite: **10 de octubre de 2026**. El video de YouTube de máximo 3 minutos debe grabarse y publicarse por el estudiante. **Pendiente:** incorporar su enlace real al informe y a este README antes de entregar. El guion no sustituye el video.

## Versión conservada de la Entrega 2

Primera versión funcional del periódico digital universitario. Está construida con HTML semántico, CSS y JavaScript sin dependencias de ejecución. Las noticias iniciales se cargan dinámicamente desde `data/noticias.json`.

Repositorio académico: [github.com/santycp/PoliTechNews](https://github.com/santycp/PoliTechNews). Informe final: [`output/pdf/PoliTechNews_Entrega_2.pdf`](output/pdf/PoliTechNews_Entrega_2.pdf).

Documentación técnica en normas APA: [PDF](output/pdf/PoliTechNews_Documentacion_Tecnica.pdf) y [Word editable](output/docx/PoliTechNews_Documentacion_Tecnica.docx). Incluye arquitectura, distribución del repositorio, explicación de archivos y funciones, modelo de datos, persistencia, validaciones, pruebas y mantenimiento.

### Ejecutar el prototipo anterior

Desde esta carpeta:

```bash
python -m http.server 8000
```

Abre [http://localhost:8000](http://localhost:8000). No abras los archivos con `file://`: los navegadores bloquean la carga de JSON local mediante `fetch` en ese modo.

Si utilizas la versión de Python incluida con Codex en Windows, también puedes ejecutar:

```powershell
& 'C:\Users\santy\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -m http.server 8000
```

## Vistas y funciones

| Vista | Archivo | Función |
| --- | --- | --- |
| Inicio | `index.html` | Noticias destacadas y accesos por categoría. |
| Noticias | `noticias.html` | Catálogo desde JSON, búsqueda, filtros y paginación. |
| Detalle | `detalle.html?id=...` | Contenido completo, relacionados y favorito. |
| Favoritos | `favoritos.html` | Guardar, ordenar y retirar noticias. |
| Gestión | `gestion.html` | Crear noticias, publicarlas o guardarlas como borrador, y eliminar contenido. |
| Contacto | `contacto.html` | Validación de campos y confirmación simulada. |

Los favoritos, las noticias creadas y las eliminaciones se guardan en `localStorage` **del navegador actual**. No hay servidor ni base de datos. El formulario de contacto valida la entrada, pero **no envía correos ni guarda datos personales**. Las noticias de ejemplo son contenido académico demostrativo, no publicaciones reales.

Las ilustraciones de las tarjetas, el logo y el panel de portada se extrajeron de los SVG originales del diseño de la Entrega 1. El archivo editable de Figma está en [PoliTechNews - Entrega 1](https://www.figma.com/design/A2QASHWYMKsV5a853lZ3dQ/PoliTechNews-%E2%80%94-Entrega-1).

## Estructura

```text
assets/images/       Imágenes extraídas del diseño
data/noticias.json   Datos iniciales
app.js               Renderizado y lógica de interacción
styles.css           Sistema visual y estilos responsivos
*.html               Páginas del sitio
```

## Criterios de revisión

1. Abrir Inicio y recorrer los enlaces del menú.
2. Buscar y filtrar noticias; comprobar paginación.
3. Entrar a una noticia y agregarla a favoritos; recargar y comprobar persistencia.
4. Crear una noticia, guardar un borrador y eliminar ambos desde Gestión.
5. Probar un formulario de contacto inválido y luego uno válido.
6. Revisar la interfaz en escritorio y móvil.

## Entrega académica

Las orientaciones del módulo piden para la Entrega 2 un prototipo en HTML, CSS y JavaScript, noticias renderizadas desde JSON, favoritos, formularios validados, código estructurado y un repositorio GitHub. También solicitan un PDF en normas APA con tabla de contenido, maquetación de la Entrega 1, código fuente explicado, conclusiones, referencias y la URL del repositorio.

El informe se genera con `build_entrega2_report.py --repo https://github.com/USUARIO/REPOSITORIO`. Sin `--repo` produce únicamente un borrador en `tmp/pdfs/`. El documento incorpora como anexo las seis páginas de mockups del PDF de la Entrega 1.

Angular, el despliegue público y el video corto corresponden a la Entrega 3 según la guía; no se presentan aquí como funcionalidades ya terminadas.
