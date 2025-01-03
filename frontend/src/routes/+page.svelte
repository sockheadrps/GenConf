<script lang="ts">
	import {
		Card,
		Button,
		Timeline,
		TimelineItem,
		List,
		Li,
		Label,
		A,
		ToolbarButton,
		Toggle,
		WidgetPlaceholder
	} from 'flowbite-svelte';
	import { onMount, onDestroy } from 'svelte';
	import { fade, fly, scale } from 'svelte/transition';
	import GeneratorCharts from '../components/GeneratorCharts.svelte';
	import FuelChart from '../components/FuelChart.svelte';
	import Dashboard from '../components/dashboard.svelte';
	import { browser } from '$app/environment';

	let completed_generators = $state([]);
	let generators = $state([
		'GEN-A3',
		'GEN-A2',
		'GEN-B3',
		'GEN-B2',
		'GEN-C3',
		'GEN-C2',
		'GEN-D3',
		'GEN-D2',
		'GEN-R3',
		'GEN-R2',
		'GEN-A1',
		'GEN-B1',
		'GEN-C1',
		'GEN-D1',
		'GEN-E2',
		'GEN-R1',
		'GEN-H3',
		'GEN-I3',
		'GEN-J3',
		'GEN-G3',
		'GEN-F3',
		'GEN-E3'
	]);

	let CURRENT_MONTH = $state('december');

	async function fetchCompletedGenerators() {
		const uri = `http://127.0.0.1:8100/records/${CURRENT_MONTH.toLowerCase()}`;
		const response = await fetch(uri);
		const data = await response.json();
		completed_generators = data.records;
	}

	let lockGenLinks = $state(true);

	function toggleLockGenLinks() {
		lockGenLinks = !lockGenLinks;
	}

	interface GeneratorEstimate {
		generator_name: string;
		fuel_capacity: number;
		current_fuel_volume: number;
		fuel_delta: number;
	}

	interface FuelEstimate {
		get_estimates: {
			[key: string]: GeneratorEstimate;
		};
		total_fuel_needed: number;
		estimate_fuel_cost: number;
	}

	interface DashboardProps {
		dataPayload: FuelEstimate;
	}
	let dashboardProps: DashboardProps = $state({
		dataPayload: {
			get_estimates: {},
			total_fuel_needed: 0,
			estimate_fuel_cost: 0
		}
	});

	let fuelEstimate: FuelEstimate = $state({
		get_estimates: {},
		total_fuel_needed: 0,
		estimate_fuel_cost: 0
	});

	async function getFuelEstimate() {
		try {
			const uri = `http://127.0.0.1:8100/gen_fuel_estimate/december`;
			const response = await fetch(uri);
			if (!response.ok) {
				throw new Error('Failed to fetch data');
			}
			const data = await response.json();
			return data;
		} catch (error) {
			console.error('Error fetching fuel estimate:', error);
			return null;
		}
	}

	let generatorName = $state('');
	let generatorData = $state<FuelEstimate | null>(null);
	let afterGenClick = $state(false);

	async function handleGenClick(gen: string) {
		generatorName = gen;
		const response = await getFuelEstimate();
		if (response) {
			generatorData = response;
			dashboardProps = { dataPayload: response };
			afterGenClick = true;
		} else {
			console.error('Failed to get fuel estimate');
		}
	}

	let fuel_estimate: FuelEstimate | null = $state(null);
	let ready = $state(false);

	// $effect(() => {
	// 	if (afterGenClick &&ready) {
	// 		console.log('dashboardProps', dashboardProps);

	// 	}
	// });

	onMount(async () => {
		const completed_generators = await fetchCompletedGenerators();

		try {
			const fuelEstimateResponse = await getFuelEstimate();
			if (!fuelEstimateResponse) {
				throw new Error('Invalid fuel estimate response - response is null or undefined');
			}
			dashboardProps = { dataPayload: fuelEstimateResponse };
		} catch (error) {
			console.error('Error fetching fuel estimate:', error);
			fuel_estimate = null;
		}
		ready = true;
	});

	function getCurrentMonth() {
		const date = new Date();
		const month = date.toLocaleString('default', { month: 'long' });
		return month;
	}
</script>

