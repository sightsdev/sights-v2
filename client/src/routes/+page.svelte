<script lang="ts">
	import { onMount } from 'svelte';

	import { AppClient, OpenAPI } from '$lib/api';
	import type { SensorConfig } from '$lib/api';
	import GridLayout from '$lib/components/dashboard/GridLayout.svelte';
	import { currentSpeed } from '$lib/stores/currentSpeed.svelte';

	let client: AppClient;
	let cameras = $state<string[]>([]);
	let sensors = $state<Record<string, SensorConfig>>({});
	let loading = $state(true);

	onMount(() => {
		client = new AppClient(OpenAPI);

		// Async data loading
		(async () => {
			try {
				const [camerasData, sensorsData] = await Promise.all([
					client.default.listCamerasCameraGet(),
					client.default.sensorListSensorListGet()
				]);
				cameras = camerasData;
				sensors = sensorsData;
				loading = false;
			} catch (error) {
				console.error('Failed to load data:', error);
				loading = false;
			}
		})();

		window.addEventListener('keydown', handleKeyDown);
		window.addEventListener('keyup', handleKeyUp);

		// Return cleanup function synchronously
		return () => {
			window.removeEventListener('keydown', handleKeyDown);
			window.removeEventListener('keyup', handleKeyUp);
		};
	});

	// Track currently pressed keys
	const pressedKeys = $state(new Set<string>());

	async function handleKeyDown(e: KeyboardEvent): Promise<void> {
		// Skip if user is typing in an input/textarea/editor
		const target = e.target as HTMLElement;
		if (
			target.matches('input, textarea, select') ||
			target.contentEditable === 'true' ||
			target.closest('.editor-wrapper') // CodeMirror editor
		) {
			return;
		}

		// Allow browser zoom with Ctrl/Cmd
		if (e.ctrlKey || e.metaKey) {
			return;
		}

		// Prevent repeating when key is held
		if (pressedKeys.has(e.key)) return;
		pressedKeys.add(e.key);

		// Drive controls
		if (e.key === 'w' || e.key === 'ArrowUp') {
			e.preventDefault();
			await client.default.driveDrivePost({ speed: [$currentSpeed * 125, $currentSpeed * 125] });
		} else if (e.key === 'a' || e.key === 'ArrowLeft') {
			e.preventDefault();
			await client.default.driveDrivePost({ speed: [$currentSpeed * -125, $currentSpeed * 125] });
		} else if (e.key === 's' || e.key === 'ArrowDown') {
			e.preventDefault();
			await client.default.driveDrivePost({
				speed: [$currentSpeed * -125, $currentSpeed * -125]
			});
		} else if (e.key === 'd' || e.key === 'ArrowRight') {
			e.preventDefault();
			await client.default.driveDrivePost({ speed: [$currentSpeed * 125, $currentSpeed * -125] });
		}
		// Arm controls - Use numpad keys specifically
		else if (e.code === 'Numpad1') {
			e.preventDefault();
			await client.default.armMoveArmServoServoNamePost('SHOULDER', { direction: true });
		} else if (e.code === 'Numpad4') {
			e.preventDefault();
			await client.default.armMoveArmServoServoNamePost('SHOULDER', { direction: false });
		} else if (e.code === 'Numpad2') {
			e.preventDefault();
			await client.default.armMoveArmServoServoNamePost('ELBOW', { direction: false });
		} else if (e.code === 'Numpad5') {
			e.preventDefault();
			await client.default.armMoveArmServoServoNamePost('ELBOW', { direction: true });
		} else if (e.code === 'Numpad3') {
			e.preventDefault();
			await client.default.armMoveArmServoServoNamePost('WRISTUD', { direction: false });
		} else if (e.code === 'Numpad6') {
			e.preventDefault();
			await client.default.armMoveArmServoServoNamePost('WRISTUD', { direction: true });
		} else if (e.code === 'Numpad7') {
			e.preventDefault();
			await client.default.armMoveArmServoServoNamePost('WRISTLR', { direction: true });
		} else if (e.code === 'Numpad8') {
			e.preventDefault();
			await client.default.armMoveArmServoServoNamePost('WRISTLR', { direction: false });
		}
		// Claw controls - numpad only
		else if (e.code === 'NumpadAdd') {
			e.preventDefault();
			await client.default.armMoveArmServoServoNamePost('CLAW', { direction: true });
		} else if (e.code === 'NumpadSubtract') {
			e.preventDefault();
			await client.default.armMoveArmServoServoNamePost('CLAW', { direction: false });
		}
		// Arm home/preset - numpad only
		else if (e.code === 'Numpad0') {
			e.preventDefault();
			await client.default.armHomeArmHomePost();
		} else if (e.code === 'NumpadDecimal') {
			e.preventDefault();
			await client.default.armPresetArmPresetPresetPost('drive');
		}
	}

	async function handleKeyUp(e: KeyboardEvent): Promise<void> {
		// Skip if user is typing in an input/textarea/editor
		const target = e.target as HTMLElement;
		if (
			target.matches('input, textarea, select') ||
			target.contentEditable === 'true' ||
			target.closest('.cm-editor')
		) {
			return;
		}

		pressedKeys.delete(e.key);

		if (['w', 'a', 's', 'd', 'ArrowUp', 'ArrowLeft', 'ArrowDown', 'ArrowRight'].includes(e.key)) {
			await client.default.driveStopDriveStopPost();
		}
	}
</script>

{#if loading}
	<div class="flex h-screen items-center justify-center">
		<div class="text-lg dark:text-white">Loading...</div>
	</div>
{:else}
	<GridLayout {cameras} {sensors} />
{/if}
