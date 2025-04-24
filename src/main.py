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

        @self.app.post("/change_reading_mode", response_class=HTMLResponse)
        async def change_reading_mode(request: TextRequest):
            """
            Change the reading mode of the RubyService.
            :param request: The request containing the new reading mode.
            :return: True if the reading mode was changed successfully, False otherwise.
            """
            if request.text == "hiragana":
                self.ruby_service.set_mode("hiragana")
            elif request.text == "romaji":
                self.ruby_service.set_mode("romaji")
            else:
                return HTMLResponse(content="Invalid mode. Use 'hiragana' or 'romaji'.", status_code=400)
            return HTMLResponse(content="Reading mode changed successfully.", status_code=200)


def create_app():
    return NLPApplication().app

app = create_app()
