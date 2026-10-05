"""Informe de la Entrega 3: APA 7, evidencias públicas y arquitectura Angular."""
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
import build_documentacion_tecnica as helpers

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'output/docx/PoliTechNews_Entrega_3.docx'
TMP = ROOT / 'tmp/entrega3-evidencias'
LIVE = 'https://santycp.github.io/PoliTechNews/'
REPO = 'https://github.com/santycp/PoliTechNews'

def font(run, bold=False, italic=False, size=12, name='Times New Roman'):
    helpers.set_font(run, name=name, size=size, bold=bold, italic=italic)
    fonts = run._element.get_or_add_rPr().rFonts
    for key in ('asciiTheme', 'hAnsiTheme', 'eastAsiaTheme', 'cstheme'):
        fonts.attrib.pop(qn('w:' + key), None)

def para(text='', indent=True):
    p = doc.add_paragraph()
    p.paragraph_format.first_line_indent = Inches(.5 if indent else 0)
    font(p.add_run(text))
    return p

def heading(text, level=1, new_page=False):
    p = doc.add_heading(text, level)
    p.paragraph_format.page_break_before = new_page and text in (
        'Introducción y alcance', 'Referencias', 'Anexo A Evidencias de la aplicación pública')
    p.paragraph_format.first_line_indent = Inches(0)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER if level == 1 else WD_ALIGN_PARAGRAPH.LEFT
    for run in p.runs: font(run, bold=True)
    return p

def title(text, style='Normal'):
    p = doc.add_paragraph(style=style)
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.first_line_indent = Inches(0)
    font(p.add_run(text), bold=True)
    return p

def link(label, url):
    p = para(label + ' ', False)
    helpers.add_hyperlink(p, url, url)

def code(text):
    p = doc.add_paragraph()
    p.paragraph_format.first_line_indent = Inches(0)
    p.paragraph_format.line_spacing = 1
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.keep_together = True
    font(p.add_run(text), size=10, name='Consolas')

def caption(label, text):
    p = helpers.caption(doc, label, text)
    p.paragraph_format.first_line_indent = Inches(0)

def table(label, text, headers, rows, widths):
    caption(label, text)
    t = helpers.add_table(doc, headers, rows, widths, font_size=10)
    for row_index,row in enumerate(t.rows):
        for index, cell in enumerate(row.cells):
            for p in cell.paragraphs:
                p.paragraph_format.first_line_indent = Inches(0)
                p.paragraph_format.space_before = Pt(0)
                p.paragraph_format.space_after = Pt(0)
                p.paragraph_format.line_spacing = 1.1
                if row_index == 0:
                    p.paragraph_format.keep_with_next = True
            helpers.cell_margins(cell, top=95, bottom=95, start=110, end=110)
            if index == len(headers)-1 and headers[-1] == 'Resultado':
                cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    return t

def picture(path, width, description):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.first_line_indent = Inches(0)
    p.paragraph_format.line_spacing = 1
    p.paragraph_format.space_after = Pt(6)
    shape = p.add_run().add_picture(str(path), width=Inches(width))
    shape._inline.docPr.set('descr', description)

def architecture():
    TMP.mkdir(parents=True, exist_ok=True)
    img = Image.new('RGB', (1500, 1030), 'white')
    draw = ImageDraw.Draw(img)
    regular = ImageFont.truetype('C:/Windows/Fonts/arial.ttf', 29)
    bold = ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf', 32)
    def box(bounds, a, b):
        draw.rounded_rectangle(bounds, 16, fill='#eff4f8', outline='#183d60', width=3)
        x1,y1,x2,y2=bounds
        draw.text(((x1+x2)/2,y1+24), a, fill='#111111', font=bold, anchor='mt')
        draw.text(((x1+x2)/2,y1+72), b, fill='#111111', font=regular, anchor='mt')
    def arrow(x1,y1,x2,y2):
        draw.line((x1,y1,x2,y2), fill='#183d60', width=5)
        draw.polygon([(x2,y2),(x2-12,y2-20),(x2+12,y2-20)], fill='#183d60')
    box((430,10,1070,135), 'Usuario y navegador', 'Eventos y representación del contenido')
    arrow(750,135,750,170)
    box((210,170,1290,295), 'AppComponent y Angular Router', 'Encabezado compartido y seis rutas con carga diferida')
    arrow(750,295,750,330)
    box((45,330,965,475), 'Páginas de la aplicación', 'Inicio   Noticias   Detalle   Favoritos   Gestión   Contacto')
    box((990,330,1455,475), 'Componentes shared', 'Banner   Tarjeta   Paginación')
    draw.line((990,400,965,400), fill='#183d60', width=5)
    arrow(510,475,510,520)
    box((210,520,1290,665), 'NewsService y NotificationService', 'Señales de estado   Datos derivados   Operaciones y avisos')
    arrow(400,665,400,720)
    arrow(1100,665,1100,720)
    box((45,720,730,855), 'HttpClient', 'Carga y validación de data/noticias.json')
    box((770,720,1455,855), 'StorageService', 'Lectura validada y escritura recuperable')
    arrow(1100,855,1100,895)
    box((770,895,1455,1020), 'localStorage', 'Favoritos   Noticias propias   IDs eliminados')
    img.save(TMP / 'arquitectura.png')

