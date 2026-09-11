<script lang="ts">
	import { onDestroy } from 'svelte';
	import { fade, scale } from 'svelte/transition';

	import { getPopupState } from '$lib/stores/popups.svelte';

	const popups = getPopupState();

	let dialog = $state<HTMLDialogElement>();
	let logs = $state<string>('');
	let loading = $state(false);
	let error = $state<string | null>(null);
	let intervalId: ReturnType<typeof setInterval> | null = null;
	let preElement = $state<HTMLPreElement>();

	function close() {
		popups.close();
	}

	async function fetchLogs() {
		loading = true;
		error = null;
		try {
			const response = await fetch('http://localhost:8000/api/logs');

			if (!response.ok) {
				throw new Error(`Failed to fetch logs: ${response.status}`);
			}

			const logText = await response.text();

			if (logText.trim().startsWith('<!DOCTYPE html>') || logText.trim().startsWith('<html')) {
				throw new Error('Received HTML instead of logs');
			}

			logs = logText;
		} catch (err) {
			error = err instanceof Error ? err.message : 'Unknown error';
		} finally {
			loading = false;
		}
	}

	$effect(() => {
		if (logs && preElement) {
			preElement.scrollTop = preElement.scrollHeight;
		}
	});

	$effect(() => {
		if (popups.isOpen('logs')) {
			fetchLogs();
			intervalId = setInterval(fetchLogs, 3000);

			return () => {
				if (intervalId) {
					clearInterval(intervalId);
					intervalId = null;
				}
			};
		}
	});

	onDestroy(() => {
		if (intervalId) {
			clearInterval(intervalId);
		}
	});
</script>

{#if popups.isOpen('logs')}
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
			aria-labelledby="logs-title"
		>
			<!-- Header -->
			<div
				class="flex items-center justify-between border-b border-gray-200 px-6 py-4 dark:border-neutral-700"
			>
				<h2 id="logs-title" class="text-xl font-semibold text-gray-900 dark:text-white">
					SIGHTS Logs
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
			<div class="flex-1 overflow-auto p-6">
				{#if error}
					<div class="text-red-500">Error: {error}</div>
				{:else}
					<pre
						bind:this={preElement}
						class="h-full overflow-auto whitespace-pre-wrap rounded-md border border-gray-300 bg-gray-200 p-4 text-sm font-mono text-gray-900 dark:border-neutral-700 dark:bg-neutral-800 dark:text-gray-100">
{logs || (loading ? 'Loading...' : 'No logs available')}</pre>
				{/if}
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
