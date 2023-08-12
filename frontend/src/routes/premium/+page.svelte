<script>
  import { onMount } from 'svelte';
  import Header from "../../includes/header.svelte";
  import Footer from "../../includes/footer.svelte";
  import ColorModes from "../../includes/color-modes.svelte";

  let t = {};

  onMount(async () => {
    t = lng;
  });
</script>

<main class="container">

  <Header notify={ () => {} } />

  <h1 class="h2 pt-xl-1 pb-3">{ t.menu?.premium }</h1>

  <div class="row row-cols-1 row-cols-md-3 mb-3 text-center justify-content-center">
    <div class="col">
      <div class="card mb-4 rounded-3 shadow-sm">
        <div class="card-header py-3">
          <h4 class="my-0 fw-normal">Free</h4>
        </div>
        <div class="card-body">
          <h1 class="card-title pricing-card-title">$0<small class="text-body-secondary fw-light">/mo</small></h1>
          <ul class="list-unstyled mt-3 mb-4">
            <li>10 users included</li>
            <li>2 GB of storage</li>
            <li>Email support</li>
            <li>Help center access</li>
          </ul>
          <button type="button" class="w-100 btn btn-lg btn-outline-primary">Sign up for free</button>
        </div>
      </div>
    </div>
    <div class="col">
      <div class="card mb-4 rounded-3 shadow-sm border-primary">
        <div class="card-header py-3 text-bg-primary border-primary">
          <h4 class="my-0 fw-normal">Premium</h4>
        </div>
        <div class="card-body">
          <h1 class="card-title pricing-card-title">$29<small class="text-body-secondary fw-light">/mo</small></h1>
          <ul class="list-unstyled mt-3 mb-4">
            <li>30 users included</li>
            <li>15 GB of storage</li>
            <li>Phone and email support</li>
            <li>Help center access</li>
          </ul>
          <button type="button" class="w-100 btn btn-lg btn-primary">Contact us</button>
        </div>
      </div>
    </div>
  </div>

  <h2 class="display-6 text-center mb-4">Compare plans</h2>

  <div class="table-responsive">
    <table class="table text-center">
      <thead>
        <tr>
          <th style="width: 34%;"></th>
          <th style="width: 33%;">Free</th>
          <th style="width: 33%;">Premium</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <th scope="row" class="text-start">Public</th>
          <td>✔</td>
          <td>✔</td>
        </tr>
        <tr>
          <th scope="row" class="text-start">Private</th>
          <td></td>
          <td>✔</td>
        </tr>
      </tbody>

      <tbody>
        <tr>
          <th scope="row" class="text-start">Permissions</th>
          <td>✔</td>
          <td>✔</td>
        </tr>
        <tr>
          <th scope="row" class="text-start">Sharing</th>
          <td></td>
          <td>✔</td>
        </tr>
        <tr>
          <th scope="row" class="text-start">Unlimited members</th>
          <td></td>
          <td>✔</td>
        </tr>
        <tr>
          <th scope="row" class="text-start">Extra security</th>
          <td></td>
          <td>✔</td>
        </tr>
      </tbody>
    </table>
  </div>


  <Footer />
  <ColorModes />

</main>