doc = Document()
section = doc.sections[0]
section.page_width = Inches(8.5)
section.page_height = Inches(11)
section.top_margin = section.bottom_margin = section.left_margin = section.right_margin = Inches(1)
section.header_distance = Inches(.5)
section.footer_distance = Inches(.5)
helpers.page_number(section.header.paragraphs[0])
section.header.paragraphs[0].paragraph_format.first_line_indent = Inches(0)
for name in ('Normal', 'Title', 'Heading 1', 'Heading 2', 'Heading 3', 'TOC 1', 'TOC 2', 'TOC 3'):
    if name not in doc.styles: continue
    style = doc.styles[name]
    for border in list(style.element.findall('.//' + qn('w:pBdr'))):
        border.getparent().remove(border)
    style.font.name = 'Times New Roman'
    style.font.size = Pt(12)
    style.font.color.rgb = RGBColor(0,0,0)
    rf=style.element.get_or_add_rPr().get_or_add_rFonts()
    for key in list(rf.attrib):
        if 'Theme' in key or 'theme' in key: del rf.attrib[key]
    rf.set(qn('w:ascii'), 'Times New Roman'); rf.set(qn('w:hAnsi'), 'Times New Roman')
    pf=style.paragraph_format
    pf.line_spacing=2; pf.space_before=Pt(0); pf.space_after=Pt(0)
    pf.first_line_indent=Inches(.5 if name=='Normal' else 0)
    pf.widow_control=True
    if name.startswith('Heading'):
        pf.keep_with_next=True; style.font.bold=True
doc.core_properties.title='PoliTechNews Informe técnico de la entrega final'
doc.core_properties.subject='Entrega 3 del módulo Front End'
doc.core_properties.author='Santiago Calvo Patiño'

# Portada de estudiante.
for _ in range(3): para('')
p=title('PoliTechNews Informe técnico de la entrega final', 'Title')
p.paragraph_format.space_before=Pt(48)
title('Entrega 3 del módulo Front End')
para('')
for text in ('Santiago Calvo Patiño', 'Politécnico Grancolombiano', 'Front End', 'Docente John Olarte Ramos', 'Medellín', '10 de octubre de 2026'):
    p=para(text,False); p.alignment=WD_ALIGN_PARAGRAPH.CENTER
doc.add_page_break()
title('Tabla de contenido')
helpers.add_toc(doc)

heading('Introducción y alcance', new_page=True)
para('PoliTechNews es una aplicación de noticias tecnológicas dirigida a la comunidad del Politécnico Grancolombiano. La entrega final integra el diseño de la primera entrega y las interacciones desarrolladas en la segunda en una aplicación Angular publicada en GitHub Pages. El sitio permite consultar, buscar y guardar noticias, gestionar publicaciones locales y validar un formulario de contacto.')
para('Este informe explica el funcionamiento de la aplicación, la arquitectura, los archivos del repositorio, los mecanismos de binding y los resultados de las pruebas. Los cambios editoriales y los favoritos se guardan en el navegador. El contacto es una simulación validada: no envía correos ni registra datos personales en un servidor.')
heading('Objetivo general',2)
para('Desarrollar y publicar una aplicación Front End funcional que represente los mockups de PoliTechNews y aplique componentes, rutas, binding y formularios de Angular, con código organizado y documentación técnica verificable.')
heading('Objetivos específicos',2)
for text in ('Organizar las seis vistas en componentes standalone y reutilizar los elementos comunes de la interfaz.', 'Cargar y validar el catálogo JSON; implementar búsqueda, categorías, paginación, detalle y favoritos persistentes.', 'Implementar formularios con validaciones, manejo de errores y operaciones locales de publicación, borrador y eliminación.', 'Compilar, probar y desplegar la aplicación mediante GitHub Actions; explicar la solución en un informe y un video de máximo tres minutos.'):
    para(text)
