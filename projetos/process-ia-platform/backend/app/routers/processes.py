from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from fastapi.security import OAuth2PasswordBearer
from ..database import get_db
from ..models import Process, ProcessStep, User
from ..schemas import ProcessCreate, ProcessRead, ProcessStepCreate, ProcessStepRead
from ..core.auth import SECRET_KEY, ALGORITHM

router = APIRouter(prefix="/processes", tags=["processes"])
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


@router.post("/", response_model=ProcessRead, status_code=status.HTTP_201_CREATED)
def create_process(payload: ProcessCreate, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    user = get_current_user(db, token)
    process = Process(owner_id=user.id, **payload.model_dump())
    db.add(process)
    db.commit()
    db.refresh(process)
    return process


    return {"message": "Etapa removida com sucesso"}
