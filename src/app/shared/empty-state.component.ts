import { Component, input } from '@angular/core';
@Component({
  selector: 'app-empty-state',
  template: `<div class="empty-state"><div class="empty-symbol" aria-hidden="true">○</div><h3>{{ title() }}</h3><p>{{ description() }}</p><ng-content /></div>`
})
export class EmptyStateComponent {
  readonly title = input.required<string>();
  readonly description = input.required<string>();
}
