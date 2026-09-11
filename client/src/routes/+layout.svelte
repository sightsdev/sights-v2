<script lang="ts">
	import About from '$lib/components/popups/About.svelte';
	import Docs from '$lib/components/popups/Docs.svelte';
	import EStop from '$lib/components/popups/EStop.svelte';
	import Logs from '$lib/components/popups/Logs.svelte';
	import Settings from '$lib/components/popups/Settings.svelte';
	import Terminal from '$lib/components/popups/Terminal.svelte';
	import Nav from '$lib/components/shared/Nav.svelte';
	import Toaster from '$lib/components/shared/Toaster.svelte';
	import { setPopupState } from '$lib/stores/popups.svelte';

	import '../app.css';

	setPopupState();

	let { children } = $props();
</script>

<div class="flex h-screen flex-col overflow-hidden">
	<About />
	<EStop />
	<Docs />
	<Logs />
	<Settings />
	<Terminal />
	<Toaster />
	<Nav />
	<main class="flex-1 overflow-hidden bg-white shadow-sm dark:bg-neutral-900">
		{@render children?.()}
	</main>
</div>
