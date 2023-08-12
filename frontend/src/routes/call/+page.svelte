<script>
  import { onMount } from 'svelte';
  import Header from "../../includes/header.svelte";
  
  async function webrtc() {

    var to = 20;

    const startButton = document.getElementById('startButton');
    const hangupButton = document.getElementById('hangupButton');
    hangupButton.disabled = true;
    const sendButton = document.getElementById('sendButton');
    sendButton.onclick = sendData;

    const localVideo = document.getElementById('localVideo');
    const remoteVideo = document.getElementById('remoteVideo');

    const dataChannelSend = document.querySelector('textarea#dataChannelSend');
    const dataChannelReceive = document.querySelector('textarea#dataChannelReceive');

    let pc;
    let localStream;
    let sendChannel;
    let receiveChannel;

    socket.onmessage = e => {
      const message = JSON.parse(e.data);
      if (!localStream) {
        return;
      }
      switch (message.type) {
        case 'offer':
          handleOffer(message);
          break;
        case 'answer':
          handleAnswer(message);
          break;
        case 'candidate':
          handleCandidate(message);
          break;
        case 'ready':
          if (pc) {
            return;
          }
          makeCall();
          break;
        case 'bye':
          if (pc) {
            hangup();
          }
          break;
        default:
          break;
      }
    };

    startButton.onclick = async () => {
      localStream = await navigator.mediaDevices.getUserMedia({audio: true, video: true});
      localVideo.srcObject = localStream;
      startButton.disabled = true;
      hangupButton.disabled = false;
      socket.send(JSON.stringify({ type: 'ready', "to": to }));
    };

    hangupButton.onclick = async () => {
      hangup();
      socket.send(JSON.stringify({ type: 'bye', "to": to }));
    };

    async function hangup() {
      if (pc) {
        pc.close();
        pc = null;
      }
      sendChannel = null;
      receiveChannel = null;

      localStream.getTracks().forEach(track => track.stop());
      localStream = null;
      startButton.disabled = false;
      sendButton.disabled = true;
      hangupButton.disabled = true;
      dataChannelSend.value = '';
      dataChannelReceive.value = '';
      dataChannelSend.disabled = true;
    };

    function createPeerConnection() {
      pc = new RTCPeerConnection();
      pc.onicecandidate = e => {
        const message = {
          type: 'candidate',
          candidate: null,
          to: to
        };
        if (e.candidate) {
          message.candidate = e.candidate.candidate;
          message.sdpMid = e.candidate.sdpMid;
          message.sdpMLineIndex = e.candidate.sdpMLineIndex;
        }
        socket.send(JSON.stringify(message));
      };
      pc.ontrack = e => remoteVideo.srcObject = e.streams[0];
      localStream.getTracks().forEach(track => pc.addTrack(track, localStream));
    }

    async function makeCall() {
      await createPeerConnection();

      sendChannel = pc.createDataChannel('sendDataChannel');
      sendChannel.onopen = onSendChannelStateChange;
      sendChannel.onmessage = onSendChannelMessageCallback;
      sendChannel.onclose = onSendChannelStateChange;

      const offer = await pc.createOffer();
      socket.send(JSON.stringify({type: 'offer', sdp: offer.sdp, to: to}));
      await pc.setLocalDescription(offer);
    }

    async function handleOffer(offer) {
      if (pc) {
        return;
      }
      await createPeerConnection();
      pc.ondatachannel = receiveChannelCallback;
      await pc.setRemoteDescription(offer);

      const answer = await pc.createAnswer();
      socket.send(JSON.stringify({type: 'answer', sdp: answer.sdp, to: to}));
      await pc.setLocalDescription(answer);
    }

    async function handleAnswer(answer) {
      if (!pc) {
        return;
      }
      await pc.setRemoteDescription(answer);
    }

    async function handleCandidate(candidate) {
      if (!pc) {
        return;
      }
      if (!candidate.candidate) {
        await pc.addIceCandidate(null);
      } else {
        await pc.addIceCandidate(candidate);
      }
    }

    function sendData() {
      const data = dataChannelSend.value;
      if (sendChannel) {
        sendChannel.send(data);
      } else {
        receiveChannel.send(data);
      }
    }

    function receiveChannelCallback(event) {
      receiveChannel = event.channel;
      receiveChannel.onmessage = onReceiveChannelMessageCallback;
      receiveChannel.onopen = onReceiveChannelStateChange;
      receiveChannel.onclose = onReceiveChannelStateChange;
    }

    function onReceiveChannelMessageCallback(event) {
      dataChannelReceive.value = event.data;
    }

    function onSendChannelMessageCallback(event) {
      dataChannelReceive.value = event.data;
    }

    function onSendChannelStateChange() {
      const readyState = sendChannel.readyState;
      if (readyState === 'open') {
        dataChannelSend.disabled = false;
        dataChannelSend.focus();
        sendButton.disabled = false;
      } else {
        dataChannelSend.disabled = true;
        sendButton.disabled = true;
      }
    }

    function onReceiveChannelStateChange() {
      if (! receiveChannel) {
        return;
      }
      const readyState = receiveChannel.readyState;
      if (readyState === 'open') {
        dataChannelSend.disabled = false;
        sendButton.disabled = false;
      } else {
        dataChannelSend.disabled = true;
        sendButton.disabled = true;
      }
    }

  }
  
  function afterHead() {
    webrtc();
  }
  
  onMount(async () => {

  });
  </script>
  
  <main class="container">
    
    <Header notify={afterHead} />
  
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
  
      <video id="localVideo" playsinline autoplay muted></video>
      <video id="remoteVideo" playsinline autoplay><track kind="captions" /></video>
  
      <div class="box">
          <button id="startButton">Start</button>
          <button id="sendButton" disabled>Send</button>
          <button id="hangupButton">Hang Up</button>
      </div>

      <div id="sendReceive">
        <div id="send">
            <h2>Send</h2>
            <textarea id="dataChannelSend" disabled
                      placeholder="Press Start, enter some text, then press Send."></textarea>
        </div>
        <div id="receive">
            <h2>Receive</h2>
            <textarea id="dataChannelReceive" disabled></textarea>
        </div>
      </div>

    </section>
  </main>
  