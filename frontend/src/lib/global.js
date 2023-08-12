import { goto } from '$app/navigation';

let isLoggedIn = () => document.cookie.includes('XSRF-TOKEN') ? true : false;

let checkLogin = () => isLoggedIn() ? true : goto('/');

export { isLoggedIn, checkLogin };
