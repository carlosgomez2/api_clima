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
import requests as req

# Load environment variables
import os
from dotenv import load_dotenv

load_dotenv()

models.Base.metadata.create_all(bind=engine)

# Metadata for swagger

description = """
clima_api challenge Carlos Gomez. 🚀

## Users

You will be able to:

* **Create users**.
* **Read users**.
* **Update users**.
* **Delete users (hard)**.
* **Deactivate users (soft delete)**.
"""

app = FastAPI(
    title="Clima API",
    description=description,
    version="0.0.1",
    terms_of_service="http://example.com/terms/",
    contact={
        "name": "Carlos Gomez",
        "url": "https://carlosgomezror.dev",
        "email": "carlosgomez.deb@gmail.com",
    },
    license_info={
        "name": "MIT",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
)

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


# Users

# GET /users/
@app.post("/users/", response_model=schemas.User, tags=["Users"])
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    else:
        db_user = crud.create_user(db=db, user=user)

    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error while creating user"
        )
    return db_user

# GET /users/:id
@app.get("/users/{user_id}", response_model=schemas.User, tags=["Users"])
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

# PATCH /users/:id
@app.patch("/users/{user_id}", response_model=schemas.User, tags=["Users"])
def update_user(user_id: int, user: schemas.UserUpdate, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    db_user = crud.update_user(db, user_id, user)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

# DELETE /users/:id (hard delete)
@app.delete("/users/{user_id}", response_model=schemas.User, tags=["Users"])
def delete_user(user_id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    db_user = crud.delete_user(db, user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

# DELETE /users/soft/:id (soft delete)
@app.delete("/users/soft/{user_id}", response_model=schemas.User, tags=["Users"])
def deactivate_user(user_id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    db_user = crud.deactivate_user(db, user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if not db_user:
        raise HTTPException(status_code=400, detail="User already deactivated")
    return db_user

# GET /users/
@app.get("/users/", response_model=List[schemas.User], tags=["Users"])
def read_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


# Pronosticos

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
    try:
        response = req.get(f"{os.getenv("API_URL")}/{os.getenv("PRONOSTICO_ENDPOINT")}/{ciudad}")
        response.raise_for_status()
        data = response.json()
        pronostico = data["pronostico"] if data["pronostico"] else "No disponible"
        temperatura = data["temperatura"] if data["temperatura"] else "No disponible"
        return pronostico, temperatura
    except req.exceptions.HTTPError as err:
        if response.status_code == 502:
            raise HTTPException(status_code=502, detail="Bad Gateway: Invalid response from upstream server")
        elif response.status_code == 504:
            raise HTTPException(status_code=504, detail="Gateway Timeout: No response from upstream server")
        else:
            raise HTTPException(status_code=500, detail="HTTP error occurred")
    except req.exceptions.RequestException as err:
        raise HTTPException(status_code=500, detail="Network error occurred")

@app.get("/db_seed", tags=["Seed"])
def seed_db(db: Session = Depends(get_db), current_user: schemas.User = Depends(auth.get_current_user)):
    try:
        response = req.get(f"{os.getenv("API_URL")}/{os.getenv("SEED_ENDPOINT")}")
        response.raise_for_status()
        cities = response.json()
        for city in cities:
            pronostico, temperatura = obtener_pronostico(city)
            weather_query = schemas.WeatherQueryCreate(
                city=city,
                temperature=temperatura
            )
            crud.create_weather_query(db=db, query=weather_query, user_id=current_user.id)
        return {"message": "Database seeded"}
    except req.exceptions.HTTPError as err:
        if response.status_code == 502:
            raise HTTPException(status_code=502, detail="Bad Gateway: Invalid response from upstream server")
        elif response.status_code == 504:
            raise HTTPException(status_code=504, detail="Gateway Timeout: No response from upstream server")
        else:
            raise HTTPException(status_code=500, detail="HTTP error occurred")
    except req.exceptions.RequestException as err:
        raise HTTPException(status_code=500, detail="Network error occurred")