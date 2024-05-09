from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Users(Base):
    __tablename__ = 'Users'

    ID = Column(Integer, primary_key=True, )
    Name = Column(String(length=255), nullable=False)

    tasks = relationship("Tasks", back_populates="user")
    achievements = relationship("Achievement", back_populates="user")


class Tasks(Base):
    __tablename__ = 'Tasks'

    ID = Column(Integer, primary_key=True)
    User_ID = Column(Integer, ForeignKey('Users.ID'))
    Type = Column(String(length=255), nullable=False)
    Title = Column(String(length=255), nullable=False)
    Status = Column(String(length=255), nullable=False)
    Reason = Column(String(length=255), nullable=False)

    user = relationship("Users", back_populates="tasks")


class Achievement(Base):
    __tablename__ = 'Achievement'

    ID = Column(Integer, primary_key=True)
    User_ID = Column(Integer, ForeignKey('Users.ID'))
    Title = Column(String(length=255), nullable=False)
    Description = Column(String(length=255), nullable=False)

    user = relationship("Users", back_populates="achievements")
