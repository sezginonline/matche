<script>
import { page } from "$app/stores";
import { onMount } from 'svelte';
import Header from '../includes/header.svelte';
import Footer from "../includes/footer.svelte";

onMount(async () => {
    
});
</script>

<svelte:head>
    <title>Match·E</title> 
</svelte:head>

<main class="container"> 
    <Header notify={ () => {} } />
    <h1 style="margin-top:  200px; margin-bottom: 300px; text-align: center">{$page.status} {$page.error.message}</h1>
    <Footer />
</main>
