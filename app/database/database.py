import os
from dotenv import load_dotenv
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Boolean,
    DateTime)
from sqlalchemy.orm import declarative_base 
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# -- Load environment variables --
# This line looks for a .env file in the directories
# and loads key-value pairs found there into the environment variables
load_dotenv()

# -- Connection to DB config --
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

# -- Construct DB url --
SQLALCHEMY_DATABASE_URL = (
    f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# -- SQLAlchemy engine setup --
# engine ensures the connection to the db
# pool_pre_ping=True -> helps ensure connections in the pool are still active
engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# every model inherits this class for the table
Base = declarative_base()

# -- Defining an ORM model (Task) --  
# That class is the table "tasks" in DB
class Task(Base):
    # __tablename__ -> points to the DB name
    __tablename__ = "tasks"

    # Defines columns, types, features of the table
    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, nullable=False)
    done = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.now)

    def __repr__(self):
        """
        Provides a helpful str representation of a Task object,
        useful for debugging and logging
        """
        return f"<Task(id='{self.id}', text='{self.text}', done='{self.done}', created_at='{self.created_at}')>"

# -- Func to create tables in DB -- 
# If table does not exits, the func will create it
def create_db_tables():
    Base.metadata.create_all(bind=engine)