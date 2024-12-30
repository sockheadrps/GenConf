<script lang="ts">
  import '../app.css';
  let { children } = $props();
	
</script>

<!-- Top navigation bar -->
<header class="bg-blue-500 dark:bg-gray-800 text-white p-4">
	<nav class="container mx-auto flex justify-between items-center">
		<h1 class="text-xl font-semibold">Genlog</h1>
		<ul class="flex space-x-6">
			<li><a href="/record" class="hover:text-blue-300">Record</a></li>
			<li><a href="/view" class="hover:text-blue-300">View</a></li>
			<li><a href="/export" class="hover:text-blue-300">Export</a></li>
		</ul>

	</nav>
</header>

<main>
  {@render children()}
</main>
