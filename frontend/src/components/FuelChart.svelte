<script>
  import { onMount } from 'svelte';

  let ApexChart;
  let isClient = false;

  // Options and data for the chart
  export let options = {
    chart: {
      type: 'bar',
    },
    title: {
      text: 'Generator Fuel Statistics',
    },
    xaxis: {
      categories: [], // Add categories dynamically
    },
    yaxis: {
      title: {
        text: 'Fuel Volume',
      },
    },
    plotOptions: {
      bar: {
        horizontal: false,
        columnWidth: '55%',
      },
    },
  };

  export let series = [];

  onMount(async () => {
    // Only load ApexCharts on the client
    isClient = true;
    const module = await import('apexcharts');
    ApexChart = module.default;

    if (ApexChart && typeof window !== 'undefined') {
      const chart = new ApexChart(document.querySelector('#chart'), {
        chart: options.chart,
        title: options.title,
        xaxis: options.xaxis,
        yaxis: options.yaxis,
        plotOptions: options.plotOptions,
        series,
      });
      chart.render();
    }
  });
</script>

{#if isClient}
  <div id="chart"></div>
{:else}
  <p>Loading chart...</p>
{/if}
