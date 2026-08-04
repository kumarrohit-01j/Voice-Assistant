const historyList = document.getElementById('historyList');
const lastUpdate = document.getElementById('lastUpdate');
const refreshButton = document.getElementById('refreshButton');
const sparkButton = document.getElementById('sparkButton');
const themeToggle = document.getElementById('themeToggle');
const themeLabel = document.getElementById('themeLabel');
const themeIcon = document.getElementById('themeIcon');
const animeAvatar = document.getElementById('animeAvatar');
const animationStage = document.getElementById('animationStage');
const robotShell = document.getElementById('robotShell');
const walkFigure = document.querySelector('.walk-figure');
const livePulseLabel = document.querySelector('.live-metrics strong');
const commandInput = document.getElementById('commandInput');
const sendButton = document.getElementById('sendButton');
const voiceButton = document.getElementById('voiceButton');
const voiceStatus = document.getElementById('voiceStatus');
const commandResponse = document.getElementById('commandResponse');
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
let recognition = null;
let isListening = false;
let shouldContinueVoice = false;
let restartAfterEnd = false;
let restartMessage = 'Listening... speak your command now.';

function applyTheme(themeName = 'dark') {
  const nextTheme = themeName === 'light' ? 'light' : 'dark';
  document.documentElement.setAttribute('data-theme', nextTheme);
  localStorage.setItem('veda-theme', nextTheme);

  if (themeLabel) {
    themeLabel.textContent = nextTheme === 'dark' ? 'Dark mode' : 'Light mode';
  }

  if (themeIcon) {
    themeIcon.textContent = nextTheme === 'dark' ? '🌙' : '☀️';
  }

  if (themeToggle) {
    themeToggle.setAttribute('aria-label', `Switch to ${nextTheme === 'dark' ? 'light' : 'dark'} mode`);
  }
}

function initTheme() {
  const storedTheme = localStorage.getItem('veda-theme');
  const prefersLight = window.matchMedia && window.matchMedia('(prefers-color-scheme: light)').matches;
  applyTheme(storedTheme || (prefersLight ? 'light' : 'dark'));
}

async function loadHistory() {
  try {
    const response = await fetch('/api/history');
    const data = await response.json();
    historyList.innerHTML = '';

    if (!data.length) {
      historyList.innerHTML = '<div class="history-item"><span>No commands recorded yet.</span></div>';
      lastUpdate.textContent = `Last updated: ${new Date().toLocaleTimeString()}`;
      return;
    }

    data.forEach(item => {
      const row = document.createElement('div');
      row.className = 'history-item';

      const commandWrap = document.createElement('div');
      const commandText = document.createElement('strong');
      commandText.textContent = item.command;
      commandWrap.appendChild(commandText);

      const timestamp = document.createElement('span');
      timestamp.textContent = item.timestamp;

      row.append(commandWrap, timestamp);
      historyList.appendChild(row);
    });

    lastUpdate.textContent = `Last updated: ${new Date().toLocaleTimeString()}`;
  } catch (error) {
    historyList.innerHTML = `<div class="history-item"><span>Error loading history: ${error.message}</span></div>`;
  }
}

function setRobotWorking(active, label = 'AI pulse active') {
  robotShell?.classList.toggle('executing', active);
  walkFigure?.classList.toggle('executing', active);
  animationStage?.classList.toggle('pulse-active', active);
  document.querySelector('.hero-visual')?.classList.toggle('pulse-active', active);

  if (livePulseLabel) {
    livePulseLabel.textContent = active ? label : 'AI pulse active';
  }
}

function animateSpark() {
  animeAvatar?.classList.add('spark');
  setRobotWorking(true, 'Executing command...');
  setTimeout(() => {
    animeAvatar?.classList.remove('spark');
    setRobotWorking(false, 'AI pulse active');
  }, 1300);
}

function applyTilt(card) {
  if (!card) {
    return;
  }

  card.addEventListener('mousemove', (event) => {
    const rect = card.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;
    const rotateY = ((x / rect.width) - 0.5) * 8;
    const rotateX = ((0.5 - (y / rect.height))) * 7;

    card.style.transform = `perspective(900px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateY(-3px)`;
  });

  card.addEventListener('mouseleave', () => {
    card.style.transform = '';
  });
}

function initInteractiveCards() {
  document.querySelectorAll('[data-tilt]').forEach((card) => applyTilt(card));
}

function normalizeSpeech(text) {
  return text.toLowerCase().replace(/[^\w\s]/g, '').replace(/\s+/g, ' ').trim();
}

function isWakePhrase(text) {
  const normalized = normalizeSpeech(text);
  return ['hey', 'veda', 'hey veda'].includes(normalized);
}

function commandAfterWakePhrase(text) {
  const normalized = text.toLowerCase().replace(/[^\w\s]/g, '').trim();
  for (const wake of ['hey veda', 'hey', 'veda']) {
    if (normalized.startsWith(`${wake} `)) {
      return normalized.slice(wake.length).trim();
    }
  }
  return '';
}

