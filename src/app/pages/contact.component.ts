import { Component, inject, signal } from '@angular/core';
import { NonNullableFormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { NotificationService } from '../core/notification.service';
import { trimmedMinLength } from '../core/form-validators';
import { BannerComponent } from '../shared/banner.component';

@Component({ selector: 'app-contact', imports: [ReactiveFormsModule, BannerComponent], templateUrl: './contact.component.html' })
export class ContactComponent {
  private readonly fb = inject(NonNullableFormBuilder);
  private readonly notices = inject(NotificationService);
  readonly sent = signal(false);
  readonly messageLength = signal(0);
  readonly form = this.fb.group({
    name: ['', [Validators.required, trimmedMinLength(3), Validators.maxLength(80)]],
    email: ['', [Validators.required, Validators.email, Validators.maxLength(254)]],
    subject: ['', [Validators.required]],
    message: ['', [Validators.required, trimmedMinLength(20), Validators.maxLength(500)]],
    privacy: [false, [Validators.requiredTrue]]
  });
  invalid(name: keyof typeof this.form.controls): boolean { const c = this.form.controls[name]; return c.invalid && c.touched; }
  count(event: Event): void { this.messageLength.set((event.target as HTMLTextAreaElement).value.length); }
  submit(): void {
    this.sent.set(false); this.form.markAllAsTouched();
    if (this.form.invalid) return;
    this.sent.set(true); this.form.reset(); this.messageLength.set(0);
    this.notices.show('Formulario validado. Envío simulado correctamente.');
  }
}
