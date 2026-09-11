import { getContext, setContext } from 'svelte';

type PopupType = 'about' | 'estop' | 'docs' | 'settings' | 'terminal' | 'logs';

class PopupState {
	current = $state<PopupType | null>(null);

	open(popup: PopupType) {
		this.current = popup;
	}

	close() {
		this.current = null;
	}

	isOpen(popup: PopupType) {
		return this.current === popup;
	}
}

const POPUP_KEY = Symbol('popups');

export function setPopupState() {
	const state = new PopupState();
	setContext(POPUP_KEY, state);
	return state;
}

export function getPopupState() {
	return getContext<PopupState>(POPUP_KEY);
}
