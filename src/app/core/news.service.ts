import { Injectable, computed, inject, signal } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { firstValueFrom } from 'rxjs';
import { Article, ArticleInput, CATEGORY_IMAGES, isArticle } from './article.model';
import { StorageService, STORAGE_KEYS } from './storage.service';

@Injectable({ providedIn: 'root' })
export class NewsService {
  private readonly http = inject(HttpClient);
  private readonly storage = inject(StorageService);
  private readonly base = signal<Article[]>([]);
  private readonly custom = signal(this.storage.read(STORAGE_KEYS.custom, isArticle));
  private readonly deleted = signal(this.storage.read(STORAGE_KEYS.deleted, (v): v is string => typeof v === 'string'));
  readonly favorites = signal(this.storage.read(STORAGE_KEYS.favorites, (v): v is string => typeof v === 'string'));
  readonly loadError = signal('');
  readonly loading = signal(true);
  readonly articles = computed(() => [...this.custom(), ...this.base()].filter(a => !this.deleted().includes(a.id)));
  readonly published = computed(() => this.articles().filter(a => a.status !== 'draft').sort((a, b) => b.date.localeCompare(a.date)));
  readonly favoriteArticles = computed(() => this.published().filter(a => this.favorites().includes(a.id)));

  async load(): Promise<void> {
    this.loading.set(true);
    this.loadError.set('');
    try {
      const data = await firstValueFrom(this.http.get<unknown>('data/noticias.json'));
      if (!Array.isArray(data) || !data.every(isArticle) || new Set(data.map(a => a.id)).size !== data.length) throw new Error('Catálogo inválido');
      this.base.set(data);
    } catch { this.loadError.set('No pudimos cargar las noticias. Comprueba tu conexión e inténtalo otra vez.'); }
    finally { this.loading.set(false); }
  }
  get(id: string): Article | undefined { return this.articles().find(a => a.id === id); }
  isFavorite(id: string): boolean { return this.favorites().includes(id); }
  toggleFavorite(id: string): boolean {
    const article = this.get(id);
    if (!article || article.status === 'draft') throw new Error('La noticia no está disponible.');
    const next = this.isFavorite(id) ? this.favorites().filter(v => v !== id) : [id, ...this.favorites()];
    this.storage.write([[STORAGE_KEYS.favorites, next]]);
    this.favorites.set(next);
    return next.includes(id);
  }
  clearFavorites(): void {
    this.storage.write([[STORAGE_KEYS.favorites, []]]);
    this.favorites.set([]);
  }
  async create(input: ArticleInput, mode: 'published' | 'draft', file?: File): Promise<void> {
    const image = await this.readImage(file, input.category);
    const content = input.content.trim().split(/\n\s*\n/).map(p => p.trim()).filter(Boolean);
    const article: Article = {
      id: `user-${crypto.randomUUID()}`, title: input.title.trim(), category: input.category,
      summary: input.summary.trim(), content, image, author: 'Redacción PoliTechNews',
      date: new Intl.DateTimeFormat('en-CA', { timeZone: 'America/Bogota', year: 'numeric', month: '2-digit', day: '2-digit' }).format(new Date()),
      minutes: Math.max(1, Math.ceil(input.content.trim().split(/\s+/).length / 200)), status: mode
    };
    const next = [article, ...this.custom()];
    this.storage.write([[STORAGE_KEYS.custom, next]]);
    this.custom.set(next);
  }
  remove(id: string): void {
    const custom = this.custom().filter(a => a.id !== id);
    const deleted = this.custom().some(a => a.id === id) ? this.deleted() : [...new Set([...this.deleted(), id])];
    const favorites = this.favorites().filter(v => v !== id);
    this.storage.write([[STORAGE_KEYS.custom, custom], [STORAGE_KEYS.deleted, deleted], [STORAGE_KEYS.favorites, favorites]]);
    this.custom.set(custom); this.deleted.set(deleted); this.favorites.set(favorites);
  }
  publishDraft(id: string): void {
    const next = this.custom().map(a => a.id === id ? { ...a, status: 'published' as const } : a);
    this.storage.write([[STORAGE_KEYS.custom, next]]);
    this.custom.set(next);
  }
  private async readImage(file: File | undefined, category: Article['category']): Promise<string> {
    if (!file) return `assets/images/${CATEGORY_IMAGES[category]}.png`;
    if (!['image/png', 'image/jpeg', 'image/webp'].includes(file.type) || file.size > 1024 * 1024) throw new Error('La imagen debe ser PNG, JPG o WebP y pesar como máximo 1 MB.');
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = () => resolve(String(reader.result));
      reader.onerror = () => reject(new Error('No se pudo leer la imagen.'));
      reader.readAsDataURL(file);
    });
  }
}
