"""Genera el informe APA de la Entrega 2 y anexa los seis mockups originales."""

from __future__ import annotations

import argparse
from io import BytesIO
from pathlib import Path
import textwrap
from xml.sax.saxutils import escape

from pypdf import PdfReader, PdfWriter
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    KeepTogether,
    PageBreak,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parent
SOURCE_PDF = ROOT / "output" / "pdf" / "PoliTechNews_Entrega_1.pdf"
FINAL_PDF = ROOT / "output" / "pdf" / "PoliTechNews_Entrega_2.pdf"
DRAFT_PDF = ROOT / "tmp" / "pdfs" / "PoliTechNews_Entrega_2_Borrador.pdf"
FIGMA_URL = "https://www.figma.com/design/A2QASHWYMKsV5a853lZ3dQ/PoliTechNews-%E2%80%94-Entrega-1"

INK = colors.HexColor("#15243b")
BLUE = colors.HexColor("#0B3A72")
TEAL = colors.HexColor("#0D9FB0")
PALE = colors.HexColor("#eef6fa")
GRAY = colors.HexColor("#506078")

styles = {
    "body": ParagraphStyle("body", fontName="Times-Roman", fontSize=12, leading=21,
                           textColor=INK, spaceAfter=10, alignment=TA_LEFT),
    "small": ParagraphStyle("small", fontName="Times-Roman", fontSize=10.5, leading=15,
                            textColor=INK, spaceAfter=7),
    "h1": ParagraphStyle("h1", fontName="Times-Bold", fontSize=16, leading=20,
                         textColor=INK, spaceAfter=16, alignment=TA_CENTER),
    "h2": ParagraphStyle("h2", fontName="Times-Bold", fontSize=12, leading=18,
                         textColor=INK, spaceBefore=13, spaceAfter=5),
    "cover": ParagraphStyle("cover", fontName="Times-Bold", fontSize=16, leading=23,
                            textColor=INK, alignment=TA_CENTER),
    "center": ParagraphStyle("center", fontName="Times-Roman", fontSize=12, leading=21,
                             textColor=INK, alignment=TA_CENTER),
    "table": ParagraphStyle("table", fontName="Times-Roman", fontSize=9.5, leading=13,
                            textColor=INK),
    "tablehead": ParagraphStyle("tablehead", fontName="Times-Bold", fontSize=9.5, leading=13,
                                textColor=colors.white),
    "code": ParagraphStyle("code", fontName="Courier", fontSize=8.2, leading=12,
                           textColor=INK),
}


def para(text: str, style: str = "body") -> Paragraph:
    return Paragraph(text, styles[style])


def heading(text: str) -> Paragraph:
    return para(escape(text), "h1")


def subheading(text: str) -> Paragraph:
    return para(escape(text), "h2")


def page_number(canvas, doc):
    canvas.saveState()
    canvas.setFont("Times-Roman", 10)
    canvas.setFillColor(INK)
    canvas.drawRightString(letter[0] - inch, letter[1] - 0.52 * inch, str(doc.page))
    canvas.restoreState()


def code_box(source: str):
    block = Preformatted(source.strip("\n"), styles["code"])
    table = Table([[block]], colWidths=[6.4 * inch])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), PALE),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#c6d9e7")),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
    ]))
    return table


def matrix(headers, rows, widths):
    data = [[para(escape(h), "tablehead") for h in headers]]
    data.extend([[para(escape(str(cell)), "table") for cell in row] for row in rows])
    table = Table(data, colWidths=widths, repeatRows=1, hAlign="LEFT")
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), BLUE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, PALE]),
        ("LINEBELOW", (0, 0), (-1, 0), 0.6, BLUE),
        ("LINEBELOW", (0, 1), (-1, -1), 0.3, colors.HexColor("#ccdce9")),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    return table


