<script lang="ts" module>
	import { fly } from 'svelte/transition';

	import { Toaster } from 'melt/builders';
	import { Progress } from 'melt/components';

	type ToastData = {
		title: string;
		description: string;
		variant?: 'success' | 'warning' | 'error';
	};

	const toaster = new Toaster<ToastData>({
		hover: 'pause-all',
		closeDelay: 4000
	});

	export const addToast = toaster.addToast;
</script>

<div
	{...toaster.root}
	class="fixed !right-4 !bottom-4 flex w-[380px] flex-col"
	style:--toasts={toaster.toasts.length}
>
	{#each toaster.toasts as toast, i (toast.id)}
		<div
			class="relative flex h-(--toast-height) w-full flex-col justify-center rounded-xl bg-gray-200 px-4 py-3 text-left text-gray-900 transition dark:bg-neutral-800 dark:text-white {toast
				.data.variant === 'error'
				? 'border-[1.2px]'
				: 'border-0'}"
			style:border-color={toast.data.variant === 'error' ? '#FF627D' : ''}
			style:--n={toaster.toasts.length - i}
			in:fly={{ y: 60, opacity: 0.9 }}
			out:fly={{ y: 20 }}
		>
			<h3 {...toast.title} class="text-sm font-medium whitespace-nowrap">
				{toast.data.title}
			</h3>

			{#if toast.data.description}
				<div {...toast.description} class="text-xs text-gray-700 dark:text-gray-300">
					{toast.data.description}
				</div>
			{/if}

			<button
				{...toast.close}
				aria-label="dismiss toast"
				class="absolute top-1 right-1 h-6 w-6 rounded-md bg-transparent p-0 text-gray-500 transition-colors hover:bg-gray-300 hover:text-gray-700 dark:text-gray-400 dark:hover:bg-neutral-700 dark:hover:text-gray-200"
			>
				<span>✕</span>
			</button>

			{#if toast.closeDelay !== 0}
				<div class="absolute right-4 bottom-4 h-[4px] w-[30px] overflow-hidden rounded-full">
					<Progress value={toast.percentage}>
						{#snippet children(progress)}
							<div
								{...progress.root}
								class="relative h-full w-full overflow-hidden bg-gray-300 dark:bg-neutral-900"
							>
								<div
									{...progress.progress}
									class="h-full w-full -translate-x-[var(--progress)]"
									class:bg-green-500={toast.data.variant === 'success'}
									class:bg-yellow-500={toast.data.variant === 'warning'}
									class:bg-red-500={toast.data.variant === 'error'}
									class:bg-orange-500={!toast.data.variant}
								></div>
							</div>
						{/snippet}
					</Progress>
				</div>
			{/if}
		</div>
	{/each}
</div>

<style>
	:global([popover]) {
		inset: unset;
	}

	[data-melt-toaster-root] {
		--gap: 0.75rem;
		--hover-offset: 1rem;
		--toast-height: 5.5rem;
		--hidden-offset: 0.75rem;
		--hidden-toasts: calc(var(--toasts) - 1);
		overflow: visible;
		display: grid;
		grid-template-rows: var(--toast-height) repeat(var(--hidden-toasts), var(--hidden-offset));
		grid-template-columns: 1fr;
		gap: 0;
		background: unset;
		padding: 0;
	}

	[data-melt-toaster-root]:hover {
		grid-template-rows:
			var(--hidden-offset) var(--toast-height)
			repeat(var(--hidden-toasts), calc(var(--toast-height) + var(--gap)));
	}

	[data-melt-toaster-root] > div {
		position: absolute;
		pointer-events: auto;
		bottom: 0;
		left: 0;
		box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.1);
		transform-origin: 50% 0%;
		transition: all 350ms ease;
	}

	:global(.dark) [data-melt-toaster-root] > div {
		box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.5);
	}

	[data-melt-toaster-root] > div:nth-last-child(n + 4) {
		z-index: 1;
		scale: 0.925;
		opacity: 0;
		translate: 0 calc(-3 * var(--hidden-offset));
	}

	[data-melt-toaster-root] > div:nth-last-child(-n + 3) {
		z-index: 2;
		scale: 0.95;
		translate: 0 calc(-2 * var(--hidden-offset));
	}

	[data-melt-toaster-root] > div:nth-last-child(-n + 2) {
		z-index: 3;
		scale: 0.975;
		translate: 0 calc(-1 * var(--hidden-offset));
	}

	[data-melt-toaster-root] > div:nth-last-child(-n + 1) {
		z-index: 4;
		scale: 1;
		translate: 0;
	}

	[data-melt-toaster-root]:hover > div {
		scale: 1;
		opacity: 1;
		--toast-gap: calc(calc(var(--gap) * var(--n)) + var(--hover-offset));
		--percentage: calc(-100% * calc(var(--n) - 1));
		translate: 0 calc(var(--percentage) - var(--toast-gap));
	}
</style>
