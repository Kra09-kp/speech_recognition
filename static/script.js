const startBtn = document.getElementById('startBtn');
const stopBtn = document.getElementById('stopBtn');
const audioPlayback = document.getElementById('audioPlayback');
const recordingIndicator = document.getElementById('recordingIndicator');
const recognizeBtn = document.getElementById('recognize');

let mediaRecorder;
let audioChunks = [];
let audioBlob;

function displayChat(messages) {
    const resultElement = document.querySelector('#Result');
    resultElement.innerHTML = ''; // Clear previous messages
    messages.forEach(message => {
        const newMessage = document.createElement('p');
        newMessage.textContent = message;
        resultElement.appendChild(newMessage);
    });
}

startBtn.addEventListener('click', async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder = new MediaRecorder(stream);

    mediaRecorder.ondataavailable = event => {
        audioChunks.push(event.data);
    };

    mediaRecorder.onstop = () => {
        audioBlob = new Blob(audioChunks, { type: 'audio/mp4; codecs=aac' });
        const audioUrl = URL.createObjectURL(audioBlob);
        audioPlayback.src = audioUrl;
        audioChunks = [];

        startBtn.classList.remove('recording');
        recordingIndicator.style.display = 'none';
    };

    mediaRecorder.start();
    startBtn.disabled = true;
    stopBtn.disabled = false;
    startBtn.classList.add('recording');
    recordingIndicator.style.display = 'block';
});

stopBtn.addEventListener('click', () => {
    mediaRecorder.stop();
    startBtn.disabled = false;
    stopBtn.disabled = true;
});

recognizeBtn.addEventListener('click', function(event) {
    event.preventDefault(); // Prevent default behavior

    document.getElementById('msg').style.display = 'block';
    const msg = ["Processing...", "Please wait...", "Almost there...", "Just a moment..."];
    document.getElementById('msg').innerHTML = msg[0];
    let i = 1;
    const interval = setInterval(() => {
        document.getElementById('msg').innerHTML = msg[i];
        i = (i + 1) % msg.length;
    }, 30000);

    const filename = `recording.m4a`;
    const formData = new FormData();
    formData.append('audio_data', audioBlob, filename);

    fetch('/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        clearInterval(interval);
        document.getElementById('msg').style.display = 'none';
        console.log('Response from server:', data);

        if (data.result) {
            fetch('/chat-history')
                .then(response => response.json())
                .then(chatHistory => {
                    displayChat(chatHistory);
                });
        } else {
            displayChat(["Please try again."]);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        clearInterval(interval);
        document.getElementById('msg').style.display = 'none';
        displayChat(["Something went wrong."]);
    });
});

document.addEventListener('DOMContentLoaded', () => {
    fetch('/chat-history')
        .then(response => response.json())
        .then(chatHistory => {
            displayChat(chatHistory);
        });
});