import sys
import os
sys.path.append(os.getcwd())

from app.db.session import engine, Base
from app.models import models

print("Creating tables in:", engine.url)
Base.metadata.create_all(bind=engine)
print("Tables created successfully.")
