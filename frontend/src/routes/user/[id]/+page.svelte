<script>
  import { onMount } from 'svelte';
  import Header from "../../../includes/header.svelte";
  import Footer from "../../../includes/footer.svelte";
  import ColorModes from "../../../includes/color-modes.svelte";

  let userId = 0;

  onMount(async () => {
    userId = window.location.pathname.split("/").pop();
  });
</script>

<main class="container">

  <Header notify={ () => {} } />

  <h1>userId: {userId}</h1>

  <Footer />
  <ColorModes />

</main>
