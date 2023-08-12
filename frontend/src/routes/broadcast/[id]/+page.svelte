<script>
  import { onMount } from 'svelte';
  import Header from "../../../includes/header.svelte";
  import Footer from "../../../includes/footer.svelte";
  import ColorModes from "../../../includes/color-modes.svelte";

  async function webrtc() {
    let peerConnection;
    const to = window.location.pathname.split("/").pop();
  
    if (socket.readyState === WebSocket.OPEN) {
      socket.send(JSON.stringify({"type": "watcher", "to": to}));
    } else {
      socket.addEventListener('open', () => {
        socket.send(JSON.stringify({"type": "watcher", "to": to}));
      });
    }

    socket.addEventListener('message', async event => {
        const message = JSON.parse(event.data);
        if (message.type == "offer") {
          peerConnection = new RTCPeerConnection({ iceServers: [{"urls": "stun:stun.l.google.com:19302"}] });
          peerConnection.setRemoteDescription(message.description).then(() => peerConnection.createAnswer())
            .then(sdp => peerConnection.setLocalDescription(sdp)).then(() => {
              socket.send(JSON.stringify({"type": "answer", "description": peerConnection.localDescription, "to": to}));
            });
          peerConnection.ontrack = event => { document.querySelector("video").srcObject = event.streams[0]; };
          peerConnection.onicecandidate = event => { if (event.candidate) {
              socket.send(JSON.stringify({"type": "candidate", "description": event.candidate, "to": to}));
          }};
        }
        if (message.type == "candidate") {
          peerConnection.addIceCandidate(new RTCIceCandidate(message.description)).catch(e => console.error(e));
        }
        if (message.type == "broadcaster") { // When broadcaster reconnects, this makes client reconnect
          socket.send(JSON.stringify({"type": "watcher", "to": to}));
        }
    });
  
    window.onunload = window.onbeforeunload = () => {
      socket.close();
      peerConnection.close();
    };
  }
  
  function afterHead() {
    webrtc();
  }
  
  onMount(async () => {
    //
  });
  </script>
  
  <main class="container">
  
    <Header notify={afterHead} />
  
    <video autoplay muted playsinline controls></video>

    <Footer />
    <ColorModes />

  </main>
  