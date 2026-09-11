<script lang="ts">
	import { fade, scale } from 'svelte/transition';

	import { getPopupState } from '$lib/stores/popups.svelte';

	const popups = getPopupState();

	let dialog = $state<HTMLDialogElement>();
	let loading = $state(true);
	let iframeElement = $state<HTMLIFrameElement>();

	function close() {
		popups.close();
	}

	function handleIframeLoad() {
		loading = false;
	}

	function handleIframeError() {
		loading = false;
	}

	$effect(() => {
		if (popups.isOpen('terminal')) {
			loading = true;
		}
	});
</script>

{#if popups.isOpen('terminal')}
	<dialog
		bind:this={dialog}
		class="fixed inset-0 z-50 m-0 flex h-screen w-screen items-center justify-center bg-transparent p-0"
		onclose={close}
	>
		<!-- Backdrop -->
		<button
			class="fixed inset-0 bg-black/50 cursor-default"
			onclick={close}
			in:fade={{ duration: 150 }}
			out:fade={{ duration: 150 }}
			tabindex="-1"
			aria-label="Close dialog"
		></button>

		<!-- Modal Content -->
		<div
			class="relative z-10 flex h-[90vh] w-[90vw] max-w-5xl flex-col overflow-hidden rounded-lg border border-gray-200 bg-white shadow-2xl dark:border-neutral-700 dark:bg-neutral-900"
			in:scale={{ duration: 150, start: 0.96, opacity: 0 }}
			out:scale={{ duration: 150, start: 0.96, opacity: 0 }}
			role="dialog"
			aria-modal="true"
			aria-labelledby="terminal-title"
		>
			<!-- Header -->
			<div
				class="flex items-center justify-between border-b border-gray-200 px-6 py-4 dark:border-neutral-700"
			>
				<h2 id="terminal-title" class="text-xl font-semibold text-gray-900 dark:text-white">
					SSH Terminal
				</h2>
				<button
					onclick={close}
					class="rounded-md p-1.5 text-gray-400 transition-colors hover:bg-gray-100 hover:text-gray-600 dark:hover:bg-neutral-800 dark:hover:text-gray-300"
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
			<div class="flex-1 overflow-hidden p-6">
				{#if loading}
					<div class="flex h-full items-center justify-center">
						<div class="flex items-center gap-3 text-gray-500 dark:text-gray-400">
							<svg class="h-5 w-5 animate-spin" viewBox="0 0 24 24" fill="none">
								<circle
									class="opacity-25"
									cx="12"
									cy="12"
									r="10"
									stroke="currentColor"
									stroke-width="4"
								></circle>
								<path
									class="opacity-75"
									fill="currentColor"
									d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
								></path>
							</svg>
							<span>Loading terminal...</span>
						</div>
					</div>
				{/if}

				<div
					class="h-full overflow-hidden rounded-md border border-gray-300 dark:border-neutral-700"
					class:hidden={loading}
				>
					<iframe
						bind:this={iframeElement}
						src={`http://${window.location.hostname}:8001`}
						title="Terminal"
						class="w-full h-full border-0"
						onload={handleIframeLoad}
						onerror={handleIframeError}
					></iframe>
				</div>
			</div>

			<!-- Footer -->
			<div
				class="flex items-center justify-between border-t border-gray-200 px-6 py-4 dark:border-neutral-700"
			>
				<div class="text-xs text-gray-500 dark:text-gray-400">
					Press <kbd
						class="rounded border border-gray-300 px-1.5 py-0.5 font-mono dark:border-neutral-600"
						>Esc</kbd
					> to close
				</div>
				<div class="flex gap-2">
					<button
						onclick={close}
						class="rounded-md border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 transition-colors hover:bg-gray-50 dark:border-neutral-600 dark:text-gray-300 dark:hover:bg-neutral-800"
					>
						Close
					</button>
				</div>
			</div>
		</div>
	</dialog>
{/if}

<style>
	dialog {
		border: none;
		outline: none;
	}

	dialog::backdrop {
		background: transparent;
	}

	kbd {
		font-size: 0.75rem;
	}
</style>
