<script>
  import { onMount } from 'svelte';
  import Header from "../../includes/header.svelte";
  import Footer from "../../includes/footer.svelte";
  import ColorModes from "../../includes/color-modes.svelte";

  onMount(async () => {
    //
  });
</script>

<main class="container">

  <Header notify={ () => {} } />

  Followers

  <Footer />
  <ColorModes />

</main>
