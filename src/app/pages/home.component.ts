import { Component, inject } from '@angular/core';
import { RouterLink } from '@angular/router';
import { NewsService } from '../core/news.service';
import { CATEGORIES, categoryClass } from '../core/article.model';
import { NewsCardComponent } from '../shared/news-card.component';

@Component({ selector: 'app-home', imports: [RouterLink, NewsCardComponent], templateUrl: './home.component.html' })
export class HomeComponent {
  readonly news = inject(NewsService);
  readonly categories = CATEGORIES;
  readonly categoryClass = categoryClass;
}
