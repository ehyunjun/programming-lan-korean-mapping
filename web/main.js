const lessons = [
  {
    id: "01_print",
    title: "출력하기",
    goal: "화면에 문장을 출력합니다.",
    code: '출력("안녕")\n출력("한글 Python 학습을 시작합니다")',
  },
  {
    id: "02_variable",
    title: "변수 만들기",
    goal: "값을 이름에 저장하고 다시 사용합니다.",
    code: '이름 = "현준"\n출력(이름)',
  },
  {
    id: "03_if",
    title: "조건문 사용하기",
    goal: "조건에 따라 다른 문장을 실행합니다.",
    code: '점수 = 80\n\n만약 점수 >= 60:\n    출력("합격")\n그외:\n    출력("불합격")',
  },
  {
    id: "04_for_range",
    title: "반복문 사용하기",
    goal: "범위 안의 숫자를 차례대로 사용합니다.",
    code: "반복 i 안에 범위(1, 6):\n    출력(i)",
  },
];

const lessonList = document.querySelector("#lessonList");
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

function selectLesson(lessonId) {
  const lesson = lessons.find((item) => item.id === lessonId);
  if (!lesson) {
    return;
  }

  koreanCode.value = lesson.code;
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
      <span class="lesson-goal">${lesson.goal}</span>
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

renderLessons();
selectLesson(lessons[0].id);
