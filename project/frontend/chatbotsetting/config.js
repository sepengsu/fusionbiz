const modelSelect = document.getElementById('modelSelect');
const temperature = document.getElementById('temperature');
const tempValue = document.getElementById('tempValue');
const sqlSystemPrompt = document.getElementById('sqlSystemPrompt');
const manualSystemPrompt = document.getElementById('manualSystemPrompt');
const manualWindowPrompt = document.getElementById('manualWindowPrompt');
const sqlResultPrompt = document.getElementById('sqlResultPrompt');
const classificationMode = document.getElementById('classificationMode');
const historySlider = document.getElementById('maxHistoryCount');
const historyValue = document.getElementById('historyValue');
const status = document.getElementById('statusMessage');

// ✅ 유저 프롬프트 필드 추가 (하나 삭제됨)
const sqlUserPrompt = document.getElementById('sqlUserPrompt');
const manualUserPrompt = document.getElementById('manualUserPrompt');
const manualWindowUserPrompt = document.getElementById('manualWindowUserPrompt');
const sqlResultUserPrompt = document.getElementById('sqlResultUserPrompt');

// 🔄 실시간 슬라이더 반영
temperature.oninput = () => {
  tempValue.textContent = temperature.value;
};

historySlider.oninput = () => {
  historyValue.textContent = historySlider.value;
};

// 💾 설정 저장
async function saveConfig() {
  const maxHistoryValue = parseInt(historySlider?.value ?? "3");
  const safeMaxHistory = isNaN(maxHistoryValue) ? 3 : maxHistoryValue;

  const payload = {
    llm_model: modelSelect.value,
    temperature: parseFloat(temperature.value),
    classification_mode: classificationMode.value,
    sql_system_prompt: sqlSystemPrompt.value,
    manual_system_prompt: manualSystemPrompt.value,
    manual_window_prompt: manualWindowPrompt.value,
    sql_result_prompt: sqlResultPrompt.value,
    sql_user_prompt: sqlUserPrompt.value,
    manual_user_prompt: manualUserPrompt.value,
    manual_window_user_prompt: manualWindowUserPrompt.value,
    sql_result_user_prompt: sqlResultUserPrompt.value,
    max_history: safeMaxHistory
  };

  console.log("📤 저장 payload:", payload);

  const res = await fetch('/chat_config', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });

  const result = await res.json();
  status.textContent = result.message || '✅ 설정이 저장되었습니다';
}

// 📥 설정 불러오기
async function loadConfig() {
  try {
    const [exampleRes] = await Promise.all([
      fetch('/config/example.json')
    ]);
    const example = await exampleRes.json();

    modelSelect.value = example.llm_model;
    temperature.value = example.temperature;
    tempValue.textContent = temperature.value;

    sqlSystemPrompt.value = example.sql_system_prompt;
    manualSystemPrompt.value = example.manual_system_prompt;
    manualWindowPrompt.value = example.manual_window_prompt;
    sqlResultPrompt.value = example.sql_result_prompt;
    classificationMode.value = example.classification_mode;

    sqlUserPrompt.value = example.sql_user_prompt || "";
    manualUserPrompt.value = example.manual_user_prompt || "";
    manualWindowUserPrompt.value = example.manual_window_user_prompt || "";
    sqlResultUserPrompt.value = example.sql_result_user_prompt || "";

    const loadedHistory = example.max_history;
    historySlider.value = loadedHistory;
    historyValue.textContent = loadedHistory;

  } catch (e) {
    console.warn("❌ 설정 또는 예시 불러오기 실패", e);
  }
}

// ✅ 초기 로드
document.addEventListener('DOMContentLoaded', async () => {
  await loadConfig();
});
