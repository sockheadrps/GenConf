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
		Toggle
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
	let dashboardProps: DashboardProps = $state({ dataPayload: {
		get_estimates: {},
		total_fuel_needed: 0,
		estimate_fuel_cost: 0
	} });

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
		class="p-8 bg-gray-50 dark:bg-gray-900 w-screen h-[calc(100vh-100px)]"
		in:fade={{ duration: 300 }}
	>
		<div class="flex justify-center items-center" in:fly={{ y: 20, duration: 400 }}>
			<Card class="p-8 min-w-[1200px] flex flex-row">
				<div class="grid lg:grid-cols-2 gap-12 min-w-full">
					<div in:fly={{ x: -20, duration: 500, delay: 200 }}>
						<Card class="p-8 shadow-lg min-w-full h-full my-auto">
							{#if ready && (dashboardProps.dataPayload !== undefined)}
								<Label class="flex flex-col items-center justify-center text-2xl font-semibold mb-6"> {generatorName}</Label>
								<Dashboard dataPayload={dashboardProps.dataPayload} parentReady={ready} parentGeneratorName={generatorName} />
							{:else}
								<p>Loading...</p>
							{/if}
							<!-- <h3 class="text-2xl font-semibold mb-6">Key Features</h3>
            <Timeline class="space-y-8">
              <div in:fly={{ x: -20, duration: 300, delay: 400 }}>
                <TimelineItem title="Generator Data Collection" date="">
                  <p class="text-lg">
                    Record pre-run and post-run generator inspections with an easy to use interface
                  </p>
                </TimelineItem>
              </div>
              <div in:fly={{ x: -20, duration: 300, delay: 500 }}>
                <TimelineItem title="Monthly Reports" date="">
                  <p class="text-lg">
                    Generate detailed monthly reports of generator performance and maintenance records to view in the app or export as an excel file, customized into a table for easy viewing
                  </p>
                </TimelineItem>
              </div>
              <div in:fly={{ x: -20, duration: 300, delay: 600 }}>
                <TimelineItem title="Data Analysis" date="">
                  <p class="text-lg">
                    Track trends and compare metrics between pre and post run checks, and view historical data to see how generators have performed over time
                  </p>
                </TimelineItem>
              </div>
              <div in:fly={{ x: -20, duration: 300, delay: 600 }}>
                <TimelineItem title="Extendable format" date="">
                  <p class="text-lg">
                    Means this tool can be customized and configured to record and analyze data as ideas form and new requirements are identified
                  </p>
                </TimelineItem>
              </div>
            </Timeline> -->
						</Card>
					</div>

					<div in:fly={{ x: 20, duration: 500, delay: 200 }}>
						<Card class="p-8 shadow-lg min-w-full">
							<h3 class="text-2xl font-semibold mb-8">Quick Actions</h3>
							<div class="space-y-8">
								<div in:scale={{ duration: 300, delay: 400 }}>
									<Button href="/record" size="xl" class="w-full text-xl py-8"
										>Record Generator Check</Button
									>
								</div>
								<div in:scale={{ duration: 300, delay: 500 }}>
									<Button
										href="/viewReport"
										color="alternative"
										size="xl"
										class="w-full text-xl py-8">View Reports</Button
									>
								</div>

								<div
									class="rounded-lg bg-gray-900/20 px-4 backdrop-blur-sm"
									in:fade={{ duration: 300, delay: 600 }}
								>
									<div class="flex flex-row justify-center items-center w-full py-2">
										<Toggle onclick={toggleLockGenLinks}>{lockGenLinks ? 'Chart' : 'Record'}</Toggle
										>
									</div>
									<List tag="ul" list="none" class="flex flex-wrap gap-2 flex-row">
										{#each generators as gen}
											<div in:scale={{ duration: 200, delay: 700 + generators.indexOf(gen) * 50 }}>
												{#if lockGenLinks}
													<Li>
														<button
															onclick={() => completed_generators.includes(gen) && handleGenClick(gen)}
															class="inline-flex items-center rounded-full bg-blue-800/60 px-3 py-1.5 text-sm font-medium text-blue-100 shadow-sm transition-colors {completed_generators.includes(gen) ? 'hover:bg-blue-800 cursor-pointer' : 'opacity-50 cursor-not-allowed'}"
														>
															{#if completed_generators.includes(gen)}
																<span
																	class="inline-flex items-center rounded-full bg-green-800/60 px-3 py-1.5 text-sm font-medium text-green-100 shadow-sm transition-colors hover:bg-green-800"
																>
																	{gen}
																</span>
															{:else}
																<span
																	class="inline-flex items-center rounded-full bg-red-800/60 px-3 py-1.5 text-sm font-medium text-red-100 shadow-sm transition-colors"
																>
																	{gen}
																</span>
															{/if}
														</button>
													</Li>
												{:else}
													<!-- If lockGenLinks is false, render a link as usual -->
													<Li>
														<A href={`/record?month=${CURRENT_MONTH.toLowerCase()}&gen=${gen}`}>
															{#if completed_generators.includes(gen)}
																<span
																	class="inline-flex items-center rounded-full bg-green-800/60 px-3 py-1.5 text-sm font-medium text-green-100 shadow-sm transition-colors hover:bg-green-800"
																>
																	{gen}
																</span>
															{:else}
																<span
																	class="inline-flex items-center rounded-full bg-red-800/60 px-3 py-1.5 text-sm font-medium text-red-100 shadow-sm transition-colors hover:bg-red-800"
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
						</Card>
					</div>
				</div>
			</Card>
		</div>
	</main>
{/if}
