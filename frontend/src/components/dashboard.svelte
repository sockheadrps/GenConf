<svelte:options runes={false} />
<script lang="ts">
  
	import { onDestroy } from 'svelte';

	interface FuelEstimate {
		[key: string]: {
			generator_name: string;
			fuel_capacity: number;
			current_fuel_volume: number;
			fuel_delta: number;
		};
	}

	interface dataPayloadObj {
		get_estimates: FuelEstimate;
		total_fuel_needed: number;
		estimate_fuel_cost: number;
	}

	let fuel_estimate: FuelEstimate | null = null;
	export let dataPayload: dataPayloadObj | string;
	export let parentReady = false;
	export let parentGeneratorName: string;

	let totalFuelDelta = 0;
	let totalFuelCapacity = 0;
	let pricePerGallon = 3.5;
	let totalCostToFill = 0;
	let costsToFill: { [key: string]: number } = {};
	let ApexChart: any = null;
	let chartInstance: any = null; // Single chart instance

	// Reactive block to process dataPayload
	$: if (parentReady && dataPayload) processDataPayload();

	function processDataPayload() {
		try {
			if (typeof dataPayload === 'string') {
				dataPayload = JSON.parse(dataPayload);
			}

			if (typeof dataPayload === 'object' && dataPayload?.get_estimates) {
				fuel_estimate = dataPayload.get_estimates;

				// Calculate total fuel delta and capacity
				totalFuelDelta = Object.values(fuel_estimate).reduce(
					(acc, generator) => acc + generator.fuel_delta,
					0
				);
				totalFuelCapacity = Object.values(fuel_estimate).reduce(
					(acc, generator) => acc + generator.fuel_capacity,
					0
				);

				// Update costs
				updateCostsToFill();
			} else {
				console.error('Invalid dataPayload structure');
			}
		} catch (error) {
			console.error('Error processing dataPayload:', error);
		}
	}

	// Function to update costs
	function updateCostsToFill() {
		if (fuel_estimate) {
			costsToFill = Object.fromEntries(
				Object.entries(fuel_estimate).map(([key, generator]) => [
					key,
					(generator.fuel_capacity - generator.current_fuel_volume) * pricePerGallon
				])
			);
		}
		totalCostToFill = totalFuelDelta * pricePerGallon;
	}

	// Function to initialize summary chart
	function initializeSummaryChart() {
		if (!dataPayload) return;

		import('apexcharts').then((module) => {
			ApexChart = module.default;

			// Destroy existing chart instance if any
			if (chartInstance) {
				chartInstance.destroy();
			}

			// Calculate percentage of fuel filled
			const fuelPercentage = ((totalFuelCapacity - totalFuelDelta) / totalFuelCapacity) * 100;

			const options = {
				chart: {
					type: 'radialBar',
					height: 400,
					animations: {
						enabled: true,
						easing: 'easeinout',
						speed: 800
					},
					background: 'transparent'
				},
				plotOptions: {
					radialBar: {
						startAngle: -120,
						endAngle: 120,
						hollow: {
							size: '70%',
							background: '#1f2937'
						},
						track: {
							background: '#374151',
							strokeWidth: '97%'
						},
						dataLabels: {
							name: {
								offsetY: -10,
								fontSize: '16px',
								fontWeight: 'bold',
								color: '#FFFFFF'
							},
							value: {
								offsetY: 5,
								fontSize: '18px',
								fontWeight: 'bold',
								color: '#34D399',
								formatter: () => `${fuelPercentage.toFixed(1)}%`
							}
						}
					}
				},
				series: [fuelPercentage],
				labels: ['Total fuel needed: ' + totalFuelDelta + ' gal'],
				colors: ['#34D399'] // Bright green for fuel level
			};

			const chartContainer = document.querySelector('#summary-chart');
			if (chartContainer) {
				chartInstance = new ApexChart(chartContainer, options);
				chartInstance.render();
			}
		});
	}

	// Function to initialize generator-specific chart
	function initializeGeneratorChart(generatorName: string) {
		if (!fuel_estimate) return;

		import('apexcharts').then((module) => {
			ApexChart = module.default;

			const generator = fuel_estimate[generatorName];
			if (!generator) return;

			// Destroy the existing chart instance if it exists
			if (chartInstance) {
				chartInstance.destroy();
			}

			const options = {
				chart: {
					type: 'donut',
					height: 400,
					animations: {
						enabled: true,
						easing: 'easeinout',
						speed: 800
					},
					background: 'transparent'
				},
				title: {
					text: `${generator.generator_name} Fuel`,
					align: 'center',
					style: {
						fontSize: '18px',
						fontWeight: 'bold',
						color: '#FFFFFF'
					}
				},
				labels: ['Current Fuel Volume', 'Fuel Delta'],
				series: [generator.current_fuel_volume || 0, generator.fuel_delta || 0],
				colors: ['#34D399', '#EF4444'], // Green for current fuel, red for delta
				legend: {
					position: 'bottom',
					horizontalAlign: 'center',
					fontSize: '12px',
					labels: {
						colors: ['#FFFFFF']
					},
					itemMargin: {
						vertical: 8
					}
				},
				tooltip: {
					theme: 'dark',
					y: {
						formatter: (val) => `${val.toFixed(0)} gal`
					}
				},
				dataLabels: {
					enabled: true,
					style: {
						fontSize: '14px',
						fontWeight: 'bold',
						colors: ['#FFFFFF']
					},
					formatter: (val) => `${val.toFixed(1)}%`
				}
			};

			// Use dynamic chart container ID
			const chartContainer = document.querySelector(`#chart-${generatorName}`);
			if (chartContainer) {
				chartInstance = new ApexChart(chartContainer, options);
				chartInstance.render();
			}
		});
	}

  function updateCostOnSliderUp(generatorName?: string) {
		if (generatorName && fuel_estimate) {
			// Update cost for a specific generator
			const generator = fuel_estimate[generatorName];
			costsToFill[generatorName] =
				(generator.fuel_capacity - generator.current_fuel_volume) * pricePerGallon;
		} else {
			// Update total cost
			totalCostToFill = totalFuelDelta * pricePerGallon;
		}
	}

	// Reactive block to initialize summary chart
	$: {
		if (parentGeneratorName && fuel_estimate) {
			initializeGeneratorChart(parentGeneratorName);
		} else if (dataPayload) {
			initializeSummaryChart();
		}
	}

	// Clean up chart on destroy
	onDestroy(() => {
		if (chartInstance) {
			chartInstance.destroy();
			chartInstance = null;
		}
	});
