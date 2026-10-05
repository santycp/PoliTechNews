import { Component, input } from '@angular/core';
import { RouterLink } from '@angular/router';
import { Article, categoryClass, dateLabel, imageSrc } from '../core/article.model';

@Component({
  selector: 'app-news-card',
  imports: [RouterLink],
  template: `<article class="news-card"><a class="card-image" [routerLink]="['/noticias', article().id]" [attr.aria-label]="'Leer ' + article().title"><img [src]="imageSrc(article())" [alt]="'Ilustración de ' + article().category" loading="lazy"></a><div class="card-content"><span class="category-tag" [class]="categoryClass(article().category)">{{ article().category }}</span><h3><a [routerLink]="['/noticias', article().id]">{{ article().title }}</a></h3><p>{{ article().summary }}</p><div class="card-bottom"><span>{{ dateLabel(article().date) }} · {{ article().minutes }} min</span><a [routerLink]="['/noticias', article().id]">Leer más <span aria-hidden="true">→</span></a></div></div></article>`
})
export class NewsCardComponent {
  readonly article = input.required<Article>();
  readonly imageSrc = imageSrc;
  readonly categoryClass = categoryClass;
  readonly dateLabel = dateLabel;
}
