<script lang="ts">
	import { page } from '$app/stores'; // Use $app/stores instead of $app/state
	import { goto } from '$app/navigation'; // Import goto for programmatic navigation
	import '../app.css';
	import { Dropdown, DropdownItem } from 'flowbite-svelte';
	import { ChevronDownOutline, HomeOutline } from 'flowbite-svelte-icons';
	import { fade, fly } from 'svelte/transition';
	let { children } = $props();

	const months = [
		'January',
		'February',
		'March',
		'April',
		'May',
		'June',
		'July',
		'August',
		'September',
		'October',
		'November',
		'December'
	];

	function reloadOnRecord() {
		// Navigate to `/record` without query parameters if they exist
		console.log('reloadOnRecord');
		// get current URL
		const url = new URL(window.location.href);
		// check if there are query params
		if (url.searchParams.size > 0) {
			// remove query params
			url.search = '';
			window.location.href = url.toString();
		}
	}

	async function generateReport(month: string) {
		try {
			const response = await fetch(`http://localhost:8100/generate_reports/${month.toLowerCase()}`);
			if (!response.ok) {
				throw new Error('Failed to generate report');
			}

			const reader = response.body?.getReader();
			const contentDisposition = response.headers.get('Content-Disposition');
			const filename =
				contentDisposition?.split('filename=')[1].replace(/"/g, '') ||
				`${month.toLowerCase()}_reports.zip`;

			if (!reader) {
				throw new Error('No reader available');
			}

			const chunks = [];
			while (true) {
				const { done, value } = await reader.read();
				if (done) break;
				chunks.push(value);
			}

			const blob = new Blob(chunks, { type: 'application/zip' });
			const url = window.URL.createObjectURL(blob);
			const a = document.createElement('a');
			a.href = url;
			a.download = filename;
			document.body.appendChild(a);
			a.click();
			window.URL.revokeObjectURL(url);
			document.body.removeChild(a);
		} catch (error) {
			console.error('Error generating report:', error);
		}
	}
</script>

<!-- Top navigation bar -->
<header
	class="bg-blue-500 p-4 text-white dark:bg-gray-800"
	in:fly={{ y: -20, duration: 300 }}
	out:fly={{ y: -20, duration: 300 }}
>
	<nav class="container mx-auto flex items-center justify-between">
		<a
			href="/"
			class="flex items-center rounded px-4 py-2 text-xl font-semibold transition-colors hover:bg-blue-600"
		>
			<HomeOutline class="mr-2 h-6 w-6" />
			Genlog
		</a>
		<ul class="flex space-x-6">
			<li class="relative">
				<a
					href="/record"
					onclick={reloadOnRecord}
					class="flex items-center rounded px-4 py-2 transition-colors hover:bg-blue-600"
				>
					Record
					<span class="ms-2 w-4"></span>
				</a>
			</li>
			<li class="relative">
				<button class="flex items-center rounded px-4 py-2 transition-colors hover:bg-blue-600">
					View
					<ChevronDownOutline class="ms-2 h-4 w-4" />
				</button>
				<Dropdown>
					<DropdownItem href="/viewRecord">Record</DropdownItem>
					<DropdownItem href="/viewReport">Report</DropdownItem>
				</Dropdown>
			</li>
			<li class="relative">
				<button class="flex items-center rounded px-4 py-2 transition-colors hover:bg-blue-600">
					Export
					<ChevronDownOutline class="ms-2 h-4 w-4" />
				</button>
				<Dropdown>
					{#each months as month}
						<DropdownItem on:click={() => generateReport(month)}>{month}</DropdownItem>
					{/each}
				</Dropdown>
			</li>
		</ul>
	</nav>
</header>

<main in:fade={{ duration: 300 }} out:fade={{ duration: 300 }}>
	{@render children()}
</main>
