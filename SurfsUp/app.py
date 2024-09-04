# Import the dependencies.
import numpy as np 
import sqlalchemy
import datetime as dt
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, desc
from pathlib import Path
from collections import OrderedDict

from flask import Flask, jsonify, render_template
 

#################################################
# Database Setup
#################################################
database_path = Path("C:/Users/Shari/Desktop/Data Science Course/Challenges/sqlalchemy-challenge/Resources/hawaii.sqlite")
engine = create_engine(f"sqlite:///{database_path}")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
station = Base.classes.station
measurement = Base.classes.measurement

# Create our session (link) from Python to the DB
# NOTE: I have opted to create a seperate session for each route.

#################################################
# Flask Setup
#################################################

app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/") # Create landing page for API
def welcome():
    """List all available api routes."""
    return render_template('index.html')
        
    
@app.route("/api/v1.0/precipitation")  # Convert the query results from your precipitation analysis (i.e. retrieve only the last 12 months of data) to a dictionary using date as the key and prcp as the value.
def precipitation():  
    # Create route session
    session = Session(engine)    
    # Filter only last 12 months of data.
    date_filter = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    # Query for the precipitation scores
    results = (session.query(measurement.date,measurement.prcp)
               .filter(measurement.date >= date_filter).all())   
    # Close session
    session.close()

    # Returns json with the date as the key and the value as the precipitation.
    all_precip = {}
    for date,prcp in results:
        all_precip[date] = prcp
    return jsonify(all_precip)

@app.route("/api/v1.0/stations") # Return a JSON list of stations from the dataset.
def stations():
    # Create route session
    session = Session(engine)
    # Query all stations
    results = session.query(station.station).all()
    # Close route session
    session.close()
    
    # Convert list of tuples into normal list
    all_stations = list(np.ravel(results))
    
    return jsonify(all_stations)

@app.route("/api/v1.0/tobs") # Query the dates and temperature observations of the most-active station for the previous year of data.
def tobs():    
    # Create route session
    session = Session(engine)
    # Filter only last 12 months of data.
    date_filter = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    # Query the dates and temperature observations of the most-active station for the previous year of data
    results = (session.query(measurement.date, measurement.tobs)
                        .filter(measurement.station == 'USC00519281')
                        .filter(measurement.date >= date_filter).all())
    # Close route session
    session.close()  
    # Return a JSON list of temperature observations for the previous year.
    station_activity = list(np.ravel(results))

    return jsonify(station_activity)

@app.route("/api/v1.0/<start>") # For a specified start, calculate TMIN, TAVG, and TMAX 
def start(start):
    # Input validation for start date
    try:
        start_date = dt.datetime.strptime(start, "%Y-%m-%d")
    except ValueError:
        return jsonify({"error": "Invalid date format. Please use YYYY-MM-DD."}), 400
        
    # Create route session
    session = Session(engine)
    # For a specified start, calculate TMIN, TAVG, and TMAX for all the dates greater than or equal to the start date
    results = (session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs))
               .filter(measurement.date >= start_date).all())
    # Close route session
    session.close()
    
    # Covert results into a dictionary for JSON response
    stats_dict = OrderedDict()
    stats_dict["start_date"] = start_date
    stats_dict["min"] = results[0][0]
    stats_dict["avg"] = results[0][1]
    stats_dict["max"] = results[0][2]
    
    # Return JSON response
    return jsonify(stats_dict)

@app.route("/api/v1.0/<start>/<end>") # For a specified start and end date, calculate TMIN, TAVG, and TMAX 
def start_end(start, end):
    # Input validation for start and end date
    try:
        start_date = dt.datetime.strptime(start, "%Y-%m-%d")
        end_date = dt.datetime.strptime(end, "%Y-%m-%d")
    except ValueError:
        return jsonify({"error": "Invalid date format. Please use YYYY-MM-DD."}), 400
    
    # Create route session
    session = Session(engine)
    # For a specified start and end date, calculate TMIN, TAVG, and TMAX for the dates from the start date to the end date
    results = (session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs))
               .filter(measurement.date >= start_date)
               .filter(measurement.date <= end_date).all())
    # Close route session
    session.close()
    
    # Covert results into a dictionary for JSON response
    stats_dict = OrderedDict()
    stats_dict["start_date"] = start_date
    stats_dict["end_date"] = end_date
    stats_dict["min"] = results[0][0]
    stats_dict["avg"] = results[0][1]
    stats_dict["max"] = results[0][2]
    
    # Return JSON response
    return jsonify(stats_dict)

if __name__ == '__main__':
    app.run(debug=True)
    

    