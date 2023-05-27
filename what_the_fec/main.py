import os
from datetime import date
from typing import Annotated

from fastapi import Depends, FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import Connection
from sqlalchemy.sql import text

from what_the_fec.dependencies import templates_init, get_templates, get_db_conn
from what_the_fec.routes.election_years import (
    get_all_election_years_func,
)
from what_the_fec.routes.home import home_page_func
from what_the_fec.routes.candidate_office_records.routes import router as candidate_office_records_router
from what_the_fec.storage.db import init as db_init
from what_the_fec.storage.mysql.config import MySQLConfig




def create_app() -> FastAPI:
    templates_init(
        templates=Jinja2Templates(directory=os.environ["TEMPLATES_DIR_PATH"])
    )

    db_init(
        config=MySQLConfig(
            db_user=os.environ["MARIA_DB_USER"],
            db_password=os.environ["MARIA_DB_PASSWORD"],
            db_hostname=os.environ["MARIA_DB_HOSTNAME"],
            db_port=os.environ["MARIA_DB_PORT"],
            db_name=os.environ["MARIA_DB_NAME"],
            pool_connections=2,
        )
    )

    app = FastAPI(
        dependencies=[Depends(get_db_conn), Depends(get_templates)],
    )
    app.mount(
        "/static", StaticFiles(directory=os.environ["STATIC_DIR_PATH"]), name="static"
    )
    

    @app.get("/", response_class=HTMLResponse)
    def home_page(request: Request):
        return home_page_func(
            request=request,
            templates=request.templates,
        )
    
    app.include_router(candidate_office_records_router)
    
    # @app.get("/election_years/", response_class=HTMLResponse)
    # def get_all_election_years(
    #     request: Request, conn: Connection = Depends(db.get_conn)
    # ):
    #     return get_all_election_years_func(
    #         conn=conn, request=request, templates=templates
    #     )


    return app
