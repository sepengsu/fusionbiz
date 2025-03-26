async function apiRequest(url, method = 'GET', body = null) {
    try {
        const options = {
            method,
            headers: { 'Content-Type': 'application/json' }
        };
        if (body) {
            options.body = JSON.stringify(body);
        }

        const response = await fetch(url, options);
        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.detail || 'API 오류');
        }

        return data;
    } catch (error) {
        console.error('❌ API 오류:', error);
        throw error;
    }
}

async function startRecording() {
    const durationInput = document.getElementById('duration');
    const recordBtn = document.getElementById('recordBtn');
    const recordingStatus = document.getElementById('recordingStatus');

    if (!durationInput || !recordBtn || !recordingStatus) return;

    const duration = parseInt(durationInput.value || "5");
    recordBtn.disabled = true;
    recordingStatus.textContent = '녹음 중...';

    try {
        const result = await apiRequest('/recordings/record', 'POST', { duration });
        recordingStatus.textContent = `녹음 완료: ${result.filename}`;
        await loadRecordings();
    } catch (error) {
        recordingStatus.textContent = `녹음 실패: ${error.message}`;
    } finally {
        recordBtn.disabled = false;
        setTimeout(() => {
            recordingStatus.textContent = '';
        }, 3000);
    }
}

async function loadRecordings() {
    try {
        const recordings = await apiRequest('/recordings/');
        const list = document.getElementById('recordings');
        list.innerHTML = '';

        recordings.forEach(name => {
            const li = document.createElement('li');
            const link = document.createElement('a');
            link.href = `/recordings/${name}`;
            link.textContent = name;
            link.download = name;
            li.appendChild(link);
            list.appendChild(li);
        });
    } catch (e) {
        console.error("녹음 목록 로딩 오류:", e);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    document.getElementById('recordBtn')?.addEventListener('click', startRecording);
    loadRecordings();
});
