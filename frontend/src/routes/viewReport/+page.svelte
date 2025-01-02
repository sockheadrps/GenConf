<script lang="ts">
	import { onMount } from 'svelte';
	import { fade, fly, scale } from 'svelte/transition';
	import {
		Table,
		TableBody,
		TableBodyCell,
		TableBodyRow,
		TableHead,
		TableHeadCell,
		List,
		Li,
		ButtonGroup,
		Button,
		Dropdown,
		DropdownItem,
		Alert,
		Toggle,
		A
	} from 'flowbite-svelte';
	import { ChevronDownOutline } from 'flowbite-svelte-icons';

	let month_menu = $state<HTMLElement | null>(null);
	let ready = $state(false);
	onMount(() => {
		month_menu = document.getElementById('month-menu');
		ready = true;
	});

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
	let selectedMonth = $state('');
	let isPreReport = $state(true);
	let reportType = $state('pre');

	let showAlert = $state(false);
	let dropdownOpen = $state(false);

	interface BaseReportRow {
		gen_name: string;
		fuel_level: number;
		battery_vdc: string;
		run_hours: string;
		coolant_temp: number;
		leaks: boolean;
		notes: string;
		last_updated: string;
	}

	interface PreReportRow extends BaseReportRow {
		oil_check: string;
	}

	interface PostReportRow extends BaseReportRow {}

	type ReportRow = PreReportRow | PostReportRow;

	let report = $state<ReportRow[] | null>(null);
	let preReport = $state<ReportRow[] | null>(null);
	let gens_no_data = $state(null);

	let reportTreportType = $state('pre');
	// Fetch the report JSON and insert it into the component
	async function getReports(month: string, report_type: string) {
		month = month.toLowerCase();
		const uri = `http://localhost:8100/reports/${month}/${report_type}`;
		try {
			const response = await fetch(uri);
			if (response.status === 200) {
				const data = await response.json();
				return data.report;
			} else {
				throw new Error(`Failed to fetch report: ${response.status}`);
			}
		} catch (error) {
			if (error instanceof Error && error.message.includes('404')) {
				showAlert = true;
			} else {
				console.error('Error fetching report:', error);
			}
		}
	}

	async function handleMonthClick(month: string) {
		selectedMonth = month;
		report = await getReports(month, reportType);

		if (report) {
			gens_no_data = report.filter((row) => row.fuel_level == 0);
		}
	}

	function getDifference(current: number | string, previous: number | string) {
		const curr = typeof current === 'string' ? parseFloat(current) : current;
		const prev = typeof previous === 'string' ? parseFloat(previous) : previous;
		if (isNaN(curr) || isNaN(prev)) return null;
		return Number((curr - prev).toFixed(2));
	}

	function formatDifference(diff: number | null) {
		if (diff === null) return '';
		if (diff === 0) return '0';
		return diff > 0 ? `+${diff}` : `${diff}`;
	}

	function getDifferenceColor(diff: number | null) {
		if (diff === null || diff === 0) return 'text-gray-400';
		return diff > 0 ? 'text-green-400' : 'text-red-400';
	}

	function getRunHoursInMinutes(run_hours: string) {
		const [hours, minutes] = run_hours.split(':').map(Number);
		return hours * 60 + minutes;
	}
	$effect(() => {
		gens_no_data = report?.filter((row) => row.fuel_level == 0) ?? [];
		reportType = isPreReport ? 'pre' : 'post';
	});
	$effect(() => {
		if (selectedMonth) {
			getReports(selectedMonth, reportType).then((data) => {
				report = data;
				if (isPreReport) preReport = data;
			});
		}
	});

	function handleGenNoDataClick(gen: string) {
		window.location.href = `/record?month=${selectedMonth}&gen=${gen}`;
	}
</script>

