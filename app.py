from flask import Flask, jsonify

import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

app = Flask(__name__)

# create engine to hawaii.sqlite
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

# Home route
@app.route("/")
def home():
    return(
        f"<center><h1>The Hawaii Climate Analysis API<h/1></center>"
        f"<center><h2>Select a route:</h2></center>"
        f"<center>/api/v1.0/precipitation</center>"
        f"<center>/api/v1.0/stations</center>"
        f"<center>/api/v1.0/tobs</center>"
        f"<center>/api/v1.0/start/end/</center>"
        )

# /api/v1.0/precipitation route
@app.route("/api/v1.0/precipitation")
def prcp():
    #return previous year as json
    # Calculate the date one year from the last date in data set.
    previous_year = dt.date(2017,8,23) - dt.timedelta(days=365)

    # Perform a query to retrieve the data and precipitation scores
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= previous_year).all()
    session.close()
    
    # Dictionary with date as key and precipitation as value
    precipitation = {date: prcp for date, prcp in results}
    # Jsonify
    return jsonify(precipitation)

#/api/v1.0/stations route
@app.route("/api/v1.0/stations")
def stations():
     # Perform a query to retrieve names of station
    results = session.query(Station.station).all()
    session.close()

    station_list = list(np.ravel(results))

    # Jsonify
    return jsonify(station_list)

# /api/v1.0/tobs route
@app.route("/api/v1.0/tobs")
def temperatures():
    #return temperature from previous year
    # Calculate the date one year from the last date in data set.
    previous_year = dt.date(2017,8,23) - dt.timedelta(days=365)

    # Perform a query to retrieve the temp from most active station from past year
    results = session.query(Measurement.tobs).\
            filter(Measurement.station == 'USC00519281').\
            filter(Measurement.date >= previous_year).all()

    session.close()
    
    temp_list = list(np.ravel(results))

    #jsonify
    return jsonify(temp_list)

# /api/v1.0/<start> and /api/v1.0/<start>/<end>
@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def date_stat(start=None, end=None):
    # Select statement
    select = [func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)]

    if not end:
        start_date = dt.datetime.strptime(start, "%m%d%Y")

        results = session.query(*select).filter(Measurement.date >= start_date).all()

        session.close()

        temp_list = list(np.ravel(results))

        #jsonify
        return jsonify(temp_list)

    else:
        start_date = dt.datetime.strptime(start, "%m%d%Y")
        end_date = dt.datetime.strptime(end, "%m%d%Y")

        results = session.query(*select)\
            .filter(Measurement.date >= start_date)\
            .filter(Measurement.date <= end_date).all()

        session.close()

        temp_list = list(np.ravel(results))

        #jsonify
        return jsonify(temp_list)

## launch the app
if __name__ == '__main__':
    app.run(debug=True)
    