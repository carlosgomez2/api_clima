from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func, Float, Boolean
from sqlalchemy.orm import relationship
from database import Base
from sqlalchemy.orm import Session

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    email = Column(String, unique=True, index=True)
    full_name = Column(String)
    active = Column(Boolean, default=True) # Soft delete

    def deactivate(self, db: Session):
        self.active = False
        db.add(self)
        db.commit()

class WeatherQuery(Base):
    __tablename__ = 'weather_queries'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    city = Column(String)
    temperature = Column(Float)
    query_time = Column(DateTime, default=func.now())

    user = relationship("User", back_populates="queries")

User.queries = relationship("WeatherQuery", back_populates="user")


class BlackListToken(Base):
    __tablename__ = 'black_list_tokens'

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, index=True)
    revoked_at = Column(DateTime, default=func.now())
