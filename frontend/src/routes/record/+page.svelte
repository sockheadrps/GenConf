<script lang="ts">
	import { onMount } from 'svelte';
	import {
		Input,
		Label,
		Select,
		Range,
		Badge,
		Datepicker,
		P,
		Button,
		Helper,
		Alert,
		CardPlaceholder,
		Skeleton,
		ListPlaceholder
	} from 'flowbite-svelte';
	import { fade, fly, scale } from 'svelte/transition';

	import { InfoCircleSolid } from 'flowbite-svelte-icons';
	import { page } from '$app/state';
	const month = page.url.searchParams.get('month');
	const generator = page.url.searchParams.get('gen');
	// if query param exists, make gen = GEN-generator
	let gen = '';
	if (generator) {
		gen = `GEN-${generator?.charAt(0).toUpperCase() + generator?.slice(1)}`;
	}

	let CURRENT_MONTH = $state('december');

	let selectedDate = $state<Date | null>(new Date());

	let leaks = $state(['Yes', 'No']);
	let oil_check = $state(['acceptable', 'unacceptable']);

	let generators = $state<string[]>([]);
	let selectedGenerator = $state('');
	type RunData = {
		fuel_level: number;
		battery_vdc: string | undefined;
		run_hours: string | undefined;
		coolant_temp: number | undefined;
		leaks: boolean;
		oil_check: string;
		notes: string;
	};
	let preRunData = $state({
		fuel_level: 50,
		battery_vdc: '',
		run_hours: undefined,
		coolant_temp: undefined,
		leaks: false,
		oil_check: oil_check[0],
		notes: ''
	});
	let postRunData = $state({
		fuel_level: 50,
		battery_vdc: '',
		run_hours: undefined,
		coolant_temp: undefined,
		leaks: false,
		oil_check: oil_check[0],
		notes: ''
	});

	let batteryVdcError = $state(false);
	let postBatteryVdcError = $state(false);
	let runHoursError = $state(false);
	let preRunHoursError = $state(false);
	let postRunHoursError = $state(false);
	let coolantTempError = $state(false);
	let postCoolantTempError = $state(false);
	let formError = $state(false);
	let coolantTempAlert = $state(false);
	let coolantTempAlertShown = $state(false);
	let runHoursAlert = $state(false);
	let runHoursAlertShown = $state(false);

	let completed_generators = $state<string[]>([]);

	async function fetchCompletedGenerators() {
		// /records/{month} lowercase month
		const uri = `http://127.0.0.1:8100/records/${getCurrentMonth().toLowerCase()}`;
		const response = await fetch(uri);
		const data = await response.json();
		return data.records;
	}

	let isFormValid: boolean;

	$: isFormValid = !!(
		selectedGenerator &&
		selectedDate &&
		preRunData.battery_vdc &&
		preRunData.run_hours &&
		preRunData.coolant_temp &&
		postRunData.battery_vdc &&
		postRunData.run_hours &&
		postRunData.coolant_temp &&
		!batteryVdcError &&
		!postBatteryVdcError &&
		!runHoursError &&
		!preRunHoursError &&
		!postRunHoursError &&
		!coolantTempError &&
		!postCoolantTempError
	);

	function validateBatteryVdc(value: string | undefined, isPost: boolean = false) {
		if (value === undefined) {
			if (isPost) {
				postBatteryVdcError = true;
				postRunData.battery_vdc = undefined;
			} else {
				batteryVdcError = true;
				preRunData.battery_vdc = undefined;
			}
			return;
		}

		// Convert to float and format to 2 decimal places
		const numValue = parseFloat(value);

		if (isNaN(numValue)) {
			if (isPost) {
				postBatteryVdcError = true;
				postRunData.battery_vdc = undefined;
			} else {
				batteryVdcError = true;
				preRunData.battery_vdc = undefined;
			}
			return;
		}

		const formattedValue = numValue.toFixed(2);

		if (isPost) {
			postBatteryVdcError = false;
			postRunData.battery_vdc = formattedValue;
		} else {
			batteryVdcError = false;
			preRunData.battery_vdc = formattedValue;
		}
	}

	function validateRunHours(value: string, isPost: boolean = false): boolean {
		// Check format matches integer:integer
		const regex = /^\d+:\d+$/;
		if (!regex.test(value)) {
			if (isPost) {
				postRunHoursError = true;
				postRunData.run_hours = '';
			} else {
				runHoursError = true;
				preRunData.run_hours = '';
			}
			return false;
		}

		const [hours, minutes] = value.split(':').map(Number);
		if (minutes >= 60) {
			if (isPost) {
				postRunHoursError = true;
				postRunData.run_hours = '';
			} else {
				runHoursError = true;
				preRunData.run_hours = '';
			}
			return false;
		}

		if (isPost) {
			// Only check run hours comparison if pre-run hours exists
			if (preRunData.run_hours) {
				const [preHours, preMinutes] = preRunData.run_hours.split(':').map(Number);
				const preTotal = preHours * 60 + preMinutes;
				const postTotal = hours * 60 + minutes;

				if (postTotal <= preTotal) {
					runHoursAlert = true;
					postRunHoursError = true;
					if (!runHoursAlertShown) {
						runHoursAlertShown = true;
					}
					return false;
				}
			}

			postRunHoursError = false;
			postRunData.run_hours = `${hours}:${minutes.toString().padStart(2, '0')}`;
		} else {
			runHoursError = false;
			preRunData.run_hours = `${hours}:${minutes.toString().padStart(2, '0')}`;
		}
		return true;
	}

	function validateCoolantTemp(value: number | string | undefined, isPost: boolean = false) {
		if (value === undefined) {
			if (isPost) {
				postCoolantTempError = true;
				postRunData.coolant_temp = undefined;
			} else {
				coolantTempError = true;
				preRunData.coolant_temp = undefined;
			}
			return;
		}

		if (isPost) {
			postCoolantTempError = false;
			postRunData.coolant_temp = Number(value);
			if (
				preRunData.coolant_temp !== undefined &&
				preRunData.coolant_temp > postRunData.coolant_temp
			) {
				coolantTempAlert = true;
				if (!coolantTempAlertShown) {
					coolantTempAlertShown = true;
					return;
				}
			}
		} else {
			coolantTempError = false;
			preRunData.coolant_temp = Number(value);
		}
	}

	function getCurrentMonth() {
		const date = new Date();
		const month = date.toLocaleString('default', { month: 'long' });
		// return month;

		return CURRENT_MONTH;
	}

	let ready = $state(false);

	async function populateGenerators() {
		completed_generators = await fetchCompletedGenerators();
		try {
			const uri = 'http://127.0.0.1:8100/generators';
			const response = await fetch(uri);

			if (!response.ok) {
				throw new Error(`Failed to fetch generators: ${response.statusText}`);
			}

			const data = await response.json();
			generators = data.generators;
			return response.ok;
		} catch (error) {
			console.error('Error fetching generators:', error);
			return false;
		}
	}

	async function handleSubmit() {
		if (preRunData.run_hours !== undefined) {
			validateRunHours(preRunData.run_hours);
		}
		if (postRunData.run_hours !== undefined) {
			validateRunHours(postRunData.run_hours, true);
		}
		validateBatteryVdc(preRunData.battery_vdc);
		validateBatteryVdc(postRunData.battery_vdc, true);
		validateCoolantTemp(preRunData.coolant_temp);
		validateCoolantTemp(postRunData.coolant_temp, true);

		// Check if any validation errors exist
		if (
			batteryVdcError ||
			postBatteryVdcError ||
			runHoursError ||
			preRunHoursError ||
			postRunHoursError ||
			coolantTempError ||
			postCoolantTempError
		) {
			formError = true;
			return;
		}

		// Check if all required fields have values
		if (
			!selectedGenerator ||
			!selectedDate ||
			!preRunData.battery_vdc ||
			!preRunData.run_hours ||
			!preRunData.coolant_temp ||
			!postRunData.battery_vdc ||
			!postRunData.run_hours ||
			!postRunData.coolant_temp
		) {
			formError = true;
			return;
		}
		// Check if post coolant temp is less than pre coolant temp
		if (Number(postRunData.coolant_temp) < Number(preRunData.coolant_temp)) {
			coolantTempAlert = true;
			if (!coolantTempAlertShown) {
				coolantTempAlertShown = true;
				return;
			}
		}

		formError = false;
		coolantTempAlert = false;

		// build the data to send to the backend
		const data = {
			generator: selectedGenerator,
			date: selectedDate,
			month: month ? month : getCurrentMonth(),
			preRunData: {
				...preRunData,
				leaks: preRunData.leaks === 'Yes'
			},
			postRunData: {
				...postRunData,
				leaks: postRunData.leaks === 'Yes'
			}
		};
		const uri = 'http://127.0.0.1:8100/record';
		const response = await fetch(uri, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json'
			},
			body: JSON.stringify(data)
		});
		if (response.ok) {
			await populateGenerators();
			selectedGenerator = '';
			selectedDate = new Date();
			preRunData = {
				fuel_level: 50,
				battery_vdc: '',
				run_hours: undefined,
				coolant_temp: undefined,
				leaks: false,
				oil_check: oil_check[0],
				notes: ''
			};
			postRunData = {
				fuel_level: 50,
				battery_vdc: '',
				run_hours: undefined,
				coolant_temp: undefined,
				leaks: false,
				oil_check: oil_check[0],
				notes: ''
			};
		}
	}

	let triggerMethod = 'click';
	let dropdownVisible = false;

	onMount(() => {
		populateGenerators();
		const dropdownTrigger = document.querySelector('[data-dropdown-trigger]');
		const dropdownMenu = document.querySelector('.dropdown-menu') as HTMLElement;

		if (dropdownMenu) {
			dropdownMenu.style.display = dropdownVisible ? 'block' : 'none';
		}

		// Close dropdown when clicking outside
		document.addEventListener('click', (e) => {
			const target = e.target as HTMLElement;
			if (!dropdownTrigger?.contains(target)) {
				dropdownVisible = false;
				if (dropdownMenu) {
					dropdownMenu.style.display = 'none';
				}
			}
		});

		if (triggerMethod === 'hover') {
			dropdownTrigger?.addEventListener('mouseenter', () => {
				dropdownVisible = true;
				if (dropdownMenu) {
					dropdownMenu.style.display = 'block';
				}
			});

			dropdownTrigger?.addEventListener('mouseleave', () => {
				dropdownVisible = false;
				if (dropdownMenu) {
					dropdownMenu.style.display = 'none';
				}
			});
		}

		if (triggerMethod === 'click') {
			dropdownTrigger?.addEventListener('click', (e) => {
				e.stopPropagation(); // Prevent click from bubbling to document
				dropdownVisible = !dropdownVisible;
				if (dropdownMenu) {
					dropdownMenu.style.display = dropdownVisible ? 'block' : 'none';
				}
			});

			// Add click handler for menu items
			dropdownMenu?.addEventListener('click', (e) => {
				if (dropdownMenu) {
					dropdownMenu.style.display = 'none';
				}
			});
		}
		ready = true;
	});

	// if ready re-order the generators, and have the completed generators at the bottom
	function reorderGenerators() {
		generators = generators.sort().reverse();
		generators = generators.filter((generator) => !completed_generators.includes(generator));
		generators = [...generators, ...completed_generators];
		return generators;
	}

	function toggleDropdown() {
		const dropdownMenu = document.querySelector('.dropdown-menu') as HTMLElement;

		if (dropdownMenu) {
			dropdownMenu.style.display = dropdownVisible ? 'block' : 'none';
		}
	}
	async function getSelectedGeneratorData(selectedGenerator: string, month: string) {
		if (!ready) return;
		const uri = `http://127.0.0.1:8100/gen_data/${month}/${selectedGenerator}`;
		try {
			const response = await fetch(uri);
			if (response.status === 404) {
				preRunData = {
					fuel_level: 50,
					battery_vdc: '',
					run_hours: undefined,
					coolant_temp: undefined,
					leaks: 'No',
					oil_check: oil_check[0],
					notes: ''
				};
				postRunData = {
					fuel_level: 50,
					battery_vdc: '',
					run_hours: undefined,
					coolant_temp: undefined,
					leaks: false,
					notes: ''
				};
				return;
			} else {
				const data = await response.json();
				// if data.pre.oil_check is true, then oil_check is unacceptable, otherwise it is acceptable
				if (data.pre.oil_check) {
					preRunData = {
						...data.pre,
						leaks: data.pre.leaks ? 'Yes' : 'No',
						oil_check: oil_check[0]
					};
				} else {
					preRunData = {
						...data.pre,
						leaks: data.pre.leaks ? 'Yes' : 'No',
						oil_check: oil_check[0]
					};
				}

				postRunData = {
					...data.post,
					leaks: data.post.leaks ? 'Yes' : 'No'
				};
			}
		} catch (error) {
			console.error('Error fetching generator data:', error);
		}
	}

	$effect(() => {
		if (month && ready && gen !== '') {
			selectedGenerator = gen.replace('GEN-', '');
		}
	});

	$effect(() => {
		if (selectedGenerator && ready) {
			getSelectedGeneratorData(selectedGenerator, getCurrentMonth().toLowerCase());
		}
	});
