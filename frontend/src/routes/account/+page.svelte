<script>
  import { onMount } from 'svelte';
  import Header from "../../includes/header.svelte";
  import Footer from "../../includes/footer.svelte";
  import ColorModes from "../../includes/color-modes.svelte";
  import { http } from '../../lib/http.js';
  import { goto } from '$app/navigation';

  let fileInput;
  let name = '';
  let email = '';
  let picture = '/assets/img/logo.png';
  let t = {};

  function afterHead() {
    name = user.name;
    email = user.email;
    if (user.picture) {
      picture = user.picture + "?" + unixTimestamp; 
    }
  }

  function submit(e) {
    http.post('account/info', Object.fromEntries((new FormData(e.target)).entries()))
      .then(() => {
        Swal.fire({
          position: 'top-end',
          icon: 'success',
          title: t.account.saved,
          showConfirmButton: false,
          timer: 1500
        }).then(() => {window.location.reload()});
      })
      .catch((error) => {
        Swal.fire({
            title: t.main.error,
            text: error.message,
            icon: 'error',
            confirmButtonText: t.main.ok
        });
      });
  }

  function deleteMe(e) {
    const form = e.target;
    const invalidElements = form.querySelectorAll('.needs-validation :invalid');
    if (invalidElements.length > 0) {
      return false;
    }
    http.post('account/info', Object.fromEntries((new FormData(form)).entries()))
      .then(() => {
        http.post('users/logout', null).then(user => { goto('/'); }).catch(error => { goto('/'); });
      });
  }

  // This function is called when the user selects a file
  function handleFileInput(event) {
    const file = event.target.files[0];
    
    // Create a FormData object and append the selected file
    const formData = new FormData();
    formData.append('file', file);
    
    // Send the file to the server using a POST request
    http.post('account/upload', formData)
      .then((data) => {
        window.location.reload();
      }).catch(error => { 
        Swal.fire({
            title: t.main.error,
            text: error.message,
            icon: 'error',
            confirmButtonText: t.main.ok
        });
      });
  }

  // This function is called when the "Change picture" button is clicked
  function handleButtonClick() {
    // Trigger a click event on the file input
    fileInput.click();
  }

  onMount(async () => {
    t = lng;

    // Add an event listener to the file input when the component is mounted
    fileInput.addEventListener('change', handleFileInput);
  });
</script>

<main class="container">

  <Header notify={afterHead} />
  
  <h1 class="h2 pt-xl-1 pb-3">{ t.menu?.account }</h1>

  <!-- Basic info -->
  <h2 class="h5 text-primary mb-4">{ t.account?.info }</h2>
  <form class="needs-validation border-bottom pb-3 pb-lg-4" on:submit|preventDefault={submit}>
    <div class="row pb-2">
      <div class="col-sm-6 mb-4">
        <label for="name" class="form-label fs-base">{ t.account?.name }</label>
        <input type="text" id="name" name="name" class="form-control form-control-lg" value="{name}" required>
      </div>
      <div class="col-sm-6 mb-4">
        <label for="email" class="form-label fs-base">{ t.account?.email }</label>
        <input type="email" id="email" name="email" class="form-control form-control-lg" value="{email}" required>
      </div>
    </div>
    <div class="d-flex mb-3">
      <button type="submit" class="btn btn-primary">{ t.account?.save }</button>
    </div>
  </form>

  <!-- Picture -->
  <h2 class="h5 text-primary pt-1 pt-lg-3 mt-4 mb-4">{ t.account?.picture }</h2>
  <div class="border-bottom pb-3 pb-lg-4">
    <input type="file" accept="image/png, image/gif, image/jpeg" style="display:none" bind:this={fileInput} />
    <!-- svelte-ignore a11y-click-events-have-key-events -->
    <!-- svelte-ignore a11y-img-redundant-alt -->
    <img src="{ picture }" alt="{ t.account?.change_picture }" title="{ t.account?.change_picture }" width="300" class="" style="cursor: pointer" on:click={handleButtonClick}>
  </div>

  <!-- Password -->
  <h2 class="h5 text-primary pt-1 pt-lg-3 mt-4 mb-4">{ t.account?.password }</h2>
  <form class="needs-validation border-bottom pb-3 pb-lg-4" on:submit|preventDefault={submit}>
    <div class="row">
      <div class="col-sm-6 mb-4">
        <label for="password" class="form-label fs-base">{ t.account?.current_password }</label>
        <input type="password" id="password" name="password" class="form-control form-control-lg">
      </div>
    </div>
    <div class="row pb-2">
      <div class="col-sm-6 mb-4">
        <label for="new_password" class="form-label fs-base">{ t.account?.new_password }</label>
        <div class="password-toggle">
          <input type="password" id="new_password" name="new_password" class="form-control form-control-lg" required minlength="8">
        </div>
      </div>
    </div>
    <div class="d-flex mb-3">
      <button type="submit" class="btn btn-primary">{ t.account?.update_password }</button>
    </div>
  </form>

  <!-- Delete account -->
  <h2 class="h5 text-primary pt-1 pt-lg-3 mt-4">{ t.account?.delete_account }</h2>
  <form class="needs-validation" novalidate on:submit|preventDefault={deleteMe}>
  <p>{ t.account?.delete_info }</p>
  <div class="form-check mb-4">
    <input type="checkbox" id="delete" name="delete" value="1" class="form-check-input" required>
    <label for="delete" class="form-check-label fs-base">{ t.account?.delete_account }</label>
  </div>
  <button type="submit" class="btn btn-danger">{ t.account?.delete }</button>
  </form>

  <Footer />
  <ColorModes />

</main>
