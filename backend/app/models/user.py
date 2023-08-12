from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from app.constants.user import UserStatus

from app.services.auth import rnd

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False)
    password = Column(String(255))
    name = Column(String(255))
    email_verified = Column(Boolean, default=False)
    picture = Column(String(255))
    refresh_token = Column(String(255), default=rnd)
    login_attempt = Column(Integer, default=0, nullable=False)
    status = Column(Integer, default=UserStatus.PASSIVE, nullable=False)
    notes = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime)
    created_ip = Column(String(255))
    updated_ip = Column(String(255))

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'picture': self.picture,
        }

    def to_public(self):
        return {
            'id': self.id,
            'name': self.name,
            'picture': self.picture,
        }
