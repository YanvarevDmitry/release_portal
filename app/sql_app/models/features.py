from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from sql_app.database import Base


class Feature(Base):
    __tablename__ = 'features'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    status = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False)
    feature_type_id = Column(Integer, nullable=False)


class FeatureType(Base):
    __tablename__ = 'feature_types'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)

