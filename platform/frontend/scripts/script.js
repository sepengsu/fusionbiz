async function fetchVideo() {
    const url = document.getElementById("urlInput").value;
    const errorMessage = document.getElementById("errorMessage");
    const videoContainer = document.getElementById("videoContainer");
    errorMessage.textContent = "";
    videoContainer.innerHTML = "";

    try {
        const response = await fetch(`http://127.0.0.1:8000/fetch_video/?url=${encodeURIComponent(url)}`);
        const data = await response.json();
        
        if (data.video_url) {
            videoContainer.innerHTML = `<video controls><source src="${data.video_url}" type="video/mp4">Your browser does not support the video tag.</video>`;
        } else if (data.iframe_url) {
            videoContainer.innerHTML = `<iframe src="${data.iframe_url}" allowfullscreen></iframe>`;
        } else {
            errorMessage.textContent = "No video found on the provided URL.";
        }
    } catch (error) {
        errorMessage.textContent = "Error fetching video.";
    }
}
