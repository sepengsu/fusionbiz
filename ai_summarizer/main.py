from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from routes import text_summary, audio_summary, web_ui

app = FastAPI(title="AI Summarizer API", version="1.0")

# Register API routes
app.include_router(text_summary.router, prefix="/text")
app.include_router(audio_summary.router, prefix="/audio")
app.include_router(web_ui.router, prefix="")
 
# Serve static files (CSS, JS)
app.mount("/static", StaticFiles(directory="static"), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
