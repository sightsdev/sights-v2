<script lang="ts">
	import {
		ChevronDown,
		Circle,
		CircleGauge,
		Clock,
		ClockArrowUp,
		Cpu,
		FileCode,
		HardDrive,
		List,
		MemoryStick,
		Monitor,
		Moon,
		OctagonX,
		Pencil,
		PencilOff,
		Power,
		RotateCcw,
		Settings,
		Sun,
		Terminal,
		Thermometer,
		Timer
	} from '@lucide/svelte';

	import { onDestroy, onMount } from 'svelte';

	import { AppClient, OpenAPI } from '$lib/api';
	import { addToast } from '$lib/components/shared/Toaster.svelte';
	import { currentSpeed } from '$lib/stores/currentSpeed.svelte';
	import { isEditMode } from '$lib/stores/editMode.svelte';
	import { getPopupState } from '$lib/stores/popups.svelte';
	import { systemStore } from '$lib/stores/systemStore.svelte';
	import { themeStore } from '$lib/stores/themeStore.svelte';

	import Button from './Button.svelte';

	const popups = getPopupState();

	let { onConfigChange = () => {} }: { onConfigChange?: (config: string) => void } = $props();

	const client = new AppClient(OpenAPI);

	// Lifecycle
	let unsubscribe: (() => void) | undefined;
	onMount(() => {
		unsubscribe = systemStore.subscribe();

		loadConfigs();
		loadActiveConfig();

		const clockInterval = setInterval(() => {
			currentTime = new Date();
		}, 1000);
		return () => clearInterval(clockInterval);
	});
	onDestroy(() => {
		unsubscribe?.();
		themeStore.destroy();
	});

	// State
	let showPowerMenu = $state(false);
	let showConfigMenu = $state(false);
	let showSpeedMenu = $state(false);
	let currentConfig = $state('Loading...');
	let availableConfigs = $state<string[]>([]);
	let timerRunning = $state(false);
	let timerSeconds = $state(300);
	let timerInterval: ReturnType<typeof setInterval> | null = null;
	let speedMenuTimeout: ReturnType<typeof setTimeout> | null = null;
	let currentTime = $state(new Date());

	// Constants
	const speedLevels = [1, 2, 3, 4, 5, 6, 7, 8];

	// Speed
	const speedProgress = $derived(($currentSpeed / 8) * 100);
	const speedColor = $derived.by(() => {
		if ($currentSpeed >= 8) return 'bg-red-500 text-red-700 dark:text-red-400';
		if ($currentSpeed >= 6) return 'bg-yellow-500 text-yellow-700 dark:text-yellow-400';
		return 'bg-green-500 text-green-700 dark:text-green-400';
	});

	// Systen Info
	const getColor = (val: number, warn: number, danger: number): string => {
		if (val < warn) return 'text-green-600 dark:text-green-500';
		if (val < danger) return 'text-yellow-600 dark:text-yellow-500';
		return 'text-red-600 dark:text-red-500';
	};

	const connectionColor = $derived.by(
		() =>
			({
				connected: 'text-orange-600 dark:text-orange-500',
				connecting: 'text-yellow-600 dark:text-yellow-500',
				disconnected: 'text-red-600 dark:text-red-500'
			})[systemStore.connectionStatus] || 'text-gray-600 dark:text-gray-400'
	);

	const cpuColor = $derived.by(() => getColor(systemStore.cpuPercent || 0, 60, 85));
	const tempColor = $derived.by(() => getColor(systemStore.temperature || 0, 70, 85));
	const ramColor = $derived.by(() => getColor(systemStore.memoryPercent || 0, 70, 90));
	const diskColor = $derived.by(() => getColor(systemStore.diskPercent || 0, 75, 90));

	// Timer
	const timerDisplay = $derived.by(() => {
		const m = Math.floor(timerSeconds / 60);
		const s = timerSeconds % 60;
		return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
	});

	// Clock
	const utcTime = $derived.by(() => {
		const h = currentTime.getUTCHours();
		const m = currentTime.getUTCMinutes();
		const s = currentTime.getUTCSeconds();
		return `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
	});

	// Theme
	const ThemeIcon = $derived(
		themeStore.mode === 'system' ? Monitor : themeStore.isDark ? Moon : Sun
	);
	const themeTitle = $derived.by(
		() =>
			({
				system: 'Switch to Light Mode',
				light: 'Switch to Dark Mode',
				dark: 'Use System Default'
			})[themeStore.mode] || 'Toggle Theme'
	);

	const EditIcon = $derived($isEditMode ? PencilOff : Pencil);

	// Formats the config name to look better (aka Pretty Name)
	function formatConfigName(filename: string): string {
		return filename.replace('.toml', '').replace(/_/g, ' ').replace(/-/g, ' ');
	}

	// Config Functions
	async function loadConfigs(): Promise<void> {
		try {
			const response = await fetch('/api/config/list');
			const data = await response.json();
			availableConfigs = data.configs || [];
		} catch (error) {
			console.error('Failed to load configs:', error);
			availableConfigs = [];
		}
	}

	async function loadActiveConfig(): Promise<void> {
		try {
			const response = await fetch('/api/config/active');
			const data = await response.json();
			currentConfig = data.active_config_file || 'Unknown';
		} catch (error) {
			console.error('Failed to load active config:', error);
			currentConfig = 'Unknown';
		}
	}

	async function switchConfig(configFile: string): Promise<void> {
		try {
			const response = await fetch('/api/config/switch', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ file: configFile })
			});

			if (!response.ok) {
				const error = await response.json();
				console.error('Failed to switch config:', error);
				addToast({
					data: {
						title: 'Failed to switch config',
						description: error.detail || 'Unknown error',
						variant: 'error'
					}
				});
				return;
			}

			currentConfig = configFile;
			showConfigMenu = false;
			onConfigChange(configFile);
		} catch (error) {
			console.error('Failed to switch config:', error);
			addToast({
				data: {
					title: 'Failed to switch config',
					description: 'Check logs for errors',
					variant: 'error'
				}
			});
		}
	}

	// Functions
	function toggleTimer(): void {
		if (timerRunning) {
			if (timerInterval) clearInterval(timerInterval);
			timerInterval = null;
			timerRunning = false;
		} else {
			timerRunning = true;
			timerInterval = setInterval(() => {
				if (timerSeconds > 0) timerSeconds--;
				else {
					if (timerInterval) clearInterval(timerInterval);
					timerInterval = null;
					timerRunning = false;
				}
			}, 1000);
		}
	}

	function selectSpeed(speed: number): void {
		$currentSpeed = speed;
		showSpeedMenu = true;
		if (speedMenuTimeout) clearTimeout(speedMenuTimeout);
		speedMenuTimeout = setTimeout(() => (showSpeedMenu = false), 1500);
	}

	async function handlePowerOff(): Promise<void> {
		const res = await client.default.powerPoweroffPost();
		if (!res.ok) {
			addToast({
				data: {
					title: 'Power off Triggered',
					description: 'Robot is powering off',
					variant: 'success'
				}
			});
		}
		showPowerMenu = false;
	}

	async function handleReboot(): Promise<void> {
		const res = await client.default.rebootRebootPost();
		if (!res.ok) {
			addToast({
				data: {
					title: 'Reboot Triggered',
					description: 'Robot is rebooting',
					variant: 'success'
				}
			});
		}
		showPowerMenu = false;
	}

	function handleClickOutside(e: MouseEvent): void {
		const target = e.target as HTMLElement;
		if (showPowerMenu && !target.closest('.power-menu')) showPowerMenu = false;
		if (showConfigMenu && !target.closest('.config-menu')) showConfigMenu = false;
		if (showSpeedMenu && !target.closest('.speed-menu') && !speedMenuTimeout) showSpeedMenu = false;
	}

	function handleKeyPress(e: KeyboardEvent): void {
		const target = e.target as HTMLElement;
		if (
			target.matches('input, textarea, select') ||
			target.contentEditable === 'true' ||
			target.closest('.editor-wrapper')
		) {
			return;
		}

		if (e.ctrlKey || e.metaKey) {
			return;
		}

		const key = e.key.toLowerCase();
		if (key === 't') {
			e.preventDefault();
			toggleTimer();
		} else if (['+', '='].includes(key) && $currentSpeed < 8) {
			e.preventDefault();
			selectSpeed($currentSpeed + 1);
		} else if (['-', '_'].includes(key) && $currentSpeed > 1) {
			e.preventDefault();
			selectSpeed($currentSpeed - 1);
		}
	}

	function toggleEditMode(): void {
		$isEditMode = !$isEditMode;
	}
</script>

<svelte:window on:click={handleClickOutside} on:keydown={handleKeyPress} />

<nav
	class="border-b border-gray-200 bg-white shadow-sm dark:border-neutral-700 dark:bg-neutral-900"
>
	<div class="px-4">
		<div class="flex h-16 items-center gap-6">
			<!-- Left -->
			<div class="flex flex-1 items-center gap-3 overflow-hidden">
				<div class="hidden items-center gap-3 overflow-hidden text-sm lg:flex">
					<div class="flex items-center gap-1 {cpuColor} shrink-0" title="CPU Usage">
						<Cpu size={15} />
						<span class="inline-block font-mono tabular-nums text-right min-w-[3ch]">
							{systemStore.cpuPercent.toFixed(0)}%
						</span>
					</div>
					<div class="flex items-center gap-1 {tempColor} shrink-0" title="CPU Temperature">
						<Thermometer size={15} />
						<span class="inline-block font-mono tabular-nums text-right min-w-[4ch]">
							{systemStore.temperature?.toFixed(0) ?? '--'}°C
						</span>
					</div>
					<div
						class="flex items-center gap-1 {ramColor} shrink-0"
						title="RAM Usage: {systemStore.memoryPercent.toFixed(0)}%"
					>
						<MemoryStick size={15} />
						<span class="inline-block font-mono tabular-nums text-right min-w-[5ch]">
							{systemStore.memoryUsedGB.toFixed(1)}GB
						</span>
					</div>
					<div
						class="flex items-center gap-1 {diskColor} shrink-0"
						title="Disk Usage: {systemStore.diskPercent.toFixed(0)}%"
					>
						<HardDrive size={15} />
						<span class="inline-block font-mono tabular-nums text-right min-w-[4ch]">
							{systemStore.diskUsedGB.toFixed(0)}GB
						</span>
					</div>
					<div
						class="flex shrink-0 items-center gap-1 text-gray-600 dark:text-gray-400"
						title="Uptime"
					>
						<ClockArrowUp size={15} />
						<span class="inline-block font-mono tabular-nums whitespace-nowrap text-right">
							{systemStore.uptimeFormatted}
						</span>
					</div>
				</div>

				<div class="hidden h-6 w-px shrink-0 bg-gray-300 lg:block dark:bg-neutral-700"></div>

				<div class="hidden items-center gap-3 overflow-hidden lg:flex">
					<div
						class="flex shrink-0 items-center gap-1.5 text-sm text-gray-600 dark:text-gray-400"
						title="UTC Time"
					>
						<Clock size={16} />
						<span class="font-mono whitespace-nowrap tabular-nums">{utcTime} UTC</span>
					</div>

					<button
						class="flex shrink-0 items-center gap-1.5 text-sm transition-colors {timerRunning
							? 'text-green-600 dark:text-green-500'
							: 'text-gray-600 dark:text-gray-400'} hover:text-orange-600 dark:hover:text-orange-500"
						title="Timer (Press T)"
						onclick={toggleTimer}
					>
						<Timer size={16} />
						<span class="font-mono tabular-nums">{timerDisplay}</span>
					</button>
				</div>
			</div>

			<!-- Center -->
			<div class="flex shrink-0 justify-center">
				<button
					onclick={() => popups.open('about')}
					class="whitespace-nowrap transition-opacity hover:opacity-80"
				>
					<span class="font-medium {connectionColor} ">SIGHTS</span>
					<span class="font-medium text-gray-900 dark:text-white">Interface</span>
				</button>
			</div>

			<!-- Right -->
			<div class="flex flex-1 items-center justify-end gap-2">
				<div class="speed-menu relative shrink-0">
					<button
						class="relative h-8.5 w-18 overflow-hidden rounded-md border border-gray-300 px-3 py-1.5 transition-all hover:border-gray-400 dark:border-neutral-600 dark:hover:border-neutral-500"
						title="Drive Speed"
						onclick={(e: MouseEvent) => {
							e.stopPropagation();
							if (speedMenuTimeout) {
								clearTimeout(speedMenuTimeout);
								speedMenuTimeout = null;
							}
							showSpeedMenu = !showSpeedMenu;
						}}
					>
						<div
							class="absolute inset-0 transition-all duration-300 {speedColor.split(
								' '
							)[0]} opacity-15"
							style="width: {speedProgress}%"
						></div>
						<div
							class="relative flex w-full items-center justify-center gap-2 {speedColor
								.split(' ')
								.slice(1)
								.join(' ')}"
						>
							<CircleGauge size={16} />
							<span class="text-xs font-medium lg:inline">{$currentSpeed}</span>
						</div>
					</button>

					{#if showSpeedMenu}
						<div
							class="animate-in absolute right-0 z-50 mt-2 w-80 rounded-lg bg-white shadow-xl ring-1 ring-black/5 dark:bg-neutral-800 dark:ring-white/10"
						>
							<div class="p-4">
								<div class="mb-3 flex items-center justify-between gap-4">
									<div class="text-xs whitespace-nowrap text-gray-500 dark:text-gray-400">
										Drive Speed
									</div>
									<div class="text-2xl font-bold {speedColor.split(' ').slice(1).join(' ')}">
										{$currentSpeed}
									</div>
									<div class="text-xs whitespace-nowrap text-gray-400 dark:text-gray-500">
										+/- keys
									</div>
								</div>
								<div
									class="flex h-2 gap-0.5 overflow-hidden rounded-full bg-gray-200 dark:bg-neutral-700"
								>
									{#each speedLevels as speed (speed)}
										<button
											class="flex-1 rounded-sm transition-all duration-200 hover:opacity-70 {speed <=
											$currentSpeed
												? $currentSpeed >= 8
													? 'bg-red-500'
													: $currentSpeed >= 6
														? 'bg-yellow-500'
														: 'bg-green-500'
												: 'bg-gray-300 dark:bg-neutral-600'}"
											onclick={() => selectSpeed(speed)}
											title="Speed {speed}"
										></button>
									{/each}
								</div>
							</div>
						</div>
					{/if}
				</div>

				<div class="config-menu relative shrink-0">
					<Button
						variant="outline"
						size="md"
						onclick={(e: MouseEvent) => {
							e.stopPropagation();
							showConfigMenu = !showConfigMenu;
						}}
						title="Configuration"
					>
						<FileCode size={16} />
						<span class="hidden max-w-25 min-w-25 truncate text-xs lg:inline"
							>{formatConfigName(currentConfig)}</span
						>
						<ChevronDown
							size={14}
							class="transition-transform duration-200 {showConfigMenu ? 'rotate-180' : ''}"
						/>
					</Button>

					{#if showConfigMenu}
						<div
							class="animate-in absolute right-0 z-50 mt-2 w-56 rounded-lg bg-white shadow-xl ring-1 ring-black/5 dark:bg-neutral-800 dark:ring-white/10"
						>
							<div class="p-1">
								{#if availableConfigs.length === 0}
									<div class="px-3 py-2 text-sm text-gray-500 dark:text-gray-400">
										No configs found
									</div>
								{:else}
									{#each availableConfigs as config (config)}
										<button
											class="flex w-full items-center justify-between gap-3 rounded-md px-3 py-2 text-sm transition-colors hover:bg-gray-100 dark:hover:bg-neutral-700 {config ===
											currentConfig
												? 'bg-orange-50 text-orange-700 dark:bg-orange-900/20 dark:text-orange-400'
												: 'text-gray-700 dark:text-gray-300'}"
											onclick={() => switchConfig(config)}
										>
											<span class="truncate">{formatConfigName(config)}</span>
											{#if config === currentConfig}
												<Circle size={6} fill="currentColor" />
											{/if}
										</button>
									{/each}
								{/if}
							</div>
						</div>
					{/if}
				</div>

				<div class="h-6 w-px shrink-0 bg-gray-300 dark:bg-neutral-700"></div>

				<div class="flex shrink-0 items-center gap-1">
					<Button variant="ghost" size="md" onclick={() => popups.open('terminal')} title="Terminal"
						><Terminal size={18} /></Button
					>
					<Button variant="ghost" size="md" onclick={() => popups.open('logs')} title="Logs"
						><List size={18} /></Button
					>
					<Button variant="ghost" size="md" title="Settings" onclick={() => popups.open('settings')}
						><Settings size={18} /></Button
					>
					<Button variant="ghost" size="md" onclick={toggleEditMode} title="Edit Layout"
						><EditIcon size={18} /></Button
					>
					<Button variant="ghost" size="md" onclick={() => themeStore.toggle()} title={themeTitle}
						><ThemeIcon size={18} /></Button
					>
				</div>

				<div class="h-6 w-px shrink-0 bg-gray-300 dark:bg-neutral-700"></div>

				<div class="power-menu relative shrink-0">
					<Button
						variant="danger"
						size="md"
						onclick={(e: MouseEvent) => {
							e.stopPropagation();
							showPowerMenu = !showPowerMenu;
						}}
						title="Power"
					>
						<Power size={18} />
						<ChevronDown
							size={14}
							class="transition-transform duration-200 {showPowerMenu ? 'rotate-180' : ''}"
						/>
					</Button>

					{#if showPowerMenu}
						<div
							class="animate-in absolute right-0 z-50 mt-2 w-48 rounded-lg bg-white shadow-xl ring-1 ring-black/5 dark:bg-neutral-800 dark:ring-white/10"
						>
							<div class="p-1">
								<button
									class="flex w-full items-center gap-3 rounded-md px-3 py-2 text-sm text-gray-700 transition-colors hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-neutral-700"
									onclick={handlePowerOff}
								>
									<Power size={16} />Power off
								</button>
								<button
									class="flex w-full items-center gap-3 rounded-md px-3 py-2 text-sm text-gray-700 transition-colors hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-neutral-700"
									onclick={handleReboot}
								>
									<RotateCcw size={16} />Reboot
								</button>
								<button
									class="flex w-full items-center gap-3 rounded-md px-3 py-2 text-sm text-gray-700 transition-colors hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-neutral-700"
									onclick={() => popups.open('estop')}
								>
									<OctagonX size={16} />Emergency Stop
								</button>
							</div>
						</div>
					{/if}
				</div>
			</div>
		</div>
	</div>
</nav>

<style>
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