{#if ready}
	<main
		class="pt-8 bg-gray-50 dark:bg-gray-900 w-screen h-[calc(100vh-80px)]"
		in:fade={{ duration: 300 }}
	>
		<div class="flex justify-center items-center  h-fit" in:fly={{ y: 20, duration: 400 }}>
			<Card class="p-8 min-w-[1200px] flex flex-row h-fit shadow-xl px-2">
				<div class="grid lg:grid-cols-2 gap-10 min-w-full h-fit">
					<div class="shadow-xl px-2 min-w-full rounded-lg box-shadow: 10 4px 12px rgba(0, 0, 0, 0.8)" in:fly={{ x: -20, duration: 500, delay: 200 }}>
						<Card class="p-8 shadow-lg min-w-full h-full my-auto ">
							{#if ready && dashboardProps.dataPayload !== undefined}
								<Label
									class="flex flex-col items-center justify-center text-2xl font-semibold mb-6"
								>
									{generatorName || 'Estimate Totals'}</Label
								>
								<Dashboard
									dataPayload={dashboardProps.dataPayload}
									parentReady={ready}
									parentGeneratorName={generatorName}
								/>
							{:else}
								<div
									class="justify-center align-middle my-auto"
								>
									<WidgetPlaceholder divClass="h-full w-full justify-center items-center" />
								</div>
							{/if}
						</Card>
					</div>

					<div class="shadow-xl px-2 min-w-full rounded-lg box-shadow: 2 4px 12px rgba(0, 0, 0, 0.8)" in:fly={{ x: 20, duration: 500, delay: 200 }}>
						<Card class="p-8 shadow-xl min-w-full rounded-lg box-shadow: 10 8px 12px rgba(0, 0, 0, 0.8)">
							<h3 class="text-2xl font-semibold mb-4 text-white text-center">Quick Actions</h3>
							<div class="my-auto">
								<div in:scale={{ duration: 300, delay: 400 }}>
									<Button
										href="/record"
										size="xl"
										class="w-full text-xl my-2 py-8 rounded-lg bg-gradient-to-r from-green-400 to-green-600 text-white hover:from-green-500 hover:to-green-700 shadow-md hover:shadow-lg transition-all duration-300"
									>
										Record Generator Check
									</Button>
								</div>
								<div in:scale={{ duration: 300, delay: 500 }}>
									<Button
										href="/viewReport"
										color="alternative"
										size="xl"
										class="w-full text-xl py-8 rounded-lg bg-gradient-to-r from-blue-400 to-blue-600 text-white hover:from-blue-500 hover:to-blue-700 shadow-md hover:shadow-lg transition-all duration-300"
									>
										View Reports
									</Button>

									<div
										class="rounded-lg bg-gray-900/20 px-4 backdrop-blur-sm py-4"
										in:fade={{ duration: 300, delay: 600 }}
									>
										<div class="flex flex-row justify-center items-center w-full py-2">
											<Toggle onclick={toggleLockGenLinks}
												>{lockGenLinks ? 'Chart' : 'Record'}</Toggle
											>
										</div>
										<List tag="ul" list="none" class="flex flex-wrap gap-2 flex-row">
											{#each generators as gen}
												<div
													in:scale={{ duration: 200, delay: 700 + generators.indexOf(gen) * 50 }}
												>
													{#if lockGenLinks}
														<Li>
															<button
																onclick={() =>
																	completed_generators.includes(gen) && handleGenClick(gen)}
																class="inline-flex items-center justify-center rounded-full px-2 py-2 text-sm font-medium shadow-md transition-all duration-300
			{completed_generators.includes(gen)
																	? 'bg-blue-600 text-white hover:bg-blue-700 cursor-pointer'
																	: 'bg-gray-400 text-gray-200 cursor-not-allowed opacity-70'}"
															>
																{#if completed_generators.includes(gen)}
																	<span
																		class="inline-flex items-center justify-center rounded-full bg-green-500 text-white px-4 py-2 text-sm font-medium shadow-sm hover:bg-green-600"
																	>
																		{gen}
																	</span>
																{:else}
																	<span
																		class="inline-flex items-center justify-center rounded-full bg-red-500 text-white px-4 py-2 text-sm font-medium shadow-sm hover:bg-red-600"
																	>
																		{gen}
																	</span>
																{/if}
															</button>
														</Li>
													{:else}
														<Li>
															<A
																href={`/record?month=${CURRENT_MONTH.toLowerCase()}&gen=${gen}`}
																class="inline-flex items-center justify-center rounded-full px-2 py-2 text-sm font-medium shadow-md transition-all duration-300
															{completed_generators.includes(gen)
																	? 'bg-blue-600 text-white hover:bg-blue-700 cursor-pointer'
																	: 'bg-gray-400 text-gray-200  opacity-70'}"
															>
																{#if completed_generators.includes(gen)}
																	<span
																		class="inline-flex items-center justify-center rounded-full bg-green-500 text-white px-4 py-2 text-sm font-medium shadow-sm hover:bg-green-600"
																	>
																		{gen}
																	</span>
																{:else}
																	<span
																		class="inline-flex items-center justify-center rounded-full bg-red-500 text-white px-4 py-2 text-sm font-medium shadow-sm hover:bg-red-600"
																	>
																		{gen}
																	</span>
																{/if}
															</A>
														</Li>
													{/if}
												</div>
											{/each}
										</List>
									</div>
								</div>
							</div></Card
						>
					</div>
				</div>
			</Card>
		</div>
	</main>
{/if}
