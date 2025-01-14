from sqlalchemy import Column, Integer, String

from sql_app.database import Base


class Platform(Base):
    __tablename__ = 'platforms'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
