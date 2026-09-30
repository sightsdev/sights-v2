<script lang="ts">
	import { ChevronDown, FileCode, History } from '@lucide/svelte';

	import { fade, scale } from 'svelte/transition';

	import TomlEditor from '$lib/components/shared/Editor.svelte';
	import { addToast } from '$lib/components/shared/Toaster.svelte';
	import { getPopupState } from '$lib/stores/popups.svelte';
	import { themeStore } from '$lib/stores/themeStore.svelte';

	const popups = getPopupState();

	let dialog = $state<HTMLDialogElement>();
	let configContent = $state('');
	let loading = $state(true);

	let currentConfig = $state('');
	let availableConfigs = $state<string[]>([]);
	let showConfigMenu = $state(false);
	let backups = $state<Array<{ filename: string; timestamp: string; size: number }>>([]);
	let showBackupMenu = $state(false);
	let isInitialized = $state(false);

	function formatConfigName(filename: string): string {
		return filename.replace('.toml', '').replace(/[_-]/g, ' ');
	}

	function formatFileSize(bytes: number): string {
		if (bytes < 1024) return `${bytes} B`;
		if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
		return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
	}

	async function loadActiveConfig() {
		const res = await fetch('/api/config/active');
		const data = await res.json();
		currentConfig = data.active_config_file || 'Unknown';
	}

	async function loadConfigs() {
		const res = await fetch('/api/config/list');
		const data = await res.json();
		availableConfigs = data.configs || [];
	}

	async function loadConfigFile() {
		loading = true;
		try {
			const res = await fetch('/api/config/file');
			const data = await res.json();
			configContent = data.content || '';
		} finally {
			loading = false;
		}
	}

	async function loadBackups() {
		const res = await fetch('/api/config/backups');
		const data = await res.json();
		backups = data.backups || [];
	}

	async function switchConfig(configFile: string) {
		const res = await fetch('/api/config/switch', {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ file: configFile })
		});

		if (!res.ok) {
			const err = await res.json();
			addToast({
				data: { title: 'Failed to switch config', description: err.detail, variant: 'error' }
			});
			return;
		}

		currentConfig = configFile;
		showConfigMenu = false;
		await loadConfigFile();
		await loadBackups();

		addToast({
			data: {
				title: 'Config switched',
				description: `Now using ${formatConfigName(configFile)}`,
				variant: 'success'
			}
		});
	}

	async function restoreBackup(backupFilename: string) {
		const res = await fetch(`/api/config/backup/${backupFilename}`);
		const data = await res.json();
		configContent = data.content || '';
		showBackupMenu = false;
		addToast({
			data: { title: 'Backup loaded', description: 'Review and save to apply.', variant: 'success' }
		});
	}

	async function saveSettings() {
		const res = await fetch('/api/config/update', {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({ content: configContent })
		});
		if (!res.ok) {
			const err = await res.json();
			addToast({ data: { title: 'Save failed', description: err.detail, variant: 'error' } });
			return;
		}
		await loadBackups();
		addToast({
			data: {
				title: 'Configuration saved',
				description: 'Settings applied successfully.',
				variant: 'success'
			}
		});
		popups.close();
	}

	function close() {
		showConfigMenu = false;
		showBackupMenu = false;
		popups.close();
	}

	function handleClickOutside(e: MouseEvent) {
		const target = e.target as HTMLElement;
		if (showConfigMenu && !target.closest('.config-dropdown')) showConfigMenu = false;
		if (showBackupMenu && !target.closest('.backup-dropdown')) showBackupMenu = false;
	}

	$effect(() => {
		if (popups.isOpen('settings') && !isInitialized) {
			dialog?.showModal();
			isInitialized = true;
			(async () => {
				await Promise.all([loadActiveConfig(), loadConfigs(), loadConfigFile(), loadBackups()]);
			})();
		} else if (!popups.isOpen('settings') && isInitialized) {
			dialog?.close();
			isInitialized = false;
		}
	});
</script>

<svelte:window onclick={handleClickOutside} />

