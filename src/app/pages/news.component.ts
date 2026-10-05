import { Component, computed, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router } from '@angular/router';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { NewsService } from '../core/news.service';
import { CATEGORIES } from '../core/article.model';
import { BannerComponent } from '../shared/banner.component';
import { NewsCardComponent } from '../shared/news-card.component';
import { PaginationComponent } from '../shared/pagination.component';
import { EmptyStateComponent } from '../shared/empty-state.component';

@Component({ selector: 'app-news', imports: [FormsModule, BannerComponent, NewsCardComponent, PaginationComponent, EmptyStateComponent], templateUrl: './news.component.html' })
export class NewsComponent {
  readonly news = inject(NewsService);
  private readonly router = inject(Router);
  readonly categories = ['Todas', ...CATEGORIES];
  readonly category = signal('Todas');
  readonly query = signal('');
  readonly page = signal(1);
  searchText = '';
  readonly filtered = computed(() => {
    const q = this.query().toLocaleLowerCase('es');
    return this.news.published().filter(a => (this.category() === 'Todas' || a.category === this.category()) && `${a.title} ${a.summary} ${a.category}`.toLocaleLowerCase('es').includes(q));
  });
  readonly totalPages = computed(() => Math.max(1, Math.ceil(this.filtered().length / 6)));
  readonly currentPage = computed(() => Math.min(this.page(), this.totalPages()));
  readonly shown = computed(() => this.filtered().slice((this.currentPage() - 1) * 6, this.currentPage() * 6));
  constructor() {
    inject(ActivatedRoute).queryParamMap.pipe(takeUntilDestroyed()).subscribe(params => {
      const category = params.get('categoria') || 'Todas';
      this.category.set(this.categories.includes(category) ? category : 'Todas');
      this.query.set(params.get('q') || '');
      this.searchText = this.query();
      this.page.set(1);
    });
  }
  filter(category: string): void { this.updateUrl(category, this.query()); }
  search(): void { this.updateUrl(this.category(), this.searchText.trim()); }
  clear(): void { this.updateUrl('Todas', ''); }
  private updateUrl(category: string, query: string): void {
    void this.router.navigate(['/noticias'], { queryParams: { categoria: category === 'Todas' ? null : category, q: query || null } });
  }
  goToPage(page: number): void {
    this.page.set(page);
    document.getElementById('news-results')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }
}
