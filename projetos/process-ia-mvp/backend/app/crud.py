from sqlalchemy.orm import Session
from . import models, schemas


# -------------------------
# Processos
# -------------------------
def create_process(db: Session, process: schemas.ProcessCreate):
    db_process = models.Process(**process.model_dump())
    db.add(db_process)
    db.commit()
    db.refresh(db_process)
    return db_process


def list_processes(db: Session):
    return db.query(models.Process).all()


def get_process(db: Session, process_id: int):
    return db.query(models.Process).filter(models.Process.id == process_id).first()


def delete_process(db: Session, process_id: int):
    process = get_process(db, process_id)
    if not process:
        return None
    db.delete(process)
    db.commit()
    return process


# -------------------------
# Etapas
# -------------------------
def create_step(db: Session, process_id: int, step: schemas.ProcessStepCreate):
    db_step = models.ProcessStep(process_id=process_id, **step.model_dump())
    db.add(db_step)
    db.commit()
    db.refresh(db_step)
    return db_step


def get_step(db: Session, step_id: int):
    return db.query(models.ProcessStep).filter(models.ProcessStep.id == step_id).first()


def delete_step(db: Session, step_id: int):
    step = get_step(db, step_id)
    if not step:
        return None
    db.delete(step)
    db.commit()
    return step
