const speechRecognition =
  window.SpeechRecognition || window.webkitSpeechRecognition;

const recognition = new speechRecognition();

const speak = (text) => {
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = "en-US";
  speechSynthesis.speak(utterance);
};

let isListening = false;

window.onload = () => {
  const voiceBtn = document.querySelector("#btn-voice");
  const form = document.querySelector("#form");
  const column = document.querySelector("#column");

  recognition.onresult = async (event) => {
    recognition.stop();
    isListening = false;
    const resultIndex = event.resultIndex;
    const transcript = event.results[resultIndex][0].transcript;

    if (transcript.toLowerCase().includes("translate")) {
      const text = transcript.split("translate")[1];
      form.value = text;
      speak(`translating ${text}`);
      column.innerHTML = `
        <p class="text-center mt-5 display-6 text-white">Translatig ${text}</p>
      `;

      const formData = new FormData();
      formData.append("text", text);
      formData.append("voice", true);

      const response = await fetch(`/`, {
        method: "POST",
        body: formData,
      });

      const data = await response.text();

      column.innerHTML = `
        <p class="text-center mt-5 display-6 text-white">${data}</p>
      `;
      await speak("translation complete");
      await speak(data);
    }
  };

  recognition.onend = () => {
    if (isListening) {
      recognition.start();
      column.innerHTML = `

        <p class="text-center mt-5 display-6 text-white">Listening...</p>
      `;
    } else {
      isListening = false;
    }
  };

  voiceBtn.addEventListener("click", () => {
    if (!isListening) {
      speak("Voice mode activated!");
      isListening = true;

      column.innerHTML = `
        <p class="text-center mt-5 display-6 text-white">Listening...</p>
      `;

      voiceBtn.classList.remove("btn-danger");
      voiceBtn.classList.add("btn-primary");

      voiceBtn.innerHTML = `
        <i class="fas fa-microphone-alt"></i>

        Disable Voice Mode
      `;
      recognition.stop();
    } else {
      speak("Voice mode deactivated!");

      isListening = false;

      column.innerHTML = `
      <form id="form" action="/" method="POST">

                    <input type="hidden" name="voice" value="">
                    <div class="form-group">
                        <input type="text" class="form-control form-control-lg" id="text" name="text"
                            placeholder="Enter text to translate">
                    </div>
                    <button type="submit" class="btn mt-2 form-control btn-primary">Translate</button>
                </form>
                `;

      voiceBtn.classList.remove("btn-primary");
      voiceBtn.classList.add("btn-danger");

      voiceBtn.innerHTML = `
            <i class="fas fa-microphone-slash"></i>
    
            Enable Voice Mode
        `;
    }
    recognition.start();
  });
};
