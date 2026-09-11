<script lang="ts">
	import { AppClient } from '$lib/api';

	const client = new AppClient();
	let { cameraName }: { cameraName: string | null } = $props();
	let imageError = $state(false);

	$effect(() => {
		if (cameraName) {
			imageError = false;
		}
	});

	const handleImageError = (): void => {
		console.log('Image error triggered for:', cameraName);
		imageError = true;
	};

	const handleImageLoad = (): void => {
		console.log('Image loaded successfully for:', cameraName);
		imageError = false;
	};
</script>

<div class="h-full w-full">
	{#if imageError || !cameraName}
		<div
			class="flex h-full w-full flex-col items-center justify-center rounded-md bg-gray-200 p-6 text-center dark:bg-neutral-800"
		>
			<img src="/logo.svg" alt="Camera" class="mb-4 h-32 w-full object-contain dark:text-white" />
			<p class="mt-5 mb-2 text-sm text-red-600 dark:text-red-400">
				Camera: {cameraName || 'Not selected'}
			</p>
			<p class="text-sm text-red-600 dark:text-red-400">No Video Stream Available</p>
		</div>
	{:else}
		<img
			class="h-full w-full rounded-md object-cover"
			src={`${client.request.config.BASE}/camera/${cameraName}/`}
			alt="Camera stream"
			onerror={handleImageError}
			onload={handleImageLoad}
		/>
	{/if}
</div>
