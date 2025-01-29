const userInfo = {};
const questions = [
    {
        question_id: 1,
        question: "I enjoy working with tools and machinery.",
        options: ["Strongly Agree", "Agree", "Neutral", "Disagree", "Strongly Disagree"]
    },
    {
        question_id: 2,
        question: "I like analyzing data and solving problems.",
        options: ["Strongly Agree", "Agree", "Neutral", "Disagree", "Strongly Disagree"]
    },
    {
        question_id: 3,
        question: "I enjoy creating art or designing projects.",
        options: ["Strongly Agree", "Agree", "Neutral", "Disagree", "Strongly Disagree"]
    },
    {
        question_id: 4,
        question: "Helping others and working in teams is fulfilling to me.",
        options: ["Strongly Agree", "Agree", "Neutral", "Disagree", "Strongly Disagree"]
    },
    {
        question_id: 5,
        question: "I am good at managing projects and taking initiative.",
        options: ["Strongly Agree", "Agree", "Neutral", "Disagree", "Strongly Disagree"]
    },
    {
        question_id: 6,
        question: "I prefer tasks that involve structure and organization.",
        options: ["Strongly Agree", "Agree", "Neutral", "Disagree", "Strongly Disagree"]
    },
    {
        question_id: 7,
        question: "I am curious about how the universe works and enjoy science.",
        options: ["Strongly Agree", "Agree", "Neutral", "Disagree", "Strongly Disagree"]
    },
    {
        question_id: 8,
        question: "I enjoy working with technology and fixing technical issues.",
        options: ["Strongly Agree", "Agree", "Neutral", "Disagree", "Strongly Disagree"]
    }
];

const difficultyQuestion = {
    question_id: "difficulty",
    question: "What level of difficulty do you prefer for your major?",
    options: ["Moderate", "Challenging"]
};

let currentQuestionIndex = 0;
let selectedAnswers = [];
let difficultyLevel = "";

function startQuiz() {
    const name = document.getElementById('name').value.trim();
    const gender = document.getElementById('gender').value;
    const dob = document.getElementById('dob').value;

    if (!name || !gender || !dob) {
        alert("Please fill in all fields.");
        return;
    }

    const dobDate = new Date(dob);
    const today = new Date();
    let age = today.getFullYear() - dobDate.getFullYear();
    const monthDiff = today.getMonth() - dobDate.getMonth();
    const dayDiff = today.getDate() - dobDate.getDate();

    // Adjust age calculation for incomplete years
    if (monthDiff < 0 || (monthDiff === 0 && dayDiff < 0)) {
        age--;
    }

    if (age < 16 || age > 80) {
        alert("Sorry, this test is only available for users between 16 and 80 years old.");
        return;
    }

    userInfo.name = name;
    userInfo.gender = gender;
    userInfo.dob = dob;

    document.getElementById('user-form').style.display = 'none';
    document.getElementById('quiz-container').style.display = 'block';
    loadQuestion();
}

function loadQuestion() {
    const currentQuestion = questions[currentQuestionIndex];
    document.querySelector('.question').textContent = currentQuestion.question;
    document.querySelector('.options').innerHTML = currentQuestion.options
        .map(option => `<li onclick="selectAnswer('${option}')">${option}</li>`)
        .join('');
}

function loadDifficultyQuestion() {
    document.querySelector('.question').textContent = difficultyQuestion.question;
    document.querySelector('.options').innerHTML = difficultyQuestion.options
        .map(option => `<li onclick="selectDifficulty('${option}')">${option}</li>`)
        .join('');
}

function selectAnswer(answer) {
    selectedAnswers[currentQuestionIndex] = {
        question_id: questions[currentQuestionIndex].question_id,
        selected_option: answer
    };
    updateSelection('.options li', answer);
}

function selectDifficulty(option) {
    difficultyLevel = option;
    updateSelection('.options li', option);
}

function updateSelection(selector, selectedValue) {
    document.querySelectorAll(selector).forEach(li => li.classList.remove('selected'));
    [...document.querySelectorAll(selector)].find(li => li.textContent === selectedValue).classList.add('selected');
}

function nextQuestion() {
    if (currentQuestionIndex < questions.length) {
        if (!selectedAnswers[currentQuestionIndex]) {
            alert("Please select an answer.");
            return;
        }

        currentQuestionIndex++;
        if (currentQuestionIndex === questions.length) {
            loadDifficultyQuestion();
        } else {
            loadQuestion();
        }
    } else if (!difficultyLevel) {
        alert("Please select a difficulty level.");
    } else {
        showReport();
    }
}

function showReport() {
    document.getElementById('quiz-container').style.display = 'none';
    document.getElementById('report-container').style.display = 'block';
    sendDataToBackend();
}

function sendDataToBackend() {
    const payload = {...userInfo, answers: selectedAnswers, difficulty: difficultyLevel};

    fetch("/analyze", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(payload)
    })
        .then(response => response.json())
        .then(displayResults)
        .catch(error => console.error("Error:", error));
}

function displayResults(data) {
    document.getElementById("user-name").textContent = data.user_info.name;
    document.getElementById("user-gender").textContent = data.user_info.gender;
    document.getElementById("user-dob").textContent = data.user_info.date_of_birth;

    const interestsList = document.getElementById("interests-list");
    interestsList.innerHTML = Object.entries(data.interests).map(([field, value]) => `<li>${field}: ${value}</li>`).join("");

    const recommendationsList = document.getElementById("recommendations-list");

    if (data.recommendations && data.recommendations.length > 0) {
        console.log(data.recommendations)
        recommendationsList.innerHTML = data.recommendations.map(item => `<li>${item.name} : ${item.description}<hr><p>Examples : ${item.career_paths}</p></<hr></li>`).join("");
    } else if (data.message) {
        recommendationsList.innerHTML = `<li>${data.message}</li>`;
    } else {
        recommendationsList.innerHTML = "<li>No recommendations available at this time.</li>";
    }
}
