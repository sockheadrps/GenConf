<script lang="ts">
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

  let generator = null;
  let pricePerGallon = 3.5;
  let costToFill = 0;
  let ready = false;
  let ApexChart: any = null;

  // Reactive block to process dataPayload
  $: if (parentReady && dataPayload) {
    try {
      // Parse dataPayload if it is a string
      if (typeof dataPayload === 'string') {
        dataPayload = JSON.parse(dataPayload);
      }

      // Validate dataPayload structure
      if (typeof dataPayload === 'object' && dataPayload?.get_estimates) {
        fuel_estimate = dataPayload.get_estimates;
        const values = Object.values(fuel_estimate);
        generator = values[0] || null;

        if (generator) {
          costToFill =
            ((generator.fuel_capacity ?? 0) - (generator.current_fuel_volume ?? 0)) *
            pricePerGallon;
        }
      } else {
        console.error('Invalid dataPayload structure');
      }
    } catch (error) {
      console.error('Error processing dataPayload:', error);
    }
  }

  // Reactive block to initialize ApexCharts
  $: if (parentReady && fuel_estimate && generator) {
    import('apexcharts').then((module) => {
      ApexChart = module.default;

      if (ApexChart) {
        const options = {
          chart: {
            type: 'bar',
            height: '300',
          },
          title: {
            text: 'Fuel Statistics for ' + generator.generator_name,
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
          series: [
            {
              name: 'Fuel Volume',
              data: [
                generator.fuel_capacity,
                generator.current_fuel_volume,
                generator.fuel_delta,
              ],
            },
          ],
        };

        const chartContainer = document.querySelector('#chart');
        if (chartContainer) {
          const chart = new ApexChart(chartContainer, options);
          chart.render();
          ready = true;
        }
      }
    });
  }

  // Function to update cost dynamically
  export function updateCost(event: Event) {
    const target = event.target as HTMLInputElement;
    pricePerGallon = parseFloat(target.value) || 0;

    if (generator) {
      costToFill =
        ((generator.fuel_capacity ?? 0) - (generator.current_fuel_volume ?? 0)) *
        pricePerGallon;
    }
  }
</script>

<div>
  <div id="chart"></div>

  <p>Cost to fill: ${costToFill.toFixed(2)}</p>
  {#if ready}
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
</div>

<style>
  .dashboard {
    padding: 2rem;
    max-width: 900px;
    margin: 0 auto;
  }
  .chart-container {
    margin-top: 2rem;
    transition: all 0.3s ease;
  }
</style>
