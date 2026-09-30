<script lang="ts">
	import { onMount } from 'svelte';

	let {
		sensorName = null,
		width = 32,
		height = 24,
		tempRange = [0, 30],
		hslRange = [0, 90],
		updatePeriod = 500
	}: {
		sensorName?: string | null;
		width?: number;
		height?: number;
		tempRange?: [number, number];
		hslRange?: [number, number];
		updatePeriod?: number;
	} = $props();

	let canvasEl = $state<HTMLCanvasElement | undefined>(undefined);
	let loading = $state(false);
	let error = $state<string | null>(null);
	let intervalId: number | null = null;
	let actualSize = $derived({ width, height });

	function hsl2rgba(h: number, s: number, l: number): number[] {
		let a = s * Math.min(l, 1 - l);
		let f = (n: number, k: number = (n + h / 30) % 12) =>
			l - a * Math.max(Math.min(k - 3, 9 - k, 1), -1);
		return [255 * f(0), 255 * f(8), 255 * f(4), 255];
	}

	function getHue(temp: number): number {
		const sDeg = (hslRange[1] - hslRange[0]) / (tempRange[1] - tempRange[0]);
		return 360 - ((tempRange[1] - temp) * sDeg - (hslRange[1] - 360));
	}

	async function fetchData() {
		if (!sensorName || loading) return;
		loading = true;
		error = null;
		try {
			const response = await fetch(`/api/sensor/${sensorName}`);
			if (!response.ok) throw new Error('Failed to fetch thermal data');
			const data: number[] = await response.json();

			if (data.length === 768) {
				actualSize = { width: 32, height: 24 };
			} else if (data.length === 1536) {
				actualSize = { width: 64, height: 48 };
			} else {
				actualSize = { width, height };
			}

			const rgbaData = data.map((temp) => hsl2rgba(getHue(temp), 1, 0.5)).flat();

			if (canvasEl) {
				const ctx = canvasEl.getContext('2d');
				if (!ctx) throw new Error('Could not get canvas context');
				ctx.imageSmoothingEnabled = false;
				const imgData = new ImageData(
					new Uint8ClampedArray(rgbaData),
					actualSize.width,
					actualSize.height
				);
				ctx.putImageData(imgData, 0, 0);
			}
		} catch (err) {
			error = err instanceof Error ? err.message : 'Unknown error';
		} finally {
			loading = false;
		}
	}

	onMount(() => {
		if (sensorName) {
			fetchData();
			intervalId = window.setInterval(fetchData, updatePeriod);
		}
		return () => intervalId && clearInterval(intervalId);
	});
</script>

<!-- Container -->
<div
	class="flex h-full w-full items-center justify-center bg-gray-100 dark:bg-neutral-800 rounded-lg"
>
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
	{:else if !sensorName}
		<p class="text-sm text-gray-500 dark:text-gray-400">No sensor selected</p>
	{:else}
		<div class="relative flex items-center justify-center w-full h-full">
			<div class="p-2 flex items-center justify-center" style="width: 100%; height: 100%;">
				<canvas
					bind:this={canvasEl}
					width={actualSize.width}
					height={actualSize.height}
					class="rounded-md"
					style="
						image-rendering: pixelated;
						width: 100%;
						height: 100%;
						object-fit: contain;
						max-width: 100%;
						max-height: 100%;
					"
				></canvas>
			</div>
		</div>
	{/if}
</div>
