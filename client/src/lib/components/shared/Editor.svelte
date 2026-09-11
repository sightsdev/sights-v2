<script lang="ts">
	import { onDestroy, onMount } from 'svelte';

	import { type PrismEditor, createEditor } from 'prism-code-editor';
	import { indentGuides } from 'prism-code-editor/guides';
	import 'prism-code-editor/layout.css';
	import { matchBrackets } from 'prism-code-editor/match-brackets';
	import 'prism-code-editor/prism/languages/toml';
	import 'prism-code-editor/scrollbar.css';
	import prismDarkCss from 'prism-themes/themes/prism-one-dark.css?inline';
	import prismLightCss from 'prism-themes/themes/prism-one-light.css?inline';

	interface Props {
		value: string;
		isDark: boolean;
		onchange?: (value: string) => void;
	}

	let { value = $bindable(''), isDark = false, onchange }: Props = $props();

	let editorContainer = $state<HTMLDivElement>();
	let editor = $state<PrismEditor>();
	let themeStyleElement: HTMLStyleElement | null = null;

	function initEditor() {
		if (!editorContainer) return;

		if (editor) {
			editor.remove();
		}

		// Inject the appropriate theme CSS
		if (themeStyleElement) {
			themeStyleElement.remove();
		}
		themeStyleElement = document.createElement('style');
		themeStyleElement.textContent = isDark ? prismDarkCss : prismLightCss;
		document.head.appendChild(themeStyleElement);

		editor = createEditor(
			editorContainer,
			{
				language: 'toml',
				value: value,
				lineNumbers: true,
				wordWrap: true,
				tabSize: 2
			},
			matchBrackets(),
			indentGuides()
		);

		const textarea = editorContainer.querySelector('textarea');
		if (textarea) {
			textarea.addEventListener('input', () => {
				value = textarea.value;
				onchange?.(textarea.value);
			});
		}
	}

	$effect(() => {
		if (editor && editorContainer) {
			const textarea = editorContainer.querySelector('textarea');
			if (textarea && textarea.value !== value) {
				textarea.value = value;
			}
		}
	});

	onMount(() => {
		initEditor();
	});

	onDestroy(() => {
		if (editor) {
			editor.remove();
		}
		if (themeStyleElement) {
			themeStyleElement.remove();
		}
	});
</script>

<div
	class="h-full overflow-auto rounded-md border border-gray-300 bg-white dark:border-neutral-700 dark:bg-neutral-800"
>
	<div bind:this={editorContainer} class="h-full editor-wrapper text-black dark:text-white"></div>
</div>

<style>
	/* Editor styling */
	:global(.editor-wrapper .prism-code-editor) {
		font-family: 'Fira Code', 'Fira Mono', 'Monaco', 'Courier New', monospace;
		font-size: 13px;
		padding: 10px;
	}

	/* Caret and selection styling */
	:global(.editor-wrapper textarea) {
		caret-color: #528bff !important;
	}

	:global(.editor-wrapper textarea::selection),
	:global(.editor-wrapper .token::selection) {
		background-color: rgba(82, 139, 255, 0.3) !important;
	}

	/* Dark mode caret - slightly brighter blue */
	:global(.dark .editor-wrapper textarea) {
		caret-color: #61afef !important;
	}

	:global(.dark .editor-wrapper textarea::selection),
	:global(.dark .editor-wrapper .token::selection) {
		background-color: rgba(97, 175, 239, 0.3) !important;
	}
</style>
