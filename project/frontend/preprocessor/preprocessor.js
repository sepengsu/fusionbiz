// ✅ 슬라이더 값 실시간 표시
document.getElementById("chunkSize").oninput = function () {
  document.getElementById("chunkSizeValue").innerText = this.value;
};
document.getElementById("chunkOverlap").oninput = function () {
  document.getElementById("chunkOverlapValue").innerText = this.value;
};
document.getElementById("topK").oninput = function () {
  document.getElementById("topKValue").innerText = this.value;
};

// ✅ 텍스트 전처리 요청
function processData() {
  const file = document.getElementById("fileInput").files[0];
  if (!file) return alert("파일을 업로드하세요.");

  const formData = new FormData();
  formData.append("file", file);
  formData.append("chunk_size", document.getElementById("chunkSize").value);
  formData.append("chunk_overlap", document.getElementById("chunkOverlap").value);
  formData.append("embedding_model", document.getElementById("embeddingModel").value);
  formData.append("vector_type", document.getElementById("vectorType").value);
  formData.append("process_type", document.getElementById("processType").value);

  document.getElementById("loading").style.display = "block";
  document.getElementById("statusArea").innerText = "";
  document.getElementById("previewArea").style.display = "none";

  fetch("/upload_log", {
    method: "POST",
    body: formData
  })
    .then(res => res.json())
    .then(data => {
      document.getElementById("loading").style.display = "none";
      document.getElementById("statusArea").innerText = `✅ 데이터 처리 완료!`;
      document.getElementById("sourceFile").innerText = data.filename;
      document.getElementById("sampleContent").innerText = data.sample || "미리보기 없음";
      document.getElementById("previewArea").style.display = "block";
    })
    .catch(err => {
      document.getElementById("loading").style.display = "none";
      document.getElementById("statusArea").innerText = `❌ 처리 실패: ${err}`;
    });
}

// ✅ 로그 파일 DB 저장용 업로드 폼 처리
document.getElementById("log-upload-form").addEventListener("submit", async function (e) {
  e.preventDefault();

  const formData = new FormData(this);
  const resultElem = document.getElementById("log-upload-result");

  resultElem.textContent = "⏳ 업로드 중...";

  try {
    const response = await fetch("/upload_log_to_db", {
      method: "POST",
      body: formData
    });

    const result = await response.json();
    if (result.error) {
      resultElem.textContent = "❌ 오류: " + result.error;
    } else {
      resultElem.textContent =
        `✅ ${result.message}\n📁 파일명: ${result.filename}\n📊 행 수: ${result.row_count}`;
    }
  } catch (err) {
    resultElem.textContent = "❌ 네트워크 오류 또는 서버 에러";
  }
});