{#if popups.isOpen('settings')}
	<dialog
		bind:this={dialog}
		class="fixed inset-0 z-50 m-0 flex h-screen w-screen items-center justify-center bg-transparent p-0"
		onclose={close}
	>
		<button
			class="fixed inset-0 bg-black/50 cursor-default"
			onclick={close}
			in:fade={{ duration: 150 }}
			out:fade={{ duration: 150 }}
			tabindex="-1"
			aria-label="Close dialog"
		></button>

		<div
			class="relative z-10 flex h-[90vh] w-[90vw] max-w-5xl flex-col overflow-hidden rounded-lg border border-gray-200 bg-white shadow-2xl dark:border-neutral-700 dark:bg-neutral-900"
			in:scale={{ duration: 150, start: 0.96, opacity: 0 }}
			out:scale={{ duration: 150, start: 0.96, opacity: 0 }}
		>
			<!-- Header -->
			<div
				class="flex items-center justify-between border-b border-gray-200 px-6 py-4 dark:border-neutral-700"
			>
				<h2 class="text-xl font-semibold text-gray-900 dark:text-white">Settings</h2>
				<div class="flex items-center gap-2">
					<!-- Config Switcher -->
					<div class="config-dropdown relative">
						<button
							onclick={(e) => {
								e.stopPropagation();
								showConfigMenu = !showConfigMenu;
								showBackupMenu = false;
							}}
							class="flex items-center gap-2 rounded-md border border-gray-300 px-3 py-1.5 text-sm transition-colors hover:bg-gray-50 dark:border-neutral-600 dark:hover:bg-neutral-800 dark:text-white text-black"
							title="Switch Configuration"
						>
							<FileCode size={16} />
							<span class="max-w-[150px] truncate">{formatConfigName(currentConfig)}</span>
							<ChevronDown
								size={14}
								class={showConfigMenu ? 'rotate-180 transition-transform' : 'transition-transform'}
							/>
						</button>

						{#if showConfigMenu}
							<div
								class="absolute right-0 top-full z-50 mt-2 w-64 rounded-lg border border-gray-200 bg-white shadow-xl dark:border-neutral-700 dark:bg-neutral-800"
							>
								<div class="max-h-80 overflow-y-auto p-1">
									{#each availableConfigs as config (config)}
										<button
											onclick={() => switchConfig(config)}
											class="flex w-full items-center justify-between gap-2 rounded-md px-3 py-2 text-left text-sm transition-colors hover:bg-gray-100 dark:hover:bg-neutral-700 {config ===
											currentConfig
												? '-50 text-orange-700 dark:bg-orange-900/20 dark:text-orange-400'
												: 'text-gray-700 dark:text-gray-300'}"
										>
											<span class="truncate">{formatConfigName(config)}</span>
											{#if config === currentConfig}
												<div class="h-2 w-2 rounded-full bg-orange-600"></div>
											{/if}
										</button>
									{/each}
								</div>
							</div>
						{/if}
					</div>

					<!-- Backups -->
					<div class="backup-dropdown relative">
						<button
							onclick={(e) => {
								e.stopPropagation();
								showBackupMenu = !showBackupMenu;
								showConfigMenu = false;
							}}
							class="flex items-center gap-2 rounded-md border border-gray-300 px-3 py-1.5 text-sm transition-colors hover:bg-gray-50 dark:border-neutral-600 dark:hover:bg-neutral-800 dark:text-white text-black"
							title="Restore from Backup"
						>
							<History size={16} />
							<span>Backups</span>
							<ChevronDown
								size={14}
								class={showBackupMenu ? 'rotate-180 transition-transform' : 'transition-transform'}
							/>
						</button>

						{#if showBackupMenu}
							<div
								class="absolute right-0 top-full z-50 mt-2 w-80 rounded-lg border border-gray-200 bg-white shadow-xl dark:border-neutral-700 dark:bg-neutral-800"
							>
								<div class="max-h-80 overflow-y-auto p-1">
									{#each backups as backup (backup.filename)}
										<button
											onclick={() => restoreBackup(backup.filename)}
											class="flex w-full flex-col items-start gap-1 rounded-md px-3 py-2 text-left text-sm transition-colors hover:bg-gray-100 dark:hover:bg-neutral-700"
										>
											<div class="flex w-full items-center justify-between gap-2">
												<span class="font-medium text-gray-900 dark:text-white"
													>{backup.timestamp}</span
												>
												<span class="text-xs text-gray-500 dark:text-gray-400"
													>{formatFileSize(backup.size)}</span
												>
											</div>
											<span class="text-xs text-gray-500 dark:text-gray-400">{backup.filename}</span
											>
										</button>
									{/each}
								</div>
							</div>
						{/if}
					</div>

					<div class="h-6 w-px bg-gray-300 dark:bg-neutral-700"></div>

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
			</div>

			<!-- Content -->
			<div class="flex-1 overflow-hidden p-6">
				{#if loading}
					<div class="flex h-full items-center justify-center text-gray-500 dark:text-gray-400">
						<svg class="h-5 w-5 animate-spin" viewBox="0 0 24 24" fill="none">
							<circle
								class="opacity-25"
								cx="12"
								cy="12"
								r="10"
								stroke="currentColor"
								stroke-width="4"
							></circle>
							<path
								class="opacity-75"
								fill="currentColor"
								d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
							></path>
						</svg>
						<span class="ml-3">Loading configuration...</span>
					</div>
				{:else}
					<TomlEditor bind:value={configContent} isDark={themeStore.isDark} />
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
						class="rounded-md border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 dark:border-neutral-600 dark:text-gray-300 dark:hover:bg-neutral-800"
					>
						Cancel
					</button>
					<button
						onclick={saveSettings}
						disabled={loading}
						class="rounded-md bg-orange-600 px-4 py-2 text-sm font-medium text-white hover:bg-orange-700 disabled:opacity-50 disabled:cursor-not-allowed"
					>
						Save Configuration
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
