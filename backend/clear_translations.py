"""
Clear cached translations to force fresh translation generation
"""
import asyncio
from sqlmodel import Session, select, delete
from db.postgres import engine
from models.translation import Translation

def clear_translations():
    """Delete all cached translations"""
    with Session(engine) as session:
        # Delete all translations
        statement = delete(Translation)
        result = session.exec(statement)
        session.commit()
        print(f"Cleared {result.rowcount} cached translations")

if __name__ == "__main__":
    print("Clearing cached translations...")
    clear_translations()
    print("Done! Next translation request will generate fresh Urdu content.")
