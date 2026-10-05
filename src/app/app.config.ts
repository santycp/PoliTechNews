import { ApplicationConfig, provideAppInitializer, inject } from '@angular/core';
import { provideHttpClient } from '@angular/common/http';
import { provideRouter, withHashLocation } from '@angular/router';
import { routes } from './app.routes';
import { NewsService } from './core/news.service';

export const appConfig: ApplicationConfig = {
  providers: [
    provideHttpClient(),
    // Las rutas con # pueden recargarse en GitHub Pages sin reescrituras del servidor.
    provideRouter(routes, withHashLocation()),
    provideAppInitializer(() => inject(NewsService).load())
  ]
};
