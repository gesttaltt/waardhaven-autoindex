from sqlalchemy.orm import Session
from .core.database import SessionLocal
from .services.refresh import refresh_all


def main():
    db: Session = SessionLocal()
    refresh_all(db)
    print("Refresh complete.")


if __name__ == "__main__":
    main()
