from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class UserBase(BaseModel):
    username: str
    email: str
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: Optional[str] = None
    full_name: Optional[str] = None
    password: Optional[str] = None

class User(UserBase):
    id: int

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class Pronostico(BaseModel):
    ciudad: str
    pronostico: str
    temperatura: float

class WeatherQueryBase(BaseModel):
    city: str
    temperature: float

class WeatherQueryCreate(WeatherQueryBase):
    pass

class WeatherQuery(WeatherQueryBase):
    id: int
    user_id: int
    query_time: str

    class Config:
        from_attributes = True