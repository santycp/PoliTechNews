import { Component, DestroyRef, inject, signal } from '@angular/core';
import { NavigationEnd, Router, RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { filter } from 'rxjs';
import { NewsService } from './core/news.service';
import { NotificationService } from './core/notification.service';

@Component({
  selector: 'app-root',
  imports: [RouterLink, RouterLinkActive, RouterOutlet],
  templateUrl: './app.component.html'
})
export class AppComponent {
  readonly news = inject(NewsService);
  readonly notices = inject(NotificationService);
  readonly menuOpen = signal(false);
  readonly links = [
    { path: '/', label: 'Inicio', exact: true }, { path: '/noticias', label: 'Noticias', exact: false },
    { path: '/favoritos', label: 'Favoritos', exact: true }, { path: '/gestion', label: 'Gestionar', exact: true },
    { path: '/contacto', label: 'Contacto', exact: true }
  ];
  constructor() {
    inject(Router).events.pipe(filter(e => e instanceof NavigationEnd), takeUntilDestroyed(inject(DestroyRef))).subscribe(() => {
      this.menuOpen.set(false);
      window.scrollTo({ top: 0, behavior: 'instant' });
      // El cambio de ruta ofrece un punto de entrada para usuarios de teclado.
      setTimeout(() => document.getElementById('contenido')?.focus({ preventScroll: true }));
    });
  }
}
