from sqlalchemy.orm import Session
import models, schemas
from passlib.context import CryptContext
from sqlalchemy.exc import IntegrityError

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = pwd_context.hash(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        hashed_password=hashed_password
    )

    # Handle unique constraint violation
    # (psycopg2.errors.UniqueViolation) duplicate key value violates unique constraint "ix_users_email"
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    except IntegrityError as e:
        db.rollback()
        print(e)
        return None
    
    return db_user


def create_weather_query(db: Session, query: schemas.WeatherQueryCreate, user_id: int):
    db_query = models.WeatherQuery(**query.dict(), user_id=user_id)
    db.add(db_query)
    db.commit()
    db.refresh(db_query)
    return db_query

# Delete user/:id (hard delete)
def delete_user(db: Session, user_id: int):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()

    if not db_user:
        return None

    db.delete(db_user)
    db.commit()

    return db_user

# Soft delete user/:id
def deactivate_user(db: Session, user_id: int):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()

    if not db_user:
        return None

    if not db_user.active:
        return False

    db_user.deactivate(db)

    return db_user

# Update user/:id
def update_user(db: Session, user_id: int, user: schemas.UserUpdate):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()

    if not db_user:
        return None

    # Update user fields only if they are not None
    if user.email:
        db_user.email = user.email
    if user.full_name:
        db_user.full_name = user.full_name
    if user.password:
        db_user.password = pwd_context.hash(user.password)

    db.commit()
    db.refresh(db_user)

    return db_user

# GET /users/
def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()