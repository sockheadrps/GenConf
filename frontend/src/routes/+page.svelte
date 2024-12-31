<script lang="ts">
  import { Card, Button, Timeline, TimelineItem, List, Li, A } from 'flowbite-svelte';
  import { onMount } from 'svelte';
  import { fade, fly, scale } from 'svelte/transition';

  let completed_generators: string[] = [];
  let generators = [
    "GEN-A3", "GEN-A2", "GEN-B3", "GEN-B2", "GEN-C3", "GEN-C2",
    "GEN-D3", "GEN-D2", "GEN-R3", "GEN-R2", "GEN-A1", "GEN-B1",
    "GEN-C1", "GEN-D1", "GEN-E2", "GEN-R1", "GEN-H3", "GEN-I3",
    "GEN-J3", "GEN-G3", "GEN-F3", "GEN-E3"
  ];
	async function fetchCompletedGenerators() {
		// /records/{month} lowercase month
		const uri = `http://127.0.0.1:8100/records/${getCurrentMonth().toLowerCase()}`;
		const response = await fetch(uri);
		const data = await response.json();
		return data.records;
	}
  onMount(async () => {
    completed_generators = await fetchCompletedGenerators();
  });

  $: uncompleted_generators = generators.filter(gen => !completed_generators.includes(gen));


  function getCurrentMonth() {
		const date = new Date();
		const month = date.toLocaleString('default', { month: 'long' });
		return month;
	}
</script>

<main class="p-8 bg-gray-50 dark:bg-gray-900 w-screen h-[calc(100vh-100px)]" in:fade={{ duration: 300 }}>
  <div class="flex justify-center items-center" in:fly={{ y: 20, duration: 400 }}>
    <Card class="p-8 min-w-[1200px] flex flex-row">
      
      <div class="grid lg:grid-cols-2 gap-12 min-w-full">
        <div in:fly={{ x: -20, duration: 500, delay: 200 }}>
          <Card class="p-8 shadow-lg min-w-full">
            <h3 class="text-2xl font-semibold mb-6">Key Features</h3>
            <Timeline class="space-y-8">
              <div in:fly={{ x: -20, duration: 300, delay: 400 }}>
                <TimelineItem title="Generator Checks" date="">
                  <p class="text-lg">
                    Record pre-run and post-run generator inspections including fuel levels, battery voltage, and more
                  </p>
                </TimelineItem>
              </div>
              <div in:fly={{ x: -20, duration: 300, delay: 500 }}>
                <TimelineItem title="Monthly Reports" date="">
                  <p class="text-lg">
                    Generate detailed monthly reports of generator performance and maintenance records to view in the app or export as a zipped excel file
                  </p>
                </TimelineItem>
              </div>
              <div in:fly={{ x: -20, duration: 300, delay: 600 }}>
                <TimelineItem title="Data Analysis" date="">
                  <p class="text-lg">
                    Track trends and compare metrics between pre and post run checks
                  </p>
                </TimelineItem>
              </div>
            </Timeline>
          </Card>
        </div>

        <div in:fly={{ x: 20, duration: 500, delay: 200 }}>
          <Card class="p-8 shadow-lg min-w-full">
            <h3 class="text-2xl font-semibold mb-8">Quick Actions</h3>
            <div class="space-y-8">
              <div in:scale={{ duration: 300, delay: 400 }}>
                <Button href="/record" size="xl" class="w-full text-xl py-8">Record Generator Check</Button>
              </div>
              <div in:scale={{ duration: 300, delay: 500 }}>
                <Button href="/viewReport" color="alternative" size="xl" class="w-full text-xl py-8">View Reports</Button>
              </div>

              <div class="rounded-lg bg-gray-900/20 px-4 py-4 backdrop-blur-sm" in:fade={{ duration: 300, delay: 600 }}>
                <p class="text-sm font-medium text-gray-200 mb-2">Generator Status This Month:</p>
                <List tag="ul" list="none" class="flex flex-wrap gap-2 flex-row">
                  {#each generators as gen}
                    <div in:scale={{ duration: 200, delay: 700 + generators.indexOf(gen) * 50 }}>
                      <Li>
                        <A href={`/record?month=${getCurrentMonth().toLowerCase()}&gen=${gen}`}>
                          {#if completed_generators.includes(gen)}
                            <span class="inline-flex items-center rounded-full bg-green-800/60 px-3 py-1.5 text-sm font-medium text-green-100 shadow-sm transition-colors hover:bg-green-800">
                              {gen}
                            </span>
                          {:else}
                            <span class="inline-flex items-center rounded-full bg-red-800/60 px-3 py-1.5 text-sm font-medium text-red-100 shadow-sm transition-colors hover:bg-red-800">
                              {gen}
                            </span>
                          {/if}
                        </A>
                      </Li>
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
