export const CATEGORIES = ['Inteligencia Artificial', 'Desarrollo', 'Cloud', 'Datos', 'Ciberseguridad', 'Innovación'] as const;
export type Category = typeof CATEGORIES[number];
export interface Article {
  id: string;
  title: string;
  category: Category;
  summary: string;
  date: string;
  minutes: number;
  image: string;
  author: string;
  content: string[];
  status?: 'published' | 'draft';
}
export interface ArticleInput { title: string; category: Category; summary: string; content: string; }
export const CATEGORY_IMAGES: Record<Category, string> = {
  'Inteligencia Artificial': 'ia', Desarrollo: 'desarrollo', Cloud: 'cloud',
  Datos: 'datos', Ciberseguridad: 'ciberseguridad', Innovación: 'innovacion'
};
export function categoryClass(category: string): string {
  const classes: Record<string, string> = { 'Inteligencia Artificial': 'ia', Desarrollo: 'dev', Cloud: 'cloud', Datos: 'data', Ciberseguridad: 'security', Innovación: 'innovation' };
  return `tag-${classes[category] || 'innovation'}`;
}
export function imageSrc(article: Article): string {
  return /^(assets\/images\/[a-z0-9-]+\.png|data:image\/(png|jpeg|webp);base64,[A-Za-z0-9+/=]+)$/.test(article.image)
    ? article.image : 'assets/images/innovacion.png';
}
export function dateLabel(value: string): string {
  return new Intl.DateTimeFormat('es-CO', { day: 'numeric', month: 'short', year: 'numeric', timeZone: 'UTC' }).format(new Date(`${value}T12:00:00Z`));
}
// Valida datos externos antes de que entren al modelo tipado de la aplicación.
export function isArticle(value: unknown): value is Article {
  if (!value || typeof value !== 'object') return false;
  const a = value as Record<string, unknown>;
  return ['id', 'title', 'summary', 'image', 'author'].every(k => typeof a[k] === 'string' && (a[k] as string).length > 0)
    && CATEGORIES.includes(a['category'] as Category)
    && typeof a['date'] === 'string' && /^\d{4}-\d{2}-\d{2}$/.test(a['date']) && Number.isFinite(Date.parse(a['date']))
    && typeof a['minutes'] === 'number' && a['minutes'] > 0
    && Array.isArray(a['content']) && a['content'].every(p => typeof p === 'string')
    && (a['status'] === undefined || a['status'] === 'draft' || a['status'] === 'published');
}