heading('Requisitos y límites del proyecto',2)
para('Las orientaciones del módulo solicitan una aplicación terminada, aplicación básica de Angular, código documentado, despliegue y un PDF acompañado de un video explicativo (Politécnico Grancolombiano, 2026). La solución usa JSON y almacenamiento local para el alcance académico; no incorpora autenticación, backend ni una base de datos compartida. Gestión es una vista demostrativa y no un panel administrativo protegido.')
link('Aplicación pública',LIVE)
link('Repositorio',REPO)

heading('Funcionamiento de las vistas',new_page=True)
table('Tabla 1','Rutas y funciones disponibles',['Ruta','Vista','Operaciones'],[
('/', 'Inicio', 'Destacadas, categorías y acceso al catálogo.'),
('/noticias','Noticias','Búsqueda por texto, categoría y paginación de seis artículos.'),
('/noticias/:id','Detalle','Contenido completo, relacionados, favorito y compartir enlace.'),
('/favoritos','Favoritos','Listar, ordenar, retirar y vaciar la selección guardada.'),
('/gestion','Gestión','Crear, guardar borrador, publicar borrador, buscar, filtrar y eliminar.'),
('/contacto','Contacto','Validar campos y consentimiento; mostrar confirmación simulada.')
],[1.35,.9,4.25])
para('Inicio presenta tres noticias destacadas y enlaces al catálogo filtrado. Noticias combina el título, el resumen y la categoría para buscar sin distinguir mayúsculas. Los filtros se reflejan en los parámetros de la URL; por ello, recargar conserva la búsqueda y la categoría. La página de paginación vuelve al inicio al cambiar los filtros o recargar.')
para('Detalle utiliza el identificador de la ruta para localizar la noticia. Si no existe o corresponde a un borrador, muestra un estado de contenido no disponible. Las noticias relacionadas priorizan la misma categoría y completan hasta tres elementos con otras publicaciones. La opción de compartir utiliza las posibilidades del navegador o comunica al usuario cómo recuperar el enlace.')
para('Favoritos muestra únicamente noticias publicadas y guardadas en el perfil actual. Puede ordenar por fecha, retirar una selección individual y vaciarla con confirmación. El orden utiliza la fecha de publicación de la noticia, no la fecha en que se añadió el favorito.')
para('Gestión crea artículos con identificadores únicos y calcula un tiempo de lectura aproximado. Un borrador no aparece en el catálogo hasta que se publica. Eliminar una noticia propia la retira del almacenamiento; eliminar una noticia del catálogo base guarda su identificador para ocultarla en ese navegador. Esta versión no incluye edición de una noticia ya creada.')
para('Contacto indica errores por campo y confirma cuando todos los datos son válidos. Después de la confirmación limpia los campos. La interfaz informa que el envío es simulado para no confundir la validación local con un servicio de mensajería real.')

heading('Arquitectura y tecnologías',new_page=True)
para('La arquitectura es una aplicación de una sola página organizada por responsabilidades: presentación en pages y shared, coordinación en los componentes y lógica de datos en core. Angular Router resuelve las vistas y HttpClient obtiene el catálogo. Los servicios inyectados comparten el estado sin duplicar la lógica en cada pantalla. No corresponde a una arquitectura de microservicios ni a una aplicación cliente servidor con API propia.')
architecture()
caption('Figura 1','Arquitectura de presentación datos y persistencia')
picture(TMP/'arquitectura.png',6.5,'Usuario, Router, páginas, componentes comunes, servicios de estado, JSON y almacenamiento local.')
para('La flecha representa la dependencia o el acceso a una responsabilidad. NewsService centraliza el estado de las noticias y favoritos; StorageService se ocupa de persistirlo. NotificationService gestiona los mensajes de resultado. Los componentes reciben datos mediante inputs; Paginación comunica la selección mediante un evento hacia la página.',False)
heading('Tecnologías utilizadas',2)
table('Tabla 2','Herramientas y finalidad',['Tecnología','Versión o recurso','Aplicación'],[
('Angular','22.2.1','Componentes standalone, Router, HttpClient y formularios.'),
('TypeScript','6.0','Tipos, interfaces y revisión estática estricta.'),
('RxJS','7.8.x','Conversión de solicitudes HTTP y suscripciones a rutas.'),
('Node.js','24.19.0 en verificación','Runtime de las herramientas de compilación y pruebas.'),
('HTML y CSS','Plantillas y estilos','Contenido semántico, diseño responsivo y estados visuales.'),
('Web Storage','localStorage','Persistencia por navegador sin backend.'),
('Playwright','Dependencia del proyecto','Pruebas de aceptación con Chromium.'),
('GitHub Actions y Pages','Workflow y alojamiento','Compilación, prueba y publicación del sitio estático.')
],[1.35,1.6,3.55])
para('Los requisitos de Node.js y TypeScript corresponden a la compatibilidad oficial de Angular 22 (Angular, s. f.-a). El archivo package-lock.json fija las versiones instaladas para reproducir el entorno mediante npm ci. Los componentes de página se cargan de forma diferida y la compilación optimiza los recursos de producción.')

