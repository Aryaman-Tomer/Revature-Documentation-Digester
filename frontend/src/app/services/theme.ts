import { Injectable, effect, inject, signal, PLATFORM_ID } from '@angular/core';
import { DOCUMENT, isPlatformBrowser } from '@angular/common';

export type Theme = 'light' | 'dark' | 'system';

@Injectable({ providedIn: 'root' })
export class ThemeService {
  private doc = inject(DOCUMENT);
  private isBrowser = isPlatformBrowser(inject(PLATFORM_ID));
  private media = this.isBrowser ? window.matchMedia('(prefers-color-scheme: dark)') : null;

  theme = signal<Theme>(this.loadSaved());

  constructor() {
    effect(() => {
      const t = this.theme();
      this.apply(t);
      if (this.isBrowser) localStorage.setItem('theme', t);
    });

    // Follow OS changes when the user picked "system"
    this.media?.addEventListener('change', () => {
      if (this.theme() === 'system') this.apply('system');
    });
  }

  toggle() {
    this.theme.set(this.isDark() ? 'light' : 'dark');
  }

  isDark(): boolean {
    const t = this.theme();
    return t === 'dark' || (t === 'system' && !!this.media?.matches);
  }

  private apply(t: Theme) {
    const dark = t === 'dark' || (t === 'system' && !!this.media?.matches);
    this.doc.documentElement.classList.toggle('dark', dark);
  }

  private loadSaved(): Theme {
    if (!this.isBrowser) return 'system';
    return (localStorage.getItem('theme') as Theme) ?? 'system';
  }
}