</script>

<div
	class="container z-10 mx-auto mt-10 min-h-[80vh] max-w-5xl rounded-lg bg-gray-900 p-6 shadow-lg"
	class:hidden={!ready}
	in:fade={{ duration: 300 }}
>
	<Badge large color="indigo">{getCurrentMonth()}</Badge>

	{#if coolantTempAlert}
		<div
			class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50"
			role="presentation"
			onclick={() => (coolantTempAlert = false)}
		>
			<Alert color="red" dismissable class="max-w-md" on:dismiss={() => (coolantTempAlert = false)}>
				<InfoCircleSolid slot="icon" class="h-5 w-5" />
				Warning: Post-run coolant temperature is lower than pre-run temperature. Please verify your readings.
			</Alert>
		</div>
	{/if}

	{#if runHoursAlert}
		<div
			class="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50"
			role="presentation"
			onclick={() => (runHoursAlert = false)}
		>
			<Alert color="red" dismissable class="max-w-md" on:dismiss={() => (runHoursAlert = false)}>
				<InfoCircleSolid slot="icon" class="h-5 w-5" />
				Warning: Post-run hours must be greater than pre-run hours. Please verify your readings.
			</Alert>
		</div>
	{/if}
	<!-- Generator Dropdown (Svelte Component) -->
	<div class="relative mb-2" data-dropdown-trigger>
		<Label for="generator" class="sr-only text-lg font-medium text-gray-400">Generator</Label>

		<!-- Dropdown Trigger (Button or Select) -->
		<button
			id="generator"
			class="mt-2 w-full bg-gray-800 py-2 text-center tracking-wide text-gray-300 focus:outline-none"
			aria-haspopup="true"
		>
			{#if selectedGenerator}
				{selectedGenerator}
			{:else}
				Select Generator
			{/if}
		</button>

		<!-- Dropdown Menu -->
		<div
			class="dropdown-menu absolute z-10 mt-1 w-full rounded-md bg-gray-700 text-gray-300 shadow-lg"
			style="display: none;"
		>
			<ul>
				{#if ready && generators.length > 0}
					{#each reorderGenerators() as generator}
						<li class="px-4">
							<button
								class="w-full cursor-pointer text-left tracking-wide hover:bg-gray-600 {completed_generators &&
								completed_generators.includes(generator)
									? 'text-green-500'
									: ''}"
								onclick={() => {
									selectedGenerator = generator;
									toggleDropdown();
								}}
							>
								{generator}
							</button>
						</li>
					{/each}
				{:else}
					<li class="px-4 py-2">Loading generators...</li>
				{/if}
			</ul>
		</div>
	</div>

	<!-- Combined Pre-run and Post-run Form -->
	{#if selectedGenerator}
		<form
			onsubmit={(e) => {
				e.preventDefault();
				handleSubmit(e);
			}}
			class="mt-4"
		>
			<div class="mb-4">
				<Datepicker bind:value={selectedDate} />
			</div>
			<div class="grid grid-cols-1 gap-8 md:grid-cols-2">
				<!-- Pre-run Section -->
				<div class="rounded-lg bg-gray-800 p-6 shadow-md">
					<h2 class="mb-4 text-xl font-semibold text-gray-300">Pre-run Data</h2>
					<div class="space-y-2">
						<div>
							<label for="fuel_level" class="block text-sm font-medium text-gray-400"
								>Fuel Level ({preRunData.fuel_level}%)</label
							>
							<div class="flex items-center gap-4">
								<div class="w-full">
									<Range id="fuel_level" min={0} max={100} bind:value={preRunData.fuel_level} />
								</div>
								<Input
									type="number"
									min={0}
									max={100}
									bind:value={preRunData.fuel_level}
									class="my-0 w-auto rounded-md border border-gray-600 bg-gray-800 py-1 text-center text-gray-300"
								/>
							</div>
						</div>
						<div class="mb-6">
							<Label
								for="battery_vdc"
								color={batteryVdcError ? 'red' : 'gray'}
								class="text-gray-500">Battery VDC</Label
							>
							<Input
								id="battery_vdc"
								color={batteryVdcError ? 'red' : 'base'}
								bind:value={preRunData.battery_vdc}
								on:change={(e) => {
									if (e?.currentTarget?.value && !e.currentTarget.value.includes('.')) {
										e.currentTarget.value = parseFloat(e.currentTarget.value).toFixed(2);
									}
									validateBatteryVdc(e?.currentTarget?.value);
								}}
								class="mt-2 w-full rounded-md border border-gray-400 bg-gray-800 text-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
							/>
							{#if batteryVdcError}
								<Helper class="mt-2" color="red">
									<span class="font-medium">Error!</span>
									Please enter a valid number for Battery VDC.
								</Helper>
							{/if}
						</div>
						<div>
							<Label
								for="run_hours_pre"
								color={preRunHoursError ? 'red' : 'gray'}
								class="text-gray-500">Run Hours (format: hours:minutes)</Label
							>
							<Input
								id="run_hours_pre"
								color={preRunHoursError ? 'red' : 'base'}
								bind:value={preRunData.run_hours}
								on:blur={(e) => validateRunHours(e.currentTarget.value)}
								placeholder="e.g. 123:45"
								class="mt-2 w-full rounded-md border border-gray-600 bg-gray-800 text-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
							/>
							{#if preRunHoursError}
								<Helper class="mt-2" color="red">
									<span class="font-medium">Error!</span>
									Please enter run hours in format "hours:minutes" (e.g. 123:45)
								</Helper>
							{/if}
						</div>
						<div>
							<Label
								for="coolant_temp"
								color={coolantTempError ? 'red' : 'gray'}
								class="text-gray-500">Coolant Temp</Label
							>
							<Input
								id="coolant_temp"
								color={coolantTempError ? 'red' : 'gray'}
								bind:value={preRunData.coolant_temp}
								on:blur={(e) => validateCoolantTemp(e.currentTarget.value)}
								class="mt-2 w-full rounded-md border border-gray-600 bg-gray-800 text-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
							/>
							{#if coolantTempError}
								<Helper class="mt-2" color="red">
									<span class="font-medium">Error!</span>
									Please enter a valid integer for Coolant Temp.
								</Helper>
							{/if}
						</div>
						<div>
							<Label for="leaks" color="gray" class="text-gray-500">Leaks</Label>
							<Select
								id="leaks"
								bind:value={preRunData.leaks}
								class="mt-2 w-full rounded-md border border-gray-600 bg-gray-800 text-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
							>
								{#each leaks as leak}
									<option value={leak}>{leak}</option>
								{/each}
							</Select>
						</div>
						<div>
							<Label for="oil_check" color="gray" class="text-gray-500">Oil Check</Label>
							<Select
								id="oil_check"
								bind:value={preRunData.oil_check}
								class="mt-2 w-full rounded-md border border-gray-600 bg-gray-800 text-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
							>
								{#each oil_check as oil}
									<option value={oil}>{oil}</option>
								{/each}
							</Select>
						</div>
						<div>
							<Label for="notes" color="gray" class="text-gray-500">Notes</Label>
							<textarea
								id="notes"
								bind:value={preRunData.notes}
								class="mt-2 w-full rounded-md border border-gray-600 bg-gray-800 p-2 text-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
							></textarea>
						</div>
					</div>
				</div>

				<!-- Post-run Section -->
				<div class="rounded-lg bg-gray-800 p-6 shadow-md">
					<h2 class="mb-4 text-xl font-semibold text-gray-300">Post-run Data</h2>
					<div class="space-y-2">
						<div>
							<label for="fuel_level_post" class="block text-sm font-medium text-gray-400"
								>Fuel Level ({postRunData.fuel_level}%)</label
							>
							<div class="flex items-center gap-4">
								<div class="w-full">
									<Range
										id="fuel_level_post"
										min={0}
										max={100}
										bind:value={postRunData.fuel_level}
									/>
								</div>
								<Input
									type="number"
									min={0}
									max={100}
									bind:value={postRunData.fuel_level}
									class="my-0 w-auto rounded-md border border-gray-600 bg-gray-800 py-1 text-center text-gray-300"
								/>
							</div>
						</div>
						<div class="mb-6">
							<Label
								for="battery_vdc_post"
								color={postBatteryVdcError ? 'red' : 'gray'}
								class="text-gray-500">Battery VDC</Label
							>
							<Input
								id="battery_vdc_post"
								color={postBatteryVdcError ? 'red' : 'gray'}
								bind:value={postRunData.battery_vdc}
								on:change={(e) => {
									if (e?.currentTarget?.value && !e.currentTarget.value.includes('.')) {
										e.currentTarget.value = parseFloat(e.currentTarget.value).toFixed(2);
									}
									validateBatteryVdc(e?.currentTarget?.value, true);
								}}
								class="mt-2 w-full rounded-md border border-gray-600 bg-gray-800 text-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
							/>
							{#if postBatteryVdcError}
								<Helper class="mt-2" color="red">
									<span class="font-medium">Error!</span>
									Please enter a valid number for Battery VDC.
								</Helper>
							{/if}
						</div>
						<div>
							<Label
								for="run_hours_post"
								color={postRunHoursError ? 'red' : 'gray'}
								class="text-gray-500">Run Hours (format: hours:minutes)</Label
							>
							<Input
								id="run_hours_post"
								color={postRunHoursError ? 'red' : 'base'}
								bind:value={postRunData.run_hours}
								on:blur={(e) => validateRunHours(e.currentTarget.value, true)}
								placeholder="e.g. 123:45"
								class="mt-2 w-full rounded-md border border-gray-600 bg-gray-800 text-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
							/>
							{#if postRunHoursError}
								<Helper class="mt-2" color="red">
									<span class="font-medium">Error!</span>
									Please enter run hours in format "hours:minutes" (e.g. 123:45)
								</Helper>
							{/if}
						</div>
						<div>
							<Label
								for="coolant_temp_post"
								color={postCoolantTempError ? 'red' : 'gray'}
								class="text-gray-500">Coolant Temp</Label
							>
							<Input
								id="coolant_temp_post"
								color={postCoolantTempError ? 'red' : 'gray'}
								bind:value={postRunData.coolant_temp}
								on:blur={(e) => validateCoolantTemp(e.currentTarget.value, true)}
								class="mt-2 w-full rounded-md border border-gray-600 bg-gray-800 text-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
							/>
							{#if postCoolantTempError}
								<Helper class="mt-2" color="red">
									<span class="font-medium">Error!</span>
									Please enter a valid integer for Coolant Temp.
								</Helper>
							{/if}
						</div>
						<div>
							<Label for="leaks_post" color="gray" class="text-gray-500">Leaks</Label>
							<Select
								id="leaks_post"
								bind:value={postRunData.leaks}
								class="mt-2 w-full rounded-md border border-gray-600 bg-gray-800 text-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
							>
								{#each leaks as leak}
									<option value={leak}>{leak}</option>
								{/each}
							</Select>
						</div>
						<div>
							<Label for="oil_check_post" color="gray" class="text-gray-500">Oil Check</Label>
							<Select
								id="oil_check_post"
								disabled
								placeholder="not applicable"
								class="mt-2 w-full rounded-md border border-gray-600 bg-gray-800 text-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
							></Select>
						</div>
						<div>
							<Label for="notes_post" color="gray" class="text-gray-500">Notes</Label>
							<textarea
								id="notes_post"
								bind:value={postRunData.notes}
								class="mt-2 w-full rounded-md border border-gray-600 bg-gray-800 p-2 text-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500"
							></textarea>
						</div>
					</div>
				</div>
			</div>

			<!-- Combined Submit Button -->
			<div class="mt-8">
				<Button
					type="submit"
					onclick={handleSubmit}
					disabled={!isFormValid}
					class="bg-primary-600 hover:bg-primary-700 focus:ring-primary-500 w-full rounded-md px-4 py-3 text-gray-100 focus:outline-none focus:ring-2 disabled:cursor-not-allowed disabled:opacity-50"
				>
					Submit All Data
				</Button>
				{#if formError}
					<Helper class="mt-2" color="red">
						<span class="font-medium">Error!</span>
						Please fill in all required fields with valid values.
					</Helper>
				{/if}
			</div>
		</form>
	{:else}
		<div class="flex flex-row gap-4">
			<div class="h-full w-full">
				<CardPlaceholder size="lg" class="mt-8 block h-96" />
			</div>
			<div class="h-full w-full">
				<CardPlaceholder size="lg" class="mt-8 block h-96" />
			</div>
		</div>
	{/if}
</div>

<style>
	.input {
		background-color: #1f2937;
		color: #9ca3af; /* Added slightly darker text color (gray-400) */
	}
</style>
