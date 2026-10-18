function speakText(text) {
  if ('speechSynthesis' in window) {
    // Cancel any ongoing speech
    window.speechSynthesis.cancel();
    
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 1.0;
    utterance.pitch = 1.0;
    // Optional: Try to pick a specific voice (e.g., a male voice if available)
    window.speechSynthesis.speak(utterance);
  }
}

// Automatically speak the latest interviewer message on page load
window.addEventListener('DOMContentLoaded', () => {
  const latestMessage = document.querySelector('.turn.interviewer[data-autoplay="true"]');
  if (latestMessage) {
    const text = latestMessage.getAttribute('data-text');
    if (text) speakText(text);
  }
});

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