heading('Distribución y explicación de los archivos',new_page=True)
para('El repositorio conserva los archivos de la Entrega 2 en la raíz para permitir su consulta. La versión que se publica se compila desde src y no utiliza app.js ni los archivos HTML antiguos como punto de entrada. El CSS común y los recursos visuales se reutilizan para conservar la identidad gráfica.')
heading('Configuración y arranque',2)
table('Tabla 3','Archivos de configuración y entrada',['Archivo','Responsabilidad'],[
('package.json','Declara dependencias y comandos start, build, build:pages, test y test:legacy.'),
('package-lock.json','Fija las dependencias transitivas y la instalación reproducible.'),
('angular.json','Configura compilación, servidor, recursos, estilos y límites de tamaño.'),
('tsconfig.json','Establece tipos y comprobaciones estrictas para TypeScript y plantillas.'),
('tsconfig.app.json','Selecciona la entrada y opciones de compilación de la aplicación.'),
('.gitignore','Excluye dependencias, dist, caché Angular y resultados temporales.'),
('src/index.html','Documento base en español, metadatos, favicon y elemento app-root.'),
('src/main.ts','Ejecuta bootstrapApplication con el componente raíz y su configuración.'),
('src/styles.css','Estilos adicionales para hosts Angular, avisos, errores y movimiento reducido.'),
('styles.css','Sistema visual original, rejillas, formularios y reglas responsivas compartidas.')
],[1.7,4.8])
heading('Componente raíz y servicios',2)
table('Tabla 4','Archivos de coordinación y dominio',['Archivo en src/app','Responsabilidad'],[
('app.config.ts','Registra Router, HttpClient e inicialización que carga las noticias.'),
('app.routes.ts','Declara seis rutas diferidas y redirección para rutas desconocidas.'),
('app.component.ts','Controla el menú móvil, foco tras navegar y avisos globales.'),
('app.component.html','Define encabezado, navegación, router-outlet, pie y mensajes de carga.'),
('core/article.model.ts','Define Article, ArticleInput, categorías y validación de datos externos; formatea fechas e imágenes seguras.'),
('core/news.service.ts','Carga el JSON, combina el catálogo y cambios locales, calcula listas y ejecuta las operaciones sobre noticias y favoritos.'),
('core/storage.service.ts','Lee JSON local validado y escribe lotes; intenta restaurar el estado previo ante fallos.'),
('core/notification.service.ts','Expone mensajes y tipo de aviso mediante señales; limpia los avisos automáticamente.'),
('core/form-validators.ts','Comprueba longitud mínima después de quitar espacios externos.')
],[1.85,4.65])
heading('Componentes de página',2)
para('Cada componente de página tiene dos archivos: el .ts declara dependencias, estado, operaciones y datos derivados; el .html presenta el contenido y conecta controles con eventos y valores. Esta separación evita mezclar cadenas HTML con reglas de negocio.')
table('Tabla 5','Páginas dentro de src/app/pages',['Par de archivos','Responsabilidad'],[
('home.component.ts y .html','Seleccionan destacadas y generan accesos por categoría.'),
('news.component.ts y .html','Interpretan parámetros de ruta, filtran noticias y construyen la página actual.'),
('detail.component.ts y .html','Resuelven el ID, muestran contenido y relacionados y controlan favorito y compartir.'),
('favorites.component.ts y .html','Derivan la selección guardada, ordenan y gestionan su retirada o vaciado.'),
('admin.component.ts y .html','Definen formulario reactivo, filtros, paginación, subida de imagen y ciclo borrador publicación eliminación.'),
('contact.component.ts y .html','Definen formulario reactivo, contador, errores y confirmación simulada.')
],[2.05,4.45])
heading('Componentes compartidos recursos y automatización',2)
table('Tabla 6','Archivos de apoyo y mantenimiento',['Archivo o directorio','Responsabilidad'],[
('shared/banner.component.ts','Presenta etiqueta, título y descripción; admite contenido adicional con ng-content.'),
('shared/news-card.component.ts','Renderiza el artículo recibido por input: imagen, categoría, título, resumen, fecha y enlace al detalle.'),
('shared/pagination.component.ts','Recibe página actual y total; emite el cambio solicitado.'),
('shared/empty-state.component.ts','Presenta título y explicación de una lista vacía; proyecta el botón de recuperación definido por la página.'),
('data/noticias.json','Contiene el catálogo inicial tipado; la compilación lo copia como recurso estático.'),
('assets/images/','Conserva logo, ilustraciones por categoría y elementos del diseño.'),
('tests/smoke-angular.cjs','Sirve dist localmente o prueba BASE_URL; verifica el recorrido funcional en un contexto aislado.'),
('.github/workflows/pages.yml','Instala, compila, prueba bajo el prefijo de Pages y publica el artefacto.'),
('scripts/github-pages.ps1','Consulta o configura Pages mediante API; utiliza la credencial Git en memoria sin imprimirla.'),
('scripts/capture-entrega3.cjs','Captura la aplicación pública con datos documentales en un perfil aislado.'),
('scripts/export-entrega3.ps1','Actualiza el índice y los campos de Word y exporta este informe a PDF.'),
('README.md','Explica instalación, arquitectura, límites y acceso a entregables.'),
('docs/Arquitectura_Entrega_3.md','Describe el flujo y el diagrama de la arquitectura.'),
('docs/Guion_Video_Entrega_3.md','Propone un recorrido de 2 minutos y 50 segundos y una lista de publicación.'),
('build_entrega3_report.py','Genera este informe editable a partir de explicaciones y capturas verificadas.'),
('output/docx/ y output/pdf/','Almacenan los informes académicos editables y exportados.'),
('HTML de raíz app.js y mockups/','Conservan el prototipo anterior y las evidencias de diseño; no ejecutan la aplicación Angular.')
],[2.15,4.35])

