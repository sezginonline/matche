<script>
import { onMount } from 'svelte';
import Header from "../../includes/header.svelte";
import Footer from "../../includes/footer.svelte";
import ColorModes from "../../includes/color-modes.svelte";
import { http } from '../../lib/http.js';
import { goto } from '$app/navigation';

async function webrtc() {
  const peerConnections = {};

  socket.addEventListener('message', async event => {
    const message = JSON.parse(event.data);
    if (message.type == "watcher") {
      const peerConnection = new RTCPeerConnection({ iceServers: [{"urls": "stun:stun.l.google.com:19302"}] });
      peerConnections[message.uid] = peerConnection;
      let stream = videoElement.srcObject;
      stream.getTracks().forEach(track => peerConnection.addTrack(track, stream));
      peerConnection.onicecandidate = event => { if (event.candidate) {
        socket.send(JSON.stringify({"type": "candidate", "description": event.candidate, "to": message.uid}));
      }};
      peerConnection.createOffer().then(sdp => peerConnection.setLocalDescription(sdp)).then(() => {
        socket.send(JSON.stringify({"type": "offer", "description": peerConnection.localDescription, "to": message.uid}));
      });
    }
    if (message.type == "answer") {
      peerConnections[message.uid].setRemoteDescription(message.description);
    }
    if (message.type == "candidate") {
      peerConnections[message.uid].addIceCandidate(new RTCIceCandidate(message.description));
    }
    if (message.type == "disconnectPeer") {
      peerConnections[message.uid].close();
      delete peerConnections[message.uid];
    }
  });

  window.onunload = window.onbeforeunload = () => {
    socket.close();
  };

  const videoElement = document.querySelector("video");
  const audioSelect = document.querySelector("select#audioSource");
  const videoSelect = document.querySelector("select#videoSource");

  audioSelect.onchange = getStream;
  videoSelect.onchange = getStream;

  getStream().then(getDevices).then(gotDevices);

  function getDevices() {
    return navigator.mediaDevices.enumerateDevices();
  }

  function gotDevices(deviceInfos) {
    window.deviceInfos = deviceInfos;
    for (const deviceInfo of deviceInfos) {
      const option = document.createElement("option");
      option.value = deviceInfo.deviceId;
      if (deviceInfo.kind === "audioinput") {
        option.text = deviceInfo.label || `Microphone ${audioSelect.length + 1}`;
        audioSelect.appendChild(option);
      } else if (deviceInfo.kind === "videoinput") {
        option.text = deviceInfo.label || `Camera ${videoSelect.length + 1}`;
        videoSelect.appendChild(option);
      }
    }
  }

  function getStream() {
    if (window.stream) {
      window.stream.getTracks().forEach(track => { track.stop(); });
    }
    const audioSource = audioSelect.value;
    const videoSource = videoSelect.value;
    const constraints = {
      audio: { deviceId: audioSource ? { exact: audioSource } : undefined },
      video: { deviceId: videoSource ? { exact: videoSource } : undefined }
    };
    return navigator.mediaDevices.getUserMedia(constraints).then(gotStream).catch(handleError);
  }

  function gotStream(stream) {
    window.stream = stream;
    audioSelect.selectedIndex = [...audioSelect.options].findIndex(option => option.text === stream.getAudioTracks()[0].label);
    videoSelect.selectedIndex = [...videoSelect.options].findIndex(option => option.text === stream.getVideoTracks()[0].label);
    videoElement.srcObject = stream;
    socket.send(JSON.stringify({"type": "broadcaster", "to": Object.keys(peerConnections)}));
  }

  function handleError(error) {
    console.error("Error: ", error);
  }
}

function afterHead() {
  webrtc();
}

onMount(async () => {

});

    // Function to take a picture and save it
    function takePicture() {
      const videoElement = document.querySelector("video");
      const canvasElement = document.querySelector("#canvas");
      const context = canvasElement.getContext("2d");

      // Set the canvas dimensions to match the video dimensions
      canvasElement.width = videoElement.videoWidth;
      canvasElement.height = videoElement.videoHeight;

      context.drawImage(videoElement, 0, 0, canvasElement.width, canvasElement.height);

      var pictureDataUrl = canvasElement.toDataURL("image/png");
      console.log(pictureDataUrl);

      // Convert the canvas content to a Blob object representing a PNG image
      canvasElement.toBlob((blob) => {
        // Create a temporary <a> element to download the image
        const link = document.createElement("a");
        link.href = URL.createObjectURL(blob);
        link.download = "image.png";

        // Programmatically click the link to trigger the download
        link.click();

        // Clean up the temporary URL object
        URL.revokeObjectURL(link.href);
      }, "image/png");
    }

    // Function to send the picture data to the server
    function sendPictureToServer(pictureDataUrl) {
      // Example Ajax call to send the picture data to the server
      // Replace this with your own implementation
      // You can use fetch or any other library for making Ajax requests
      fetch("/save-picture", {
        method: "POST",
        body: JSON.stringify({ pictureDataUrl }),
        headers: {
          "Content-Type": "application/json"
        }
      })
        .then(response => response.json())
        .then(data => {
          console.log("Picture saved successfully:", data);
        })
        .catch(error => {
          console.error("Error saving picture:", error);
        });
    }

</script>

<main class="container">

  <Header notify={afterHead} />

  <div class="d-lg-flex align-items-center justify-content-between py-3 mt-lg-4">
    <h1 class="me-3">Broadcast</h1>
    <div class="d-md-flex mb-3">
      <select class="form-select me-md-4 mb-2 mb-md-0" style="min-width: 240px;" id="videoSource"></select>
      <select class="form-select me-md-4 mb-2 mb-md-0" style="min-width: 240px;" id="audioSource"></select>
    </div>
  </div>
  
  <video playsinline autoplay muted></video>
  
  <!-- Add the "Take a Picture" button -->
  <button on:click={takePicture}>Take a Picture</button>
  <canvas id="canvas" style="display: none;"></canvas>

  <Footer />
  <ColorModes />
  
</main>
