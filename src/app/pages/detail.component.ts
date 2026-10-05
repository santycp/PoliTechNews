import { Component, computed, effect, inject } from '@angular/core';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { toSignal } from '@angular/core/rxjs-interop';
import { Title } from '@angular/platform-browser';
import { NewsService } from '../core/news.service';
import { NotificationService } from '../core/notification.service';
import { categoryClass, dateLabel, imageSrc } from '../core/article.model';
import { EmptyStateComponent } from '../shared/empty-state.component';

@Component({ selector: 'app-detail', imports: [RouterLink, EmptyStateComponent], templateUrl: './detail.component.html' })
export class DetailComponent {
  readonly news = inject(NewsService);
  private readonly notices = inject(NotificationService);
  private readonly params = toSignal(inject(ActivatedRoute).paramMap);
  readonly article = computed(() => { const a = this.news.get(this.params()?.get('id') || ''); return a?.status === 'draft' ? undefined : a; });
  readonly related = computed(() => this.news.published().filter(a => a.id !== this.article()?.id).sort((a, b) => Number(b.category === this.article()?.category) - Number(a.category === this.article()?.category)).slice(0, 3));
  readonly categoryClass = categoryClass;
  readonly dateLabel = dateLabel;
  readonly imageSrc = imageSrc;
  constructor() {
    const title = inject(Title);
    effect(() => title.setTitle(`${this.article()?.title || 'Noticia no disponible'} | PoliTechNews`));
  }
  initials(name: string): string { return name.split(' ').map(s => s[0]).join('').slice(0, 2); }
  toggle(): void {
    try { const added = this.news.toggleFavorite(this.article()!.id); this.notices.show(added ? 'Noticia agregada a favoritos.' : 'Noticia eliminada de favoritos.'); }
    catch (error) { this.notices.show((error as Error).message, 'error'); }
  }
  async share(): Promise<void> {
    try {
      if (navigator.share) await navigator.share({ title: this.article()?.title, url: location.href });
      else { await navigator.clipboard.writeText(location.href); this.notices.show('Enlace copiado al portapapeles.'); }
    } catch (error) { if ((error as Error).name !== 'AbortError') this.notices.show('Puedes copiar el enlace de la barra de direcciones.'); }
  }
}
