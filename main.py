from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from datetime import timedelta
from jose import JWTError, jwt
import random
from pydantic import BaseModel
from typing import List, Optional
from passlib.context import CryptContext
from database import engine, SessionLocal, get_db
import models, schemas, crud, auth

# Load environment variables
import os
from dotenv import load_dotenv

load_dotenv()

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.post("/token", response_model=schemas.Token, tags=["Authentication"])
async def login_for_access_token(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=400,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# GET /users/
@app.post("/users/", response_model=schemas.User, tags=["Users"])
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return crud.create_user(db=db, user=user)

# GET /users/:id
@app.get("/users/{user_id}", response_model=schemas.User, tags=["Users"])
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

# PATCH /users/:id
@app.patch("/users/{user_id}", response_model=schemas.User, tags=["Users"])
def update_user(user_id: int, user: schemas.UserUpdate, db: Session = Depends(get_db)):
    db_user = crud.update_user(db, user_id, user)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

# DELETE /users/:id
@app.delete("/users/{user_id}", response_model=schemas.User, tags=["Users"])
def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.delete_user(db, user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user




@app.get("/pronostico/{ciudad}", response_model=schemas.Pronostico, tags=["Pronostico"])
async def get_pronostico(ciudad: str, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    pronostico, temperatura = obtener_pronostico(ciudad)
    weather_query = schemas.WeatherQueryCreate(
        city=ciudad,
        temperature=temperatura
    )
    crud.create_weather_query(db=db, query=weather_query, user_id=current_user.id)
    return {"ciudad": ciudad, "pronostico": pronostico, "temperatura": temperatura}

def obtener_pronostico(ciudad: str):
    pronosticos = ["Soleado", "Parcialmente nublado", "Nublado", "Lluvias ligeras", "Tormentas", "Despejado"]
    pronostico = random.choice(pronosticos)
    temperatura = round(random.uniform(15.0, 35.0), 1)
    return pronostico, temperatura