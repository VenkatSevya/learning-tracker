import os
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, Response
from sqlalchemy import func, select, text
from sqlalchemy.orm import Session

from . import models, schemas
from .database import Base, engine, get_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)  # create the table on first start
    yield


app = FastAPI(
    title="Learning Tracker API",
    version=os.environ.get("APP_VERSION", "dev"),
    lifespan=lifespan,
    # Everything lives under /api so Nginx can send /api/* to this container
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
    redoc_url=None,
)


@app.get("/api/health")
def health(response: Response, db: Session = Depends(get_db)):
    """Used by Docker, Nginx and CI to know the API AND the database are alive."""
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ok", "database": "up", "version": app.version}
    except Exception:  # noqa: BLE001
        response.status_code = 503
        return {"status": "degraded", "database": "down"}


@app.get("/api/entries", response_model=list[schemas.EntryOut])
def list_entries(db: Session = Depends(get_db)):
    return db.scalars(select(models.Entry).order_by(models.Entry.id.desc())).all()


@app.post("/api/entries", response_model=schemas.EntryOut, status_code=201)
def create_entry(payload: schemas.EntryCreate, db: Session = Depends(get_db)):
    entry = models.Entry(
        topic=payload.topic.strip(), notes=payload.notes.strip(), hours=payload.hours
    )
    if not entry.topic:
        raise HTTPException(status_code=422, detail="topic cannot be blank")
    db.add(entry)
    db.commit()
    return entry


@app.delete("/api/entries/{entry_id}", status_code=204)
def delete_entry(entry_id: int, db: Session = Depends(get_db)):
    entry = db.get(models.Entry, entry_id)
    if entry is None:
        raise HTTPException(status_code=404, detail="entry not found")
    db.delete(entry)
    db.commit()
    return Response(status_code=204)


@app.get("/api/stats", response_model=schemas.Stats)
def stats(db: Session = Depends(get_db)):
    count, total = db.execute(
        select(func.count(models.Entry.id), func.coalesce(func.sum(models.Entry.hours), 0.0))
    ).one()
    top = db.execute(
        select(models.Entry.topic)
        .group_by(models.Entry.topic)
        .order_by(func.sum(models.Entry.hours).desc())
        .limit(1)
    ).scalar()
    return {"entries": count, "total_hours": round(float(total), 2), "top_topic": top}
