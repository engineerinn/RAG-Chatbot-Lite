import asyncio
import logging
import json
import re
from fastapi import APIRouter, HTTPException, File, UploadFile
from pydantic import BaseModel
from app.core.constants.enums import UploadedFileType
from fastapi.responses import StreamingResponse
from fastapi.responses import JSONResponse
from typing import AsyncGenerator, Any, Dict

log = logging.getLogger(__name__)

class SearchRequest(BaseModel):
    query: str
    contextData: Dict[str, Any]

class RoutingController:

    def __init__(self):

        self.router = self.init_router()

    def init_router(self):
        try:
            self.router = APIRouter()

            #These routings if for dev environment and testing
            self.router.add_api_route("/hybridsearchtest/", self.hybrid_search_test, methods=["POST"])
            self.router.add_api_route("/vector", self.return_vector, methods=["POST"])
            # -----------------------------------------------------------------------------------

            #These routings are for live / production environment
            self.router.add_api_route("/chat/inquiry", self.stream_response, methods=["POST"])
            self.router.add_api_route("/process/docs", self.retrieve_docs, methods=["POST"])
            self.router.add_api_route("/upload/docs", self.retrieve_docs_pymupdf, methods=["POST"])


            return self.router
        except Exception as e:
            log.error(f"Router Initialization failed. Error: {str(e)}")

    #For Development and Testing
    async def hybrid_search_test(self, request: SearchRequest):

        try:
            query_embedding = await self.emdb_service.get_kr_embedding("EU AI 법에서 금지하는 AI 활용 사례 두 가지를 제시하세요")
            log.info(f"Query embedding: {query_embedding}")

            results = await self.es_service.hybrid_search(doc_title=request.contextData["doc_title"],
                                                          query=request.query)

            return results

        except RuntimeError as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def return_vector(self, request: SearchRequest):
        return await self.emdb_service.get_kr_embedding(text=request.query)

    async def summarize_doc(self, request: SearchRequest):
        chunk = await self.es_service.get_all_chunks(doc_title=request.query)
        await self.llm_service.summarize(chunk)
        pass

    # -----------------------------------------------------------------------------------
    #These functions are "live-to-be" functions
    async def stream_response(self, request:SearchRequest) -> StreamingResponse:

        log.info(f"Incoming request: {request}")
        async def event_generator() -> AsyncGenerator[str, None]:

            #await asyncio.sleep(1)
            log.info(f"Incoming request --> {request.query} || {request.contextData}")

            data = None
            if (request.contextData['doc_title']==""):
                log.info("요청하는 문저 이름이 없습니다. 질문을 분석하겠습니다.")
                result = await self.llm_service.parse_the_questions(query=request.query)
                match = re.search(r"\{.*\}", result, re.DOTALL)
                if match:
                    data = json.loads(match.group())
                    print(data)
            else:
                log.info("요청하는 문저 이름이 있습니다.")
                data= {}
                data["document_title"] = request.contextData['doc_title']
                data["user_input"] = request.query

            ctx_data = await self.es_service.hybrid_search(doc_title=data["document_title"],
                                                               query=data["user_input"])
            response_chunks = await self.llm_service.generate_response(query=data["user_input"],
                                                                       doc_title=data["document_title"],
                                                                       ctx_data= ctx_data)

            #response_chunks = "더미 반응"
            print("Received data")
            print(response_chunks)

            for chunk in response_chunks:
                #print(chunk)
                if chunk == "\n":
                    chunk = chunk.replace("\n", "<br>")
                if chunk =="*":
                    continue

                yield f"data: {chunk}\n\n"
                await asyncio.sleep(0.01)

            yield "data: [END]\n\n"

        return StreamingResponse(event_generator(), media_type="text/event-stream")

    async def retrieve_docs(self, file: UploadFile = File(...)):

        log.info("받은 문서: "+ file.filename)
        log.info("받은 문서 유형:"+ file.content_type)

        match file.content_type:
            case UploadedFileType.PDF:
                await self.pdf_cnvter.convert_pdf( filename = file.filename,
                                                       file_bytes = await file.read())
            case UploadedFileType.DOCX:
                await self.docx_cnvter.convert_docx( filename = file.filename,
                                                       file_bytes = await file.read())
            case _:
                log.info("처리는 안됩니다.")
                raise HTTPException(status_code=500, detail="Internal Server Error")

    async def retrieve_docs_pymupdf(self, file: UploadFile = File(...)):

        log.info("받은 문서: " + file.filename)
        log.info("받은 문서 유형:" + file.content_type)

        await self.pdf_cnvter.convert_pdf( filename = file.filename, file_bytes = await file.read())



