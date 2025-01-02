<script lang="ts" context="module">
  interface FuelEstimate {
    [key: string]: {
      generator_name: string;
      fuel_capacity: number;
      current_fuel_volume: number;
      fuel_delta: number;
    };
  }

  export interface dataPayload {
    dataPoint: FuelEstimate;
  }

  // Props

  let ApexChart: any = null;
  let generator: {
    generator_name: string;
    fuel_capacity: number;
    current_fuel_volume: number;
    fuel_delta: number;
  } | null = null;

  let pricePerGallon = 3.5;
  let costToFill = 0;
  let ready = false;

  // Wait for dataPayload and initialize chart
  if (typeof window !== 'undefined') {
    // Run in browser environment only
    if (dataPayload?.dataPoint) {
      // Ensure generator data is set
      const fuel_estimate = dataPayload.dataPoint;
      generator = Object.values(fuel_estimate)[0]; // Assuming the first generator is used

      // Calculate cost to fill
      costToFill =
        ((generator?.fuel_capacity ?? 0) -
          (generator?.current_fuel_volume ?? 0)) *
        pricePerGallon;

      // Dynamically import ApexCharts
      import('apexcharts').then((module) => {
        ApexChart = module.default;

        if (ApexChart && generator) {
          const options = {
            chart: {
              type: 'bar',
              height: '300',
            },
            title: {
              text: 'Fuel Statistics for ' + (generator.generator_name || ''),
              align: 'center',
            },
            xaxis: {
              categories: ['Fuel Capacity', 'Current Fuel Volume', 'Fuel Delta'],
            },
            yaxis: {
              title: {
                text: 'Fuel Volume (gallons)',
              },
            },
            plotOptions: {
              bar: {
                horizontal: true,
                columnWidth: '55%',
              },
            },
          };

          const series = [
            {
              name: 'Fuel Volume',
              data: [
                generator?.fuel_capacity,
                generator?.current_fuel_volume,
                generator?.fuel_delta,
              ],
            },
          ];

          // Initialize the chart
          const chart = new ApexChart(
            document.querySelector('#chart'),
            {
              chart: options.chart,
              title: options.title,
              xaxis: options.xaxis,
              yaxis: options.yaxis,
              plotOptions: options.plotOptions,
              series: series,
            }
          );
          chart.render();

          ready = true;
        }
      });
    }
  }

  // Update cost to fill when pricePerGallon changes
  export function updateCost(event: Event) {
    const target = event.target as HTMLInputElement;
    pricePerGallon = parseFloat(target.value);

    // Recalculate cost to fill
    costToFill =
      ((generator?.fuel_capacity ?? 0) -
        (generator?.current_fuel_volume ?? 0)) *
      pricePerGallon;
  }
</script>

<div>
  {#if typeof window !== 'undefined'}
    <div id="chart"></div>

    {#if ready}
      <p>Cost to fill: ${costToFill.toFixed(2)}</p>
      <label>
        Price per gallon:
        <input
          type="number"
          min="0"
          step="0.01"
          value={pricePerGallon}
          on:input={updateCost}
        />
      </label>
    {/if}
  {/if}
</div>

<style>
	.dashboard {
		padding: 2rem;
		max-width: 900px;
		margin: 0 auto;
	}

	.slider {
		@apply transition-all duration-200;
	}

	.slider::-webkit-slider-thumb {
		@apply appearance-none w-6 h-6 bg-blue-600 rounded-full cursor-pointer transition-all duration-200;
	}

	.slider::-webkit-slider-thumb:hover {
		@apply bg-blue-700 transform scale-110;
	}

	.slider::-moz-range-thumb {
		@apply w-6 h-6 bg-blue-600 border-none rounded-full cursor-pointer transition-all duration-200;
	}

	.slider::-moz-range-thumb:hover {
		@apply bg-blue-700 transform scale-110;
	}

	.chart-container {
		margin-top: 2rem;
		transition: all 0.3s ease;
	}
</style>
