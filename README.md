# PoliTechNews - Entrega 2

Primera versión funcional del periódico digital universitario. Está construida con HTML semántico, CSS y JavaScript sin dependencias de ejecución. Las noticias iniciales se cargan dinámicamente desde `data/noticias.json`.

## Ejecutar localmente

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
