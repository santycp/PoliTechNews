# Arquitectura de PoliTechNews en Angular

```mermaid
flowchart TD
    A[main.ts: bootstrapApplication] --> B[app.config.ts: Router y HttpClient]
    B --> C[AppComponent: navegación y avisos]
    C --> D[RouterOutlet: seis componentes de página]
    D --> E[Componentes compartidos: tarjeta, banner, paginación]
    D --> F[NewsService: signals y computed]
    F --> G[HttpClient: data/noticias.json]
    F --> H[StorageService]
    H --> I[localStorage: favoritos, publicaciones y eliminaciones]
    D --> J[Formularios reactivos y validadores]
    J --> F
```

La presentación usa plantillas Angular y la hoja visual original. Los componentes de página gestionan filtros y formularios; NewsService reúne el estado compartido y valida los datos; StorageService adapta la persistencia del navegador. El enrutador carga cada página bajo demanda. La compilación genera archivos estáticos servidos por GitHub Pages.

El CRUD y los favoritos no sincronizan datos entre dispositivos. El formulario de contacto es una demostración de validación. No hay autenticación, API de escritura ni base de datos; esas capacidades no son exigidas por las orientaciones de esta entrega.
