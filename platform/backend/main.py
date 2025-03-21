from fastapi import FastAPI
import requests
from bs4 import BeautifulSoup
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

app = FastAPI()

# CORS 설정 (프론트엔드에서 API 호출 허용)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 도메인 허용 (개발용)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 루트 엔드포인트 (기본 페이지)
@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <html>
        <head>
            <title>FastAPI Video Fetcher</title>
            <script>
                async function fetchVideo() {
                    const url = document.getElementById("urlInput").value.trim();
                    const errorMessage = document.getElementById("errorMessage");
                    const videoContainer = document.getElementById("videoContainer");
                    errorMessage.textContent = "";
                    videoContainer.innerHTML = "";
                    
                    if (!url) {
                        errorMessage.textContent = "Please enter a valid URL.";
                        return;
                    }
                    
                    try {
                        const response = await fetch(`/fetch_video/?url=${encodeURIComponent(url)}`);
                        const data = await response.json();
                        if (data.video_url) {
                            videoContainer.innerHTML = `<video controls><source src="${data.video_url}" type="video/mp4">Your browser does not support the video tag.</video>`;
                        } else if (data.iframe_url) {
                            videoContainer.innerHTML = `<iframe src="${data.iframe_url}" allowfullscreen></iframe>`;
                        } else {
                            errorMessage.textContent = "No video found on the provided URL.";
                        }
                    } catch (error) {
                        errorMessage.textContent = "Error fetching video. Please try again.";
                    }
                }
            </script>
        </head>
        <body>
            <h1>FastAPI Video Fetcher</h1>
            <input type="text" id="urlInput" placeholder="Enter webpage URL">
            <button onclick="fetchVideo()">Fetch Video</button>
            <p id="errorMessage" style="color: red;"></p>
            <div id="videoContainer"></div>
        </body>
    </html>
    """

# 비디오 URL 가져오기 API
@app.get("/fetch_video/")
async def fetch_video(url: str):
    url = url.strip()
    if not url:
        return {"error": "Invalid URL. Please provide a valid URL."}
    
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            return {"error": "Failed to fetch webpage"}
    except requests.exceptions.RequestException:
        return {"error": "Failed to connect to the provided URL."}
    
    soup = BeautifulSoup(response.text, "html.parser")
    
    # <video> 태그의 src 찾기
    video_tag = soup.find("video")
    if video_tag and video_tag.get("src"):
        return {"video_url": video_tag["src"]}
    
    # <iframe> 태그 (유튜브, Vimeo 등) 찾기
    iframe_tag = soup.find("iframe")
    if iframe_tag and iframe_tag.get("src"):
        return {"iframe_url": iframe_tag["src"]}

    return {"error": "No video found"}

# favicon.ico 요청 방지
@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return ""