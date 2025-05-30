const modelSelect = document.getElementById('modelSelect');
const temperature = document.getElementById('temperature');
const tempValue = document.getElementById('tempValue');
const systemPrompt = document.getElementById('systemPrompt');
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
    system_prompt: systemPrompt.value,
    user_prompt_template: userPrompt.value,
    classification_mode: classificationMode.value
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
  const res = await fetch('/chat_config');
  const config = await res.json();

  modelSelect.value = config.llm_model || 'gpt-4';
  temperature.value = config.temperature || 0.7;
  tempValue.textContent = temperature.value;
  systemPrompt.value = config.system_prompt || '';
  userPrompt.value = config.user_prompt_template || '';
  classificationMode.value = config.classification_mode || 'keyword';
}

document.addEventListener('DOMContentLoaded', loadConfig);
