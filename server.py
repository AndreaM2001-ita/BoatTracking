# main server

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from database import engine, get_db, BoatDetails  # Import from database file

# Initialise the FastAPI app
app = FastAPI()

# Creation of database tables if they don't exist, ensuring they are always there
BoatDetails.metadata.create_all(bind=engine)

# API endpoint to create a boat launch event
@app.post("/boat/launch/")
def create_launch_event(boatID: int, boatModel: str, launchTime: str, db: Session = Depends(get_db)):
    # Convert epoch time to a datetime object
    launch_time_obj = datetime.fromtimestamp(launchTime)
    
    # Create a new boat event instance
    boat_event = BoatDetails(
        boatID=boatID,
        boatModel=boatModel,
        launchTime=launch_time_obj
    )
    
    # Add and commit the event to the database 
    db.add(boat_event)
    db.commit()
    db.refresh(boat_event)
    
    # Return the newly created boat event
    return boat_event

# API endpoint to update boat retrieval event and calculate time at sea
@app.put("/boat/retrieve/{boat_id}")
def update_retrieval_event(boat_id: int, retrievalTime: str, db: Session = Depends(get_db)):
    
    # Get the boat event from the database
    boat_event = db.query(BoatDetails).filter(BoatDetails.boatID == boat_id).first()
    
    if not boat_event:
        raise HTTPException(status_code=404, detail="Boat event not found")
    
    # Convert timestamp to a datetime object
    retrieval_time_obj = datetime.fromtimestamp(retrievalTime)
    
    # Update the retrieval time and calculate time at sea
    boat_event.retrievalTime = retrieval_time_obj
    boat_event.timeAtSea = (retrieval_time_obj - boat_event.launchTime).total_seconds() / 3600.0  # Convert seconds to hours
    
    # Commit the changes to the database
    db.commit()
    
    return boat_event

# API endpoint to get all boat events
@app.get("/boats/")
def read_boats(db: Session = Depends(get_db)):
    # Fetch all boat events from the database
    boats = db.query(BoatDetails).all()
    
    # Return the list of boat events
    return boats

