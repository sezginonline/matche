from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    from_user_id = Column(Integer, index=True)
    to_user_id = Column(Integer, index=True)
    message = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
