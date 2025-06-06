console.log("✅ 최신 config.js 로드됨");

const modelSelect = document.getElementById('modelSelect');
const temperature = document.getElementById('temperature');
const tempValue = document.getElementById('tempValue');
const sqlSystemPrompt = document.getElementById('sqlSystemPrompt');
const manualSystemPrompt = document.getElementById('manualSystemPrompt');
const userPrompt = document.getElementById('userPrompt');
const classificationMode = document.getElementById('classificationMode');
const status = document.getElementById('statusMessage');

temperature.oninput = () => {
  tempValue.textContent = temperature.value;
};

async function saveConfig() {
  const payload = {
    llm_model: modelSelect.value,
    temperature: parseFloat(temperature.value),
    user_prompt_template: userPrompt.value,
    classification_mode: classificationMode.value,
    sql_system_prompt: sqlSystemPrompt.value,
    manual_system_prompt: manualSystemPrompt.value
  };

  const res = await fetch('/chat_config', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });

  const result = await res.json();
  status.textContent = result.message || '✅ 설정이 저장되었습니다';
}

async function loadConfig() {
  try {
    const [configRes, exampleRes] = await Promise.all([
      fetch('/chat_config'),
      fetch('/config/example.json')
    ]);
    const config = await configRes.json();
    const example = await exampleRes.json();

    // 설정값이 존재하지 않으면 example.json 값으로 초기화
    modelSelect.value = config.llm_model || example.llm_model || 'gpt-4o-mini';
    temperature.value = config.temperature ?? example.temperature ?? 0.7;
    tempValue.textContent = temperature.value;

    sqlSystemPrompt.value = config.sql_system_prompt || example.sql_system_prompt || '';
    manualSystemPrompt.value = config.manual_system_prompt || example.manual_system_prompt || '';
    userPrompt.value = config.user_prompt_template || example.user_prompt_template || '';
    classificationMode.value = config.classification_mode || example.classification_mode || 'keyword';

  } catch (e) {
    console.warn("❌ 설정 또는 예시 불러오기 실패", e);
  }
}

document.addEventListener('DOMContentLoaded', async () => {
  await loadConfig();
  await loadExamplePrompts();  // ✅ 반드시 호출
});

