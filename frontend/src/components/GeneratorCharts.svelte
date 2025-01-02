<script>
  import { onMount } from 'svelte';

  let ApexChart;
  let isClient = false;

  // Check if running in the browser
  onMount(async () => {
    isClient = true;

    // Dynamically import ApexCharts only on the client
    const module = await import('apexcharts');
    ApexChart = module.default;
  });

  const options = {
    chart: {
      type: 'bar',
    },
    title: {
      text: 'Generator Fuel Statistics',
    },
    xaxis: {
      categories: ['GEN-R2', 'GEN-R3', 'GEN-E3', 'GEN-F3'], // Add more as necessary
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

  const series = [
    {
      name: 'Current Fuel Volume',
      data: [7546, 7546, 7007, 6737], // Add corresponding data
    },
    {
      name: 'Fuel Delta',
      data: [1437, 1437, 1976, 2246], // Add corresponding data
    },
    {
      name: 'Fuel Capacity',
      data: [8983, 8983, 8983, 8983], // Add corresponding data
    },
  ];
</script>

{#if isClient && ApexChart}
  <!-- Render ApexChart only on the client -->
  <ApexChart type="bar" options={options} series={series} />
{:else}
  <p>Loading chart...</p>
{/if}
