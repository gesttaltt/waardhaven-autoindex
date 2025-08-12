from .core.database import Base, engine
from . import models

def main():
    Base.metadata.create_all(bind=engine)
    print("DB tables created.")

if __name__ == "__main__":
    main()