def build_main(repo_url: str, source_pages: int) -> bytes:
    stream = BytesIO()
    doc = SimpleDocTemplate(
        stream, pagesize=letter, leftMargin=inch, rightMargin=inch,
        topMargin=0.9 * inch, bottomMargin=0.8 * inch,
        title="PoliTechNews - Entrega 2", author="Santiago Calvo Patiño",
    )
    story = []

    # 1. Portada académica.
    story += [Spacer(1, 1.6 * inch), para("PoliTechNews", "cover"), Spacer(1, 0.15 * inch),
              para("Prototipo funcional de plataforma web de noticias tecnológicas", "cover"),
              Spacer(1, 1.25 * inch), para("Santiago Calvo Patiño", "center"),
              para("Politécnico Grancolombiano", "center"), para("Front End", "center"),
              para("John Olarte Ramos", "center"), Spacer(1, 1.2 * inch),
              para("Medellín, Colombia", "center"), para("09/12/2026", "center"), PageBreak()]

    # 2. Tabla de contenido. La sección de mockups conserva la secuencia del informe original.
    story += [heading("Tabla de contenido")]
    contents = [
        ("Introducción y objetivos", "3"),
        ("Cumplimiento de los requisitos", "4"),
        ("Arquitectura e implementación", "5"),
        ("Código fuente representativo", "6"),
        ("Verificación funcional", "7"),
        ("Conclusiones y referencias", "8"),
        ("Anexo A. Maquetación de la Entrega 1", "9-14"),
        ("Anexo B. Código fuente completo", f"15-{14 + source_pages}"),
    ]
    story.append(matrix(["Sección", "Página"], contents, [5.4 * inch, 1 * inch]))
    story += [Spacer(1, 0.3 * inch), para(
        "<b>Repositorio:</b> " + escape(repo_url) + "<br/>"
        "<b>Diseño original:</b> " + escape(FIGMA_URL), "small"), PageBreak()]

    # 3. Introducción y objetivos.
    story += [heading("Introducción y objetivos"),
              para("La segunda entrega presenta una primera versión funcional de PoliTechNews, "
                   "un periódico digital universitario enfocado en noticias de tecnología. "
                   "El desarrollo parte de los seis mockups realizados en Figma durante la Entrega 1 "
                   "y conserva su navegación, jerarquía visual, colores y componentes principales."),
              para("De acuerdo con las orientaciones del módulo, esta etapa requiere HTML, CSS y "
                   "JavaScript, renderizado dinámico desde JSON, favoritos, formularios con validación, "
                   "código organizado y un repositorio de GitHub (Olarte Ramos, 2026)."),
              subheading("Objetivo general"),
              para("Implementar un prototipo web de noticias tecnológicas que permita consultar "
                   "publicaciones, ver sus detalles e interactuar con favoritos y formularios."),
              subheading("Objetivos específicos"),
              para("1. Reproducir en navegador las vistas diseñadas en la primera entrega.<br/>"
                   "2. Cargar y presentar las noticias iniciales desde un archivo JSON local.<br/>"
                   "3. Permitir buscar, filtrar, consultar y guardar noticias favoritas.<br/>"
                   "4. Validar la creación de noticias y el formulario de contacto.<br/>"
                   "5. Verificar la interfaz en resoluciones de escritorio y móvil."), PageBreak()]

    # 4. Matriz de trazabilidad con el documento del tutor.
    story += [heading("Cumplimiento de los requisitos"),
              para("La Tabla 1 relaciona los criterios explícitos de la Entrega 2 con la implementación "
                   "actual. Angular, el despliegue público y el video explicativo se reservan para la "
                   "Entrega 3, según la secuencia indicada por la guía."),
              subheading("Tabla 1"), para("Trazabilidad de los requisitos del prototipo", "small")]
    story.append(matrix(["Requisito", "Implementación verificable"], [
        ("HTML, CSS y JavaScript", "Seis páginas HTML; estilos responsivos en styles.css; lógica compartida en app.js."),
        ("Datos desde JSON", "data/noticias.json contiene 12 noticias; init() las obtiene con fetch()."),
        ("Favoritos", "Alta y retiro desde detalle; listado y persistencia en localStorage."),
        ("Formularios validados", "Gestión y contacto usan validaciones HTML y reportValidity()."),
        ("Código estructurado", "Separación por páginas, datos, recursos, estilos y funciones de vista/interacción."),
        ("Repositorio GitHub", repo_url),
        ("Correspondencia con mockups", "Inicio, Noticias, Detalle, Favoritos, Gestión y Contacto siguen las vistas del Anexo A."),
    ], [2.15 * inch, 4.25 * inch]))
    story += [Spacer(1, 0.2 * inch), para("<b>Alcance:</b> el prototipo no emplea servidor ni base de datos. "
              "Las modificaciones realizadas por el usuario se conservan únicamente en su navegador.", "small"), PageBreak()]

    # 5. Arquitectura.
    story += [heading("Arquitectura e implementación"),
              para("La aplicación usa un directorio raíz sencillo para abrirse en cualquier navegador "
                   "moderno mediante un servidor estático. El archivo app.js identifica la vista a "
                   "partir del atributo data-page del documento y comparte encabezado, pie, tarjetas "
                   "y mensajes de estado entre las seis páginas."),
              subheading("Organización de archivos")]
    story.append(matrix(["Ruta", "Responsabilidad"], [
        ("index.html y demás *.html", "Puntos de entrada de cada vista."),
        ("styles.css", "Colores, tipografía, componentes y reglas responsivas."),
        ("app.js", "Carga de datos, renderizado y manejo de eventos."),
        ("data/noticias.json", "Noticias demostrativas iniciales."),
        ("assets/images/", "Logo e ilustraciones derivados de la maquetación."),
        ("tests/smoke.js", "Pruebas automáticas de navegación y funcionalidades."),
    ], [2.05 * inch, 4.35 * inch]))
    story += [subheading("Flujo de datos"),
              para("Al cargar una página, init() lee las preferencias guardadas en localStorage, "
                   "solicita el JSON con fetch(), combina las noticias base con las creadas localmente "
                   "y renderiza la vista. Los eventos de búsqueda, filtros, favoritos y gestión actualizan "
                   "el estado y vuelven a renderizar el fragmento pertinente."),
              subheading("Vistas desarrolladas"),
              para("Inicio muestra destacados y categorías; Noticias permite buscar, filtrar y paginar; "
                   "Detalle presenta el contenido completo y el control de favoritos; Favoritos reúne "
                   "la selección personal; Gestión permite publicar, guardar borradores y eliminar; "
                   "Contacto valida los campos y muestra una confirmación simulada."), PageBreak()]

    # 6. Extractos reales, legibles y relacionados con la rúbrica.
    story += [heading("Código fuente representativo"),
              para("Los fragmentos siguientes proceden de app.js. El código íntegro, comentado por "
                   "responsabilidades, figura en el Anexo B y en el repositorio de la página 2."),
              subheading("Carga dinámica de noticias desde JSON"),
              code_box('''const response = await fetch("data/noticias.json");
if (!response.ok) throw new Error(`HTTP ${response.status}`);
const data = await response.json();
if (!Array.isArray(data)) throw new Error("Formato JSON incorrecto");
state.base = data;'''),
              Spacer(1, 0.13 * inch),
              para("La comprobación de respuesta y tipo de dato evita mostrar contenido incompleto "
                   "si falla la carga del archivo."),
              subheading("Persistencia de favoritos"),
              code_box('''if (state.favorites.includes(id))
  state.favorites = state.favorites.filter((value) => value !== id);
else state.favorites.unshift(id);
save(KEY.favorites, state.favorites);'''),
              Spacer(1, 0.13 * inch),
              para("La función save() serializa el arreglo en localStorage; al abrir otra página, "
                   "read() recupera la selección personal. El almacenamiento es local al navegador "
                   "y no equivale a una cuenta de usuario."), PageBreak()]

    # 7. Verificación.
    story += [heading("Verificación funcional"),
              para("Se ejecutaron pruebas automatizadas de interfaz con un navegador real y comprobaciones "
                   "de sintaxis y datos. La Tabla 2 resume los recorridos cubiertos."),
              subheading("Tabla 2"), para("Recorridos de prueba del prototipo", "small")]
    story.append(matrix(["Recorrido", "Resultado esperado"], [
        ("Inicio y navegación", "Las seis páginas abren y el menú dirige a la vista correcta."),
        ("Noticias", "Búsqueda, categorías y paginación modifican el listado."),
        ("Detalle y favoritos", "Una noticia abre por su identificador y permanece guardada tras recargar."),
        ("Gestión", "Crear, publicar, guardar borradores y eliminar actualiza el contenido local."),
        ("Contacto", "La validación rechaza datos incompletos y confirma un formulario válido."),
        ("Diseño adaptable", "La vista móvil conserva la navegación y no presenta desbordamiento horizontal."),
    ], [2 * inch, 4.4 * inch]))
    story += [Spacer(1, 0.18 * inch),
              para("La prueba de humo finalizó sin errores. También se verificó la sintaxis de "
                   "app.js y la integridad de las 12 entradas iniciales del JSON."),
              subheading("Limitaciones deliberadas"),
              para("El formulario de contacto no envía correos ni almacena datos personales. "
                   "Las noticias creadas y eliminadas, así como los favoritos, existen solo en "
                   "el navegador actual. El despliegue público y la implementación básica en Angular "
                   "corresponden a la Entrega 3, no a este prototipo."), PageBreak()]

    # 8. Cierre y fuentes.
    story += [heading("Conclusiones y referencias"),
              para("PoliTechNews convierte la maquetación inicial en un prototipo navegable y funcional. "
                   "La separación de datos, presentación e interacciones permite demostrar el uso "
                   "de HTML, CSS y JavaScript sin depender de un backend. La carga dinámica, los "
                   "favoritos persistentes y las validaciones cubren los requisitos de esta etapa."),
              para("La solución mantiene una correspondencia visual con los seis mockups de la "
                   "Entrega 1, reproducidos en el Anexo A. La siguiente fase podrá incorporar Angular, "
                   "despliegue público y un video explicativo sin redefinir el contenido ni la navegación."),
              subheading("Referencias"),
              para("GitHub. (s. f.). <i>Creating a new repository</i>. GitHub Docs. "
                   "https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-new-repository", "small"),
              para("Mozilla. (s. f.). <i>Uso de Fetch</i>. MDN Web Docs. "
                   "https://developer.mozilla.org/es/docs/Web/API/Fetch_API/Using_Fetch", "small"),
              para("Mozilla. (s. f.). <i>Window.localStorage</i>. MDN Web Docs. "
                   "https://developer.mozilla.org/es/docs/Web/API/Window/localStorage", "small"),
              para("Olarte Ramos, J. (2026). <i>Orientaciones para las entregas del módulo Front End "
                   "Agosto 2026-1</i> [Documento de curso]. Politécnico Grancolombiano.", "small"),
              para("Calvo Patiño, S. (2026). <i>PoliTechNews - Entrega 1</i> [Maquetación en Figma]. "
                   + escape(FIGMA_URL), "small"),
              Spacer(1, 0.15 * inch),
              para("<b>URL del código fuente:</b> " + escape(repo_url), "small"),
              para("<b>Anexo A:</b> Figuras 1 a 6 del informe de maquetación de la Entrega 1, "
                   "incorporadas sin alterar los diseños originales.", "small"),
              para("<b>Anexo B:</b> Código fuente completo de las seis páginas, CSS, JavaScript "
                   "y archivo de datos JSON.", "small")]

    doc.build(story, onFirstPage=page_number, onLaterPages=page_number)
    return stream.getvalue()


