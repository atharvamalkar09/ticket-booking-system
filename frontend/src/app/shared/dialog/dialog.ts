import { Component, EventEmitter, Input, Output } from '@angular/core';

export type DialogType = 'confirm' | 'success' | 'error' | 'warning' | 'info';

@Component({
  selector: 'app-dialog',
  standalone: true,
  imports: [],
  templateUrl: './dialog.html',
  styleUrl: './dialog.css',
})
export class Dialog {

  @Input() isOpen = false;
  @Input() title = '';
  @Input() message = '';
  @Input() type: DialogType = 'info';

  @Input() confirmText = 'OK';
  @Input() cancelText = 'Cancel';

  @Input() showCancel = false;

  @Output() confirmed = new EventEmitter<void>();
  @Output() cancelled = new EventEmitter<void>();

  onConfirm(): void {
    this.confirmed.emit();
  }

  onCancel(): void {
    this.cancelled.emit();
  }

  closeOnBackdrop(event: MouseEvent): void {
    if (event.target === event.currentTarget) {
      this.onCancel();
    }
  }
}