import uvicorn
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from statsapi.api.endpoints import router as endpoint_router
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError, HTTPException
from statsapi.api.models import ChannelType
import re

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


@app.middleware("https")
@app.middleware("http")
async def validate_request(request: Request, call_next):

    string = [str(ch.value) for ch in ChannelType]
    exp = re.compile("|".join(string))
    channels_type = exp.findall(request.url.query)
    path = request.url.components.path

    if path == "/channels":
        if not channels_type and bool(request.query_params):
            return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                content={"reason": "Requested invalid channel type"})

        elif len(channels_type) > 1:
            return JSONResponse(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                content={"reason": f"Duplicated channel_type query param: {', '.join(channels_type)}"})

    response = await call_next(request)
    return response


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder(content={"reason": {exc.name}}))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
