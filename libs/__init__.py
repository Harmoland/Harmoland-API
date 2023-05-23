from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import ORJSONResponse

from .database import DatabaseManager

app = FastAPI(
    title='Harmoland Console',
    description='API of Harmoland Console',
    default_response_class=ORJSONResponse,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

db = DatabaseManager('sqlite+aiosqlite:///data/harmoland-console.db')
