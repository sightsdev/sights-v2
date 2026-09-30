<script lang="ts">
	import type { Snippet } from 'svelte';
	import type { HTMLButtonAttributes } from 'svelte/elements';

	type Variant = 'ghost' | 'outline' | 'danger' | 'primary';
	type Size = 'sm' | 'md' | 'lg';

	interface ButtonProps extends Omit<HTMLButtonAttributes, 'onclick'> {
		variant?: Variant;
		size?: Size;
		title?: string;
		onclick?: (event: MouseEvent) => void;
		disabled?: boolean;
		children?: Snippet;
	}

	let {
		variant = 'ghost',
		size = 'md',
		title = '',
		onclick = () => {},
		disabled = false,
		children,
		...restProps
	}: ButtonProps = $props();

	const baseStyles =
		'inline-flex items-center justify-center gap-2 font-medium transition-all duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50';

	const variants: Record<Variant, string> = {
		ghost:
			'hover:bg-gray-100 dark:hover:bg-neutral-700 text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white',
		outline:
			'border border-gray-300 dark:border-neutral-600 hover:bg-gray-50 dark:hover:bg-neutral-800 text-gray-700 dark:text-gray-300 hover:border-gray-400 dark:hover:border-neutral-500',
		danger:
			'border border-red-600 dark:border-red-500 text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-950/30 hover:border-red-700 dark:hover:border-red-400',
		primary: 'bg-orange-600 hover:bg-orange-700 text-white border border-transparent shadow-sm'
	};

	const sizes: Record<Size, string> = {
		sm: 'text-xs px-2.5 py-1.5 rounded-md',
		md: 'text-sm px-3 py-2 rounded-lg',
		lg: 'text-base px-4 py-2.5 rounded-lg'
	};

	const buttonClass = $derived(`${baseStyles} ${variants[variant]} ${sizes[size]}`);
</script>

<button type="button" class={buttonClass} {title} {onclick} {disabled} {...restProps}>
	{@render children?.()}
</button>
