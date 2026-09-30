<script lang="ts">
	import { onMount } from 'svelte';

	let {
		title = 'Sensor',
		sensorName = null,
		series = '',
		suffix = '%',
		updatePeriod = 500
	}: {
		title?: string;
		sensorName?: string | null;
		series?: string;
		suffix?: string;
		updatePeriod?: number;
	} = $props();

	let value = $state(0);
	let loading = $state(false);
	let error = $state<string | null>(null);
	let intervalId: number | null = null;
	let isDark = $state(false);

	async function fetchData() {
		if (!sensorName || !series || loading) return;
		loading = true;
		error = null;
		try {
			const response = await fetch(`/api/sensor/${sensorName}`);
			if (!response.ok) throw new Error('Failed to fetch');
			const data: Record<string, number> = await response.json();
			value = Math.round(data[series] ?? 0);
		} catch (err) {
			error = err instanceof Error ? err.message : 'Unknown error';
		} finally {
			loading = false;
		}
	}

	// Detect dark mode
	onMount(() => {
		const checkDark = () => {
			isDark = document.documentElement.classList.contains('dark');
		};
		checkDark();
		const observer = new MutationObserver(checkDark);
		observer.observe(document.documentElement, {
			attributes: true,
			attributeFilter: ['class']
		});

		// Start polling
		if (sensorName && series) {
			fetchData();
			intervalId = window.setInterval(fetchData, updatePeriod);
		}

		return () => {
			observer.disconnect();
			if (intervalId) clearInterval(intervalId);
		};
	});

	// Watch for config changes
	$effect(() => {
		// Clear existing interval
		if (intervalId) {
			clearInterval(intervalId);
			intervalId = null;
		}

		// Reset and start new polling if configured
		if (sensorName && series) {
			value = 0;
			fetchData();
			intervalId = window.setInterval(fetchData, updatePeriod);
		}

		// Cleanup when effect re-runs or component unmounts
		return () => {
			if (intervalId) {
				clearInterval(intervalId);
				intervalId = null;
			}
		};
	});

	// Calculate circular progress
	const circumference = 251.2; // 2 * PI * 40 (radius)
	const progress = $derived((value / 100) * circumference);
	const offset = $derived(circumference - progress);
</script>

<div class="flex h-full w-full flex-col bg-gray-100 dark:bg-neutral-800 rounded-lg p-4">
	<div class="mb-3 flex items-center justify-between flex-shrink-0">
		<h5 class="text-sm font-medium text-gray-900 dark:text-white">{title}</h5>
		{#if loading}
			<div class="h-2 w-2 rounded-full bg-orange-500 animate-pulse"></div>
		{/if}
	</div>
	<div class="flex-1 flex items-center justify-center">
		{#if error}
			<div class="text-center">
				<p class="text-sm text-red-600 dark:text-red-400">{error}</p>
				<button
					onclick={fetchData}
					class="mt-2 text-xs text-orange-600 hover:text-orange-700 dark:text-orange-400"
				>
					Retry
				</button>
			</div>
		{:else if !sensorName || !series}
			<p class="text-sm text-gray-500 dark:text-gray-400">Configure sensor and series</p>
		{:else}
			<div class="relative w-full max-w-[200px] aspect-square">
				<svg class="w-full h-full -rotate-90" viewBox="0 0 100 100">
					<!-- Background circle -->
					<circle
						cx="50"
						cy="50"
						r="40"
						fill="none"
						stroke={isDark ? '#404040' : '#d1d5db'}
						stroke-width="8"
					/>
					<!-- Progress circle -->
					<circle
						cx="50"
						cy="50"
						r="40"
						fill="none"
						stroke={isDark ? '#0ea5e9' : '#0284c7'}
						stroke-width="8"
						stroke-linecap="round"
						stroke-dasharray={circumference}
						stroke-dashoffset={offset}
						style="transition: stroke-dashoffset 0.5s ease"
					/>
				</svg>
				<!-- Text overlay -->
				<div class="absolute inset-0 flex items-center justify-center">
					<span class="text-2xl font-semibold" style="color: {isDark ? '#0ea5e9' : '#0284c7'}">
						{value}{suffix}
					</span>
				</div>
			</div>
		{/if}
	</div>
</div>
