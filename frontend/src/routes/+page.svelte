<script>
import { onMount } from 'svelte';
import { http } from '../lib/http.js';
import Header from '../includes/header.svelte';
import Footer from "../includes/footer.svelte";
import ColorModes from '../includes/color-modes.svelte';
import InfiniteLoading from 'svelte-infinite-loading';

let t = {};

let page = 1;
let list = [];
let gender = 'all';
let infiniteId = Symbol();

function infiniteHandler({ detail: { loaded, complete } }) {
  http.get(`users/discover?page=${page}&gender=${gender}`).then(data => { 
    if (data.length) {
      page++; 
      list = [...list, ...data];
      loaded();
    } else {
      complete();
    }
  });
}
function changeGender() {
  page = 1;
  list = [];
  infiniteId = Symbol();
}

onMount(async () => {

  t = lng;

});

</script>

<main class="container">  

  <Header notify={ () => {} } />

  <div class="d-lg-flex align-items-center justify-content-between py-3 mt-lg-4">
    <h1 class="me-3">{ t.menu?.discover }</h1>
    <div class="d-md-flex mb-3">
      <select class="form-select me-md-4 mb-2 mb-md-0" style="min-width: 240px;" bind:value={gender} on:change={changeGender}>
        <option value="all">All genders</option>
        <option value="male">Male</option>
        <option value="female">Female</option>
        <option value="n/a">Not specified</option>
      </select>
      <div class="position-relative" style="min-width: 300px;">
        <input type="text" class="form-control pe-5" placeholder="Search">
        <i class="bx bx-search text-nav fs-lg position-absolute top-50 end-0 translate-middle-y me-3"></i>
      </div>
    </div>
  </div>

  <div class="row row-cols-1 row-cols-sm-2 row-cols-md-3 row-cols-lg-4 g-4 pb-lg-2 pb-xl-3">

    {#each list as user, index}
      { #if user.picture }
        <div class="col" data-num={index + 1}>
          <div class="card card-hover border-0 bg-transparent">
            <div class="position-relative text-center">
              <a href="user/{user.id}">
                <img src="{ user.picture?.replace(/=s\d+/, '=s0') }" width="250" class="rounded-3" alt="">
              </a>
              <h3 class="fs-lg fw-semibold pt-1 mb-2">{ user.name }</h3>
            </div>
          </div>
        </div>
      {/if}
    {/each}
    <InfiniteLoading on:infinite={infiniteHandler} identifier={infiniteId} />

  </div>

  <Footer />
  <ColorModes />
  
</main>
