import { browser } from '$app/environment';

type ThemeMode = 'system' | 'light' | 'dark';

class ThemeStore {
	private _mode = $state<ThemeMode>('system');
	private _isDark = $state(false);
	private mediaQuery: MediaQueryList | null = null;

	constructor() {
		if (browser) {
			this.init();
		}
	}

	private init() {
		// Load saved preference or default to system
		const saved = localStorage.getItem('theme-mode') as ThemeMode | null;
		if (saved && ['system', 'light', 'dark'].includes(saved)) {
			this._mode = saved;
		}

		// Set up system theme detection
		this.mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');

		// Listen for system theme changes
		this.mediaQuery.addEventListener('change', this.handleSystemThemeChange);

		// Apply initial theme
		this.applyTheme();
	}

	private handleSystemThemeChange = (e: MediaQueryListEvent) => {
		if (this._mode === 'system') {
			this._isDark = e.matches;
			this.updateDOM();
		}
	};

	private applyTheme() {
		this._isDark = this.calculateIsDark();
		this.updateDOM();
	}

	private calculateIsDark(): boolean {
		if (this._mode === 'system') {
			return this.mediaQuery?.matches ?? false;
		}
		return this._mode === 'dark';
	}

	private updateDOM() {
		document.documentElement.classList.toggle('dark', this._isDark);
	}

	get mode(): ThemeMode {
		return this._mode;
	}

	get isDark(): boolean {
		return this._isDark;
	}

	toggle() {
		const themeMap: Record<ThemeMode, ThemeMode> = {
			system: 'light',
			light: 'dark',
			dark: 'system'
		};

		this._mode = themeMap[this._mode];
		localStorage.setItem('theme-mode', this._mode);
		this.applyTheme();
	}

	setMode(mode: ThemeMode) {
		this._mode = mode;
		localStorage.setItem('theme-mode', mode);
		this.applyTheme();
	}

	destroy() {
		if (this.mediaQuery) {
			this.mediaQuery.removeEventListener('change', this.handleSystemThemeChange);
		}
	}
}

export const themeStore = new ThemeStore();
