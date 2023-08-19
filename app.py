# Import the dependencies.
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
from flask import Flask, jsonify

#################################################
# Database Setup
#################################################

# Create engine to database
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station

# Create our session (link) from Python to the database
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

# Welcome route with available routes information
@app.route("/")
def welcome():
    return (
        '''
        Welcome to the Hawaii climate for surfing API!<br>
        Your available routes are:<br>
        /api/v1.0/precipitation<br>
        /api/v1.0/stations<br>
        /api/v1.0/tobs<br>
        /api/v1.0/temp/start<br>
        /api/v1.0/temp/start/end<br>
        '''
    )

#####################
# Precipitation Route
#####################

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Calculate earliest date in range
    date_one_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # query rainfall for a one-year period using the earliest datapoint calculated above
    rain_one_year = session.query(measurement.date, measurement.prcp).filter(measurement.date >= date_one_year).all()

    # Create dictionary using jsonify
    rain_and_date = {date: prcp for date, prcp in rain_one_year}

    session.close()  # Close the session

    return jsonify(rain_and_date)

################
# Stations Route
################

@app.route("/api/v1.0/stations")
def stations():
    # Query stations from stations dataset
    outputs = session.query(station.station).all()

    # Use np.ravel function to convert tuples to a regular flattened one-dimensional list
    stations = list(np.ravel(outputs))

    session.close()  # Close the session

    return jsonify(stations=stations)

###################
# Temperature Route
###################

@app.route("/api/v1.0/tobs")
def temperatures():
    # Define earliest point of date range
    date_one_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Filter temeperature by both station and date
    outputs = session.query(measurement.tobs).filter(measurement.station == 'USC00519281', measurement.date >= date_one_year).all()

    # Use np.ravel function to convert tuples to a regular flattened one-dimensional list
    most_active_temps = list(np.ravel(outputs))

    session.close()  # Close the session

    return jsonify(most_active_temps=most_active_temps)

###############################
# Temperature for Start and End
###############################

# Create routes where you either input a specific start date or start and end date 
# Input date as YYYY-MM-DD
@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")

def temperature_final(start=None, end=None):
    # Use a select statement which will query min, max and avg temp
    select = [func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)]

    # Use an if-not statement to get 1 of 2 options: 1) a date range with a specific start date which will calculate a date range from the start-date to the latest date in the dataset
    # 2) get a specific date range after inputting a start and end-date
    if not end:
        outputs = session.query(*select).filter(measurement.date >= start).all()
    else:
        outputs = session.query(*select).filter(measurement.date >= start, measurement.date <= end).all()

    # Use np.ravel function to convert tuples to a regular flattened one-dimensional list 
    temp_final = list(np.ravel(outputs))

    session.close()  # Close the session

    return jsonify(temp_final=temp_final)

if __name__ == "__main__":
    app.run(debug=True)