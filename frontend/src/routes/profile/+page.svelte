<script>
  import { onMount } from 'svelte';
  import Header from "../../includes/header.svelte";
  import Footer from "../../includes/footer.svelte";
  import ColorModes from "../../includes/color-modes.svelte";
  import { http } from '../../lib/http.js';

  let location = null;
  let current_data = null;
  let t = {};

  let genderOptions = {};
  let educationOptions = {};
  let goalOptions = {};
  let relationshipOptions = {};

  let selectedGender = '';
  let selectedEducation = '';
  let selectedGoal = '';
  let selectedRelationship = '';

  function afterHead() {
    //
  }

  function submit(e) {

    const formData = new FormData(e.target);
    const lookingValues = Array.from(formData.getAll('looking'));
    const data = {
      ...Object.fromEntries(formData.entries()),
      looking: lookingValues
    };

    http.post('account/profile', data)
      .then(() => {
        Swal.fire({
          position: 'top-end',
          icon: 'success',
          title: t.account.saved,
          showConfirmButton: false,
          timer: 1500
        }).then(() => { /* window.location.reload() */ });
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

  function getProfile() {
    http.get('account/profile').then(data => { 
      current_data = data; 
      selectedGender = data.gender;
      selectedEducation = data.education;
      selectedGoal = data.goal;
      selectedRelationship = data.relationship;
    });
  }

  onMount(async () => {
    t = lng;

    genderOptions = {
      "": t.profile.select,
      male: t.profile.male,
      female: t.profile.female,
      na: t.profile.na,
    };
    educationOptions = {
      "": t.profile.select,
      elementary: t.profile.elementary,
      high: t.profile.high,
      bachelor: t.profile.bachelor,
      master: t.profile.master,
      doctorate: t.profile.doctorate,
    };
    goalOptions = {
      "": t.profile.select,
      short: t.profile.short,
      long: t.profile.long,
    };
    relationshipOptions = {
      "": t.profile.select,
      single: t.profile.single,
      married: t.profile.married,
    };

    getProfile();

    fetch('https://ipinfo.io/json')
    .then(res => res.json())
    .then(data => location = data)

  });
</script>

<main class="container">

  <Header notify={afterHead} />
  
  <h1 class="h2 pt-xl-1 pb-3">{ t.menu?.profile }</h1>

  <form class="needs-validation pb-3 pb-lg-4" on:submit|preventDefault={submit}>
    <div class="row pb-2">
      <div class="col-sm-4 mb-4">
        <label for="gender" class="form-label fs-base">{ t.profile?.gender }</label>
        <select id="gender" class="form-select form-select-lg" name="gender" bind:value={selectedGender}>
          {#each Object.entries(genderOptions) as [value, label]}
            <option value={value}>{label}</option>
          {/each}
        </select>
      </div>
      <div class="col-sm-4 mb-4">
        <label for="age" class="form-label fs-base">{ t.profile?.age }</label>
        <input type="number" id="age" name="age" class="form-control form-control-lg" value="{current_data?.age || ''}" min="18" max="99">
      </div>
      <div class="col-sm-4 mb-4">
        <label for="lookingM" class="form-label fs-base">{ t.profile?.looking }</label>
        <br>
        <input class="form-check-input" type="checkbox" name="looking" value="male" id="lookingM"
          checked={current_data?.looking?.includes("male")}>
        <label class="form-check-label" for="lookingM">{ t.profile?.male }</label>
        
        <input class="form-check-input" type="checkbox" name="looking" value="female" id="lookingF"
          checked={current_data?.looking?.includes("female")}>
        <label class="form-check-label" for="lookingF">{ t.profile?.female }</label>
        
        <input class="form-check-input" type="checkbox" name="looking" value="na" id="lookingN"
          checked={current_data?.looking?.includes("na")}>
        <label class="form-check-label" for="lookingN">{ t.profile?.na }</label>
      </div>
      <div class="col-sm-4 mb-4">
        <label for="height" class="form-label fs-base">{ t.profile?.height }</label>
        <input type="number" id="height" name="height" class="form-control form-control-lg" value="{current_data?.height || ''}" min="0" max="300">
      </div>
      <div class="col-sm-4 mb-4">
        <label for="weight" class="form-label fs-base">{ t.profile?.weight }</label>
        <input type="number" id="weight" name="weight" class="form-control form-control-lg" value="{current_data?.weight || ''}" min="0" max="300">
      </div>
      <div class="col-sm-4 mb-4">
        <label for="education" class="form-label fs-base">{ t.profile?.education }</label>
        <select id="education" class="form-select form-select-lg" name="education" bind:value={selectedEducation}>
          {#each Object.entries(educationOptions) as [value, label]}
            <option value={value}>{label}</option>
          {/each}
        </select>
      </div>
      <div class="col-sm-4 mb-4">
        <label for="goal" class="form-label fs-base">{ t.profile?.goal }</label>
        <select id="goal" class="form-select form-select-lg" name="goal" bind:value={selectedGoal}>
          {#each Object.entries(goalOptions) as [value, label]}
            <option value={value}>{label}</option>
          {/each}
        </select>
      </div>
      <div class="col-sm-4 mb-4">
        <label for="religion" class="form-label fs-base">{ t.profile?.religion }</label>
        <input type="text" id="religion" name="religion" class="form-control form-control-lg" value="{current_data?.religion || ''}">
      </div>
      <div class="col-sm-4 mb-4">
        <label for="relationship" class="form-label fs-base">{ t.profile?.relationship }</label>
        <select id="relationship" class="form-select form-select-lg" name="relationship" bind:value={selectedRelationship}>
          {#each Object.entries(relationshipOptions) as [value, label]}
            <option value={value}>{label}</option>
          {/each}
        </select>
      </div>
      <div class="col-6 mb-4">
        <label for="bio" class="form-label fs-base">{ t.profile?.yourself }</label>
        <textarea id="bio" name="bio" class="form-control form-control-lg" rows="4" placeholder="{ t.profile?.bio }">{current_data?.bio || ''}</textarea>
      </div>
      <div class="col-6 mb-4">
        <label for="partner" class="form-label fs-base">{ t.profile?.partner }</label>
        <textarea id="partner" name="partner" class="form-control form-control-lg" rows="4" placeholder="{ t.profile?.ideal }">{current_data?.partner || ''}</textarea>
      </div>
      <div class="col-sm-4 mb-4">
        <label for="city" class="form-label fs-base">{ t.profile?.city }</label>
        <select id="city" name="city" class="form-select form-select-lg" autocomplete="off">
          <option>{ location?.city || '' }</option>
        </select>
      </div>
      <div class="col-sm-4 mb-4">
        <label for="region" class="form-label fs-base">{ t.profile?.region }</label>
        <select id="region" name="region" class="form-select form-select-lg" autocomplete="off">
          <option>{ location?.region || '' }</option>
        </select>
      </div>
      <div class="col-sm-4 mb-4">
        <label for="country" class="form-label fs-base">{ t.profile?.country }</label>
        <select id="country" name="country" class="form-select form-select-lg" autocomplete="off">
          <option>{ location?.country || '' }</option>
        </select>
      </div>
      <input type="hidden" name="location" value="{ location?.loc }">
    </div>
    <div class="d-flex mb-3">
      <button type="submit" class="btn btn-primary">{ t.profile?.save }</button>
    </div>
  </form>

  <Footer />
  <ColorModes />

</main>
