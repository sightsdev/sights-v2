<script lang="ts">
	import { fade, scale } from 'svelte/transition';

	import { getPopupState } from '$lib/stores/popups.svelte';

	const popups = getPopupState();

	let dialog = $state<HTMLDialogElement>();
	let version = $state<string>('');
	let loading = $state(false);

	function close() {
		popups.close();
	}

	async function fetchVersion() {
		loading = true;
		try {
			const response = await fetch('http://localhost:8000/api/version');
			if (response.ok) {
				version = (await response.text()).trim();
			}
		} catch (err) {
			console.log(err);
			version = 'Unknown';
		} finally {
			loading = false;
		}
	}

	$effect(() => {
		if (popups.isOpen('about')) {
			fetchVersion();
		}
	});
</script>

{#if popups.isOpen('about')}
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
			class="relative z-10 flex w-[600px] flex-col items-center gap-4 rounded-lg border border-gray-200 bg-white p-8 shadow-2xl dark:border-neutral-700 dark:bg-neutral-900"
			in:scale={{ duration: 150, start: 0.96, opacity: 0 }}
			out:scale={{ duration: 150, start: 0.96, opacity: 0 }}
			role="dialog"
			aria-modal="true"
			tabindex="-1"
		>
			<!-- Logo -->
			<img src="/logo.svg" alt="SIGHTS Logo" class="h-32 w-120" />

			<!-- Version -->
			{#if loading}
				<div class="text-sm text-gray-500 dark:text-gray-400">Loading...</div>
			{:else}
				<div class="text-sm text-gray-600 dark:text-gray-400">Version {version}</div>
			{/if}

			<!-- Made with love -->
			<div class="text-sm text-gray-600 dark:text-gray-400">
				Made with <span class="text-red-500">♥</span> by the Semi Autonomous Rescue Team
			</div>

			<!-- Links -->
			<div
				class="flex gap-4 text-sm pt-2 border-t border-gray-200 dark:border-neutral-700 w-full justify-center"
			>
				<a
					href="https://github.com/your-repo"
					target="_blank"
					rel="noopener noreferrer"
					class="text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-gray-100 transition-colors"
				>
					GitHub
				</a>
				<a
					href="https://docs.example.com"
					target="_blank"
					rel="noopener noreferrer"
					class="text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-gray-100 transition-colors"
				>
					Documentation
				</a>
				<a
					href="https://example.com"
					target="_blank"
					rel="noopener noreferrer"
					class="text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-gray-100 transition-colors"
				>
					Website
				</a>
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
</style>
