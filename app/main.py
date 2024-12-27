from fastapi import FastAPI
from routes import router
from db.session import engine
from sqlmodel import SQLModel
from db import TableModel
from core.config import Settings

# Create the tables in the database
# TableModel.metadata.create_all(bind=engine)

def include_router(app):
    app.include_router(router)


def start_application():
    app = FastAPI(
        title=Settings.PROJECT_NAME,
        version=Settings.PROJECT_VERSION,
        description=Settings.PROJECT_DESCRIPTION
    ) 
    include_router(app)
    return app

app = start_application()


@app.get("/")
def read_root():
    return {"message": "FastAPI app is!"}
