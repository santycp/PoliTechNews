import { AbstractControl, ValidationErrors, ValidatorFn } from '@angular/forms';

export function trimmedMinLength(min: number): ValidatorFn {
  return (control: AbstractControl): ValidationErrors | null =>
    typeof control.value === 'string' && control.value.trim().length >= min ? null : { trimmedMinLength: { min } };
}
