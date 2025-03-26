import os
import uuid
import sounddevice as sd
import soundfile as sf
from datetime import datetime

class AudioRecorderService:
    def __init__(self, recordings_dir='recordings'):
        self.recordings_dir = recordings_dir
        os.makedirs(self.recordings_dir, exist_ok=True)

    def record_system_audio(self, duration=10, sample_rate=44100):
        file_id = str(uuid.uuid4())
        filename = f"recording_{file_id}.wav"
        file_path = os.path.join(self.recordings_dir, filename)

        try:
            print(">>> [1] 루프백 장치 탐지 시작")
            device_index = self._find_loopback_device()
            print(f">>> [2] 장치 탐지 완료: index={device_index}")

            wasapi_settings = sd.WasapiSettings(loopback=True)

            print(f">>> [3] 녹음 시작: {filename}")
            recording = sd.rec(
                int(duration * sample_rate),
                samplerate=sample_rate,
                channels=2,
                dtype='float32',
                device=device_index,
                blocking=True,
                extra_settings=wasapi_settings
            )
            sd.wait()
            print(f">>> [4] 녹음 완료, shape={recording.shape}")

            if recording is None or recording.size == 0:
                raise RuntimeError("녹음된 데이터가 없습니다. 오디오 장치를 확인하세요.")

            print(f">>> [5] 녹음 max={recording.max()}, min={recording.min()}")

            sf.write(file_path, recording, sample_rate)
            print(f">>> [6] 파일 저장 완료: {file_path}")

            return {
                'id': file_id,
                'filename': filename,
                'duration': duration,
                'created_at': datetime.now(),
                'file_path': file_path
            }

        except Exception as e:
            print(f">>> [오류] 녹음 중 예외 발생: {e}")
            raise RuntimeError(f"오디오 녹음 실패: {e}")

    def list_recordings(self):
        return [f for f in os.listdir(self.recordings_dir) if f.endswith('.wav')]

    def get_recording(self, filename):
        file_path = os.path.join(self.recordings_dir, filename)
        return file_path if os.path.exists(file_path) else None

    def _find_loopback_device(self):
        try:
            devices = sd.query_devices()
            for i, dev in enumerate(devices):
                if (
                    dev['hostapi'] == sd.default.hostapi and
                    dev['max_output_channels'] > 0 and
                    'WASAPI' in dev['name'] and
                    ('Speaker' in dev['name'] or '스피커' in dev['name'])
                ):
                    print(f">>> [탐지] 루프백 장치 발견: {dev['name']} (index={i})")
                    return i
        except Exception as e:
            raise RuntimeError(f"장치 탐지 중 오류: {e}")

        raise RuntimeError("루프백 가능한 WASAPI 스피커 장치를 찾을 수 없습니다.")
