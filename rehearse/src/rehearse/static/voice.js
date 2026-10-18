// 1. Function to find the latest message and speak it
function speakLatestMessage() {
  const latest = document.querySelector('.turn.interviewer.latest-message');
  
  if (latest && 'speechSynthesis' in window) {
    const text = latest.innerText;
    window.speechSynthesis.cancel(); // Stop any overlapping audio
    
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 1.0;
    window.speechSynthesis.speak(utterance);
    
    // Remove the class so it doesn't speak again if the page re-renders
    latest.classList.remove('latest-message');
  }
}

// 2. Run on the very first page load (Start Interview)
window.addEventListener('DOMContentLoaded', speakLatestMessage);

// 3. Run every time HTMX swaps the body (Send Answer)
document.addEventListener('htmx:afterSwap', speakLatestMessage);

// 4. Keep the microphone function below
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