async function sendCommand(commandOverride = null) {
  const command = (commandOverride || commandInput.value).trim();
  if (!command) {
    commandResponse.textContent = 'Please type a command first.';
    return;
  }

  commandResponse.textContent = 'Sending command to Veda...';
  commandInput.value = '';
  setRobotWorking(true, `Working: ${command}`);

  try {
    const response = await fetch('/api/command', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ command })
    });

    const result = await response.json();
    if (response.ok) {
      commandResponse.textContent = result.message;
      animateSpark();
      loadHistory();
      if (shouldContinueVoice && result.awaiting) {
        const message = result.awaiting === 'play_youtube_music'
          ? 'Listening for the song name...'
          : 'Listening for your search...';
        startVoiceListening(message);
      }
    } else {
      commandResponse.textContent = result.message || 'Unable to send command.';
    }
  } catch (error) {
    commandResponse.textContent = `Error: ${error.message}`;
  } finally {
    setTimeout(() => {
      if (!animeAvatar?.classList.contains('spark')) {
        setRobotWorking(false, 'AI pulse active');
      }
    }, 900);
  }
}

function setVoiceListening(active) {
  isListening = active;
  voiceButton.classList.toggle('listening', active);
  voiceButton.setAttribute('aria-pressed', String(active));
  voiceButton.textContent = active ? 'Stop' : 'Mic';
}

function startVoiceListening(message = 'Listening... speak your command now.') {
  if (!recognition) {
    return;
  }

  restartMessage = message;
  shouldContinueVoice = true;

  if (isListening) {
    restartAfterEnd = true;
    recognition.stop();
    return;
  }

  try {
    recognition.start();
  } catch (error) {
    restartAfterEnd = true;
    voiceStatus.textContent = 'Preparing microphone...';
  }
}

function setupVoiceCommands() {
  if (!SpeechRecognition) {
    voiceButton.disabled = true;
    voiceStatus.textContent = 'Voice command is not supported in this browser. Try Chrome or Edge.';
    return;
  }

  recognition = new SpeechRecognition();
  recognition.lang = 'en-IN';

  recognition.continuous = false;
  recognition.interimResults = false;
  recognition.maxAlternatives = 1;

  recognition.onstart = () => {
    setVoiceListening(true);
    voiceStatus.textContent = restartMessage;
  };

  recognition.onresult = (event) => {
    const transcript = Array.from(event.results)
      .slice(event.resultIndex)
      .map(result => result[0].transcript)
      .join(' ')
      .replace(/\s+/g, ' ')
      .trim();

    commandInput.value = transcript;
    voiceStatus.textContent = event.results[event.results.length - 1].isFinal
      ? `Heard: ${transcript}`
      : `Hearing: ${transcript}`;

    if (event.results[event.results.length - 1].isFinal && transcript) {
      const wakeCommand = commandAfterWakePhrase(transcript);
      if (wakeCommand) {
        commandInput.value = wakeCommand;
        sendCommand(wakeCommand);
        return;
      }

      if (isWakePhrase(transcript)) {
        commandInput.value = '';
        commandResponse.textContent = "Yes, I'm active. What would you like me to do?";
        startVoiceListening('Listening for your command...');
        return;
      }

      sendCommand();
    }
  };

  recognition.onerror = (event) => {
    const messages = {
      'not-allowed': 'Microphone permission was blocked.',
      'no-speech': 'No speech detected. Try again.',
      network: 'Voice recognition needs browser network access.',
      'audio-capture': 'No microphone was found.'
    };

    voiceStatus.textContent = messages[event.error] || `Voice error: ${event.error}`;
    if (event.error !== 'no-speech') {
      shouldContinueVoice = false;
      restartAfterEnd = false;
    }
  };

  recognition.onend = () => {
    setVoiceListening(false);
    if (restartAfterEnd && shouldContinueVoice) {
      restartAfterEnd = false;
      setTimeout(() => startVoiceListening(restartMessage), 350);
      return;
    }

    if (voiceStatus.textContent === restartMessage) {
      voiceStatus.textContent = 'Voice command is ready.';
    }
  };
}

function toggleVoiceCommand() {
  if (!recognition) {
    return;
  }

  if (isListening) {
    shouldContinueVoice = false;
    recognition.stop();
    return;
  }

  try {
    startVoiceListening();
  } catch (error) {
    voiceStatus.textContent = 'Voice command is already starting.';
  }
}

refreshButton.addEventListener('click', loadHistory);
sparkButton.addEventListener('click', animateSpark);
themeToggle?.addEventListener('click', () => {
  const currentTheme = document.documentElement.getAttribute('data-theme') === 'light' ? 'light' : 'dark';
  applyTheme(currentTheme === 'light' ? 'dark' : 'light');
});
sendButton.addEventListener('click', () => sendCommand());
voiceButton.addEventListener('click', toggleVoiceCommand);
commandInput.addEventListener('keydown', (event) => {
  if (event.key === 'Enter') {
    sendCommand();
  }
});

initTheme();
initInteractiveCards();
setupVoiceCommands();
loadHistory();