def build_source_appendix() -> bytes:
    """Lista el código completo con nombre de archivo y números de línea legibles."""
    files = [
        "index.html", "noticias.html", "detalle.html", "favoritos.html",
        "gestion.html", "contacto.html", "styles.css", "app.js", "data/noticias.json",
    ]
    stream = BytesIO()
    c = canvas.Canvas(stream, pagesize=letter)
    page = 15
    y = 710

    def start_page():
        nonlocal y
        c.setFillColor(INK)
        c.setFont("Times-Roman", 10)
        c.drawRightString(letter[0] - inch, letter[1] - 0.52 * inch, str(page))
        c.setFont("Times-Bold", 12)
        c.drawString(inch, 738, "Anexo B. Código fuente de PoliTechNews")
        c.setStrokeColor(colors.HexColor("#c6d9e7"))
        c.line(inch, 730, letter[0] - inch, 730)
        y = 710

    def next_page():
        nonlocal page
        c.showPage()
        page += 1
        start_page()

    start_page()
    for file_name in files:
        if y < 95:
            next_page()
        c.setFont("Times-Bold", 10)
        c.setFillColor(BLUE)
        c.drawString(inch, y, file_name)
        y -= 16
        for number, raw in enumerate((ROOT / file_name).read_text(encoding="utf-8").splitlines(), 1):
            wrapped = textwrap.wrap(raw.expandtabs(2), width=97, replace_whitespace=False,
                                    drop_whitespace=False, break_long_words=True,
                                    break_on_hyphens=False) or [""]
            for part, chunk in enumerate(wrapped):
                if y < 61:
                    next_page()
                    c.setFont("Times-Bold", 10)
                    c.setFillColor(BLUE)
                    c.drawString(inch, y, file_name + " (continuación)")
                    y -= 16
                c.setFont("Courier", 7.5)
                c.setFillColor(GRAY)
                c.drawRightString(92, y, str(number) if part == 0 else "")
                c.setFillColor(INK)
                c.drawString(100, y, chunk)
                y -= 10.2
        y -= 14
    c.save()
    return stream.getvalue()


