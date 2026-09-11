<script lang="ts">
	import { onMount } from 'svelte';

	import uPlot from 'uplot';
	import 'uplot/dist/uPlot.min.css';

	let {
		title = 'Sensor Data',
		sensorName = null,
		updatePeriod = 500,
		length = 20,
		series = []
	}: {
		title?: string;
		sensorName?: string | null;
		updatePeriod?: number;
		length?: number;
		series?: string[] | string;
	} = $props();

	const seriesArray = $derived(Array.isArray(series) ? series : series ? [series] : []);

	let loading = $state(false);
	let error = $state<string | null>(null);
	let intervalId: number | null = null;
	let isDark = $state(false);
	let chartContainer: HTMLDivElement;
	let chart: uPlot | null = null;

	let chartData: uPlot.AlignedData = [[]];
	let dataVersion = $state(0);

	let prevSensorName = $derived(sensorName);
	let prevSeries = $derived('');
	let prevUpdatePeriod = $derived(updatePeriod);

	$effect(() => {
		prevSeries = JSON.stringify(seriesArray);
	});

	const colors = {
		light: ['#059669', '#0284c7', '#7c3aed', '#e11d48'],
		dark: ['#34d399', '#38bdf8', '#a78bfa', '#fb7185']
	};

	async function fetchData() {
		if (!sensorName || loading) return;

		loading = true;
		error = null;

		try {
			const response = await fetch(`/api/sensor/${sensorName}`);
			if (!response.ok) throw new Error('Failed to fetch');

			const newValue: Record<string, number> = await response.json();

			const timestamp = Date.now() / 1000;
			(chartData[0] as number[]).push(timestamp);

			seriesArray.forEach((s, i) => {
				if (!chartData[i + 1]) chartData[i + 1] = [];
				(chartData[i + 1] as number[]).push(newValue[s] ?? 0);
			});

			if (chartData[0].length > length) {
				chartData = chartData.map((arr) => arr.slice(-length)) as uPlot.AlignedData;
			}

			if (chart) {
				chart.setData(chartData);
			}

			dataVersion++;
		} catch (err) {
			error = err instanceof Error ? err.message : 'Unknown error';
		} finally {
			loading = false;
		}
	}

	function getChartOptions(): uPlot.Options {
		const palette = isDark ? colors.dark : colors.light;
		const textColor = isDark ? '#d1d5db' : '#1f2937';
		const gridColor = isDark ? '#374151' : '#e5e7eb';

		const rect = chartContainer?.getBoundingClientRect();
		const width = rect?.width || 400;
		const height = rect?.height || 300;

		return {
			width,
			height,
			series: [
				{ label: 'Time' },
				...seriesArray.map((s, i) => ({
					label: s,
					stroke: palette[i % palette.length],
					width: 2,
					points: { show: true, size: 4 },
					smooth: true
				}))
			],
			axes: [
				{
					stroke: textColor,
					grid: { stroke: gridColor, width: 1 },
					ticks: { stroke: gridColor }
				},
				{
					stroke: textColor,
					grid: { stroke: gridColor, width: 1 },
					ticks: { stroke: gridColor }
				}
			],
			legend: {
				show: true,
				live: false
			},
			cursor: {
				drag: { x: false, y: false }
			}
		};
	}

	function initChart() {
		if (chart) {
			chart.destroy();
			chart = null;
		}

		if (!chartContainer || seriesArray.length === 0) return;

		chartData = [[], ...seriesArray.map(() => [])];

		const opts = getChartOptions();
		chart = new uPlot(opts, chartData, chartContainer);

		requestAnimationFrame(() => {
			if (!chart || !chartContainer) return;
			const legend = chartContainer.querySelector('.u-legend');
			if (legend) {
				const legendHeight = legend.getBoundingClientRect().height;
				const rect = chartContainer.getBoundingClientRect();
				chart.setSize({
					width: rect.width,
					height: Math.max(100, rect.height - legendHeight - 5)
				});
			}
		});
	}

	function updateTheme() {
		const newIsDark = document.documentElement.classList.contains('dark');
		if (newIsDark !== isDark) {
			isDark = newIsDark;
			initChart();
		}
	}

	function handleResize() {
		if (chart && chartContainer) {
			const rect = chartContainer.getBoundingClientRect();
			const legend = chartContainer.querySelector('.u-legend');
			const legendHeight = legend?.getBoundingClientRect().height || 0;
			chart.setSize({
				width: rect.width,
				height: Math.max(100, rect.height - legendHeight - 5)
			});
		}
	}

	onMount(() => {
		updateTheme();
		const observer = new MutationObserver(updateTheme);
		observer.observe(document.documentElement, {
			attributes: true,
			attributeFilter: ['class']
		});

		const resizeObserver = new ResizeObserver(handleResize);
		resizeObserver.observe(chartContainer);

		initChart();

		if (sensorName && seriesArray.length > 0) {
			fetchData();
			intervalId = window.setInterval(fetchData, updatePeriod);
		}

		return () => {
			observer.disconnect();
			resizeObserver.disconnect();
			if (intervalId) clearInterval(intervalId);
			if (chart) chart.destroy();
		};
	});

	$effect(() => {
		const currentSeries = JSON.stringify(seriesArray);
		const configChanged =
			sensorName !== prevSensorName ||
			currentSeries !== prevSeries ||
			updatePeriod !== prevUpdatePeriod;

		if (!configChanged) return;

		prevSensorName = sensorName;
		prevSeries = currentSeries;
		prevUpdatePeriod = updatePeriod;

		if (intervalId) {
			clearInterval(intervalId);
			intervalId = null;
		}

		initChart();

		if (sensorName && seriesArray.length > 0) {
			fetchData();
			intervalId = window.setInterval(fetchData, updatePeriod);
		}

		return () => {
			if (intervalId) clearInterval(intervalId);
		};
	});

	const hasData = $derived(dataVersion > 0 && chartData[0].length > 0);
</script>

<div class="flex h-full flex-col bg-gray-100 dark:bg-neutral-800 rounded-lg p-4">
	<div class="mb-3 flex items-center justify-between">
		<h5 class="text-sm font-medium text-gray-900 dark:text-white">{title}</h5>
	</div>

	<div class="flex-1 min-h-0 relative">
		<div bind:this={chartContainer} class="h-full w-full text-black dark:text-white"></div>

		{#if error}
			<div
				class="absolute inset-0 flex items-center justify-center bg-gray-100 dark:bg-neutral-800"
			>
				<div class="text-center">
					<p class="text-sm text-red-600 dark:text-red-400">{error}</p>
					<button
						onclick={fetchData}
						class="mt-2 text-xs text-blue-600 hover:text-blue-700 dark:text-blue-400"
					>
						Retry
					</button>
				</div>
			</div>
		{:else if !sensorName}
			<div
				class="absolute inset-0 flex items-center justify-center bg-gray-100 dark:bg-neutral-800"
			>
				<p class="text-sm text-gray-500 dark:text-gray-400">No sensor selected</p>
			</div>
		{:else if !hasData && loading}
			<div
				class="absolute inset-0 flex items-center justify-center bg-gray-100 dark:bg-neutral-800"
			>
				<div class="text-center">
					<div
						class="inline-block h-8 w-8 animate-spin rounded-full border-4 border-blue-500 border-r-transparent"
					></div>
					<p class="mt-2 text-xs text-gray-500 dark:text-gray-400">Loading...</p>
				</div>
			</div>
		{/if}
	</div>
</div>
