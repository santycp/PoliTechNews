"""Genera la documentación técnica APA 7 de PoliTechNews en formato DOCX."""

from pathlib import Path
from textwrap import dedent

from PIL import Image, ImageDraw, ImageFont
from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK, WD_LINE_SPACING
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "output" / "docx" / "PoliTechNews_Documentacion_Tecnica.docx"
TMP = ROOT / "tmp" / "documentacion_tecnica"
ARCH = TMP / "arquitectura.png"
REPO = "https://github.com/santycp/PoliTechNews"

NAVY = "0B3A72"
PALE = "EAF3F8"
GRID = "D9D9D9"
INK = RGBColor(0, 0, 0)


def set_repeat_header(row):
    tr_pr = row._tr.get_or_add_trPr()
    header = OxmlElement("w:tblHeader")
    header.set(qn("w:val"), "true")
    tr_pr.append(header)


def prevent_row_split(row):
    tr_pr = row._tr.get_or_add_trPr()
    cant_split = OxmlElement("w:cantSplit")
    cant_split.set(qn("w:val"), "true")
    tr_pr.append(cant_split)


def shade(cell, fill):
    tc_pr = cell._tc.get_or_add_tcPr()
    node = tc_pr.find(qn("w:shd"))
    if node is None:
        node = OxmlElement("w:shd")
        tc_pr.append(node)
    node.set(qn("w:fill"), fill)


def cell_margins(cell, top=100, start=120, bottom=100, end=120):
    tc_pr = cell._tc.get_or_add_tcPr()
    tc_mar = tc_pr.first_child_found_in("w:tcMar")
    if tc_mar is None:
        tc_mar = OxmlElement("w:tcMar")
        tc_pr.append(tc_mar)
    for side, value in (("top", top), ("start", start), ("bottom", bottom), ("end", end)):
        item = tc_mar.find(qn(f"w:{side}"))
        if item is None:
            item = OxmlElement(f"w:{side}")
            tc_mar.append(item)
        item.set(qn("w:w"), str(value))
        item.set(qn("w:type"), "dxa")


def borders(table):
    tbl_pr = table._tbl.tblPr
    node = tbl_pr.find(qn("w:tblBorders"))
    if node is None:
        node = OxmlElement("w:tblBorders")
        tbl_pr.append(node)
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        line = OxmlElement(f"w:{edge}")
        line.set(qn("w:val"), "single")
        line.set(qn("w:sz"), "5")
        line.set(qn("w:color"), GRID)
        node.append(line)


def set_font(run, name="Times New Roman", size=12, bold=False, italic=False, color=INK):
    run.font.name = name
    run._element.get_or_add_rPr().rFonts.set(qn("w:ascii"), name)
    run._element.get_or_add_rPr().rFonts.set(qn("w:hAnsi"), name)
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = color


def page_number(paragraph):
    paragraph.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    run = paragraph.add_run()
    begin = OxmlElement("w:fldChar")
    begin.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = " PAGE "
    end = OxmlElement("w:fldChar")
    end.set(qn("w:fldCharType"), "end")
    run._r.extend([begin, instr, end])
    set_font(run, size=10)


def add_hyperlink(paragraph, text, url):
    rid = paragraph.part.relate_to(
        url,
        "http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink",
        is_external=True,
    )
    link = OxmlElement("w:hyperlink")
    link.set(qn("r:id"), rid)
    run = OxmlElement("w:r")
    props = OxmlElement("w:rPr")
    color = OxmlElement("w:color")
    color.set(qn("w:val"), "0563C1")
    underline = OxmlElement("w:u")
    underline.set(qn("w:val"), "single")
    props.extend([color, underline])
    run.append(props)
    text_node = OxmlElement("w:t")
    text_node.text = text
    run.append(text_node)
    link.append(run)
    paragraph._p.append(link)


def add_toc(document):
    p = document.add_paragraph()
    run = p.add_run()
    begin = OxmlElement("w:fldChar")
    begin.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = ' TOC \\o "1-3" \\h \\z \\u '
    separate = OxmlElement("w:fldChar")
    separate.set(qn("w:fldCharType"), "separate")
    placeholder = OxmlElement("w:t")
    placeholder.text = "Actualice la tabla de contenido si Word lo solicita."
    end = OxmlElement("w:fldChar")
    end.set(qn("w:fldCharType"), "end")
    run._r.extend([begin, instr, separate, placeholder, end])


def body(document, text="", bold_lead=None):
    p = document.add_paragraph(style="Normal")
    if bold_lead:
        r = p.add_run(bold_lead)
        set_font(r, bold=True)
    r = p.add_run(text)
    set_font(r)
    return p


def bullet(document, text, level=0):
    p = document.add_paragraph(style="List Bullet" if level == 0 else "List Bullet 2")
    r = p.add_run(text)
    set_font(r)
    return p


def numbered(document, text, number=None):
    if number is None:
        p = document.add_paragraph(style="List Number")
        prefix = ""
    else:
        p = document.add_paragraph(style="Normal")
        p.paragraph_format.left_indent = Inches(0.5)
        p.paragraph_format.first_line_indent = Inches(-0.25)
        p.paragraph_format.space_before = Pt(5)
        prefix = f"{number}.  "
    r = p.add_run(prefix + text)
    set_font(r)
    return p


def heading(document, text, level=1):
    return document.add_heading(text, level=level)


def caption(document, label, title):
    p = document.add_paragraph()
    p.paragraph_format.keep_with_next = True
    p.paragraph_format.line_spacing = 1.0
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(4)
    r = p.add_run(label)
    set_font(r, bold=True)
    r = p.add_run("\n" + title)
    set_font(r, italic=True)
    return p


