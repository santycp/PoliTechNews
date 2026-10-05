import { Injectable } from '@angular/core';

export const STORAGE_KEYS = {
  favorites: 'politechnews:favorites:v1',
  custom: 'politechnews:custom:v1',
  deleted: 'politechnews:deleted:v1'
};

@Injectable({ providedIn: 'root' })
export class StorageService {
  read<T>(key: string, validate: (value: unknown) => value is T): T[] {
    try {
      const value: unknown = JSON.parse(localStorage.getItem(key) || '[]');
      return Array.isArray(value) ? value.filter(validate) : [];
    } catch { return []; }
  }

  // No se actualizan las señales si la persistencia falla. Se restaura el lote anterior.
  write(entries: [string, unknown[]][]): void {
    const previous = entries.map(([key]) => [key, localStorage.getItem(key)] as const);
    try {
      for (const [key, value] of entries) localStorage.setItem(key, JSON.stringify(value));
    } catch {
      for (const [key, value] of previous) {
        try { if (value === null) localStorage.removeItem(key); else localStorage.setItem(key, value); } catch { /* El navegador puede bloquear también la restauración. */ }
      }
      throw new Error('No se pudieron guardar los cambios. Revisa el espacio y los permisos de tu navegador.');
    }
  }
}
