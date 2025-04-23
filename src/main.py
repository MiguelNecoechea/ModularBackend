# Fast API
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List


# Services
from .services.ruby_service import RubyService

class TextRequest(BaseModel):
    text: str


class NLPApplication:
    def __init__(self):
        self.app = FastAPI(title="NLPApi", version="1.0.0")
        self.ruby_service = RubyService()
        self._setup_middleware()
        self._register_routes()

    def _setup_middleware(self):
        # CORS Middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    def _register_routes(self):
        @self.app.post("/annotate_html", response_class=HTMLResponse)
        async def annotate_html(request: TextRequest):
            annotated_text = self.ruby_service.annotate_html(request.text)
            return HTMLResponse(content=annotated_text, status_code=200)


def create_app():
    return NLPApplication().app

app = create_app()
