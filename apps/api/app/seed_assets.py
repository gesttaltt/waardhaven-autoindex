from sqlalchemy.orm import Session
from .core.database import SessionLocal
from .services.refresh import ensure_assets

def main():
    db: Session = SessionLocal()
    ensure_assets(db)
    print("Assets ensured.")

if __name__ == "__main__":
    main()
