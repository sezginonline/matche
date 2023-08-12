<script>
import { onMount } from 'svelte';
import Header from "../../includes/header.svelte";

async function webrtc() {
    const localVideo = document.querySelector('#localVideo');
    const remoteVideo = document.querySelector('#remoteVideo');
    const url = new URL(window.location.href);
    const domain = url.hostname;
    const websocketUrl = `wss://${domain}/wss/rtc`;

    let localStream = await navigator.mediaDevices.getUserMedia({video: true, audio: true});
    localVideo.srcObject = localStream;

    const configuration = {'iceServers': [{'urls': 'stun:stun.l.google.com:19302'}]};
    let peerConnection = new RTCPeerConnection(configuration);

    var handleDataChannelOpen = function (event) {
      //
    };

    var handleDataChannelMessageReceived = function (event) {
      document.getElementById('chat').value += event.data + '\n';
    };

    var handleDataChannelError = function (error) {
      //
    };

    var handleDataChannelClose = function (event) {
      // Recreate the data channel
      createChannel();
    };

    var handleChannelCallback = function (event) {
      dataChannel = event.channel;
      setChannel();
    };

    peerConnection.ondatachannel = handleChannelCallback;

    function createChannel() {
      dataChannel = peerConnection.createDataChannel("chat", {});
      setChannel();
    }

    function setChannel() {
      dataChannel.onopen = handleDataChannelOpen;
      dataChannel.onmessage = handleDataChannelMessageReceived;
      dataChannel.onerror = handleDataChannelError;
      dataChannel.onclose = handleDataChannelClose;
    }

    createChannel();

    peerConnection.addEventListener('icecandidate', async (event) => {
        if (event.candidate) {
            const ws = new WebSocket(websocketUrl);
            ws.addEventListener('open', () => {
                ws.send(JSON.stringify({'ice': event.candidate}));
            });
        }
    });
    peerConnection.addEventListener('track', (event) => {
        remoteVideo.srcObject = event.streams[0];
    });
    localStream.getTracks().forEach(track => peerConnection.addTrack(track, localStream));

    const offer = await peerConnection.createOffer();
    await peerConnection.setLocalDescription(offer);

    const ws = new WebSocket(websocketUrl);
    ws.addEventListener('open', () => {
        ws.send(JSON.stringify({'sdp': peerConnection.localDescription}));
    });
    ws.addEventListener('message', async event => {
        const message = JSON.parse(event.data);
        if (message.sdp) {
            if (message.sdp.type === 'offer') {
                await peerConnection.setRemoteDescription(new RTCSessionDescription(message.sdp));
                const answer = await peerConnection.createAnswer();
                await peerConnection.setLocalDescription(answer);
                ws.send(JSON.stringify({'sdp': peerConnection.localDescription}));
            } else if (message.sdp.type === 'answer') {
                await peerConnection.setRemoteDescription(new RTCSessionDescription(message.sdp));
            }
        } else if (message.ice) {
            if (peerConnection.remoteDescription) {
                await peerConnection.addIceCandidate(new RTCIceCandidate(message.ice));
            } else {
                peerConnection.pendingIceCandidates = peerConnection.pendingIceCandidates || [];
                peerConnection.pendingIceCandidates.push(message.ice);
            }
        }
    });
}

function sendMessage() {
    const chat = document.getElementById('chat');
    const message = document.getElementById('message').value;
    chat.value += message + '\n';
    dataChannel.send(message)
}

onMount(async () => {

  webrtc();

});
</script>

<main class="container">
  <Header notify={() => {}} />

  <!-- Page content -->
  <section class="container">
    <!-- Breadcrumb -->
    <nav class="pt-4 mt-lg-3" aria-label="breadcrumb">
      <ol class="breadcrumb mb-0">
        <li class="breadcrumb-item">
          <a href="landing-online-courses.html"
            ><i class="bx bx-home-alt fs-lg me-1" />Home</a
          >
        </li>
        <li class="breadcrumb-item active" aria-current="page">Search</li>
      </ol>
    </nav>

    <!-- Page title + Filters -->
    <div
      class="d-lg-flex align-items-center justify-content-between py-4 mt-lg-2"
    >
      <h1 class="me-3">Search</h1>
      <div class="d-md-flex mb-3">
        <select
          class="form-select me-md-4 mb-2 mb-md-0"
          style="min-width: 240px;"
        >
          <option value="All">All categories</option>
          <option value="Web Development">Web Development</option>
          <option value="Mobile Development">Mobile Development</option>
          <option value="Programming">Programming</option>
          <option value="Game Development">Game Development</option>
          <option value="Software Testing">Software Testing</option>
          <option value="Software Engineering">Software Engineering</option>
          <option value="Network & Security">Network &amp; Security</option>
        </select>
        <div class="position-relative" style="min-width: 300px;">
          <input
            type="text"
            class="form-control pe-5"
            placeholder="Search courses"
          />
          <i
            class="bx bx-search text-nav fs-lg position-absolute top-50 end-0 translate-middle-y me-3"
          />
        </div>
      </div>
    </div>

    <video id="localVideo" width="320" height="240" autoplay muted><track kind="captions" /></video>
    <video id="remoteVideo" width="320" height="240" autoplay><track kind="captions" /></video>

    <textarea id="chat"></textarea>
    <input type="text" id="message">
    <button on:click={sendMessage}>Send</button>

  </section>
</main>