def note(document, text):
    p = document.add_paragraph()
    r = p.add_run("Nota. ")
    set_font(r, italic=True)
    r = p.add_run(text)
    set_font(r)
    return p


def add_table(document, headers, rows, widths=None, font_size=9):
    table = document.add_table(rows=1, cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    set_repeat_header(table.rows[0])
    for index, value in enumerate(headers):
        cell = table.rows[0].cells[index]
        shade(cell, NAVY)
        cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(value)
        set_font(r, size=font_size, bold=True, color=RGBColor(255, 255, 255))
    for row_index, values in enumerate(rows):
        cells = table.add_row().cells
        for index, value in enumerate(values):
            cell = cells[index]
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            if row_index % 2:
                shade(cell, PALE)
            p = cell.paragraphs[0]
            p.paragraph_format.line_spacing = 1.0
            p.paragraph_format.space_after = Pt(0)
            r = p.add_run(str(value))
            set_font(r, size=font_size)
    if widths:
        for index, width in enumerate(widths):
            table.columns[index].width = Inches(width)
        for row in table.rows:
            for index, width in enumerate(widths):
                cell = row.cells[index]
                cell.width = Inches(width)
                tc_pr = cell._tc.get_or_add_tcPr()
                tc_width = tc_pr.find(qn("w:tcW"))
                if tc_width is None:
                    tc_width = OxmlElement("w:tcW")
                    tc_pr.append(tc_width)
                tc_width.set(qn("w:w"), str(int(width * 1440)))
                tc_width.set(qn("w:type"), "dxa")
    for row in table.rows:
        prevent_row_split(row)
        for cell in row.cells:
            cell_margins(cell)
    borders(table)
    document.add_paragraph().paragraph_format.space_after = Pt(2)
    return table


def code_block(document, code, language="JavaScript"):
    p = document.add_paragraph()
    p.paragraph_format.left_indent = Inches(0.25)
    p.paragraph_format.right_indent = Inches(0.25)
    p.paragraph_format.space_before = Pt(5)
    p.paragraph_format.space_after = Pt(8)
    p.paragraph_format.line_spacing = 1.0
    p_pr = p._p.get_or_add_pPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), "F3F6F8")
    p_pr.append(shd)
    r = p.add_run(dedent(code).strip())
    set_font(r, name="Consolas", size=8.5)
    return p


