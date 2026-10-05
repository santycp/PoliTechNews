import { Component, computed, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { NewsService } from '../core/news.service';
import { NotificationService } from '../core/notification.service';
import { categoryClass, dateLabel, imageSrc } from '../core/article.model';
import { BannerComponent } from '../shared/banner.component';
import { EmptyStateComponent } from '../shared/empty-state.component';

@Component({ selector: 'app-favorites', imports: [FormsModule, RouterLink, BannerComponent, EmptyStateComponent], templateUrl: './favorites.component.html' })
export class FavoritesComponent {
  readonly news = inject(NewsService);
  private readonly notices = inject(NotificationService);
  readonly order = signal('newest');
  readonly items = computed(() => { const items = [...this.news.favoriteArticles()]; return this.order() === 'oldest' ? items.reverse() : items; });
  readonly categoryClass = categoryClass;
  readonly dateLabel = dateLabel;
  readonly imageSrc = imageSrc;
  remove(id: string): void {
    try { this.news.toggleFavorite(id); this.notices.show('Noticia eliminada de favoritos.'); }
    catch (error) { this.notices.show((error as Error).message, 'error'); }
  }
  clear(): void {
    if (!confirm('¿Quitar todas las noticias de favoritos?')) return;
    try { this.news.clearFavorites(); this.notices.show('La lista de favoritos quedó vacía.'); }
    catch (error) { this.notices.show((error as Error).message, 'error'); }
  }
}
