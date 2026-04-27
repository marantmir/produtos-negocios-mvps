from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from ..db.database import get_db
from ..models import Process, ProcessStep, User
from ..schemas import ProcessCreate, ProcessRead, ProcessStepCreate, ProcessStepRead
from ..core.auth import SECRET_KEY, ALGORITHM

router = APIRouter(prefix="/processes", tags=["processes"])

def get_token(authorization: str | None = Header(None)) -> str | None:
    if authorization and authorization.startswith("Bearer "):
        return authorization.split(" ", 1)[1]
    return None

def get_default_user(db: Session) -> User:
    guest_email = "guest@process-ia.local"
    guest = db.query(User).filter(User.email == guest_email).first()
    if not guest:
        guest = User(full_name="Convidado", email=guest_email, password_hash="")
        db.add(guest)
        db.commit()
        db.refresh(guest)
    return guest

def get_current_user(db: Session, token: str | None):
    if not token:
        return get_default_user(db)

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=401, detail="Usuário não encontrado")
    return user

@router.post("/", response_model=ProcessRead, status_code=status.HTTP_201_CREATED)
def create_process(payload: ProcessCreate, token: str | None = Depends(get_token), db: Session = Depends(get_db)):
    user = get_current_user(db, token)
    process = Process(owner_id=user.id, **payload.model_dump())
    db.add(process)
    db.commit()
    db.refresh(process)
    return process

@router.get("/", response_model=list[ProcessRead])
def list_processes(token: str | None = Depends(get_token), db: Session = Depends(get_db)):
    user = get_current_user(db, token)
    return db.query(Process).filter(Process.owner_id == user.id).all()

@router.get("/{process_id}", response_model=ProcessRead)
def get_process(process_id: int, token: str | None = Depends(get_token), db: Session = Depends(get_db)):
    user = get_current_user(db, token)
    process = db.query(Process).filter(Process.id == process_id, Process.owner_id == user.id).first()
    if not process:
        raise HTTPException(status_code=404, detail="Processo não encontrado")
    return process

@router.put("/{process_id}", response_model=ProcessRead)
def update_process(process_id: int, payload: ProcessCreate, token: str | None = Depends(get_token), db: Session = Depends(get_db)):
    user = get_current_user(db, token)
    process = db.query(Process).filter(Process.id == process_id, Process.owner_id == user.id).first()
    if not process:
        raise HTTPException(status_code=404, detail="Processo não encontrado")

    for field, value in payload.model_dump().items():
        setattr(process, field, value)

    db.commit()
    db.refresh(process)
    return process

@router.delete("/{process_id}")
def delete_process(process_id: int, token: str | None = Depends(get_token), db: Session = Depends(get_db)):
    user = get_current_user(db, token)
    process = db.query(Process).filter(Process.id == process_id, Process.owner_id == user.id).first()
    if not process:
        raise HTTPException(status_code=404, detail="Processo não encontrado")

    db.delete(process)
    db.commit()
    return {"message": "Processo removido com sucesso"}

@router.post("/{process_id}/steps", response_model=ProcessStepRead, status_code=status.HTTP_201_CREATED)
def create_step(process_id: int, payload: ProcessStepCreate, token: str | None = Depends(get_token), db: Session = Depends(get_db)):
    user = get_current_user(db, token)
    process = db.query(Process).filter(Process.id == process_id, Process.owner_id == user.id).first()
    if not process:
        raise HTTPException(status_code=404, detail="Processo não encontrado")

    step = ProcessStep(process_id=process_id, **payload.model_dump())
    db.add(step)
    db.commit()
    db.refresh(step)
    return step

@router.put("/steps/{step_id}", response_model=ProcessStepRead)
def update_step(step_id: int, payload: ProcessStepCreate, token: str | None = Depends(get_token), db: Session = Depends(get_db)):
    user = get_current_user(db, token)
    step = db.query(ProcessStep).join(Process).filter(ProcessStep.id == step_id, Process.owner_id == user.id).first()
    if not step:
        raise HTTPException(status_code=404, detail="Etapa não encontrada")

    for field, value in payload.model_dump().items():
        setattr(step, field, value)

    db.commit()
    db.refresh(step)
    return step

@router.delete("/steps/{step_id}")
def delete_step(step_id: int, token: str | None = Depends(get_token), db: Session = Depends(get_db)):
    user = get_current_user(db, token)
    step = db.query(ProcessStep).join(Process).filter(ProcessStep.id == step_id, Process.owner_id == user.id).first()
    if not step:
        raise HTTPException(status_code=404, detail="Etapa não encontrada")

    db.delete(step)
    db.commit()
    return {"message": "Etapa removida com sucesso"}
