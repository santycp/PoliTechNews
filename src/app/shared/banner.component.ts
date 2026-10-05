import { Component, input } from '@angular/core';

@Component({
  selector: 'app-banner',
  template: `<section class="banner container"><div class="banner-copy"><span class="eyebrow">{{ eyebrow() }}</span><h1>{{ title() }}</h1><p>{{ description() }}</p><ng-content /></div><div class="banner-mark" aria-hidden="true"><span></span><span></span><span></span></div></section>`
})
export class BannerComponent {
  readonly eyebrow = input.required<string>();
  readonly title = input.required<string>();
  readonly description = input.required<string>();
}
