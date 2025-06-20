from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from sqlalchemy import text

# Create the database engine

print(settings.DATABASE_URL)
engine = create_engine(settings.DATABASE_URL)

# Create a session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()

# Dependency for getting the database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def setup_trade_notify_trigger():
    sql_function = text("""
    CREATE OR REPLACE FUNCTION trade_notify() RETURNS trigger AS $$
    BEGIN
      PERFORM pg_notify('trade_updates', to_json(NEW)::text);
      RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
    """)

    sql_trigger = text("""
    DO $$
    BEGIN
      IF NOT EXISTS (
        SELECT 1 FROM pg_trigger WHERE tgname = 'on_trade_change'
      ) THEN
        CREATE TRIGGER on_trade_change
        AFTER INSERT OR UPDATE ON trades
        FOR EACH ROW EXECUTE PROCEDURE trade_notify();
      END IF;
    END;
    $$;
    """)

    session = SessionLocal()
    try:
        session.execute(sql_function)
        session.execute(sql_trigger)
        session.commit()
    except Exception as e:
        session.rollback()
        print(f"Trigger setup failed: {e}")
    finally:
        session.close()