{#if showAlert}
	<div
		class="absolute left-0 top-0 z-10 flex h-full w-full items-center justify-center bg-gray-900/50 backdrop-blur-sm"
		onclick={() => (showAlert = false)}
		onkeydown={() => (showAlert = false)}
		role="button"
		tabindex="0"
	>
		<Alert color="red" class="w-96">
			<span class="font-medium">No report found for {selectedMonth}!</span>
		</Alert>
	</div>
{/if}
<div class="container mx-auto min-h-[calc(100vh-72px)] w-full bg-gray-900 px-4 py-6">
	<div class="flex flex-col items-center gap-6">
		<div class="flex items-center justify-between gap-4" in:fade={{ duration: 300 }}>
			<div class="flex items-center gap-2">
				<Button color="dark" data-dropdown-toggle="month-menu" data-dropdown-delay="100">
					{selectedMonth || 'Month'}
					<ChevronDownOutline class="ms-2 h-4 w-4" />
				</Button>
				<Dropdown bind:open={dropdownOpen} class="dropdown-menu w-48" id="month-menu">
					{#each months as month}
						<DropdownItem
							onclick={() => {
								dropdownOpen = false;
								handleMonthClick(month);
							}}
							class="flex items-center justify-between"
						>
							{month}
						</DropdownItem>
					{/each}
				</Dropdown>
				<ButtonGroup>
					<Button color={isPreReport ? 'blue' : 'dark'} onclick={() => (isPreReport = true)}
						>Pre</Button
					>
					<Button color={!isPreReport ? 'blue' : 'dark'} onclick={() => (isPreReport = false)}
						>Post</Button
					>
				</ButtonGroup>
			</div>
			{#if gens_no_data && gens_no_data.length > 0}
				<div
					class="flex items-center gap-4 rounded-lg bg-red-900/20 px-1 py-1 backdrop-blur-sm"
					in:fade={{ duration: 300 }}
					out:fade={{ duration: 300 }}
				>
					<p class="text-sm font-medium text-red-200">Generators not recorded:</p>
					<List tag="ul" list="none" class="flex flex-wrap gap-1">
						{#each gens_no_data as gen}
							<div>
								<Li>
									<A href={`/record?month=${selectedMonth}&gen=${gen.gen_name}`}>
										<span
											class="inline-flex items-center rounded-full bg-red-800/60 px-3 py-1.5 text-sm font-medium text-red-100 shadow-sm transition-colors hover:bg-red-800"
											in:fly={{ x: -20, duration: 1000 }}
											out:fly={{ x: 20, duration: 1000 }}
										>
											{gen.gen_name}
										</span>
									</A>
								</Li>
							</div>
						{/each}
					</List>
				</div>
			{/if}
		</div>

		{#if report && reportType}
			<div class="w-full overflow-x-auto rounded-lg" in:fade={{ duration: 300 }}>
				<Table striped={true} class="rounded-lg">
					{#if reportType === 'pre'}
						<TableHead>
							<TableHeadCell>Gen Name</TableHeadCell>
							<TableHeadCell>Fuel Level</TableHeadCell>
							<TableHeadCell>Battery VDC</TableHeadCell>
							<TableHeadCell>Run Hours</TableHeadCell>
							<TableHeadCell>Coolant Temp</TableHeadCell>
							<TableHeadCell>Leaks</TableHeadCell>
							<TableHeadCell>Oil Check</TableHeadCell>
							<TableHeadCell>Notes</TableHeadCell>
							<TableHeadCell>Last Updated</TableHeadCell>
						</TableHead>
					{:else}
						<TableHead>
							<TableHeadCell>Gen Name</TableHeadCell>
							<TableHeadCell>Fuel Level</TableHeadCell>
							<TableHeadCell>Battery VDC</TableHeadCell>
							<TableHeadCell>Run Hours</TableHeadCell>
							<TableHeadCell>Coolant Temp</TableHeadCell>
							<TableHeadCell>Leaks</TableHeadCell>
							<TableHeadCell>Notes</TableHeadCell>
							<TableHeadCell>Last Updated</TableHeadCell>
						</TableHead>
					{/if}
					<TableBody>
						{#each report as row, i}
							{#if row.fuel_level == 0}{:else}
								<TableBodyRow>
									<TableBodyCell>
										<span
											class="inline-flex items-center rounded-full bg-green-700 px-3 text-sm font-medium shadow-sm transition-colors hover:bg-green-800"
											in:fade={{ duration: 1000, delay: i * 200 }}
											out:fade={{ duration: 1000, delay: i * 200 }}
										>
											<A
												href={`/record?month=${selectedMonth}&gen=${row.gen_name}`}
												color="white"
												class="hover:bg-green-800"
											>
												{row.gen_name}
											</A>
										</span>
									</TableBodyCell>
									<TableBodyCell>
										<span
											class="inline-flex items-center rounded-full bg-blue-900/50 px-2.5 py-0.5 text-sm text-blue-200"
										>
											{Number(row.fuel_level).toFixed(2)}%
											{#if !isPreReport && preReport}
												{#each preReport as preRow}
													{#if preRow.gen_name === row.gen_name}
														{@const diff = getDifference(row.fuel_level, preRow.fuel_level)}
														<span class="ml-2 text-xs {getDifferenceColor(diff)}">
															({formatDifference(diff)}%)
														</span>
													{/if}
												{/each}
											{/if}
										</span>
									</TableBodyCell>
									<TableBodyCell>
										{Number(row.battery_vdc).toFixed(2)}
										{#if !isPreReport && preReport}
											{#each preReport as preRow}
												{#if preRow.gen_name === row.gen_name}
													{@const diff = getDifference(row.battery_vdc, preRow.battery_vdc)}
													<span class="ml-2 text-xs {getDifferenceColor(diff)}">
														({formatDifference(diff)})
													</span>
												{/if}
											{/each}
										{/if}
									</TableBodyCell>
									<TableBodyCell>
										{row.run_hours}
										{#if !isPreReport && preReport}
											{#each preReport as preRow}
												{#if preRow.gen_name === row.gen_name}
													{@const diff = getDifference(
														getRunHoursInMinutes(row.run_hours),
														getRunHoursInMinutes(preRow.run_hours)
													)}
													<span class="ml-2 text-xs {getDifferenceColor(diff)}">
														({formatDifference(diff)})
													</span>
												{/if}
											{/each}
										{/if}
									</TableBodyCell>
									<TableBodyCell>
										{Number(row.coolant_temp).toFixed(2)}
										{#if !isPreReport && preReport}
											{#each preReport as preRow}
												{#if preRow.gen_name === row.gen_name}
													{@const diff = getDifference(row.coolant_temp, preRow.coolant_temp)}
													<span class="ml-2 text-xs text-gray-400">
														({formatDifference(diff)})
													</span>
												{/if}
											{/each}
										{/if}
									</TableBodyCell>
									<TableBodyCell>
										<span class={row.leaks ? 'text-green-400' : 'text-red-400'}>
											{row.leaks ? 'No' : 'Yes'}
										</span>
									</TableBodyCell>
									{#if reportType === 'pre'}
										<TableBodyCell>
											<span class={row.oil_check ? 'text-green-400' : 'text-red-400'}>
												{row.oil_check ? 'Accepted' : 'Rejected'}
											</span>
										</TableBodyCell>
									{:else}
										<!-- pass -->
									{/if}
									<TableBodyCell class="max-w-xs truncate">{row.notes}</TableBodyCell>
									<TableBodyCell class="text-gray-400">{row.last_updated}</TableBodyCell>
								</TableBodyRow>
							{/if}
						{/each}
					</TableBody>
				</Table>
			</div>
		{/if}
	</div>
</div>
