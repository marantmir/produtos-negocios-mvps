from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List


class UserRegister(BaseModel):
    full_name: str = Field(..., min_length=2, max_length=255)
    email: EmailStr
    password: str = Field(..., min_length=6)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserRead(BaseModel):
    id: int
    full_name: str
    email: EmailStr

    model_config = {"from_attributes": True}


class ProcessStepBase(BaseModel):
    step_name: str
    step_order: int
    owner: Optional[str] = None
    execution_time: float = 0.0
    waiting_time: float = 0.0
    adds_value: bool = True
    has_rework: bool = False
    approvals: int = 0
    notes: Optional[str] = None


class ProcessStepCreate(ProcessStepBase):
    pass


class ProcessStepRead(ProcessStepBase):
    id: int
    process_id: int

    model_config = {"from_attributes": True}


class ProcessBase(BaseModel):
    name: str
    area: Optional[str] = None
    objective: Optional[str] = None
    customer: Optional[str] = None
    start_event: Optional[str] = None
    end_event: Optional[str] = None
    latest_answer: Optional[str] = None