heading('Componentes binding y estado reactivo',new_page=True)
para('Un componente standalone declara las piezas de Angular y los componentes que necesita en imports. Router monta cada página dentro de router-outlet, mientras que el encabezado y el pie permanecen en AppComponent. Las tarjetas, banners y paginación se reutilizan para mantener el mismo comportamiento entre vistas.')
heading('Binding en las plantillas',2)
para('Angular sincroniza valores y eventos entre la clase y la plantilla. La interpolación presenta texto; el binding de propiedades modifica atributos o propiedades de un elemento; el binding de eventos ejecuta una operación; ngModel mantiene el valor de un control simple en ambos sentidos (Angular, s. f.-b). Los siguientes ejemplos corresponden a los mecanismos usados en el proyecto.')
code('{{ article.title }}\n[disabled]="saving()"\n(click)="filter(category)"\n[(ngModel)]="searchText"\n[formGroup]="form"')
para('El título se muestra como texto y no se interpreta como HTML. El botón deshabilitado refleja una operación de guardado. El evento click selecciona una categoría. ngModel actualiza el texto de búsqueda, mientras que formGroup conecta el formulario con controles y validadores definidos en TypeScript.')
heading('Señales y valores derivados',2)
para('NewsService define señales para catálogo base, artículos propios, eliminaciones y favoritos. Los valores computed combinan esas señales para obtener artículos disponibles, publicados y favoritos. Angular registra sus dependencias y actualiza las partes que consumen dichos valores cuando cambia el estado (Angular, s. f.-e).')
code('readonly articles = computed(() =>\n  [...this.custom(), ...this.base()]\n    .filter(a => !this.deleted().includes(a.id)));\n\nreadonly published = computed(() =>\n  this.articles().filter(a => a.status !== \'draft\')\n    .sort((a, b) => b.date.localeCompare(a.date)));')
para('El estado derivado no necesita guardarse de forma independiente: se recalcula desde su fuente. Así, publicar un borrador actualiza el catálogo y eliminar una noticia actualiza la lista y los favoritos relacionados. Las señales solo cambian después de una escritura local exitosa.')
heading('Rutas y carga del catálogo',2)
para('Las rutas usan loadComponent para cargar páginas bajo demanda. ActivatedRoute obtiene identificadores y parámetros de consulta; RouterLink navega sin recargar el documento completo. La estrategia hash mantiene enlaces como #/noticias/ia-aulas compatibles con GitHub Pages, que no resuelve rutas de aplicación en un servidor propio.')
para('HttpClient solicita data/noticias.json durante la inicialización. La respuesta se recibe como unknown y se valida antes de incorporarla al estado, porque un tipo TypeScript no comprueba automáticamente los datos recibidos en ejecución (Angular, s. f.-d). Si la carga falla, el encabezado de la aplicación muestra un error y una acción de reintento.')

