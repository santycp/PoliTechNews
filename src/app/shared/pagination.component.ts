import { Component, computed, input, output } from '@angular/core';
@Component({
  selector: 'app-pagination',
  template: `@if (total() > 1) { <nav class="pagination" aria-label="Paginación"><button type="button" [disabled]="current() <= 1" aria-label="Página anterior" (click)="change.emit(current() - 1)">‹</button>@for (p of pages(); track p) { <button type="button" [attr.aria-current]="current() === p ? 'page' : null" (click)="change.emit(p)">{{ p }}</button> }<button type="button" [disabled]="current() >= total()" aria-label="Página siguiente" (click)="change.emit(current() + 1)">›</button></nav> }`
})
export class PaginationComponent {
  readonly total = input.required<number>();
  readonly current = input.required<number>();
  readonly change = output<number>();
  readonly pages = computed(() => Array.from({ length: this.total() }, (_, i) => i + 1));
}
