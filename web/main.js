let lessons = [];

const REQUIRED_LESSON_FIELDS = ["id:", "title:", "description:", "starter_code:", "answer_code:"];
const LESSON_LOAD_ERROR_MESSAGE =
  "lesson 데이터를 불러오지 못했습니다. 로컬 서버로 실행했는지 확인해주세요.";

const lessonList = document.querySelector("#lessonList");
const lessonDescription = document.querySelector("#lessonDescription");
const koreanCode = document.querySelector("#koreanCode");
const pythonOutput = document.querySelector("#pythonOutput");
const runOutput = document.querySelector("#runOutput");
const convertButton = document.querySelector("#convertButton");
const runButton = document.querySelector("#runButton");

function setNotice(target, message) {
  target.classList.add("notice");
  target.textContent = message;
}

function clearNotice(target) {
  target.classList.remove("notice");
}

function showLessonLoadError() {
  lessonList.innerHTML = "";
  lessonDescription.textContent = LESSON_LOAD_ERROR_MESSAGE;
  koreanCode.value = "";
  pythonOutput.textContent = "";
  runOutput.textContent = "";

  const message = document.createElement("div");
  message.className = "lesson-item active";
  message.textContent = LESSON_LOAD_ERROR_MESSAGE;
  lessonList.appendChild(message);
}

function getLessonSummary(lesson) {
  return (lesson.description || "").split(".")[0] + ".";
}

async function loadLessons() {
  try {
    const response = await fetch("../lessons/lessons.json");
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const data = await response.json();
    if (!Array.isArray(data)) {
      throw new Error("lessons.json의 최상위 구조가 배열이 아닙니다.");
    }

    lessons = data;
    renderLessons();

    if (lessons.length > 0) {
      selectLesson(lessons[0].id);
    }
  } catch (error) {
    console.error(error);
    showLessonLoadError();
  }
}

function selectLesson(lessonId) {
  const lesson = lessons.find((item) => item.id === lessonId);
  if (!lesson) {
    return;
  }

  koreanCode.value = lesson.starter_code;
  lessonDescription.textContent = lesson.description;
  clearNotice(pythonOutput);
  clearNotice(runOutput);
  pythonOutput.textContent = "";
  runOutput.textContent = "";

  document.querySelectorAll(".lesson-item").forEach((button) => {
    button.classList.toggle("active", button.dataset.lessonId === lessonId);
  });
}

function renderLessons() {
  lessonList.innerHTML = "";

  lessons.forEach((lesson) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "lesson-item";
    button.dataset.lessonId = lesson.id;
    button.innerHTML = `
      <span class="lesson-title">${lesson.title}</span>
      <span class="lesson-goal">${getLessonSummary(lesson)}</span>
    `;
    button.addEventListener("click", () => selectLesson(lesson.id));
    lessonList.appendChild(button);
  });
}

convertButton.addEventListener("click", () => {
  setNotice(pythonOutput, "아직 변환 API가 연결되지 않았습니다.");
});

runButton.addEventListener("click", () => {
  setNotice(runOutput, "아직 실행 API가 연결되지 않았습니다.");
});

void REQUIRED_LESSON_FIELDS;
loadLessons();
