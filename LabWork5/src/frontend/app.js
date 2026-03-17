async function loadGradebooks() {
  const output = document.getElementById("gradebooks-output");

  try {
    const response = await fetch("/api/v1/gradebooks");
    const data = await response.json();
    output.textContent = JSON.stringify(data, null, 2);
  } catch (error) {
    output.textContent = "Ошибка загрузки ведомостей: " + error.message;
  }
}

async function createGrade() {
  const output = document.getElementById("create-grade-output");

  const student_name = document.getElementById("student_name").value;
  const control_name = document.getElementById("control_name").value;
  const score = Number(document.getElementById("score").value);

  try {
    const response = await fetch("/api/v1/gradebooks/1/grades", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        student_name,
        control_name,
        score
      })
    });

    const data = await response.json();
    output.textContent = JSON.stringify(data, null, 2);
  } catch (error) {
    output.textContent = "Ошибка добавления оценки: " + error.message;
  }
}
