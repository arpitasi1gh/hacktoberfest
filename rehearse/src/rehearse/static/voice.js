function speakText(text) {
  if ('speechSynthesis' in window) {
    window.speechSynthesis.cancel(); // Stop any currently playing audio
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 1.0;
    utterance.pitch = 1.0;
    window.speechSynthesis.speak(utterance);
  }
}

function playLatestAudio() {
  const latestMessage = document.querySelector('.turn.interviewer[data-autoplay="true"]');
  if (latestMessage) {
    const text = latestMessage.getAttribute('data-text');
    if (text) {
      speakText(text);
      // Mark it as played so it doesn't repeat on future swaps
      latestMessage.setAttribute('data-autoplay', 'false');
    }
  }
}

// Run on initial page load (e.g., when clicking "Start interview")
window.addEventListener('DOMContentLoaded', playLatestAudio);

// Run every time HTMX swaps the content (e.g., when clicking "Send answer")
document.body.addEventListener('htmx:afterSwap', playLatestAudio);

function startDictation() {
  const micBtn = document.getElementById('mic-btn');
  const answerBox = document.getElementById('answer-box');
  
  if (window.hasOwnProperty('webkitSpeechRecognition')) {
    const recognition = new webkitSpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = "en-IN";

    micBtn.textContent = "🔴";
    recognition.start();

    recognition.onresult = function(e) {
      answerBox.value += e.results[0][0].transcript;
      micBtn.textContent = "🎤";
    };

    recognition.onerror = function(e) {
      micBtn.textContent = "🎤";
      alert("Microphone error: " + e.error);
    };

    recognition.onend = function() {
      micBtn.textContent = "🎤";
    };
  } else {
    alert("Your browser does not support speech recognition. Use Chrome or Edge.");
  }
}