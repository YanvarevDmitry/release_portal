from sqlalchemy import Column, Integer, String

from sql_app.database import Base


class Channel(Base):
    __tablename__ = 'channels'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
