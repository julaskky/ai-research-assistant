from backend.app.database.database import Base, engine
from backend.app.database.models import Paper


def initialize_database():
    Base.metadata.create_all(bind=engine)