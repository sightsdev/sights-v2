<!-- DISCLAMER -->
<!-- This code has been made with heavy AI use, I am so sorry. -->
<!-- I welcome anyone reading this with more knowledge to make this not awful -->

<script lang="ts">
	import { Download, Plus, Settings, Upload, User } from '@lucide/svelte';

	import { onMount } from 'svelte';
	import { fade, scale as scaleTransition } from 'svelte/transition';

	import type { SensorConfig } from '$lib/api/models/SensorConfig';
	import { WIDGET_TYPES } from '$lib/components/dashboard/widgetRegistry';
	import { addToast } from '$lib/components/shared/Toaster.svelte';
	import { isEditMode } from '$lib/stores/editMode.svelte';

	let { cameras = [], sensors }: Props = $props();

	interface Props {
		cameras: string[];
		sensors: Record<string, SensorConfig>;
	}

	interface WidgetItem {
		id: number;
		type: string;
		x: number;
		y: number;
		w: number;
		h: number;
		config: Record<string, unknown>;
	}

	type ConfigField = {
		key: string;
		label: string;
		type: string;
		required?: boolean;
		placeholder?: string;
		min?: number;
		max?: number;
		step?: number;
		options?: Array<{ value: unknown; label: string }> | 'cameras' | 'sensors';
	};

	interface ResizeState {
		item: WidgetItem;
		handle: string;
		startX: number;
		startY: number;
		startWidth: number;
		startHeight: number;
		startLeft: number;
		startTop: number;
	}

	const MIN_SIZE = { w: 200, h: 150 };
	const GRID_SNAP = 20;
	const STORAGE_KEY = 'dashboard-layout';
	const PROFILES_KEY = 'dashboard-profiles';
	const CURRENT_PROFILE_KEY = 'dashboard-current-profile';

	const snapToGrid = (v: number) => Math.round(v / GRID_SNAP) * GRID_SNAP;
	const pxToPercent = (px: number, dim: number) => (px / dim) * 100;
	const percentToPx = (pct: number, dim: number) => (pct / 100) * dim;
	const clamp = (v: number, lo: number, hi: number) => Math.max(lo, Math.min(hi, v));

	// State
	let showDropdown = $state(false);
	let showConfigModal = $state(false);
	let showProfileModal = $state(false);
	let configuringWidget = $state<WidgetItem | null>(null);
	let items = $state<WidgetItem[]>([]);
	let dragging = $state<{ item: WidgetItem; offsetX: number; offsetY: number } | null>(null);
	let resizing: ResizeState | null = null;
	let focusedWidgetId = $state<number | null>(null);
	let containerEl: HTMLDivElement;
	let containerWidth = $state(1200);
	let containerHeight = $state(800);
	let initialContainerWidth = $state(1200);
	let initialContainerHeight = $state(800);
	let profiles = $state<Record<string, WidgetItem[]>>({});
	let currentProfile = $state<string>('');
	let newProfileName = $state('');
	let confirmDelete = $state<string | null>(null);

	const dashScale = $derived(
		Math.min(containerWidth / initialContainerWidth, containerHeight / initialContainerHeight)
	);

	onMount(() => {
		const savedProfiles: Record<string, WidgetItem[]> = JSON.parse(
			localStorage.getItem(PROFILES_KEY) ?? '{}'
		);
		const savedCurrentProfile = localStorage.getItem(CURRENT_PROFILE_KEY) ?? '';

		if (savedCurrentProfile && savedProfiles[savedCurrentProfile]) {
			items = JSON.parse(JSON.stringify(savedProfiles[savedCurrentProfile]));
		} else {
			const saved = localStorage.getItem(STORAGE_KEY);
			items = saved ? JSON.parse(saved) : [];
		}

		profiles = savedProfiles;
		currentProfile = savedCurrentProfile;
	});

	function saveProfiles(): void {
		localStorage.setItem(PROFILES_KEY, JSON.stringify(profiles));
	}

	function saveLayout(): void {
		localStorage.setItem(STORAGE_KEY, JSON.stringify(items));
		if (currentProfile) {
			profiles[currentProfile] = [...items];
			saveProfiles();
		}
	}

	function updateItem(id: number, fn: (item: WidgetItem) => WidgetItem): void {
		items = items.map((item) => (item.id === id ? fn(item) : item));
	}

	function getWidgetRect(e: MouseEvent): DOMRect | undefined {
		return (e.currentTarget as HTMLElement).closest('.widget-container')?.getBoundingClientRect();
	}

	function parseArrayValue(value: string | string[]): string[] {
		if (Array.isArray(value)) return value;
		return value
			.split(',')
			.map((s) => s.trim())
			.filter(Boolean);
	}

	function formatArrayValue(value: unknown): string {
		return Array.isArray(value) ? value.join(', ') : String(value ?? '');
	}

	// Container resize observer
	$effect(() => {
		if (!containerEl) return;
		let first = true;
		const observer = new ResizeObserver((entries) => {
			const { width, height } = entries[0].contentRect;
			containerWidth = width;
			containerHeight = height;
			if (first) {
				initialContainerWidth = width;
				initialContainerHeight = height;
				first = false;
			} else {
				if (width > initialContainerWidth) initialContainerWidth = width;
				if (height > initialContainerHeight) initialContainerHeight = height;
			}
		});
		observer.observe(containerEl);
		return () => observer.disconnect();
	});

	// Drag & drop
	function startDrag(item: WidgetItem, e: MouseEvent): void {
		if (!$isEditMode) return;
		const rect = getWidgetRect(e);
		if (!rect) return;
		dragging = { item, offsetX: e.clientX - rect.left, offsetY: e.clientY - rect.top };
	}

	function startResize(item: WidgetItem, handle: string, e: MouseEvent): void {
		if (!$isEditMode) return;
		e.stopPropagation();
		const rect = getWidgetRect(e);
		if (!rect) return;
		resizing = {
			item,
			handle,
			startX: e.clientX,
			startY: e.clientY,
			startWidth: rect.width,
			startHeight: rect.height,
			startLeft: item.x,
			startTop: item.y
		};
	}

	function onMouseMove(e: MouseEvent): void {
		const container = containerEl?.getBoundingClientRect();
		if (!container) return;

		if (dragging) {
			const xPx = snapToGrid(e.clientX - container.left - dragging.offsetX);
			const yPx = snapToGrid(e.clientY - container.top - dragging.offsetY);
			updateItem(dragging.item.id, (item) => {
				const wPx = percentToPx(item.w, initialContainerWidth) * dashScale;
				const hPx = percentToPx(item.h, initialContainerHeight) * dashScale;
				return {
					...item,
					x: pxToPercent(clamp(xPx, 0, container.width - wPx), initialContainerWidth),
					y: pxToPercent(clamp(yPx, 0, container.height - hPx), initialContainerHeight)
				};
			});
		} else if (resizing) {
			const dx = e.clientX - resizing.startX;
			const dy = e.clientY - resizing.startY;
			const { handle, startWidth, startHeight, startLeft, startTop } = resizing;
			const startLeftPx = percentToPx(startLeft, initialContainerWidth);
			const startTopPx = percentToPx(startTop, initialContainerHeight);

			updateItem(resizing.item.id, (w) => {
				let newW = startWidth / dashScale;
				let newH = startHeight / dashScale;
				let newXPx = startLeftPx;
				let newYPx = startTopPx;

				if (handle.includes('e'))
					newW = Math.max(MIN_SIZE.w, snapToGrid((startWidth + dx) / dashScale));
				if (handle.includes('w')) {
					newW = Math.max(MIN_SIZE.w, snapToGrid((startWidth - dx) / dashScale));
					newXPx = snapToGrid(startLeftPx + (startWidth / dashScale - newW));
				}
				if (handle.includes('s'))
					newH = Math.max(MIN_SIZE.h, snapToGrid((startHeight + dy) / dashScale));
				if (handle.includes('n')) {
					newH = Math.max(MIN_SIZE.h, snapToGrid((startHeight - dy) / dashScale));
					newYPx = snapToGrid(startTopPx + (startHeight / dashScale - newH));
				}

				newXPx = clamp(newXPx, 0, initialContainerWidth - newW);
				newYPx = clamp(newYPx, 0, initialContainerHeight - newH);
				newW = Math.min(newW, initialContainerWidth - newXPx);
				newH = Math.min(newH, initialContainerHeight - newYPx);

				return {
					...w,
					w: pxToPercent(newW, initialContainerWidth),
					h: pxToPercent(newH, initialContainerHeight),
					x: pxToPercent(newXPx, initialContainerWidth),
					y: pxToPercent(newYPx, initialContainerHeight)
				};
			});
		}
	}

	function onMouseUp(): void {
		if (dragging || resizing) {
			saveLayout();
			dragging = null;
			resizing = null;
		}
	}

	// Widget management
	function addWidget(type: string): void {
		const widgetConfig = WIDGET_TYPES[type as keyof typeof WIDGET_TYPES];
		if (!widgetConfig) return;

		const newWidget: WidgetItem = {
			id: Math.max(0, ...items.map((i) => i.id)) + 1,
			type,
			x: pxToPercent(20, initialContainerWidth),
			y: pxToPercent(20, initialContainerHeight),
			w: pxToPercent(widgetConfig.defaultSize.w, initialContainerWidth),
			h: pxToPercent(widgetConfig.defaultSize.h, initialContainerHeight),
			config: { ...widgetConfig.defaultConfig }
		};

		items = [...items, newWidget];
		saveLayout();
		showDropdown = false;

		if (widgetConfig.configSchema?.length) {
			configuringWidget = newWidget;
			showConfigModal = true;
		}
	}

	function removeWidget(id: number): void {
		items = items.filter((item) => item.id !== id);
		if (focusedWidgetId === id) focusedWidgetId = null;
		saveLayout();
	}

	function saveConfig(): void {
		if (!configuringWidget) return;
		const widgetToUpdate = configuringWidget;
		items = items.filter((item) => item.id !== widgetToUpdate.id);
		queueMicrotask(() => {
			items = [...items, widgetToUpdate as WidgetItem];
			saveLayout();
		});
		showConfigModal = false;
		configuringWidget = null;
	}

	function handleKeyDown(item: WidgetItem, e: KeyboardEvent): void {
		if (!$isEditMode) return;
		const step = e.shiftKey ? 100 : 20;
		e.preventDefault();

		if (e.key === 'Delete' || e.key === 'Backspace') {
			removeWidget(item.id);
			return;
		}

		const deltas: Record<string, [number, number]> = {
			ArrowLeft: [-step, 0],
			ArrowRight: [step, 0],
			ArrowUp: [0, -step],
			ArrowDown: [0, step]
		};
		const delta = deltas[e.key];
		if (!delta) return;

		const [dx, dy] = delta;
		updateItem(item.id, (it) => {
			const xPx = percentToPx(it.x, initialContainerWidth);
			const yPx = percentToPx(it.y, initialContainerHeight);
			const wPx = percentToPx(it.w, initialContainerWidth);
			const hPx = percentToPx(it.h, initialContainerHeight);
			return {
				...it,
				x: pxToPercent(
					clamp(snapToGrid(xPx + dx / dashScale), 0, initialContainerWidth - wPx),
					initialContainerWidth
				),
				y: pxToPercent(
					clamp(snapToGrid(yPx + dy / dashScale), 0, initialContainerHeight - hPx),
					initialContainerHeight
				)
			};
		});
		saveLayout();
	}

	function getConfigOptions(field: ConfigField) {
		if (field.options === 'cameras')
			return (cameras || []).map((cam) => ({ value: cam, label: cam }));
		if (field.options === 'sensors')
			return Object.keys(sensors || {}).map((name) => ({ value: name, label: name }));
		return Array.isArray(field.options) ? field.options : [];
	}

	// Profile management
	function createProfile(): void {
		if (!newProfileName.trim()) return;
		const name = newProfileName.trim();
		profiles = { ...profiles, [name]: [...items] };
		currentProfile = name;
		saveProfiles();
		localStorage.setItem(CURRENT_PROFILE_KEY, name);
		newProfileName = '';
		showProfileModal = false;
		addToast({
			data: {
				title: 'Profile created',
				description: `"${name}" saved successfully`,
				variant: 'success'
			}
		});
	}

	function loadProfile(name: string): void {
		if (!profiles[name]) return;
		items = JSON.parse(JSON.stringify(profiles[name]));
		currentProfile = name;
		localStorage.setItem(STORAGE_KEY, JSON.stringify(items));
		localStorage.setItem(CURRENT_PROFILE_KEY, name);
		showProfileModal = false;
		addToast({
			data: { title: 'Profile loaded', description: `Switched to "${name}"`, variant: 'success' }
		});
	}

	function deleteProfile(name: string): void {
		const rest = { ...profiles };
		delete rest[name];
		profiles = rest;

		if (currentProfile === name) {
			currentProfile = '';
			localStorage.setItem(CURRENT_PROFILE_KEY, '');
		}
		saveProfiles();
		addToast({
			data: {
				title: 'Profile deleted',
				description: `"${name}" has been removed`,
				variant: 'success'
			}
		});
	}

	function exportProfile(name: string): void {
		const data = {
			name,
			version: '1.0',
			widgets: profiles[name],
			exportedAt: new Date().toISOString()
		};
		const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
		const url = URL.createObjectURL(blob);
		const a = Object.assign(document.createElement('a'), {
			href: url,
			download: `dashboard-profile-${name.replace(/\s+/g, '-')}.json`
		});
		a.click();
		URL.revokeObjectURL(url);
		addToast({
			data: {
				title: 'Profile exported',
				description: `"${name}" downloaded successfully`,
				variant: 'success'
			}
		});
	}

	function importProfile(): void {
		const input = Object.assign(document.createElement('input'), { type: 'file', accept: '.json' });
		input.onchange = (e) => {
			const file = (e.target as HTMLInputElement).files?.[0];
			if (!file) return;
			const reader = new FileReader();
			reader.onload = (e) => {
				try {
					const data = JSON.parse(e.target?.result as string);
					if (data.widgets && Array.isArray(data.widgets)) {
						const name = data.name || 'Imported Profile';
						profiles = { ...profiles, [name]: data.widgets };
						saveProfiles();
						addToast({
							data: {
								title: 'Profile imported',
								description: `"${name}" imported successfully`,
								variant: 'success'
							}
						});
					} else {
						addToast({
							data: {
								title: 'Import failed',
								description: 'Invalid profile format',
								variant: 'error'
							}
						});
					}
				} catch {
					addToast({
						data: {
							title: 'Import failed',
							description: 'Please check the file format',
							variant: 'error'
						}
					});
				}
			};
			reader.readAsText(file);
		};
		input.click();
	}
