from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from ..db.database import get_db
from ..models import Process, User, ProcessStep
from ..core.auth import SECRET_KEY, ALGORITHM
from ..services.analysis import generate_diagnostic

router = APIRouter(prefix="/diagnostics", tags=["diagnostics"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_current_user(db: Session, token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=401, detail="Usuário não encontrado")
    return user

@router.get("/{process_id}")
def get_diagnostic(process_id: int, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    user = get_current_user(db, token)
    process = db.query(Process).filter(Process.id == process_id, Process.owner_id == user.id).first()
    if not process:
        raise HTTPException(status_code=404, detail="Processo não encontrado")
    return generate_diagnostic(process)

@router.get("/dashboard/overview")
def dashboard_overview(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    user = get_current_user(db, token)
    processes = db.query(Process).filter(Process.owner_id == user.id).all()
    process_ids = [p.id for p in processes]
    steps = db.query(ProcessStep).filter(ProcessStep.process_id.in_(process_ids)).all() if process_ids else []

    return {
        "total_processes": len(processes),
        "total_steps": len(steps),
        "execution_time_total": sum(step.execution_time for step in steps),
        "waiting_time_total": sum(step.waiting_time for step in steps),
        "rework_steps": sum(1 for step in steps if step.has_rework),
        "non_value_steps": sum(1 for step in steps if not step.adds_value),
    }
