<script lang="ts">
	import { onMount } from 'svelte';

	// State variables
	let months = [
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
	let selectedMonth = getCurrentMonth(); // Default to the current month
	let generators: string[] = [];
	let completedGenerators: string[] = [];
	let selectedGenerator: string | null = null;
	let preRunData: any = null;
	let postRunData: any = null;

	// Get the current month as a string
	function getCurrentMonth() {
		const now = new Date();
		return months[now.getMonth()];
	}

	// Fetch the completed generators for the selected month
	async function fetchCompletedGenerators(month: string) {
		const uri = `http://127.0.0.1:8100/records/${month.toLowerCase()}`;
		const response = await fetch(uri);
		const data = await response.json();
		completedGenerators = data.records;
	}

	async function fetchGeneratorData() {
		if (!selectedGenerator || !selectedMonth) return;

		const uri = `http://127.0.0.1:8100/gen_data/${selectedMonth.toLowerCase()}/${selectedGenerator}`;
		try {
			const response = await fetch(uri);
			if (!response.ok) {
				throw new Error('Failed to fetch generator data');
			}
			const data = await response.json();
			preRunData = data.pre;
			postRunData = data.post;
		} catch (error) {
			console.error('Error fetching generator data:', error);
			preRunData = null;
			postRunData = null;
		}
	}

	async function populateGenerators() {
		await fetchCompletedGenerators(selectedMonth);
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

	// Run once on component mount
	onMount(() => {
		populateGenerators();
	});

	// Watch for month changes
	$: if (selectedMonth) {
		populateGenerators();
		selectedGenerator = null;
		preRunData = null;
		postRunData = null;
	}

	// Watch for generator selection changes
	$: if (selectedGenerator) {
		fetchGeneratorData();
	}
</script>

<div class="min-h-screen bg-gray-900 p-6 text-gray-300">
	<h1 class="mb-4 text-2xl font-bold">Generator Records</h1>

	<!-- Month Selector -->
	<div class="mb-6">
		<label for="month-select" class="text-lg font-medium">Select Month</label>
		<select
			id="month-select"
			bind:value={selectedMonth}
			class="mt-2 block w-full rounded bg-gray-800 p-2 text-gray-300 focus:outline-none focus:ring-2 focus:ring-gray-700"
		>
			{#each months as month}
				<option value={month}>
					{month}
				</option>
			{/each}
		</select>
	</div>

	<!-- Generator Selector -->
	<div class="mb-6">
		<label for="generator-select" class="text-lg font-medium">Select Generator</label>
		<select
			id="generator-select"
			bind:value={selectedGenerator}
			class="mt-2 block w-full rounded bg-gray-800 p-2 text-gray-300 focus:outline-none focus:ring-2 focus:ring-gray-700"
		>
			<option value={null}>Select a generator</option>
			{#each completedGenerators as generator}
				<option value={generator}>
					{generator}
				</option>
			{/each}
		</select>
	</div>

	<!-- Generator Data Display -->
	{#if selectedGenerator && preRunData && postRunData}
		<div class="mt-8">
			<h2 class="mb-4 text-xl font-bold">Generator Records</h2>

			<!-- Pre-Run Data -->
			<div class="mb-4 rounded-lg bg-gray-800 p-4">
				<h3 class="mb-2 text-lg font-semibold">Pre-Run Check</h3>
				<div class="data-row py-2">
					<div class="grid grid-cols-2 gap-4">
						<div>
							<p><span class="font-medium">Fuel Level:</span> {preRunData.fuel_level}%</p>
							<p><span class="font-medium">Battery VDC:</span> {preRunData.battery_vdc}V</p>
							<p><span class="font-medium">Run Hours:</span> {preRunData.run_hours}</p>
							<p><span class="font-medium">Coolant Temp:</span> {preRunData.coolant_temp}°C</p>
						</div>
						<div>
							<p><span class="font-medium">Leaks:</span> {preRunData.leaks ? 'Yes' : 'No'}</p>
							<p>
								<span class="font-medium">Oil Check:</span>
								{preRunData.oil_check ? 'Passed' : 'Failed'}
							</p>
							<p><span class="font-medium">Notes:</span> {preRunData.notes || 'No notes'}</p>
						</div>
					</div>
				</div>
			</div>

			<!-- Post-Run Data -->
			<div class="rounded-lg bg-gray-800 p-4">
				<h3 class="mb-2 text-lg font-semibold">Post-Run Check</h3>
				<div class="data-row py-2">
					<div class="grid grid-cols-2 gap-4">
						<div>
							<p><span class="font-medium">Fuel Level:</span> {postRunData.fuel_level}%</p>
							<p><span class="font-medium">Battery VDC:</span> {postRunData.battery_vdc}V</p>
							<p><span class="font-medium">Run Hours:</span> {postRunData.run_hours}</p>
							<p><span class="font-medium">Coolant Temp:</span> {postRunData.coolant_temp}°C</p>
						</div>
						<div>
							<p><span class="font-medium">Leaks:</span> {postRunData.leaks ? 'Yes' : 'No'}</p>
							<p><span class="font-medium">Notes:</span> {postRunData.notes || 'No notes'}</p>
							<p><span class="font-medium">Last Updated:</span> {postRunData.last_updated}</p>
						</div>
					</div>
				</div>
			</div>
		</div>
	{:else}
		<p class="text-gray-400">Please select a generator to view records.</p>
	{/if}
</div>

<style>
	.completed {
		color: #22c55e; /* Tailwind 'green-500' */
		font-weight: bold;
	}
	.incomplete {
		color: #f87171; /* Tailwind 'red-400' */
	}
	.data-row {
		border-bottom: 1px solid #374151;
	}
</style>
