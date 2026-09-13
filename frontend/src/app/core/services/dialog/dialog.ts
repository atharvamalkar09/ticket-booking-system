import { Injectable, signal } from '@angular/core';
import { DialogType } from '../../../shared/dialog/dialog';

export interface DialogConfig {
  title: string;
  message: string;
  type?: DialogType;
  confirmText?: string;
  cancelText?: string;
  showCancel?: boolean;
}

@Injectable({
  providedIn: 'root',
})
export class DialogService {
  private readonly _isOpen = signal(false);

  private readonly _config = signal<DialogConfig>({
    title: '',
    message: '',
    type: 'info',
    confirmText: 'OK',
    cancelText: 'Cancel',
    showCancel: false,
  });

  readonly isOpen = this._isOpen.asReadonly();
  readonly config = this._config.asReadonly();

  private resolveAction: ((confirmed: boolean) => void) | null = null;

  open(config: DialogConfig): Promise<boolean> {
    this._config.set({
      title: config.title,
      message: config.message,
      type: config.type ?? 'info',
      confirmText: config.confirmText ?? 'OK',
      cancelText: config.cancelText ?? 'Cancel',
      showCancel: config.showCancel ?? false,
    });

    this._isOpen.set(true);

    return new Promise<boolean>((resolve) => {
      this.resolveAction = resolve;
    });
  }

  confirm(config: DialogConfig): Promise<boolean> {
    return this.open({
      ...config,
      showCancel: true,
      type: config.type ?? 'confirm',
    });
  }

  success(
    title: string,
    message: string,
    confirmText = 'OK'
  ): Promise<boolean> {
    return this.open({
      title,
      message,
      type: 'success',
      confirmText,
      showCancel: false,
    });
  }

  error(
    title: string,
    message: string,
    confirmText = 'OK'
  ): Promise<boolean> {
    return this.open({
      title,
      message,
      type: 'error',
      confirmText,
      showCancel: false,
    });
  }

  warning(
    title: string,
    message: string,
    confirmText = 'OK'
  ): Promise<boolean> {
    return this.open({
      title,
      message,
      type: 'warning',
      confirmText,
      showCancel: false,
    });
  }

  info(
    title: string,
    message: string,
    confirmText = 'OK'
  ): Promise<boolean> {
    return this.open({
      title,
      message,
      type: 'info',
      confirmText,
      showCancel: false,
    });
  }

  confirmAction(): void {
    this.close(true);
  }

  cancelAction(): void {
    this.close(false);
  }

  private close(result: boolean): void {
    this._isOpen.set(false);

    if (this.resolveAction) {
      this.resolveAction(result);
      this.resolveAction = null;
    }
  }
}