heading('Modelo de datos validaciones y persistencia',new_page=True)
table('Tabla 7','Contrato Article',['Campo','Tipo','Significado'],[
('id','string','Identificador único; las noticias creadas incluyen UUID.'),
('title y summary','string','Título y resumen que aparecen en las tarjetas.'),
('category','Category','Una de las seis categorías declaradas.'),
('date','string','Fecha de publicación con formato YYYY-MM-DD.'),
('minutes','number','Tiempo aproximado de lectura en minutos.'),
('image','string','Ruta local PNG o imagen de usuario en data URL permitida.'),
('author','string','Autor del contenido.'),
('content','string[]','Párrafos del contenido completo.'),
('status','published o draft opcional','Sin estado explícito se considera publicada para mantener compatibilidad.')
],[1.25,1.55,3.7])
heading('Formularios reactivos',2)
para('Gestión y Contacto definen un FormGroup con NonNullableFormBuilder. Los controles tienen validadores y las plantillas presentan errores cuando están inválidos y han sido tocados. Al intentar enviar se marcan todos como tocados, de modo que un formulario vacío informa al usuario qué debe corregir (Angular, s. f.-c).')
table('Tabla 8','Reglas de validación',['Formulario','Campo','Regla'],[
('Gestión','Título','Obligatorio; entre 8 y 120 caracteres.'),
('Gestión','Categoría','Obligatoria; opciones de la lista del modelo.'),
('Gestión','Resumen','Obligatorio; entre 20 y 160 caracteres.'),
('Gestión','Contenido','Obligatorio; entre 80 y 20 000 caracteres.'),
('Gestión','Imagen opcional','PNG, JPEG o WebP; como máximo 1 MB.'),
('Contacto','Nombre','Obligatorio; entre 3 y 80 caracteres.'),
('Contacto','Correo','Obligatorio; formato de correo y máximo 254 caracteres.'),
('Contacto','Asunto','Obligatorio; selección disponible en el formulario.'),
('Contacto','Mensaje','Obligatorio; entre 20 y 500 caracteres.'),
('Contacto','Consentimiento','Debe estar aceptado antes de confirmar.')
],[1,1.25,4.25])
para('La longitud mínima se comprueba después de quitar espacios externos. No se acepta una entrada que solo alcance el mínimo mediante espacios. Las imágenes se leen con FileReader después de comprobar tipo y tamaño. Una imagen válida puede exceder la cuota de localStorage cuando se combina con otras publicaciones; en ese caso la aplicación informa el fallo sin mostrar una publicación guardada que no existe.')
heading('Persistencia y tratamiento de fallos',2)
para('StorageService conserva tres claves: politechnews:favorites:v1 guarda identificadores seleccionados; politechnews:custom:v1 guarda artículos creados; politechnews:deleted:v1 guarda IDs del catálogo base ocultos. Son las mismas claves del prototipo anterior. La lectura filtra elementos incompatibles y devuelve una lista vacía si el JSON local está dañado.')
para('Las operaciones sobre varias claves capturan el valor anterior e intentan restaurarlo si falla la escritura. No constituye una transacción de base de datos: un navegador que bloquea también la restauración puede impedir recuperar todas las claves. La aplicación comunica el error y no actualiza su estado en memoria como si el guardado hubiera terminado.')
para('localStorage pertenece al origen del sitio y al perfil del navegador. No sincroniza datos entre dispositivos ni usuarios y puede borrarse al limpiar el navegador. Las noticias base siguen disponibles desde el JSON del repositorio. Los formularios de contacto no guardan la información personal ingresada.')
heading('Seguridad y accesibilidad básica',2)
para('Las plantillas interpolan el contenido editable en lugar de insertarlo mediante innerHTML. imageSrc limita las fuentes a recursos locales y data URLs de los formatos permitidos. Estos controles reducen riesgos del contenido demostrativo, pero no reemplazan validación de servidor ni permisos en una aplicación real.')
para('La interfaz incluye etiquetas de campos, textos alternativos, avisos con roles de estado, nombres de controles y foco en el contenido después de navegar. El menú móvil tiene estado expandido y el CSS considera movimiento reducido. Se comprobó ausencia de desbordamiento horizontal a 390 píxeles; no se afirma una auditoría completa de conformidad WCAG.')

