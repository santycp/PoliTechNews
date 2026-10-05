import { Component, computed, inject, signal } from '@angular/core';
import { FormsModule, NonNullableFormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { RouterLink } from '@angular/router';
import { NewsService } from '../core/news.service';
import { NotificationService } from '../core/notification.service';
import { Article, CATEGORIES, Category, dateLabel, imageSrc } from '../core/article.model';
import { trimmedMinLength } from '../core/form-validators';
import { BannerComponent } from '../shared/banner.component';
import { PaginationComponent } from '../shared/pagination.component';

@Component({ selector: 'app-admin', imports: [FormsModule, ReactiveFormsModule, RouterLink, BannerComponent, PaginationComponent], templateUrl: './admin.component.html' })
export class AdminComponent {
  readonly news = inject(NewsService);
  private readonly notices = inject(NotificationService);
  private readonly fb = inject(NonNullableFormBuilder);
  readonly categories = CATEGORIES;
  readonly dateLabel = dateLabel;
  readonly imageSrc = imageSrc;
  readonly saving = signal(false);
  readonly error = signal('');
  readonly query = signal('');
  readonly status = signal('Todas');
  readonly page = signal(1);
  searchText = '';
  selectedStatus = 'Todas';
  file?: File;
  readonly form = this.fb.group({
    title: ['', [Validators.required, trimmedMinLength(8), Validators.maxLength(120)]],
    category: ['', [Validators.required]],
    summary: ['', [Validators.required, trimmedMinLength(20), Validators.maxLength(160)]],
    content: ['', [Validators.required, trimmedMinLength(80), Validators.maxLength(20000)]]
  });
  readonly filtered = computed(() => {
    const q = this.query().toLocaleLowerCase('es');
    return this.news.articles().filter(a => `${a.title} ${a.category}`.toLocaleLowerCase('es').includes(q) && (this.status() === 'Todas' || (this.status() === 'Borradores' ? a.status === 'draft' : a.status !== 'draft'))).sort((a, b) => b.date.localeCompare(a.date));
  });
  readonly pages = computed(() => Math.max(1, Math.ceil(this.filtered().length / 6)));
  readonly currentPage = computed(() => Math.min(this.page(), this.pages()));
  readonly shown = computed(() => this.filtered().slice((this.currentPage() - 1) * 6, this.currentPage() * 6));
  readonly drafts = computed(() => this.news.articles().filter(a => a.status === 'draft').length);
  invalid(name: keyof typeof this.form.controls): boolean { const c = this.form.controls[name]; return c.invalid && c.touched; }
  fileChanged(event: Event): void { this.file = (event.target as HTMLInputElement).files?.[0]; }
  filter(): void { this.query.set(this.searchText.trim()); this.status.set(this.selectedStatus); this.page.set(1); }
  async submit(event: Event, htmlForm: HTMLFormElement, fileInput: HTMLInputElement): Promise<void> {
    this.error.set('');
    this.form.markAllAsTouched();
    if (this.form.invalid || this.saving()) return;
    const mode = ((event as SubmitEvent).submitter as HTMLButtonElement | null)?.value === 'draft' ? 'draft' : 'published';
    this.saving.set(true);
    try {
      const value = this.form.getRawValue();
      await this.news.create({ ...value, category: value.category as Category }, mode, this.file);
      this.form.reset(); htmlForm.reset(); fileInput.value = ''; this.file = undefined;
      this.searchText = ''; this.selectedStatus = 'Todas'; this.filter();
      this.notices.show(mode === 'draft' ? 'Borrador guardado en este navegador.' : 'Noticia publicada en este navegador.');
    } catch (error) { this.error.set((error as Error).message); this.notices.show(this.error(), 'error'); }
    finally { this.saving.set(false); }
  }
  remove(article: Article): void {
    if (!confirm(`¿Eliminar la noticia «${article.title}»?`)) return;
    try { this.news.remove(article.id); this.notices.show('Noticia eliminada de este navegador.'); }
    catch (error) { this.notices.show((error as Error).message, 'error'); }
  }
  publish(article: Article): void {
    try { this.news.publishDraft(article.id); this.notices.show('Borrador publicado en este navegador.'); }
    catch (error) { this.notices.show((error as Error).message, 'error'); }
  }
}
