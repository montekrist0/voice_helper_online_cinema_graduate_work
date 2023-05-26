let previewMsg = document.getElementById('preview-msg')
let previewMsgTypeWriter = document.getElementById('preview-msg-typewriter')
let userMsg = document.getElementById('user-msg')
let userMsgTypeWriter = document.getElementById('user-msg-typewriter')
let botMsg = document.getElementById('bot-msg')
let botMsgTypeWriter = document.getElementById('bot-msg-typewriter')
let waveSpeak = document.getElementById('wave-speak')
let btnSpeak = document.getElementById('btn-speak')


// socket
let socket = null;

const startSocket = () => {
    socket = new WebSocket('ws://localhost/api/v1/message/');

    socket.onopen = (event) => {
        console.log('WebSocket opened.');
    };

    socket.onmessage = (event) => {
        console.log('Message received from server:', event.data);
        const utterance = new SpeechSynthesisUtterance(event.data);
        utterance.lang = 'ru-RU';
        speechSynthesis.speak(utterance);
        botMsgSpeak(event.data)

        utterance.onend = () => {
            console.log('Speech synthesis finished.');
            toggleVisibleClass(waveSpeak, false)
            toggleVisibleClass(btnSpeak, true)
        };

    };

    socket.onerror = (event) => {
        console.error('WebSocket error:', event);
    };

    socket.onclose = (event) => {
        console.log('WebSocket closed:', event);
        setTimeout(startSocket, 1000);
    };
}

startSocket();

const messagesList = document.getElementById('messages-list')
const botMsgSpeak = (msg) => {
    toggleVisibleClass(botMsg, true)
    botMsgTypeWriter.innerText = msg
    toggleVisibleClass(waveSpeak, true)
    typeWriterEffect(botMsgTypeWriter, 35, () => {
    }, () => {
        messagesList.scrollTop = messagesList.scrollHeight
    })
}

// настройки speak
let finalTranscript = '';
let isListening = false;
const recognition = new window.webkitSpeechRecognition();
recognition.lang = 'ru-RU';
recognition.continuous = true;
recognition.interimResults = true;

recognition.onresult = (event) => {
    let interimTranscript = '';

    for (let i = event.resultIndex; i < event.results.length; i++) {
        const transcript = event.results[i][0].transcript;
        if (event.results[i].isFinal) {
            finalTranscript += transcript + ' ';
        } else {
            interimTranscript += transcript;
        }
    }
    userMsgTypeWriter.innerHTML = finalTranscript + interimTranscript;

    if (event.results[event.results.length - 1].isFinal) {
        stopSpeak()
        socket.send(JSON.stringify(finalTranscript));
        finalTranscript = ''
    }
};

recognition.onerror = (event) => {
    console.error('Recognition error:', event.error);
};


const startSpeak = () => {
    if (!isListening) {
        recognition.start();
        isListening = true;
        userMsgTypeWriter.innerHTML = '';
        toggleVisibleClass(userMsg, true)
        console.log('Recognition started.');
    }
};

const stopSpeak = () => {
    if (isListening) {
        recognition.stop();
        isListening = false;
        toggleVisibleClass(waveSpeak, false)
        console.log('Recognition stopped.');
    }
};


// анимация набора текста
const typeWriterEffect = (element, speed = 50, fn = null, fnSpeak = null) => {
    var text = element.textContent;
    element.textContent = '';

    function typeNextCharacter(i) {
        if (i < text.length) {
            element.textContent += text.charAt(i);

            setTimeout(function () {
                typeNextCharacter(i + 1);

                if (fnSpeak) {
                    console.log('TWE fnSpeak')
                    fnSpeak()
                }
            }, speed);


        } else {

            if (fn) {
                console.log('TWE FN')
                fn()
            }
        }
    }

    typeNextCharacter(0);
}

// toggle классов
const toggleVisibleClass = (el, view) => {
    if (view) {
        el.classList.remove('hidden')
    } else {
        el.classList.add('hidden')
    }
}

// event кнопки микрофона
btnSpeak.onclick = () => {
    console.log('запись')
    // убираем чаты сообщений
    toggleVisibleClass(userMsg, false)
    toggleVisibleClass(botMsg, false)

    // убираем кнопку микрофона
    toggleVisibleClass(btnSpeak, false)
    // отображаем волну
    toggleVisibleClass(waveSpeak, true)
    // запуск
    startSpeak()
}


// печатающийся текст при старте страницы 
typeWriterEffect(previewMsgTypeWriter, 10);