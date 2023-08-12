let language = localStorage.getItem('language') ?? 'en';
let script = document.createElement('script'); script.src = '/assets/lang/' + language + '.js?v=1.0.0';
document.getElementsByTagName('body')[0].appendChild(script);

let user = null;
let socket = null;
let dataChannel = null;
let unixTimestamp = null;
