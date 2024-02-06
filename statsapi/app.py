from typing import Union
import uvicorn
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError, HTTPException
from statsapi.api.endpoints import router as endpoint_router


def api_schema():
    openapi_schema = get_openapi(
        title="Channel stats API",
        version="1.0",
        routes=app.routes)

    openapi_schema["info"] = {"title": "Channel stats API"}
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app = FastAPI()
app.openapi = api_schema
app.include_router(endpoint_router)


@app.exception_handler(RequestValidationError)
@app.exception_handler(HTTPException)
async def validation_exception_handler(request: Request, exc: Union[RequestValidationError, HTTPException]):

    if isinstance(exc, RequestValidationError):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=jsonable_encoder(exc.errors()))

    if isinstance(exc, HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content=jsonable_encoder(exc.detail))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
