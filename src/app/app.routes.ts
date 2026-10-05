import { Routes } from '@angular/router';

export const routes: Routes = [
  { path: '', title: 'Inicio | PoliTechNews', loadComponent: () => import('./pages/home.component').then(m => m.HomeComponent) },
  { path: 'noticias', title: 'Noticias | PoliTechNews', loadComponent: () => import('./pages/news.component').then(m => m.NewsComponent) },
  { path: 'noticias/:id', title: 'Detalle | PoliTechNews', loadComponent: () => import('./pages/detail.component').then(m => m.DetailComponent) },
  { path: 'favoritos', title: 'Favoritos | PoliTechNews', loadComponent: () => import('./pages/favorites.component').then(m => m.FavoritesComponent) },
  { path: 'gestion', title: 'Gestionar | PoliTechNews', loadComponent: () => import('./pages/admin.component').then(m => m.AdminComponent) },
  { path: 'contacto', title: 'Contacto | PoliTechNews', loadComponent: () => import('./pages/contact.component').then(m => m.ContactComponent) },
  { path: '**', redirectTo: '' }
];
