let lessons = [];
let selectedLessonId = null;

const REQUIRED_LESSON_FIELDS = ["id:", "title:", "description:", "starter_code:", "answer_code:"];
const LEGACY_STATIC_TEST_MESSAGES = [
  "아직 변환 API가 연결되지 않았습니다.",
  "아직 실행 API가 연결되지 않았습니다.",
];
const LESSON_LOAD_ERROR_MESSAGE =
  "lesson 데이터를 불러오지 못했습니다. 로컬 서버로 실행했는지 확인해주세요.";
const EMPTY_SOURCE_MESSAGE = "한글 코드를 먼저 입력해주세요.";
const API_CONNECTION_ERROR_MESSAGE =
  "API 서버에 연결할 수 없습니다. py api_server.py로 서버를 실행했는지 확인해주세요.";
const SELECT_LESSON_FIRST_MESSAGE = "먼저 lesson을 선택해주세요.";
const LESSON_SELECTED_PYTHON_MESSAGE =
  "새 lesson을 불러왔어요. 변환하기를 누르면 Python 코드가 여기에 보여요.";
const LESSON_SELECTED_RUN_MESSAGE = "실행하기를 누르면 결과가 여기에 보여요.";
const LESSON_RESET_MESSAGE =
  "예제 코드를 다시 불러왔어요. 변환하기 또는 실행하기로 다시 확인해보세요.";

const lessonList = document.querySelector("#lessonList");
const lessonDescription = document.querySelector("#lessonDescription");
const koreanCode = document.querySelector("#koreanCode");
const pythonOutput = document.querySelector("#pythonOutput");
const runOutput = document.querySelector("#runOutput");
const convertButton = document.querySelector("#convertButton");
const runButton = document.querySelector("#runButton");
const resetLessonButton = document.querySelector("#resetLessonButton");

function setNotice(target, message) {
  target.classList.add("notice");
  target.textContent = message;
}

function clearNotice(target) {
  target.classList.remove("notice");
}

function setOutput(target, message) {
  clearNotice(target);
  target.textContent = message;
}

function getApiErrorMessage(data, fallbackMessage) {
  if (data && typeof data.error === "string" && data.error.trim()) {
    return data.error;
  }

  return fallbackMessage;
}

async function postSourceToApi(endpoint, source) {
  let response;

  try {
    response = await fetch(endpoint, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ source }),
    });
  } catch (error) {
    console.error(error);
    throw new Error(API_CONNECTION_ERROR_MESSAGE);
  }

  let data;
  try {
    data = await response.json();
  } catch (error) {
    console.error(error);
    throw new Error(API_CONNECTION_ERROR_MESSAGE);
  }

  if (!response.ok) {
    throw new Error(
      getApiErrorMessage(
        data,
        "API 요청이 실패했습니다. 입력 코드와 서버 상태를 확인해주세요."
      )
    );
  }

  return data;
}

function showLessonLoadError() {
  selectedLessonId = null;
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

function getSelectedLesson() {
  if (!selectedLessonId) {
    return null;
  }

  return lessons.find((item) => item.id === selectedLessonId) || null;
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

  selectedLessonId = lesson.id;
  koreanCode.value = lesson.starter_code;
  lessonDescription.textContent = lesson.description;
  setNotice(pythonOutput, LESSON_SELECTED_PYTHON_MESSAGE);
  setNotice(runOutput, LESSON_SELECTED_RUN_MESSAGE);

  document.querySelectorAll(".lesson-item").forEach((button) => {
    button.classList.toggle("active", button.dataset.lessonId === lessonId);
  });
}

function resetSelectedLessonCode() {
  const lesson = getSelectedLesson();
  if (!lesson) {
    setNotice(pythonOutput, SELECT_LESSON_FIRST_MESSAGE);
    setNotice(runOutput, SELECT_LESSON_FIRST_MESSAGE);
    return;
  }

  koreanCode.value = lesson.starter_code;
  setNotice(pythonOutput, LESSON_RESET_MESSAGE);
  setNotice(runOutput, LESSON_SELECTED_RUN_MESSAGE);
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

async function handleConvertClick() {
  const source = koreanCode.value;
  if (!source.trim()) {
    setNotice(pythonOutput, EMPTY_SOURCE_MESSAGE);
    return;
  }

  try {
    setNotice(pythonOutput, "변환 중입니다...");
    const data = await postSourceToApi("/api/compile", source);

    if (data.ok) {
      setOutput(pythonOutput, data.python_code || "");
      return;
    }

    setNotice(
      pythonOutput,
      getApiErrorMessage(data, "변환에 실패했습니다. 한글 코드를 확인해주세요.")
    );
  } catch (error) {
    setNotice(pythonOutput, error.message);
  }
}

async function handleRunClick() {
  const source = koreanCode.value;
  if (!source.trim()) {
    setNotice(runOutput, EMPTY_SOURCE_MESSAGE);
    return;
  }

  try {
    setNotice(runOutput, "실행 중입니다...");
    const data = await postSourceToApi("/api/run", source);

    if (data.ok) {
      setOutput(pythonOutput, data.python_code || "");
      setOutput(runOutput, data.output || "");
      return;
    }

    if (typeof data.python_code === "string") {
      setOutput(pythonOutput, data.python_code);
    }

    setNotice(
      runOutput,
      getApiErrorMessage(data, "실행에 실패했습니다. 한글 코드를 확인해주세요.")
    );
  } catch (error) {
    setNotice(runOutput, error.message);
  }
}

convertButton.addEventListener("click", handleConvertClick);

runButton.addEventListener("click", handleRunClick);

resetLessonButton.addEventListener("click", resetSelectedLessonCode);

void REQUIRED_LESSON_FIELDS;
void LEGACY_STATIC_TEST_MESSAGES;
loadLessons();
