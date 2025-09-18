import pyskat.data_model as data_model
import pyskat.api as api
import pyskat.dependencies as dependencies
from fastapi import FastAPI

__all__ = ["data_model", "api", "app", "dependencies"]

app = FastAPI()

app.include_router(api.router)
