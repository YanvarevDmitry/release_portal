from app.models import ReleaseStageCreate
from app.sql_app.models.releases import ReleaseStage


def create_release_stage(stage: ReleaseStageCreate, db) -> ReleaseStage:
    db_stage = ReleaseStage(**stage.dict())
    db.add(db_stage)
    db.commit()
    db.refresh(db_stage)
    return db_stage


def get_all_releases(db) -> list[ReleaseStage]:
    return db.query(ReleaseStage).all()