def make_architecture(path):
    width, height = 1800, 1120
    img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(img)
    font_paths = [
        Path("C:/Windows/Fonts/arial.ttf"),
        Path("C:/Windows/Fonts/calibri.ttf"),
    ]
    font_path = next((p for p in font_paths if p.exists()), None)
    def f(size, bold=False):
        candidate = Path("C:/Windows/Fonts/arialbd.ttf") if bold else font_path
        return ImageFont.truetype(str(candidate), size) if candidate and candidate.exists() else ImageFont.load_default()
    title, label, small = f(45, True), f(29, True), f(25)
    draw.text((width // 2, 45), "Arquitectura lógica del prototipo PoliTechNews", font=title, fill="#071B3B", anchor="ma")
    layers = [
        (110, 160, 1690, 350, "Capa de presentación", "Seis documentos HTML  |  styles.css  |  componentes renderizados\nNavegación, tarjetas, formularios, tablas y diseño responsivo", "#E8F8F7", "#0D9FB0"),
        (110, 430, 1690, 680, "Capa de aplicación", "app.js\nEstado en memoria  |  funciones de renderizado  |  eventos  |  validaciones\nBúsqueda, filtros, paginación, detalle, favoritos y mini CRUD", "#EDF3FF", "#0B3A72"),
        (110, 760, 810, 1000, "Datos iniciales", "data/noticias.json\n12 noticias académicas\nLectura asíncrona con Fetch", "#F4EEFF", "#7143A8"),
        (990, 760, 1690, 1000, "Persistencia del navegador", "localStorage\nfavoritos  |  noticias creadas\nidentificadores eliminados", "#FFF1E8", "#B35C2B"),
    ]
    for x1, y1, x2, y2, head, text, fill, outline in layers:
        draw.rounded_rectangle((x1, y1, x2, y2), radius=28, fill=fill, outline=outline, width=5)
        draw.text((x1 + 40, y1 + 30), head, font=label, fill="#071B3B")
        for i, line in enumerate(text.split("\n")):
            draw.text((x1 + 40, y1 + 85 + i * 39), line, font=small, fill="#26374A")
    # Arrows between logical layers.
    for x, start, end in ((900, 350, 430), (470, 680, 760), (1330, 680, 760)):
        draw.line((x, start + 8, x, end - 18), fill="#0D9FB0", width=9)
        draw.polygon([(x, end), (x - 18, end - 28), (x + 18, end - 28)], fill="#0D9FB0")
    img.save(path, quality=95)


def configure(document):
    section = document.sections[0]
    section.page_width = Inches(8.5)
    section.page_height = Inches(11)
    section.top_margin = Inches(1)
    section.bottom_margin = Inches(1)
    section.left_margin = Inches(1)
    section.right_margin = Inches(1)
    page_number(section.header.paragraphs[0])
    styles = document.styles
    normal = styles["Normal"]
    normal.font.name = "Times New Roman"
    normal._element.rPr.rFonts.set(qn("w:ascii"), "Times New Roman")
    normal._element.rPr.rFonts.set(qn("w:hAnsi"), "Times New Roman")
    normal.font.size = Pt(12)
    normal.font.color.rgb = INK
    normal.paragraph_format.line_spacing_rule = WD_LINE_SPACING.DOUBLE
    normal.paragraph_format.space_after = Pt(0)
    normal.paragraph_format.first_line_indent = Inches(0.5)
    for style_name, size in (("Title", 15), ("Heading 1", 14), ("Heading 2", 12), ("Heading 3", 12)):
        style = styles[style_name]
        style.font.name = "Times New Roman"
        style._element.rPr.rFonts.set(qn("w:ascii"), "Times New Roman")
        style._element.rPr.rFonts.set(qn("w:hAnsi"), "Times New Roman")
        style.font.size = Pt(size)
        style.font.bold = True
        style.font.color.rgb = INK
        style.paragraph_format.space_before = Pt(12 if style_name != "Title" else 0)
        style.paragraph_format.space_after = Pt(6)
        style.paragraph_format.keep_with_next = True
    styles["Title"].paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    title_ppr = styles["Title"]._element.get_or_add_pPr()
    title_border = title_ppr.find(qn("w:pBdr"))
    if title_border is not None:
        title_ppr.remove(title_border)
    for name in ("List Bullet", "List Bullet 2", "List Number"):
        styles[name].font.name = "Times New Roman"
        styles[name].font.size = Pt(12)
        styles[name].paragraph_format.line_spacing_rule = WD_LINE_SPACING.DOUBLE
        styles[name].paragraph_format.space_after = Pt(0)
        styles[name].paragraph_format.first_line_indent = Inches(0)


def build():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    TMP.mkdir(parents=True, exist_ok=True)
    make_architecture(ARCH)
    doc = Document()
    configure(doc)

    # Portada APA para trabajo estudiantil.
    doc.add_paragraph().add_run("\n\n\n")
    p = doc.add_paragraph(style="Title")
    r = p.add_run("Documentación técnica de PoliTechNews")
    set_font(r, size=15, bold=True)
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.first_line_indent = Inches(0)
    for line in (
        "Santiago Calvo Patiño",
        "Politécnico Grancolombiano",
        "Front End",
        "John Olarte Ramos",
        "Medellín",
        "26 de septiembre de 2026",
    ):
        r = p.add_run(line + "\n")
        set_font(r)
    doc.add_page_break()

    heading(doc, "Resumen", 1)
    summary = body(doc, "PoliTechNews es un prototipo de periódico digital universitario construido con HTML, CSS y JavaScript sin dependencias de ejecución. Esta documentación explica su arquitectura lógica, la distribución del repositorio, las responsabilidades de cada archivo y el funcionamiento de las rutinas que cargan noticias desde JSON, renderizan vistas, validan formularios y conservan favoritos y cambios editoriales en localStorage. El sistema utiliza seis documentos HTML como puntos de entrada, una hoja de estilos compartida, un módulo JavaScript autocontenido y un archivo JSON con los datos iniciales. La interfaz se adapta a escritorio, tableta y teléfono mediante cuadrículas, flexbox y puntos de ruptura. Las pruebas de humo automatizadas recorren el catálogo, la búsqueda, los filtros, el detalle, los favoritos, la gestión de noticias, el contacto y la navegación móvil. La arquitectura es adecuada para una primera versión académica del lado del cliente, pero no reemplaza un backend: los datos creados existen solo en el navegador y la validación de contacto no envía información a un servidor. El documento también identifica restricciones, medidas de seguridad aplicadas y una ruta de evolución hacia Angular y servicios persistentes.")
    summary.paragraph_format.first_line_indent = Inches(0)
    p = doc.add_paragraph()
    p.paragraph_format.first_line_indent = Inches(0.5)
    r = p.add_run("Palabras clave: ")
    set_font(r, italic=True)
    r = p.add_run("arquitectura front end, JavaScript, JSON, localStorage, validación, diseño responsivo")
    set_font(r)
    doc.add_page_break()

    heading(doc, "Tabla de contenido", 1)
    add_toc(doc)
    doc.add_page_break()

    heading(doc, "Introducción", 1)
    body(doc, "Esta documentación técnica describe cómo está construida la segunda entrega de PoliTechNews y cómo colaboran sus componentes. Su finalidad es facilitar la evaluación académica, el mantenimiento del código y una futura migración a Angular. La explicación se basa en el código publicado en el repositorio del proyecto y en las orientaciones del módulo Front End.")
    body(doc, "El prototipo se ejecuta completamente en el navegador. Las noticias iniciales se solicitan con la API Fetch y se interpretan como JSON; las preferencias y modificaciones del usuario se serializan en localStorage. Fetch ofrece una interfaz basada en promesas para solicitar recursos y procesar sus respuestas (Mozilla, s. f.-a), mientras que localStorage conserva datos entre sesiones para un mismo origen (Mozilla, s. f.-b). Estas capacidades permiten demostrar interacción sin implementar todavía un servidor.")

    heading(doc, "Objetivos de la documentación", 2)
    numbered(doc, "Presentar la arquitectura y el flujo de ejecución del prototipo.")
    numbered(doc, "Explicar la distribución del repositorio y la responsabilidad de cada archivo.")
    numbered(doc, "Describir las funciones, estructuras de datos, eventos y validaciones del código.")
    numbered(doc, "Registrar las pruebas, restricciones técnicas y criterios de mantenimiento.")

    heading(doc, "Alcance y límites", 2)
    body(doc, "El documento cubre la versión estática disponible en la rama main del repositorio. No describe una API, base de datos, autenticación ni envío real de correo porque esas capacidades no forman parte de esta entrega. El mini CRUD y los favoritos son persistentes solo en el navegador que los creó. La documentación distingue esta limitación para evitar interpretar el prototipo como una aplicación de producción.")

    heading(doc, "Tecnologías y decisiones de diseño", 1)
    caption(doc, "Tabla 1", "Tecnologías empleadas")
    add_table(doc, ["Tecnología", "Uso en el proyecto", "Decisión técnica"], [
        ("HTML5", "Seis puntos de entrada semánticos", "Mantiene rutas legibles y metadatos propios por vista."),
        ("CSS3", "Diseño visual y responsivo", "Centraliza tokens, componentes y tres rangos de adaptación."),
        ("JavaScript ES6+", "Estado, renderizado e interacción", "Evita dependencias y hace explícitos los fundamentos del módulo."),
        ("JSON", "Catálogo inicial de 12 noticias", "Separa el contenido de la presentación y permite carga dinámica."),
        ("Web Storage", "Favoritos, altas y eliminaciones", "Ofrece persistencia local sin backend (Mozilla, s. f.-b)."),
        ("Playwright", "Pruebas de humo", "Automatiza recorridos críticos en un navegador real."),
        ("Git y GitHub", "Control de versiones y publicación del código", "Conserva historial y facilita revisión (GitHub, s. f.)."),
    ], [1.25, 2.15, 3.1], 8.7)
    note(doc, "El prototipo no utiliza Bootstrap, Tailwind ni un framework JavaScript; la interfaz se implementa con capacidades nativas del navegador.")

    heading(doc, "Arquitectura del sistema", 1)
    body(doc, "PoliTechNews adopta una arquitectura front end por capas. Los documentos HTML y CSS conforman la presentación; app.js concentra el estado y la lógica de aplicación; noticias.json proporciona los registros iniciales; localStorage conserva las modificaciones del usuario. La separación es conceptual, pues todo se ejecuta en el mismo proceso del navegador, pero permite identificar responsabilidades y preparar una migración posterior.")
    caption(doc, "Figura 1", "Arquitectura lógica de PoliTechNews")
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run()
    shape = run.add_picture(str(ARCH), width=Inches(6.3))
    shape._inline.docPr.set("descr", "Diagrama de arquitectura en cuatro bloques: presentación, aplicación, datos JSON y almacenamiento local.")
    note(doc, "Elaboración propia a partir de la implementación de PoliTechNews.")

    heading(doc, "Capa de presentación", 2)
    body(doc, "Los archivos HTML declaran idioma, codificación, metadatos, título, hoja de estilos y script. Cada body contiene un atributo data-page y un contenedor #app. La aplicación lee ese atributo para decidir qué vista debe renderizar. styles.css define el sistema visual, los componentes compartidos y los puntos de ruptura.")
    heading(doc, "Capa de aplicación", 2)
    body(doc, "app.js se encapsula en una función inmediatamente invocada. Esto evita introducir nombres en el espacio global. El módulo reúne constantes, estado, utilidades, constructores de interfaz, funciones de vista, acciones del usuario e inicialización. La delegación de eventos permite que elementos generados después de la carga inicial respondan sin registrar un controlador individual para cada tarjeta o fila.")
    heading(doc, "Capa de datos y persistencia", 2)
    body(doc, "data/noticias.json actúa como fuente de solo lectura. El estado efectivo combina ese catálogo con las noticias creadas en el navegador y excluye los identificadores eliminados. Tres claves versionadas de localStorage separan favoritos, contenido personalizado y eliminaciones. Como los valores de Web Storage son cadenas, el módulo aplica JSON.stringify y JSON.parse al guardar y recuperar listas.")

    heading(doc, "Flujo de ejecución", 2)
    numbered(doc, "El navegador analiza el HTML y carga styles.css y app.js con defer.", 1)
    numbered(doc, "init lee las tres colecciones persistidas y muestra un indicador de carga.", 2)
    numbered(doc, "fetch solicita data/noticias.json; el código verifica el estado HTTP y el tipo del resultado.", 3)
    numbered(doc, "El módulo enlaza los eventos globales y selecciona el renderizador según data-page.", 4)
    numbered(doc, "Cada acción actualiza state, localStorage o la URL, y vuelve a renderizar la región afectada.", 5)
    numbered(doc, "Si la carga falla, se muestra una instrucción para ejecutar el proyecto mediante un servidor local.", 6)

    heading(doc, "Distribución del repositorio", 1)
    code_block(doc, """
    PoliTechNews/
    ├── index.html, noticias.html, detalle.html
    ├── favoritos.html, gestion.html, contacto.html
    ├── app.js
    ├── styles.css
    ├── data/noticias.json
    ├── assets/images/
    ├── tests/smoke.js
    ├── output/docx/ y output/pdf/
    ├── README.md
    └── build_*.py
    """, "Árbol de directorios")
    body(doc, "La raíz contiene los archivos necesarios para ejecutar el sitio y revisar su entrega. Los recursos se agrupan por tipo. La carpeta output contiene artefactos académicos; tests contiene la verificación automatizada; los scripts build generan documentación y no intervienen durante la ejecución de la aplicación.")

    caption(doc, "Tabla 2", "Responsabilidad de los archivos principales")
    add_table(doc, ["Archivo o ruta", "Responsabilidad", "Dependencias directas"], [
        ("index.html", "Punto de entrada de Inicio.", "styles.css y app.js"),
        ("noticias.html", "Punto de entrada del catálogo.", "styles.css, app.js y noticias.json"),
        ("detalle.html", "Punto de entrada del detalle por parámetro id.", "app.js, JSON y query string"),
        ("favoritos.html", "Lista personalizada de publicaciones guardadas.", "app.js y localStorage"),
        ("gestion.html", "Formulario editorial, estadísticas y mini CRUD.", "app.js, FileReader y localStorage"),
        ("contacto.html", "Formulario validado y preguntas frecuentes.", "app.js y validación HTML"),
        ("app.js", "Estado, carga de datos, plantillas, eventos y persistencia.", "DOM, Fetch, History, Storage y FileReader"),
        ("styles.css", "Tokens, componentes, vistas y reglas responsivas.", "Fuentes web con alternativas locales"),
        ("data/noticias.json", "Catálogo base estructurado.", "Consumido por fetch en init"),
        ("assets/images/", "Logo, portada e ilustraciones por categoría.", "Referenciadas por HTML, JS y JSON"),
        ("tests/smoke.js", "Prueba automatizada de recorridos críticos.", "Playwright y Chrome"),
        ("README.md", "Ejecución, alcance y criterios de revisión.", "Repositorio GitHub"),
    ], [1.7, 2.7, 2.1], 8.3)

    heading(doc, "Documentos HTML", 1)
    body(doc, "Los seis documentos comparten una plantilla mínima. Esta decisión evita duplicar cabecera, menú, pie y contenido. app.js genera esos componentes una vez y los adapta a la vista actual.")
    code_block(doc, """
    <body data-page="noticias">
      <div id="app"></div>
    </body>
    """)
    body(doc, "data-page funciona como un identificador de ruta. #app es el nodo de montaje. El script se carga con defer para ejecutarse cuando el documento ya fue analizado, y cada archivo conserva un title y una meta description específicos. Esta estructura facilita el SEO básico, la navegación sin framework y la lectura del código.")
    caption(doc, "Tabla 3", "Correspondencia entre documentos y renderizadores")
    add_table(doc, ["Valor data page", "Archivo", "Función de vista", "Resultado"], [
        ("inicio", "index.html", "renderHome", "Portada, destacados, categorías y CTA."),
        ("noticias", "noticias.html", "renderNews", "Buscador, filtros, tarjetas y paginación."),
        ("detalle", "detalle.html", "renderDetail", "Artículo, favoritos, relacionados y compartir."),
        ("favoritos", "favoritos.html", "renderFavorites", "Selección persistida y ordenamiento."),
        ("gestion", "gestion.html", "renderAdmin", "Formulario, estadísticas, filtros y eliminación."),
        ("contacto", "contacto.html", "renderContact", "Información, formulario y preguntas frecuentes."),
    ], [1.25, 1.4, 1.45, 2.4], 8.2)

    heading(doc, "Hoja de estilos", 1)
    body(doc, "styles.css contiene el sistema visual completo. Las variables declaradas en :root almacenan colores, sombra y radios; así se evita repetir valores y se mantiene correspondencia con los mockups. Los componentes comunes preceden a los estilos de cada vista para que la cascada avance de lo general a lo específico.")
    caption(doc, "Tabla 4", "Organización de styles.css")
    add_table(doc, ["Bloque", "Selectores representativos", "Función"], [
        ("Base", ":root, *, body, h1-h3, input", "Reinicio, tokens, tipografía y controles."),
        ("Estructura", ".container, .section", "Ancho máximo y espaciado vertical."),
        ("Navegación", ".site-header, .main-nav, .menu-toggle", "Menú de escritorio y móvil."),
        ("Componentes", ".button, .toast, .banner, .panel", "Acciones, mensajes y contenedores reutilizables."),
        ("Inicio", ".home-hero, .news-grid, .community-card", "Portada y tarjetas destacadas."),
        ("Detalle", ".article-page, .article-layout, .article-aside", "Lectura principal y contenido relacionado."),
        ("Favoritos", ".favorite-card, .toolbar, .tip-panel", "Listado personal y acciones."),
        ("Gestión", ".admin-grid, .stats-grid, .admin-table", "Panel editorial y tabla de noticias."),
        ("Contacto", ".contact-grid, .contact-info, .faq-grid", "Datos de contacto, formulario y FAQ."),
        ("Responsividad", "@media 1020, 760 y 560 px", "Reorganiza cuadrículas, menú, tablas y formularios."),
    ], [1.4, 2.45, 2.65], 8.2)
    heading(doc, "Diseño adaptable", 2)
    body(doc, "A 1020 píxeles se oculta el CTA del encabezado y los paneles complejos pasan a una columna. A 760 píxeles aparece el menú móvil, el hero omite la ilustración decorativa y las cuadrículas reducen columnas. A 560 píxeles las tarjetas, formularios y acciones se apilan. Las pruebas verifican que una ventana de 390 píxeles no produzca desplazamiento horizontal.")

    heading(doc, "Módulo JavaScript", 1)
    body(doc, "app.js contiene 33 funciones agrupables en siete responsabilidades. La variable state mantiene el modelo actual de la interfaz: datos base, registros personalizados, elementos eliminados, favoritos, filtros y páginas. Las constantes CATEGORIES, DEFAULT_IMAGE y KEY centralizan opciones y nombres de almacenamiento.")
    caption(doc, "Tabla 5", "Funciones de almacenamiento, datos y utilidades")
    add_table(doc, ["Función", "Entrada y salida", "Responsabilidad"], [
        ("read", "clave y valor alternativo -> arreglo", "Lee JSON de localStorage; ante bloqueo o formato inválido devuelve el valor seguro."),
        ("save", "clave y valor -> booleano", "Serializa una lista; informa al usuario si el navegador no puede guardarla."),
        ("esc", "cualquier valor -> texto HTML seguro", "Escapa &, <, >, comillas dobles y simples antes de insertar contenido editable."),
        ("plain", "valor -> cadena", "Convierte a texto y elimina espacios exteriores."),
        ("dateLabel", "fecha ISO -> fecha es CO", "Formatea fechas con Intl.DateTimeFormat y zona UTC."),
        ("allArticles", "estado -> arreglo", "Fusiona registros base y personalizados y descarta los identificadores eliminados."),
        ("published", "estado -> arreglo", "Conserva solo publicados y ordena por fecha descendente."),
        ("getArticle", "id -> noticia o undefined", "Busca una noticia dentro del catálogo efectivo."),
        ("href", "id -> URL", "Construye detalle.html?id=... con codificación segura."),
        ("categoryClass", "categoría -> clase CSS", "Asocia categorías con etiquetas visuales."),
        ("imageSrc", "noticia -> ruta o data URL", "Acepta recursos locales o imágenes cargadas; usa una alternativa si el origen no es válido."),
    ], [1.55, 1.75, 3.2], 8.1)

    caption(doc, "Tabla 6", "Funciones de componentes y renderizado")
    add_table(doc, ["Función", "Responsabilidad"], [
        ("nav", "Construye marca, navegación, estado activo, botón móvil y CTA."),
        ("footer", "Genera información institucional, enlaces y región aria live para avisos."),
        ("shell", "Monta cabecera, main y pie dentro de #app."),
        ("announce", "Muestra un toast temporal de éxito o error."),
        ("banner", "Crea la cabecera reutilizable de las vistas internas."),
        ("card", "Convierte una noticia en tarjeta con imagen, categoría, resumen y enlace."),
        ("emptyState", "Presenta un estado vacío consistente y una acción opcional."),
        ("renderHome", "Compone hero, tres noticias recientes, categorías y bloque comunitario."),
        ("renderNews", "Monta filtros y entrega el listado a newsResults."),
        ("renderDetail", "Lee id, valida disponibilidad, muestra contenido, favoritos y relacionados."),
        ("renderFavorites", "Resuelve identificadores guardados, ordena y presenta la colección."),
        ("renderAdmin", "Calcula estadísticas y construye formulario y panel de gestión."),
        ("renderContact", "Construye información, formulario validado y preguntas frecuentes."),
    ], [1.45, 5.05], 8.5)

    heading(doc, "Catálogo, búsqueda y paginación", 2)
    body(doc, "filteredNews normaliza la consulta a minúsculas con configuración de español y aplica dos condiciones: coincidencia exacta de categoría y presencia del texto en título, resumen o categoría. pagination construye controles con estado activo, botones anterior y siguiente y atributos aria. newsResults calcula el número de páginas, limita el índice actual, recorta seis noticias y devuelve tarjetas o un estado vacío.")
    code_block(doc, """
    const items = filteredNews();
    const perPage = 6;
    const pages = Math.max(1, Math.ceil(items.length / perPage));
    state.page = Math.min(state.page, pages);
    const shown = items.slice((state.page - 1) * perPage, state.page * perPage);
    """)
    body(doc, "Este cálculo evita páginas inexistentes después de cambiar un filtro. Al seleccionar una categoría, history.replaceState sincroniza la URL sin recargar el documento.")

    heading(doc, "Favoritos", 2)
    body(doc, "toggleFavorite alterna el identificador de una noticia dentro de state.favorites, persiste la lista y actualiza la vista correspondiente. Guardar solo identificadores evita duplicar el objeto completo. Cuando se abre Favoritos, renderFavorites resuelve cada id contra el catálogo efectivo; por ello, una noticia eliminada deja de mostrarse aunque su id estuviera guardado.")

    heading(doc, "Gestión básica de noticias", 2)
    body(doc, "imageForForm valida que una imagen sea PNG, JPEG o WebP y no supere 1 MB. FileReader la convierte en data URL para almacenarla junto al registro. Si el usuario no carga una imagen, se reutiliza la ilustración de la categoría. createArticle ejecuta reportValidity, lee el formulario con FormData, divide el contenido por párrafos, calcula un tiempo de lectura aproximado y guarda un registro published o draft.")
    code_block(doc, """
    const article = {
      id: `user-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`,
      title: plain(fields.get("title")),
      category: plain(fields.get("category")),
      content,
      status: mode === "draft" ? "draft" : "published"
    };
    """)
    body(doc, "La eliminación distingue registros personalizados y noticias base. Los primeros se retiran de la colección custom; los segundos conservan el JSON intacto y agregan su id a deleted. También se elimina el id de favoritos para evitar referencias huérfanas.")

    heading(doc, "Eventos e inicialización", 2)
    caption(doc, "Tabla 7", "Funciones de interacción y ciclo de vida")
    add_table(doc, ["Función", "Funcionamiento"], [
        ("onClick", "Delega categorías, paginación, limpieza de filtros, favoritos, eliminación, compartir y navegación administrativa mediante data-action."),
        ("onSubmit", "Intercepta búsqueda, filtros administrativos, creación editorial y contacto; impide recargas innecesarias."),
        ("bindEvents", "Registra click, submit, change e input una sola vez; también controla el menú móvil y el contador de caracteres."),
        ("init", "Recupera Storage, solicita el JSON, valida el resultado, enlaza eventos y despacha la función de vista."),
    ], [1.35, 5.15], 8.7)
    body(doc, "El objeto que despacha vistas funciona como un enrutador liviano: asigna a cada valor de data-page su renderizador. Si el valor no existe, renderHome opera como alternativa segura.")

    heading(doc, "Modelo de datos JSON", 1)
    body(doc, "noticias.json contiene 12 objetos con una estructura uniforme. La separación entre datos y vista permite reutilizar la misma información en Inicio, Noticias, Detalle, Favoritos y Gestión.")
    caption(doc, "Tabla 8", "Esquema de una noticia")
    add_table(doc, ["Propiedad", "Tipo", "Uso"], [
        ("id", "string", "Identificador único usado en URL, favoritos y eliminación."),
        ("title", "string", "Título de tarjeta, detalle y búsqueda."),
        ("category", "string", "Filtro, etiqueta y selección de imagen."),
        ("summary", "string", "Resumen de tarjetas y panel lateral."),
        ("date", "string ISO", "Orden cronológico y etiqueta localizada."),
        ("minutes", "number", "Tiempo estimado de lectura."),
        ("image", "string", "Ruta de recurso o data URL validada."),
        ("author", "string", "Crédito editorial."),
        ("content", "string[]", "Párrafos del cuerpo de la noticia."),
        ("status", "string opcional", "published o draft en noticias creadas localmente."),
    ], [1.25, 1.3, 3.95], 8.5)

    heading(doc, "Persistencia local", 1)
    caption(doc, "Tabla 9", "Claves de localStorage")
    add_table(doc, ["Clave", "Contenido", "Actualización"], [
        ("politechnews:favorites:v1", "Arreglo de identificadores favoritos.", "toggleFavorite y eliminación."),
        ("politechnews:custom:v1", "Objetos creados o borradores.", "createArticle y eliminación."),
        ("politechnews:deleted:v1", "Identificadores base ocultos.", "Eliminación desde Gestión."),
    ], [2.25, 2.45, 1.8], 8.5)
    body(doc, "El sufijo v1 permite cambiar el formato en una versión futura sin sobrescribir silenciosamente datos antiguos. read captura errores de análisis o acceso y devuelve un arreglo seguro. save captura errores de cuota o permisos y muestra un mensaje. De acuerdo con MDN, localStorage conserva datos entre sesiones pero depende del origen; por eso el proyecto debe ejecutarse con un servidor local y no mediante file:// (Mozilla, s. f.-b).")

    heading(doc, "Validaciones y seguridad", 1)
    body(doc, "Los formularios combinan restricciones HTML con reportValidity. HTML define required, type=email, minlength, maxlength y límites de archivos; JavaScript controla el flujo y presenta confirmación. La validación del cliente mejora la experiencia, pero no sustituye una validación de servidor cuando existen datos remotos (Mozilla, s. f.-c). En PoliTechNews el contacto es simulado y no transmite información.")
    caption(doc, "Tabla 10", "Controles de seguridad y robustez")
    add_table(doc, ["Control", "Implementación", "Riesgo mitigado"], [
        ("Escape HTML", "esc procesa contenido antes de usar innerHTML.", "Inyección de etiquetas desde entradas editables."),
        ("Lista permitida de imágenes", "imageSrc acepta assets/images o data:image.", "Carga arbitraria de orígenes no previstos."),
        ("Tipo y tamaño de archivo", "PNG, JPEG o WebP hasta 1 MB.", "Datos incompatibles y consumo excesivo de Storage."),
        ("Validación de JSON", "init exige response.ok y un arreglo.", "Renderizado con respuesta inválida."),
        ("Confirmación de borrado", "confirm antes de retirar contenido.", "Eliminación accidental."),
        ("Manejo de errores", "try/catch en Storage, archivo y carga inicial.", "Fallas silenciosas."),
    ], [1.55, 2.9, 2.05], 8.4)

    heading(doc, "Accesibilidad y experiencia de usuario", 1)
    bullet(doc, "El documento declara lang=es y títulos específicos por página.")
    bullet(doc, "El enlace Saltar al contenido permite omitir la navegación con teclado.")
    bullet(doc, "aria-current identifica la sección activa y aria-expanded comunica el estado del menú.")
    bullet(doc, "Los avisos usan role=status y aria-live=polite.")
    bullet(doc, "Los botones de paginación y favoritos tienen etiquetas accesibles y estados disabled o aria-pressed.")
    bullet(doc, "Las imágenes de contenido incluyen texto alternativo; los adornos se marcan como ocultos para tecnologías de asistencia.")
    body(doc, "La implementación aplica una base accesible, pero una entrega de producción debería incorporar auditorías con lectores de pantalla, contraste automatizado y navegación completa por teclado.")

    heading(doc, "Pruebas y verificación", 1)
    body(doc, "tests/smoke.js inicia Chrome mediante Playwright, crea un contexto aislado y registra errores de página. Las aserciones verifican tanto el número de elementos como la persistencia después de recargar. Las capturas generadas por la prueba sirven para revisión visual, pero no se almacenan en Git porque tmp está ignorado.")
    caption(doc, "Tabla 11", "Cobertura de la prueba de humo")
    add_table(doc, ["Recorrido", "Comprobación"], [
        ("Inicio", "Tres tarjetas destacadas y captura completa."),
        ("Noticias", "Seis resultados por página, filtro Cloud y búsqueda por texto."),
        ("Detalle y favoritos", "Alta de favorito, visualización y persistencia tras recargar."),
        ("Gestión", "Publicación, visibilidad en catálogo, eliminación y borrador no publicado."),
        ("Contacto", "Campos válidos, privacidad y mensaje de confirmación."),
        ("Móvil", "Menú abre y cierra; ancho de documento no supera 390 px."),
        ("Errores", "La colección pageerror termina vacía."),
    ], [2.0, 4.5], 8.7)
    code_block(doc, """
    $env:NODE_PATH='.../node_modules'
    node tests/smoke.js

    SMOKE_OK: inicio, catálogo, búsqueda, filtros, detalle,
    favoritos, CRUD, contacto y móvil
    """, "PowerShell")

    heading(doc, "Ejecución y mantenimiento", 1)
    heading(doc, "Ejecución local", 2)
    code_block(doc, """
    cd C:\\Users\\santy\\Documents\\ChatGPT\\webPage
    python -m http.server 8000
    # Abrir http://localhost:8000
    """, "PowerShell")
    body(doc, "Se requiere un servidor HTTP porque fetch debe solicitar el archivo JSON dentro de un origen válido. Abrir index.html directamente con file:// puede bloquear la solicitud.")
    heading(doc, "Repositorio y control de versiones", 2)
    p = body(doc, "El código y los documentos se encuentran en ")
    add_hyperlink(p, REPO, REPO)
    r = p.add_run(". Git conserva el historial de cambios y GitHub publica el repositorio para revisión. Un sistema de control de versiones permite rastrear qué cambió, quién lo hizo y cuándo ocurrió (GitHub, s. f.).")
    set_font(r)
    heading(doc, "Convenciones de mantenimiento", 2)
    bullet(doc, "Conservar los id de noticias únicos y estables.")
    bullet(doc, "Añadir categorías tanto a CATEGORIES como a categoryClass y a la selección de imagen.")
    bullet(doc, "Actualizar el sufijo de claves si cambia el esquema persistido.")
    bullet(doc, "Mantener las plantillas con esc para cualquier contenido que provenga de formularios.")
    bullet(doc, "Ejecutar node --check app.js y tests/smoke.js antes de publicar cambios.")
    bullet(doc, "No modificar archivos generados de output sin regenerar la documentación correspondiente.")

    heading(doc, "Limitaciones y evolución propuesta", 1)
    caption(doc, "Tabla 12", "Limitaciones y alternativa de evolución")
    add_table(doc, ["Limitación actual", "Efecto", "Evolución recomendada"], [
        ("Sin backend", "Los datos no se comparten entre dispositivos.", "API REST y base de datos."),
        ("Sin autenticación", "Gestión está disponible para cualquier visitante.", "Roles y sesión segura."),
        ("localStorage", "Cuota limitada y sin sincronización.", "Persistencia remota; Storage solo para preferencias."),
        ("Plantillas HTML en cadenas", "app.js concentra presentación y lógica.", "Componentes Angular y servicios."),
        ("Contacto simulado", "No llega una solicitud al equipo.", "Servicio de correo o endpoint de formularios."),
        ("Prueba de humo única", "Cobertura parcial de casos extremos.", "Pruebas unitarias, accesibilidad y CI."),
    ], [1.65, 2.1, 2.75], 8.5)
    body(doc, "La migración a Angular puede conservar el modelo de noticia, las rutas y la identidad visual. Las funciones renderHome, renderNews y demás se convertirían en componentes; read y save pasarían a un servicio de persistencia; el estado de filtros podría gestionarse mediante propiedades y binding; la carga JSON se realizaría con HttpClient. Esta transición reduce el tamaño del módulo único y coincide con la Entrega 3 indicada en las orientaciones.")

    heading(doc, "Conclusiones", 1)
    body(doc, "La arquitectura de PoliTechNews separa de forma comprensible la presentación, la lógica, los datos y la persistencia dentro de un prototipo del lado del cliente. Los seis archivos HTML actúan como rutas; styles.css garantiza una identidad visual compartida y adaptable; app.js coordina carga, renderizado, validaciones y eventos; JSON y localStorage proporcionan datos iniciales y continuidad local.")
    body(doc, "La explicación función por función demuestra que el sistema no consiste solo en páginas estáticas. La carga asíncrona, los filtros, la paginación, los favoritos, el mini CRUD y las validaciones responden a un mismo estado controlado. Las pruebas automatizadas respaldan los recorridos principales. Las limitaciones registradas son coherentes con una segunda entrega académica y definen una ruta clara hacia Angular, persistencia remota y despliegue en la siguiente fase.")

    heading(doc, "Referencias", 1)
    refs = [
        "Calvo Patiño, S. (2026). PoliTechNews [Código fuente]. GitHub. https://github.com/santycp/PoliTechNews",
        "GitHub. (s. f.). Acerca de Git. GitHub Docs. https://docs.github.com/es/get-started/using-git/about-git",
        "Mozilla. (s. f.-a). Uso de Fetch. MDN Web Docs. https://developer.mozilla.org/es/docs/Web/API/Fetch_API/Using_Fetch",
        "Mozilla. (s. f.-b). Window.localStorage. MDN Web Docs. https://developer.mozilla.org/es/docs/Web/API/Window/localStorage",
        "Mozilla. (s. f.-c). Validación de formularios en el lado del cliente. MDN Web Docs. https://developer.mozilla.org/es/docs/Learn_web_development/Extensions/Forms/Form_validation",
        "Olarte Ramos, J. (2026). Orientaciones para las entregas del módulo Front End Agosto 2026-1 [Documento de curso]. Politécnico Grancolombiano.",
    ]
    for value in refs:
        p = doc.add_paragraph(style="Normal")
        p.paragraph_format.first_line_indent = Inches(-0.5)
        p.paragraph_format.left_indent = Inches(0.5)
        r = p.add_run(value)
        set_font(r)

    doc.core_properties.title = "Documentación técnica de PoliTechNews"
    doc.core_properties.subject = "Arquitectura, código, distribución de archivos y pruebas"
    doc.core_properties.author = "Santiago Calvo Patiño"
    doc.core_properties.keywords = "PoliTechNews, Front End, JavaScript, APA, arquitectura"
    doc.save(OUT)
    print(OUT)


if __name__ == "__main__":
    build()
