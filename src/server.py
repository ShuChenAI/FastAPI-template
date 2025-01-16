import os
import subprocess
from typing import Annotated

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from starlette.requests import Request

from src.dependencies.auth import get_admin_user
from src.dependencies.basic import get_db
from src.routers.server import router
from src.schemas.basic import TextOnly

app = FastAPI(
    title="Template FastAPI Backend Server",
    description="Template Description",
    version="0.0.1",
    contact={
        "name": "Author Name",
        "email": "example@exmaple.com",
    },
    swagger_ui_parameters={'docExpansion': 'none'}
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/", response_model=TextOnly)
async def root():
    return TextOnly(text="Hello World")


@app.get("/elements", include_in_schema=False)
async def api_documentation(request: Request):
    return HTMLResponse("""
<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <title>Elements in HTML</title>

    <script src="https://unpkg.com/@stoplight/elements/web-components.min.js"></script>
    <link rel="stylesheet" href="https://unpkg.com/@stoplight/elements/styles.min.css">
  </head>
  <body>

    <elements-api
      apiDescriptionUrl="openapi.json"
      router="hash"
    />

  </body>
</html>""")


if os.getenv('DEV', 'false') == 'true':
    @app.post("/renewDB", dependencies=[Depends(get_admin_user)])
    async def renew_database():
        from src.database.database import TRIAL_URL, DB_NAME, engine, drop_all_tables
        from src.database.database import create_all_tables, create_database_if_not_exists
        from src.database.utils import add_test_data

        create_database_if_not_exists(TRIAL_URL, DB_NAME)
        drop_all_tables(engine)
        create_all_tables(engine)
        add_test_data()
        return TextOnly(text="Database Renewed")


@app.post('/alembic', dependencies=[Depends(get_admin_user)])
async def alembic(
        db: Annotated[Session, Depends(get_db)]
):
    # remove alembic_version table
    db.execute(text("DROP TABLE IF EXISTS alembic_version"))
    db.commit()

    # execute `bash /run/run_alembic.sh` and return the output
    process = subprocess.Popen(['/bin/bash', '/run/run_alembic.sh'],
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    output, error = process.communicate()

    return {
        "output": output.decode('utf-8').split('\n'),
        "error": error.decode('utf-8').split('\n')
    }