</script>

<svelte:window
	onmousemove={onMouseMove}
	onmouseup={onMouseUp}
	onclick={(e) => {
		if (showDropdown && !(e.target as HTMLElement).closest('.widget-menu')) showDropdown = false;
	}}
/>

<div class="flex h-full flex-col overflow-hidden p-4">
	<div
		bind:this={containerEl}
		class="dashboard-container relative flex-1 overflow-hidden rounded-lg bg-gray-50 dark:bg-neutral-900"
		style="background-size: 20px 20px; background-image: {$isEditMode
			? 'radial-gradient(circle, #cbd5e1 1px, transparent 1px)'
			: 'none'};"
	>
		{#if $isEditMode}
			<div class="absolute right-4 bottom-4 z-50 flex items-end gap-3">
				<div
					class="mb-0.5 rounded-lg bg-white px-4 py-2 shadow-lg ring-1 ring-black/5 dark:bg-neutral-800 dark:ring-white/10"
				>
					<div class="text-xs text-gray-500 dark:text-gray-400">
						Drag to move • Handles to resize • Arrow keys for precision
					</div>
				</div>

				<button
					onclick={(e) => {
						e.stopPropagation();
						showProfileModal = true;
					}}
					class="inline-flex items-center gap-2 rounded-lg border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 shadow-sm transition-colors hover:bg-gray-50 dark:border-neutral-600 dark:bg-neutral-800 dark:text-gray-300 dark:hover:bg-neutral-700"
					title={currentProfile ? `Current: ${currentProfile}` : 'Manage Profiles'}
				>
					<User size={16} />
					{currentProfile || 'Profiles'}
				</button>

				<div class="widget-menu relative">
					<button
						onclick={(e) => {
							e.stopPropagation();
							showDropdown = !showDropdown;
						}}
						class="inline-flex items-center gap-2 rounded-lg border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 shadow-sm transition-colors hover:bg-gray-50 dark:border-neutral-600 dark:bg-neutral-800 dark:text-gray-300 dark:hover:bg-neutral-700"
					>
						<Plus size={16} /> Add Widget
					</button>

					{#if showDropdown}
						<div
							class="animate-in absolute bottom-full right-0 mb-2 w-56 rounded-lg bg-white shadow-xl ring-1 ring-black/5 dark:bg-neutral-800 dark:ring-white/10"
						>
							<div class="p-1">
								{#each Object.entries(WIDGET_TYPES) as [type, config] (type)}
									<button
										onclick={() => addWidget(type)}
										class="flex w-full items-center gap-3 rounded-md px-3 py-2 text-sm text-gray-700 transition-colors hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-neutral-700"
									>
										{config.label}
									</button>
								{/each}
							</div>
						</div>
					{/if}
				</div>
			</div>
		{/if}

		{#each items as item (item.id)}
			{@const WidgetComponent = WIDGET_TYPES[item.type as keyof typeof WIDGET_TYPES]?.component}
			{@const xPx = percentToPx(item.x, initialContainerWidth) * dashScale}
			{@const yPx = percentToPx(item.y, initialContainerHeight) * dashScale}
			{@const wPx = percentToPx(item.w, initialContainerWidth) * dashScale}
			{@const hPx = percentToPx(item.h, initialContainerHeight) * dashScale}
			<div
				class="widget-container absolute"
				class:cursor-move={$isEditMode}
				class:ring-2={$isEditMode && focusedWidgetId === item.id}
				class:ring-blue-500={$isEditMode && focusedWidgetId === item.id}
				style="left: {xPx}px; top: {yPx}px; width: {wPx}px; height: {hPx}px;"
			>
				{#if $isEditMode}
					<div
						class="pointer-events-none absolute inset-0 z-10 rounded-lg border-2 border-blue-400 dark:border-blue-500"
					></div>

					<div class="absolute left-2 right-2 top-2 z-20 flex justify-center">
						<div
							class="flex items-center gap-1 rounded-lg border border-gray-200 bg-white/95 shadow-lg backdrop-blur-sm dark:border-neutral-700 dark:bg-neutral-800/95"
						>
							<button
								onclick={(e) => {
									e.stopPropagation();
									configuringWidget = item;
									showConfigModal = true;
								}}
								class="flex items-center gap-1.5 rounded-l-lg px-3 py-1.5 text-sm text-gray-700 transition-colors hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-neutral-700"
								title="Configure widget"
							>
								<Settings size={14} />
								<span class="text-xs font-medium">Config</span>
							</button>
							<div class="h-4 w-px bg-gray-200 dark:bg-neutral-700"></div>
							<button
								onclick={() => removeWidget(item.id)}
								class="flex items-center gap-1.5 rounded-r-lg px-3 py-1.5 text-sm text-red-600 transition-colors hover:bg-red-50 dark:text-red-400 dark:hover:bg-red-950/20"
								title="Remove widget"
							>
								<span class="text-xs font-medium">Delete</span>
							</button>
						</div>
					</div>

					<button
						onmousedown={(e) => startDrag(item, e)}
						onkeydown={(e) => handleKeyDown(item, e)}
						onfocus={() => (focusedWidgetId = item.id)}
						onblur={() => (focusedWidgetId = null)}
						class="absolute inset-0 z-10 cursor-move focus:outline-none"
						aria-label="Move widget"
					></button>

					{#each ['n', 'ne', 'e', 'se', 's', 'sw', 'w', 'nw'] as handle (handle)}
						<button
							onmousedown={(e) => startResize(item, handle, e)}
							class="resize-handle resize-{handle} z-20"
							aria-label="Resize {handle}"
						></button>
					{/each}
				{/if}

				<div
					class="h-full w-full overflow-hidden rounded-lg"
					class:pointer-events-none={$isEditMode}
				>
					{#if WidgetComponent}
						<WidgetComponent {...item.config} />
					{/if}
				</div>
			</div>
		{/each}
	</div>
</div>

{#if showProfileModal}
	<div
		role="dialog"
		aria-modal="true"
		class="fixed inset-0 z-[100] flex items-center justify-center"
	>
		<button
			class="fixed inset-0 cursor-default bg-black/50"
			onclick={() => (showProfileModal = false)}
			in:fade={{ duration: 150 }}
			out:fade={{ duration: 150 }}
			tabindex="-1"
			aria-label="Close dialog"
		></button>

		<div
			class="relative z-10 w-full max-w-md rounded-lg bg-white p-6 shadow-xl dark:bg-neutral-800"
			in:scaleTransition={{ duration: 150, start: 0.96, opacity: 0 }}
			out:scaleTransition={{ duration: 150, start: 0.96, opacity: 0 }}
		>
			<h2 class="mb-4 text-xl font-semibold text-gray-900 dark:text-white">Dashboard Profiles</h2>

			<div class="mb-4">
				<div class="mb-2 block text-sm font-medium text-gray-700 dark:text-gray-300">
					Create New Profile
				</div>
				<div class="flex gap-2">
					<input
						type="text"
						bind:value={newProfileName}
						placeholder="Profile name..."
						onkeydown={(e) => e.key === 'Enter' && createProfile()}
						class="flex-1 rounded-md border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900 dark:border-neutral-600 dark:bg-neutral-700 dark:text-white"
					/>
					<button
						onclick={createProfile}
						disabled={!newProfileName.trim()}
						class="rounded-md bg-blue-500 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-blue-600 disabled:cursor-not-allowed disabled:opacity-50"
					>
						Create
					</button>
				</div>
			</div>

			<div class="mb-4">
				<div class="mb-2 flex items-center justify-between">
					<div class="block text-sm font-medium text-gray-700 dark:text-gray-300">
						Saved Profiles
					</div>
					<button
						onclick={importProfile}
						class="flex items-center gap-1.5 rounded-md px-2 py-1 text-xs font-medium text-blue-600 transition-colors hover:bg-blue-50 dark:text-blue-400 dark:hover:bg-blue-950/20"
					>
						<Upload size={14} /> Import
					</button>
				</div>
				<div class="max-h-64 space-y-2 overflow-y-auto">
					{#if Object.keys(profiles).length === 0}
						<p class="py-4 text-center text-sm text-gray-500 dark:text-gray-400">
							No profiles saved yet
						</p>
					{:else}
						{#each Object.keys(profiles) as name (name)}
							<div
								class="flex items-center gap-2 rounded-lg border border-gray-200 bg-gray-50 p-3 dark:border-neutral-700 dark:bg-neutral-900"
							>
								<User size={16} class="text-gray-400 dark:text-gray-500" />
								<span class="flex-1 text-sm font-medium text-gray-900 dark:text-white">{name}</span>
								{#if currentProfile === name}
									<span class="text-xs font-medium text-blue-600 dark:text-blue-400">Active</span>
								{/if}
								<div class="flex gap-1">
									{#if currentProfile !== name}
										<button
											onclick={() => loadProfile(name)}
											class="rounded px-2 py-1 text-xs font-medium text-gray-700 transition-colors hover:bg-gray-200 dark:text-gray-300 dark:hover:bg-neutral-700"
										>
											Load
										</button>
									{/if}
									<button
										onclick={() => exportProfile(name)}
										class="rounded p-1.5 text-gray-600 transition-colors hover:bg-gray-200 dark:text-gray-400 dark:hover:bg-neutral-700"
										title="Export profile"
									>
										<Download size={14} />
									</button>
									{#if confirmDelete === name}
										<button
											onclick={() => {
												deleteProfile(name);
												confirmDelete = null;
											}}
											class="rounded bg-red-600 px-2 py-1 text-xs font-medium text-white transition-colors hover:bg-red-700"
										>
											Confirm
										</button>
										<button
											onclick={() => (confirmDelete = null)}
											aria-label="Cancel"
											class="rounded p-1.5 text-gray-600 transition-colors hover:bg-gray-200 dark:text-gray-400 dark:hover:bg-neutral-700"
										>
											<svg
												width="14"
												height="14"
												viewBox="0 0 24 24"
												fill="none"
												stroke="currentColor"
												stroke-width="2"
											>
												<path d="M18 6L6 18M6 6l12 12" />
											</svg>
										</button>
									{:else}
										<button
											onclick={() => (confirmDelete = name)}
											class="rounded p-1.5 text-red-600 transition-colors hover:bg-red-50 dark:text-red-400 dark:hover:bg-red-950/20"
											title="Delete profile"
										>
											<svg
												width="14"
												height="14"
												viewBox="0 0 24 24"
												fill="none"
												stroke="currentColor"
												stroke-width="2"
											>
												<path
													d="M3 6h18M19 6v14a2 2 0 01-2 2H7a2 2 0 01-2-2V6m3 0V4a2 2 0 012-2h4a2 2 0 012 2v2"
												/>
											</svg>
										</button>
									{/if}
								</div>
							</div>
						{/each}
					{/if}
				</div>
			</div>

			<div class="flex justify-end gap-3 border-t border-gray-200 pt-4 dark:border-neutral-700">
				<button
					onclick={() => (showProfileModal = false)}
					class="rounded-md px-4 py-2 text-sm font-medium text-gray-700 transition-colors hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-neutral-700"
				>
					Close
				</button>
			</div>
		</div>
	</div>
{/if}

{#if showConfigModal && configuringWidget}
	{@const widgetType = configuringWidget.type as keyof typeof WIDGET_TYPES}
	{@const configSchema = (WIDGET_TYPES[widgetType]?.configSchema || []) as ConfigField[]}
	<div
		role="dialog"
		aria-modal="true"
		class="fixed inset-0 z-[100] flex items-center justify-center"
	>
		<button
			class="fixed inset-0 cursor-default bg-black/50"
			onclick={() => {
				showConfigModal = false;
				configuringWidget = null;
			}}
			in:fade={{ duration: 150 }}
			out:fade={{ duration: 150 }}
			tabindex="-1"
			aria-label="Close dialog"
		></button>

		<div
			class="relative z-10 w-full max-w-md rounded-lg bg-white p-6 shadow-xl dark:bg-neutral-800"
			in:scaleTransition={{ duration: 150, start: 0.96, opacity: 0 }}
			out:scaleTransition={{ duration: 150, start: 0.96, opacity: 0 }}
		>
			<h2 class="mb-4 text-xl font-semibold text-gray-900 dark:text-white">
				Configure {WIDGET_TYPES[widgetType]?.label}
			</h2>

			<div class="space-y-4">
				{#each configSchema as field (field.key)}
					<div>
						<label
							for={field.key}
							class="mb-1 block text-sm font-medium text-gray-700 dark:text-gray-300"
						>
							{field.label}
							{#if field.required}<span class="text-red-500">*</span>{/if}
						</label>

						{#if field.type === 'select'}
							<select
								id={field.key}
								bind:value={configuringWidget.config[field.key]}
								class="w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900 dark:border-neutral-600 dark:bg-neutral-700 dark:text-white"
							>
								<option value={null}>Select {field.label}</option>
								{#each getConfigOptions(field) as option (option.value)}
									<option value={option.value}>{option.label}</option>
								{/each}
							</select>
						{:else if field.type === 'text'}
							<input
								id={field.key}
								type="text"
								bind:value={configuringWidget.config[field.key]}
								placeholder={field.placeholder ?? ''}
								class="w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900 dark:border-neutral-600 dark:bg-neutral-700 dark:text-white"
							/>
						{:else if field.type === 'number'}
							<input
								id={field.key}
								type="number"
								bind:value={configuringWidget.config[field.key]}
								min={field.min}
								max={field.max}
								step={field.step}
								class="w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900 [appearance:textfield] [&::-webkit-inner-spin-button]:appearance-none [&::-webkit-outer-spin-button]:appearance-none dark:border-neutral-600 dark:bg-neutral-700 dark:text-white"
							/>
						{:else if field.type === 'array'}
							<input
								id={field.key}
								type="text"
								value={formatArrayValue(configuringWidget.config[field.key])}
								oninput={(e) => {
									if (configuringWidget) {
										configuringWidget.config[field.key] = parseArrayValue(
											(e.target as HTMLInputElement).value
										);
									}
								}}
								placeholder={field.placeholder ?? 'Comma-separated values'}
								class="w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-sm text-gray-900 dark:border-neutral-600 dark:bg-neutral-700 dark:text-white"
							/>
						{:else if field.type === 'range'}
							<div class="grid grid-cols-2 gap-3">
								<div>
									<label
										for="{field.key}-min"
										class="mb-1 block text-xs text-gray-600 dark:text-gray-400">Min</label
									>
									<input
										id="{field.key}-min"
										type="number"
										value={(configuringWidget.config[field.key] as [number, number])?.[0] ??
											field.min}
										oninput={(e) => {
											const val = parseFloat((e.target as HTMLInputElement).value);
											if (configuringWidget) {
												const range = (configuringWidget.config[field.key] as [number, number]) || [
													field.min ?? 0,
													field.max ?? 100
												];
												configuringWidget.config[field.key] = [val, range[1]];
											}
										}}
										class="w-full rounded-md border border-gray-300 bg-white px-2 py-1.5 text-sm text-gray-900 [appearance:textfield] [&::-webkit-inner-spin-button]:appearance-none [&::-webkit-outer-spin-button]:appearance-none dark:border-neutral-600 dark:bg-neutral-700 dark:text-white"
									/>
								</div>
								<div>
									<label
										for="{field.key}-max"
										class="mb-1 block text-xs text-gray-600 dark:text-gray-400">Max</label
									>
									<input
										id="{field.key}-max"
										type="number"
										value={(configuringWidget.config[field.key] as [number, number])?.[1] ??
											field.max}
										oninput={(e) => {
											const val = parseFloat((e.target as HTMLInputElement).value);
											if (configuringWidget) {
												const range = (configuringWidget.config[field.key] as [number, number]) || [
													field.min ?? 0,
													field.max ?? 100
												];
												configuringWidget.config[field.key] = [range[0], val];
											}
										}}
										class="w-full rounded-md border border-gray-300 bg-white px-2 py-1.5 text-sm text-gray-900 [appearance:textfield] [&::-webkit-inner-spin-button]:appearance-none [&::-webkit-outer-spin-button]:appearance-none dark:border-neutral-600 dark:bg-neutral-700 dark:text-white"
									/>
								</div>
							</div>
						{/if}
					</div>
				{/each}
			</div>

			<div class="mt-6 flex justify-end gap-3">
				<button
					onclick={saveConfig}
					class="rounded-md bg-blue-500 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-blue-600"
				>
					Done
				</button>
			</div>
		</div>
	</div>
{/if}

<style>
	.resize-handle {
		position: absolute;
		background: white;
		border: 2px solid #3b82f6;
		width: 10px;
		height: 10px;
		border-radius: 50%;
		transition: all 0.15s ease;
	}

	:global(.dark) .resize-handle {
		background: #1f2937;
		border-color: #60a5fa;
	}

	.resize-n {
		top: -5px;
		left: 50%;
		transform: translateX(-50%);
		cursor: ns-resize;
	}
	.resize-ne {
		top: -5px;
		right: -5px;
		cursor: nesw-resize;
	}
	.resize-e {
		top: 50%;
		right: -5px;
		transform: translateY(-50%);
		cursor: ew-resize;
	}
	.resize-se {
		bottom: -5px;
		right: -5px;
		cursor: nwse-resize;
	}
	.resize-s {
		bottom: -5px;
		left: 50%;
		transform: translateX(-50%);
		cursor: ns-resize;
	}
	.resize-sw {
		bottom: -5px;
		left: -5px;
		cursor: nesw-resize;
	}
	.resize-w {
		top: 50%;
		left: -5px;
		transform: translateY(-50%);
		cursor: ew-resize;
	}
	.resize-nw {
		top: -5px;
		left: -5px;
		cursor: nwse-resize;
	}

	.resize-handle:hover {
		background: #3b82f6;
		transform: scale(1.25);
	}
	:global(.dark) .resize-handle:hover {
		background: #60a5fa;
	}
	.resize-n:hover,
	.resize-s:hover {
		transform: translateX(-50%) scale(1.25);
	}
	.resize-e:hover,
	.resize-w:hover {
		transform: translateY(-50%) scale(1.25);
	}

	.animate-in {
		animation:
			fadeIn 0.15s ease-out,
			slideDown 0.15s ease-out;
	}

	@keyframes fadeIn {
		from {
			opacity: 0;
		}
		to {
			opacity: 1;
		}
	}

	@keyframes slideDown {
		from {
			transform: translateY(-0.5rem);
		}
		to {
			transform: translateY(0);
		}
	}
</style>