heading('Verificación y resultados',new_page=True)
results=json.loads((ROOT/'tmp/entrega3-qa/resultados.json').read_text(encoding='utf-8'))
para('La compilación de producción y las pruebas automatizadas de aceptación finalizaron correctamente. Se ejecutó el recorrido sobre la compilación local, bajo el prefijo /PoliTechNews/ y sobre el sitio público. La última prueba pública utilizó perfiles aislados y no modificó los datos del navegador personal del estudiante.')
para(f"Ejecución pública registrada: {results['date']}. Destino: {results['base']}. Resultado: {results['result']}. Errores de ejecución capturados: {len(results['errors'])}.",False)
table('Tabla 9','Cobertura funcional de aceptación',['Área','Comprobaciones','Resultado'],[
('Carga y navegación','Angular activo, JSON, rutas SPA y recarga con parámetros.','Aprobado'),
('Catálogo','Búsqueda, categorías, paginación y estado sin resultados.','Aprobado'),
('Detalle y favoritos','Detalle existente y ausente; persistencia y orden por fecha.','Aprobado'),
('Gestión','Campos inválidos, imagen incompatible, creación, borrador, publicación y eliminación.','Aprobado'),
('Contenido editable','Un título con etiquetas HTML aparece como texto y no crea nodos ejecutables.','Aprobado'),
('Contacto','Errores por entrada vacía y confirmación con datos válidos.','Aprobado'),
('Diseño móvil','Menú y seis vistas sin desbordamiento a 390 px.','Aprobado'),
('Persistencia adversa','JSON local corrupto y cuota bloqueada; mensaje de error y estado coherente.','Aprobado'),
('Red','Respuesta 503 simulada y recuperación después de Reintentar.','Aprobado')
],[1.15,4.25,1.1])
para('El script registra diecinueve áreas de cobertura y exige que no se capturen errores de JavaScript en el recorrido principal. Esto es una prueba de aceptación y no una suite exhaustiva de pruebas unitarias, de rendimiento, de seguridad o de todos los navegadores. Las capturas del anexo corresponden al sitio desplegado con contenido inicial y un favorito de demostración.')
heading('Cómo repetir las pruebas',2)
code('npm ci\nnpx playwright install chromium\nnpm run build:pages\nnpm test')
para('Si Chrome está instalado en su ruta predeterminada de Windows, el script puede utilizarlo sin descargar Chromium. Para comprobar el sitio publicado se establece BASE_URL con la dirección pública antes de ejecutar npm test. El script crea su servidor de vista previa únicamente cuando no se proporciona esa variable.')

heading('Despliegue y entregables',new_page=True)
para('El workflow pages.yml se ejecuta al modificar el código en main o cuando se activa manualmente. Instala dependencias con npm ci, compila con el prefijo /PoliTechNews/, instala Chromium, prueba el artefacto compilado y lo publica con las acciones de Pages. La configuración usa GitHub Actions como origen de publicación (GitHub, s. f.).')
code('npm run build:pages\n# angular build con --base-href /PoliTechNews/')
para('El prefijo permite resolver scripts, imágenes, estilos y JSON dentro del repositorio alojado. Las rutas hash evitan respuestas 404 al recargar una vista interna. Los permisos del workflow se limitan a lectura del repositorio y publicación en Pages, con el token de identidad necesario para el despliegue.')
link('Sitio desplegado',LIVE)
link('Código fuente',REPO)
link('Despliegue exitoso verificado','https://github.com/santycp/PoliTechNews/actions/runs/37345582835')
heading('Documentos y demostración en video',2)
para('El repositorio contiene este informe en PDF y una copia Word editable, además de la documentación de arquitectura y el guion de demostración. El guion propone un recorrido de 2 minutos y 50 segundos por las funciones, la vista móvil, el código y los enlaces de entrega.')
para('La publicación del video en YouTube corresponde al estudiante. Antes de presentar la entrega debe incorporarse el enlace del video al informe y al README y comprobar que el docente pueda abrirlo. El guion no sustituye la grabación solicitada por el módulo.')
heading('Lista de comprobación para el 10 de octubre de 2026',2)
for text in ('Abrir el sitio y el repositorio desde una ventana sin sesión y confirmar que las seis vistas funcionan.', 'Grabar el recorrido con voz y pantalla, revisar que no exceda tres minutos y publicarlo como Público o No listado.', 'Añadir el enlace real de YouTube al PDF y al README; comprobar el acceso sin iniciar sesión.', 'Entregar el PDF con enlaces y los archivos adicionales que indique el aula virtual, conservando una copia del envío.'):
    para(text)

