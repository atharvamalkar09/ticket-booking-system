import { HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { Auth } from '../../services/auth/auth';

export const authInterceptor: HttpInterceptorFn = (req, next) => {

  const authService = inject(Auth);
  const token = authService.get_token();

  console.log('AUTH INTERCEPTOR TOKEN:', token);
  if (
    req.url.includes('/auth/login') ||
    req.url.includes('/auth/register')
  ) {
    return next(req);
  }

  if (token) {
    const clonedReq = req.clone({
      setHeaders: {
        Authorization: `Bearer ${token}`
      }
    });

    return next(clonedReq);
  }

  return next(req);
};