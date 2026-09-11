<script lang="ts">
	import { fade, scale } from 'svelte/transition';

	import { AppClient, OpenAPI } from '$lib/api';
	import { addToast } from '$lib/components/shared/Toaster.svelte';
	import { getPopupState } from '$lib/stores/popups.svelte';

	const popups = getPopupState();

	const client = new AppClient(OpenAPI);

	let dialog = $state<HTMLDialogElement>();

	async function confirm() {
		popups.close();
		const res = await client.default.estopEstopPost();
		if (!res.ok) {
			addToast({
				data: {
					title: 'Emergency Stop Triggered',
					description: 'Emergency Stop triggered successfully',
					variant: 'success'
				}
			});
		}
	}

	function close() {
		popups.close();
	}
</script>

{#if popups.isOpen('estop')}
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
			<b class="text-3xl font-semibold text-red-500">Emergency Stop</b>
			<p>This operation ignores any safeties and immediately shuts down.</p>
			<p>
				This can result in <b class="text-red-500">data corruption</b> or the
				<b class="text-red-500">inability to boot</b> the system.
			</p>
			<p>This should only be used if absolutely neccecary.</p>
			<b class="text-red-500">USE AT YOUR OWN RISK</b>

			<br />

			<div class="flex gap-2">
				<button
					onclick={close}
					class="rounded-md border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 dark:border-neutral-600 dark:text-gray-300 dark:hover:bg-neutral-800"
				>
					Cancel
				</button>
				<button
					onclick={confirm}
					class="rounded-md bg-red-500 px-4 py-2 text-sm font-medium text-white hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed"
				>
					Confirm
				</button>
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
