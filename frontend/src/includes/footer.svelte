<script>
import { onMount } from 'svelte';

let t = {};

onMount(async () => {

  t = lng;

});

</script>

<footer class="py-3 my-4">
  <ul class="nav justify-content-center border-bottom pb-3 mb-3">
      <li class="nav-item"><a href="/{ t.code }/privacy" class="nav-link px-2 text-body-secondary">{ t.menu?.privacy }</a></li>
      <li class="nav-item"><a href="/{ t.code }/terms" class="nav-link px-2 text-body-secondary">{ t.menu?.terms }</a></li>
      <li class="nav-item"><a href="/{ t.code }/cookie" class="nav-link px-2 text-body-secondary">{ t.menu?.cookie }</a></li>
  </ul>
  <p class="text-center text-body-secondary">Match·E © { new Date().getFullYear() }</p>
</footer>
