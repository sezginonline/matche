<script>
import { onMount } from 'svelte';
import { http } from '../lib/http.js';
import { goto } from '$app/navigation';

export let notify;

const logout = async () => {
    http.post('users/logout', null).then(user => { goto('/'); }).catch(error => { goto('/'); });
};

let t = {};

let name = '';
let picture = '/assets/img/logo.png';
let wssToken = '';

function assignVars() {
  if (unixTimestamp === null) {
    unixTimestamp = Math.floor(new Date().getTime() / 1000)
  }

  name = user.name;
  if (user.picture) {
    picture = user.picture + "?" + unixTimestamp;
  }
  wssToken = user.wss_token;

  if (socket === null) {
    let domain = new URL(window.location.href).hostname;
    socket = new WebSocket(`wss://${domain}/wss?uid=${user.id}&token=${wssToken}`);
  }

  notify();
}

onMount(async () => {

  t = lng;

  if (user === null) {
    http.get('users/me').then(data => { user = data; assignVars(); });
  } else {
    assignVars();
  }

});

function goHome() {
    goto('./'); // on:click={goHome}
}

function setLanguage(code) {
    localStorage.setItem('language', code);
    window.location.reload();
}

</script>

<header class="d-flex flex-wrap align-items-center justify-content-center justify-content-md-between py-3 mb-4 border-bottom">
    <div class="mb-2 mb-md-0">
        <a href="./" class="d-flex align-items-center mb-3 mb-md-0 me-md-auto link-body-emphasis text-decoration-none">
            <img src="/assets/img/logo32.svg" style="border-radius: 0.375rem; width: 32px; height: 32px; margin-right: 10px; background-color: white;" alt="Match·E">
            <span class="fs-4 navbar-brand">Match·E</span>
        </a>
    </div>

    <ul class="nav col-12 col-md-auto mb-2 justify-content-center mb-md-0">
        <li><a href="./" class="nav-link px-2">{ t.menu?.discover }</a></li>
        <li><a href="broadcasts" class="nav-link px-2">{ t.menu?.broadcasts }</a></li>
        <li><a href="messages" class="nav-link px-2">{ t.menu?.messages } <span class="badge text-bg-primary d-none">1</span></a></li>
        <li><a href="followers" class="nav-link px-2">{ t.menu?.followers }</a></li>
    </ul>

    <div class="dropdown text-end ms-2">
        <a href="./" class="d-block text-decoration-none dropdown-toggle" data-bs-toggle="dropdown" aria-expanded="false">
            { t.label }
        </a>
        <ul class="dropdown-menu text-small">
            <li><button on:click={() => setLanguage("en")} class="dropdown-item">English</button></li>
            <li><button on:click={() => setLanguage("tr")} class="dropdown-item">Türkçe</button></li>
        </ul>
    </div>

    <div class="dropdown text-end ms-2">
        <a href="./" class="d-block link-dark text-decoration-none dropdown-toggle" data-bs-toggle="dropdown"
            aria-expanded="false">
            <img src="{ picture }" alt="mdo" width="32" height="32" class="rounded-circle">
        </a>
        <ul class="dropdown-menu text-small">
            <li><a class="dropdown-item" href="account">{ t.menu?.account }</a></li>
            <li><a class="dropdown-item" href="profile">{ t.menu?.profile }</a></li>
            <li><a class="dropdown-item" href="premium">{ t.menu?.premium }</a></li>
            <li>
                <hr class="dropdown-divider">
            </li>
            <li><a class="dropdown-item" href="/" on:click={logout}>{ t.menu?.logout }</a></li>
        </ul>
    </div>
</header>
