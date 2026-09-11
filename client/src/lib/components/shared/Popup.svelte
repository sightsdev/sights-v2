<script lang="ts">
	import type { Snippet } from 'svelte';

	import { getPopupState } from '$lib/stores/popups.svelte';

	let {
		name,
		title,
		children,
		maxWidth = 'max-w-2xl'
	}: {
		name: 'about' | 'docs' | 'settings' | 'terminal' | 'logs';
		title: string;
		children?: Snippet;
		maxWidth?: string;
	} = $props();

	const popups = getPopupState();
	let dialog = $state<HTMLDialogElement>();

	$effect(() => {
		if (popups.isOpen(name)) {
			dialog?.showModal();
		} else {
			dialog?.close();
		}
	});

	function close() {
		popups.close();
	}
</script>

<dialog
	bind:this={dialog}
	class="rounded-lg border border-gray-200 bg-white p-0 shadow-xl backdrop:bg-black/50 dark:border-neutral-700 dark:bg-neutral-900"
	onclose={close}
>
	<div class="w-[90vw] {maxWidth}">
		<!-- Header -->
		<div
			class="flex items-center justify-between border-b border-gray-200 px-6 py-4 dark:border-neutral-700"
		>
			<h2 class="text-xl font-semibold text-gray-900 dark:text-white">{title}</h2>
			<button
				onclick={close}
				class="rounded-md p-1 text-gray-400 transition-colors hover:bg-gray-100 hover:text-gray-600 dark:hover:bg-neutral-800 dark:hover:text-gray-300"
				title="Close (Esc)"
			>
				<svg
					width="20"
					height="20"
					viewBox="0 0 24 24"
					fill="none"
					stroke="currentColor"
					stroke-width="2"
				>
					<path d="M18 6L6 18M6 6l12 12" />
				</svg>
			</button>
		</div>
		<!-- Content -->
		<div class="p-6">
			{@render children?.()}
		</div>
	</div>
</dialog>

<style>
	dialog::backdrop {
		backdrop-filter: blur(2px);
	}
</style>
