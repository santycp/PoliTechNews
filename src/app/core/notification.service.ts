import { Injectable, signal } from '@angular/core';

@Injectable({ providedIn: 'root' })
export class NotificationService {
  readonly message = signal('');
  readonly kind = signal<'success' | 'error'>('success');
  private timer?: ReturnType<typeof setTimeout>;
  show(message: string, kind: 'success' | 'error' = 'success'): void {
    clearTimeout(this.timer);
    this.kind.set(kind);
    this.message.set(message);
    this.timer = setTimeout(() => this.message.set(''), 4200);
  }
}
