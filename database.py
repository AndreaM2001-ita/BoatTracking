#database 

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, Boolean
from sqlalchemy.orm import sessionmaker, declarative_base
#from sqlalchemy.ext.declarative import 

# SQL Sever login credentials/connection string
SQLALCHEMY_DATABASE_URL = "mssql+pyodbc://BoatTracker:ecu2024@Slipstream\\SQLEXPRESS/master?driver=ODBC+Driver+17+for+SQL+Server"


#connection and interaction to database
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

base = declarative_base()

# Definition of BoatDetails model that will map to the 'boatDetails' table in the database
class BoatDetails(base):
    __tablename__ = "boatDetails"

    boatID = Column(Integer, primary_key=True, index=True)  
    boatModel = Column(String)  
    launchTime = Column(DateTime)  
    retrievalTime = Column(DateTime, nullable=True) 
    timeAtSea = Column(Float, nullable= True) 
    isOrphan = Column (Boolean, default= True)
    matchID = Column(Integer, nullable=True)

# Function that allows connection to the database and ensures it is closed after use 
async def get_db():
    db = SessionLocal() 
    try:
        yield db
        await db.refresh()
    finally:
        db.close()
