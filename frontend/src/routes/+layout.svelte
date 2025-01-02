<script lang="ts">
	import '../app.css';
	import { Dropdown, DropdownItem, AccordionItem, Accordion } from 'flowbite-svelte';
	import { ChevronDownOutline, HomeOutline } from 'flowbite-svelte-icons';
	let { children } = $props();
	import { Button, DropdownDivider } from 'flowbite-svelte';
  import {  ChevronRightOutline } from 'flowbite-svelte-icons';
	import { onMount, onDestroy } from 'svelte';
	import { fade } from 'svelte/transition';
	import { browser } from '$app/environment';

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

	let downloadOptions = ['CSV', 'Excel', 'ZIP'];

	function showDownloadOptions(month: string) {
		return downloadOptions.map((option) => ({
			label: option
			// onclick: () => generateReport(month, option.toLowerCase())
		}));
	}

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

	async function generateReport(month, option) {
		try {
			// Construct the URL based on the selected month and option
			const response = await fetch(`http://localhost:8100/generate_reports/${month.toLowerCase()}/${option.toLowerCase()}`);
			if (!response.ok) {
				throw new Error('Failed to generate report');
			}

			// Get the content disposition header to determine the filename
			const contentDisposition = response.headers.get('Content-Disposition');
			const filename = contentDisposition
				? contentDisposition.split('filename=')[1].replace(/"/g, '')
				: `${month.toLowerCase()}_${option.toLowerCase()}_report`;

			// Determine the MIME type and file extension based on the option
			let mimeType;
			let fileExtension;
			console.log(option);
			if (option === 'csv') {
				mimeType = 'application/zip';
				fileExtension = 'zip';
			} else if (option === 'excel') {
				mimeType = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet';
				fileExtension = 'xlsx';
			} else if (option === 'zip') {
				mimeType = 'application/zip';
				fileExtension = 'zip';
			} else {
				throw new Error('Unsupported report option');
			}

			// Read the response body as a Blob
			const blob = await response.blob();

			// Create a download link and trigger the download
			const url = window.URL.createObjectURL(blob);
			const a = document.createElement('a');
			a.href = url;
			a.download = `${filename}.${fileExtension}`;
			document.body.appendChild(a);
			a.click();
			window.URL.revokeObjectURL(url);
			document.body.removeChild(a);
		} catch (error) {
			console.error('Error generating report:', error);
		}
	}


// Helper function to determine the file extension based on the option
function getFileExtension(option) {
  switch (option.toLowerCase()) {
    case 'csv':
      return 'csv';
    case 'xlsx':
      return 'xlsx';
    case 'zip':
      return 'zip';
    default:
			return 'txt';
		}
	}
	
	let expTypeIsOpen = $state(false);

	function toggleDropdownExportType() {
		expTypeIsOpen = !expTypeIsOpen;
	}

	function closeDropdownExportType() {
		expTypeIsOpen = false;
	}
	

	let selectedMonth = '';

	let dropdownRef;
  
  // Close dropdown when clicked outside
  function handleClickOutside(event) {
    if (dropdownRef && !dropdownRef.contains(event.target)) {
      expTypeIsOpen = false;
    }
  }

	$effect(() => {
		if (browser) {
			handleClickOutside();
		}
	});
	let ready = $state(false);
  // Add event listener when the component is mounted
  onMount(() => {
		if (browser) {
			ready = true;

			document.addEventListener('mousedown', handleClickOutside);
			dropdownRef = document.getElementById('export-dropdown');
			
		}
  });

  // Clean up event listener when the component is destroyed
  onDestroy(() => {
		if (browser) {
			document.removeEventListener('mousedown', handleClickOutside);
		}
  });
</script>
<header class="bg-blue-500 p-4 text-white dark:bg-gray-800">
	<nav class="container mx-auto flex items-center justify-between"
		out:fade={{ duration: 400 }} in:fade={{ delay: 400, duration: 400 }}
	>
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
				<button
					class="flex items-center rounded px-4 py-2 transition-colors hover:bg-blue-600"
					data-dropdown-toggle="view-dropdown"
				>
					View
					<ChevronDownOutline class="ms-2 h-4 w-4" />
				</button>
				<Dropdown>
					<DropdownItem href="/viewRecord">Record</DropdownItem>
					<DropdownItem href="/viewReport">Report</DropdownItem>
				</Dropdown>
			</li>
			<li class="relative"
				
			>
				<button class="flex items-center rounded px-4 py-2 transition-colors hover:bg-blue-600" onclick={() => {
					expTypeIsOpen = !expTypeIsOpen;
				}}>
					Export
					<ChevronDownOutline class="ms-2 h-4 w-4" />
				</button>
				<div
					transition:fade={{ duration: 200 }}
				>
				<div class="absolute z-10 h-min bg-slate-700 shadow-lg rounded-lg w-30 py-0"
					id="export-dropdown"
					transition:fade={{ duration: 200 }}
				>
					{#if expTypeIsOpen}
					<div class="overflow-hidden"
						transition:fade={{ duration: 200 }}
					>
						<Accordion activeClass="bg-blue-600" >
							{#each months as month}
							<!-- if active no hover style -->
								<AccordionItem class="py-2 mb-2 h-full" paddingFlush={true} transitionType="fade" transitionParams={{ duration: 200 }}>
									<button slot="header" class="flex items-center py-1 my-0 h-auto mx-4 text-sm transition-colors ">
											{month}
									</button>
									<div class="flex flex-col m-auto border-gray-500 h-auto my-0 py-0">
										{#each downloadOptions as option}
											<Button
												class="bg-blue-100 py-1 transition-colors dark:bg-gray-800 text-blue-600 dark:text-white focus:ring-4 focus:ring-blue-200 dark:focus:ring-blue-400 hover:bg-blue-200 dark:hover:bg-blue-700 my-1"
												onclick={() => generateReport(month, option.toLowerCase())}
											>
													{option}
											</Button>
										{/each}
									</div>
								</AccordionItem>
							{/each}
						</Accordion>
					</div>
					{/if}
				</div>

				</div>
			</li>
		</ul>
		
	</nav>
</header>

<main>
	{@render children()}
</main>