</script>

<div class="dashboard">
	{#if parentGeneratorName && fuel_estimate}
		{#each Object.entries(fuel_estimate) as [key, generator]}
			{#if key === parentGeneratorName}
				<div class="chart-container bg-gray-800">
					<div id={`chart-${key}`}></div>
					<p>
						<strong>{generator.generator_name}</strong> - Cost to fill: $
						{costsToFill[key]?.toFixed(2) || '0.00'}
					</p>
					<label for={`price-slider-${key}`}
						>Price per gallon: $<span id="price-value">{pricePerGallon.toFixed(2)}</span></label
					>
					<input
						type="range"
						id={`price-slider-${key}`}
						min="0"
						max="10"
						step="0.01"
						bind:value={pricePerGallon}
						on:mouseup={() => updateCostOnSliderUp(key)}
					/>
				</div>
			{/if}
		{/each}
	{:else}
		<div class="chart-container bg-gray-800">
			<div id="summary-chart"></div>
			<div class="slider-container">
				<label>Estimated Cost: $<span id="total-cost">{totalCostToFill.toFixed(2)}</span></label>
				<label for="summary-price-slider"
					>Price per gallon: $<span id="price-value">{pricePerGallon.toFixed(2)}</span></label
				>
				<input
					id="summary-price-slider"
					type="range"
					min="0"
					max="10"
					step="0.01"
					bind:value={pricePerGallon}
					on:mouseup={() => updateCostOnSliderUp()}
				/>
			</div>
		</div>
	{/if}
</div>

<style>
	.chart-container {
		margin: auto;
		padding: 1.5rem;
		border-radius: 12px;
		background-color: #1f2937; /* Dark gray for modern look */
		box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
		color: #ffffff; /* Ensure text is readable */
		transition: all 0.3s ease-in-out;
		text-align: center;
	}

	input[type='range'] {
		width: 100%;
		margin: 1rem 0;
		accent-color: #34d399; /* Matches the green chart color */
		cursor: pointer;
	}

	.slider-container {
		margin-top: 1rem;
		text-align: center;
	}

	label {
		font-size: 14px;
		color: #ffffff;
		margin-bottom: 0.5rem;
		display: block;
	}
</style>
