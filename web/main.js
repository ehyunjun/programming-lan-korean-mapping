const lessons = [
  {
    id: "01_print",
    title: "출력하기",
    description:
      "출력은 화면에 글자나 숫자를 보여주는 기능입니다. Python에서는 print를 사용하고, 한글 코드에서는 출력으로 사용할 수 있습니다.",
    starter_code: '출력("안녕")\n출력("한글 파이썬에 오신 것을 환영합니다")',
    answer_code: '출력("안녕")\n출력("한글 파이썬에 오신 것을 환영합니다")',
  },
  {
    id: "02_variable",
    title: "변수 만들기",
    description:
      "변수는 값을 저장해두는 이름입니다. 이름표를 붙여두는 것처럼, 값을 변수에 넣어두고 나중에 다시 사용할 수 있습니다.",
    starter_code: '이름 = "현준"\n출력(이름)',
    answer_code: '이름 = "현준"\n출력(이름)',
  },
  {
    id: "03_if",
    title: "조건문 사용하기",
    description:
      "조건문은 조건이 맞을 때와 맞지 않을 때 실행할 코드를 나누는 문법입니다. 한글 코드에서는 만약, 그외를 사용합니다.",
    starter_code: '점수 = 80\n\n만약 점수 >= 60:\n    출력("합격")\n그외:\n    출력("불합격")',
    answer_code: '점수 = 80\n\n만약 점수 >= 60:\n    출력("합격")\n그외:\n    출력("불합격")',
  },
  {
    id: "04_for_range",
    title: "반복문 사용하기",
    description:
      "반복문은 같은 코드를 여러 번 실행할 때 사용합니다. edu-v1에서는 반복 i 안에 범위(...) 형태를 먼저 연습합니다.",
    starter_code: "반복 i 안에 범위(1, 6):\n    출력(i)",
    answer_code: "반복 i 안에 범위(1, 6):\n    출력(i)",
  },
];

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
      <span class="lesson-goal">${lesson.description.split(".")[0]}.</span>
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
