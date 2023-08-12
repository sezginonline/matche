<script>
  import { onMount } from 'svelte';
  import Header from "../../includes/header.svelte";
  import Footer from "../../includes/footer.svelte";
  import ColorModes from "../../includes/color-modes.svelte";
  import { goto } from '$app/navigation';

  onMount(async () => {
    //
  });
</script>

<main class="container">

  <Header notify={ () => {} } />

  Broadcasts

  <button on:click={ () => goto('broadcast') }>Create Broadcast</button>

  <button on:click={ () => goto('broadcast/1') }>Broadcast User 1</button>
  <button on:click={ () => goto('broadcast/2') }>Broadcast User 2</button>


  <Footer />
  <ColorModes />

</main>