heading('Conclusiones',new_page=True)
para('PoliTechNews integra los mockups y las interacciones previas en una aplicación Angular con seis rutas funcionales. La separación entre páginas, componentes reutilizables y servicios facilita localizar el código y cambiar una responsabilidad sin repetirla en todas las vistas.')
para('La aplicación demuestra binding de texto, propiedades, eventos y controles; también utiliza formularios reactivos y señales para mantener la interfaz sincronizada. El catálogo JSON y la persistencia local permiten completar la experiencia académica sin infraestructura de servidor.')
para('Las pruebas de aceptación confirmaron los recorridos principales y los estados de error previstos en la versión desplegada. El workflow de GitHub Actions reproduce la compilación, comprueba el prefijo de publicación y actualiza GitHub Pages cuando cambia el código.')
para('Las publicaciones son locales y Contacto no envía mensajes. Una versión de producción requeriría backend, autenticación, permisos editoriales, persistencia compartida y pruebas adicionales.')

heading('Referencias',new_page=True)
references=[
('Angular. (s. f.-a). ', 'Version compatibility', 'https://angular.dev/reference/versions'),
('Angular. (s. f.-b). ', 'Binding dynamic text properties and attributes', 'https://angular.dev/guide/templates/binding'),
('Angular. (s. f.-c). ', 'Reactive forms', 'https://angular.dev/guide/forms/reactive-forms'),
('Angular. (s. f.-d). ', 'HTTP Client', 'https://angular.dev/guide/http'),
('Angular. (s. f.-e). ', 'Angular Signals', 'https://angular.dev/guide/signals'),
('GitHub. (s. f.). ', 'Using custom workflows with GitHub Pages', 'https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages'),
('Politécnico Grancolombiano. (2026). ', 'Orientaciones para las entregas del módulo Front End Agosto 2026-1', None)
]
# Las letras se asignan por título; las citas del cuerpo se ajustan después.
mapping={'s. f.-a':'s. f.-e','s. f.-b':'s. f.-b','s. f.-c':'s. f.-d','s. f.-d':'s. f.-c','s. f.-e':'s. f.-a'}
for p in doc.paragraphs:
    for r in p.runs:
        if 'Angular, s. f.-' not in r.text:
            continue
        for source,target in mapping.items():
            if f'Angular, {source}' in r.text:
                r.text=r.text.replace(f'Angular, {source}',f'Angular, TEMP{target}')
        r.text=r.text.replace('Angular, TEMP','Angular, ')
for prefix,text,url in sorted(references,key=lambda item: (item[0].split('(')[0],item[1].lower())):
    for source,target in mapping.items():
        if source in prefix:
            prefix=prefix.replace(source,target);break
    p=doc.add_paragraph()
    p.paragraph_format.left_indent=Inches(.5)
    p.paragraph_format.first_line_indent=Inches(-.5)
    font(p.add_run(prefix))
    font(p.add_run(text),italic=True)
    font(p.add_run('. '))
    if url: helpers.add_hyperlink(p,url,url)
    else: font(p.add_run('[Guía del módulo].'))

heading('Anexo A Evidencias de la aplicación pública',new_page=True)
para('Capturas del sitio desplegado verificadas el 5 de octubre de 2026. Las vistas de escritorio se muestran a 1440 por 1000 píxeles. La captura móvil usa 390 por 844 píxeles. Las imágenes representan la parte visible de cada pantalla, no todo el contenido desplazable.',False)
screens=[('01-inicio','Inicio y noticias destacadas'),('02-noticias','Catálogo con búsqueda categorías y paginación'),('03-detalle','Detalle de una noticia publicada'),('04-favoritos','Una noticia guardada en el perfil de demostración'),('05-gestion','Formulario y lista de gestión local'),('06-contacto','Formulario de contacto con validación local')]
for i,(name,label) in enumerate(screens):
    if i: doc.add_page_break()
    caption(f'Figura {i+2}',label)
    picture(TMP/(name+'.png'),6.5,label)
    para('Nota. Elaboración propia a partir de la aplicación publicada. El encabezado y la navegación mantienen la identidad gráfica del diseño original.',False)
doc.add_page_break()
caption('Figura 8','Adaptación móvil de la pantalla de inicio')
picture(TMP/'07-movil.png',2.7,'Inicio de PoliTechNews en pantalla móvil de 390 píxeles de ancho.')
para('Nota. La rejilla se reorganiza y la navegación se presenta mediante un botón de menú. Las seis rutas se verificaron sin desbordamiento horizontal.',False)
OUT.parent.mkdir(parents=True,exist_ok=True)
doc.save(OUT)
print(OUT)