def merge_appendices(main_pdf: bytes, source_pdf: bytes, output: Path):
    main = PdfReader(BytesIO(main_pdf))
    original = PdfReader(str(SOURCE_PDF))
    if len(main.pages) != 8:
        raise RuntimeError(f"El cuerpo del informe debe tener 8 páginas; obtuvo {len(main.pages)}")
    writer = PdfWriter()
    for page in main.pages:
        writer.add_page(page)
    for sequence, index in enumerate(range(9, 15), start=9):
        page = original.pages[index]
        overlay = BytesIO()
        c = canvas.Canvas(overlay, pagesize=letter)
        c.setFillColor(colors.white)
        c.rect(490, 738, 90, 30, stroke=0, fill=1)
        c.setFont("Times-Roman", 10)
        c.setFillColor(INK)
        c.drawRightString(letter[0] - inch, letter[1] - 0.52 * inch, str(sequence))
        c.save()
        overlay.seek(0)
        page.merge_page(PdfReader(overlay).pages[0])
        writer.add_page(page)
    for page in PdfReader(BytesIO(source_pdf)).pages:
        writer.add_page(page)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("wb") as file:
        writer.write(file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", help="URL pública y verificada del repositorio")
    args = parser.parse_args()
    repo_url = args.repo or "Pendiente de creación en GitHub"
    target = FINAL_PDF if args.repo else DRAFT_PDF
    appendix = build_source_appendix()
    merge_appendices(build_main(repo_url, len(PdfReader(BytesIO(appendix)).pages)), appendix, target)
    print(target)
