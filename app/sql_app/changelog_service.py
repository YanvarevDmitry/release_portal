from sql_app.models.changelog import ChangeLog


def create_changelog(stage_id: int, user_id: int, action: str, db) -> ChangeLog:
    changelog = ChangeLog(stage_id=stage_id, user_id=user_id, action=action)
    db.session.add(changelog)
    db.session.commit()
    return changelog
