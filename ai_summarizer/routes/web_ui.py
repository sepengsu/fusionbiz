from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@router.get("/result")
async def result(request: Request, summary: str = ""):
    return templates.TemplateResponse("result.html", {"request": request, "summary": summary})
