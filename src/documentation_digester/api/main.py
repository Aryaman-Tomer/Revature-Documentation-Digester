from fastapi import FastAPI

from documentation_digester.api.routers.test import router

app = FastAPI()

app.include_router(router)
