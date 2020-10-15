import sqlalchemy
from sqlalchemy.ext.automap import automap_base 
from sqlalchemy.orm import Session 
from sqlalchemy import create_engine, func, inspect

from matplotlib import style
import numpy as np
import pandas as pd
import datetime as dt

from flask import Flask, jsonify

#################################################
# Declare Database
#################################################

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

Base = automap_base()

Base.prepare(engine, reflect=True)

Base.classes.keys()

Measurement = Base.classes.measurement
Station = Base.classes.station

session = Session(engine)


#################################################
# Flask Setup
#################################################

app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def ClimateData():
    return(
        f"Welcome to the Climate Data<br>"
        f"Here's the available routes:<br>"
        f"/api/v1.0/precipitation<br>"
        f"/api/v1.0/stations<br>"
        f"/api/v1.0/tobs<br>"
        f"/api/v1.0/start<br>"
        f"/api/v1.0/start/end<br>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():

    # Convert the query results to a dictionary using date as the key and prcp as the value.
    # Return the JSON representation of your dictionary.
    
    session = Session(engine)

    end_date = dt.datetime(2017,8,23)
    begin_date = dt.datetime(2016,8,22)

    precipitation_results = session.query(Measurement.date, Measurement.prcp).\
                                      filter(Measurement.date <= end_date).\
                                      filter(Measurement.date >= begin_date).\
                                      order_by(Measurement.date).all()
    
    precipitation_results_df = pd.DataFrame(precipitation_results)

    precipitation_results_df.sort_index(ascending=True)
    precipitation_results_df.dropna().head()

    precipitation_results_df.set_index('date').dropna().head()

    session.close()

    # Convert the query results to a dictionary using date as the key and prcp as the value.
    rainfall = []
    for date, prcp in precipitation_results:
        rainfall_dict = {}
        rainfall_dict["date"] = date
        rainfall_dict["prcp"] = prcp
        rainfall.append(rainfall_dict)

    return jsonify(rainfall)

@app.route("/api/v1.0/stations")
def stations():

    # Return a JSON list of stations from the dataset.

    session = Session(engine)

    active_station = session.query(Measurement.station, func.count(Measurement.tobs)).group_by(Measurement.station).\
                        order_by(func.count(Measurement.tobs).desc()).all()
    
    session.close()

    station_list = []
    for station,count in active_station:
        station_list_dict = {}
        station_list_dict["station"] = station
        station_list_dict["count"] = count
        station_list.append(station_list_dict)

    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():

    # Query the dates and temperature observations of the most active station for the last year of data.
    # Return a JSON list of temperature observations (TOBS) for the previous year.
    
    session = Session(engine)

    end_date = '2017-08-23'
    begin_date = '2016-08-22'

    temperature = session.query(Measurement.station, Measurement.tobs, Measurement.date).\
                    filter(Measurement.date >= begin_date).\
                    filter(Measurement.date <= end_date).\
                    order_by(Measurement.tobs.desc()).all()
    
    session.close()

    temperature_list = []
    for tobs in temperature:
        temperature_dict = {}
        temperature_dict["tobs"] = temperature
        temperature_list.append(temperature_dict)

    return jsonify(temperature_list)
                    

    # Return a JSON list of the minimum temperature, the average temperature, 
    # and the max temperature for a given start or start-end range.

@app.route("/api/v1.0/start")
def start():

    # When given the start only, calculate TMIN, TAVG, and TMAX 
    # for all dates greater than and equal to the start date.
    session = Session(engine)

    start_date = dt.datetime(2016,8,22)

    start_year = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                 filter(Measurement.date >= start_date).all()

    session.close()

    start = []
    for tobs in start_year:
        start_dict = {}
        start_dict["tobs"] = temperature
        start_dict["date"] = date
        start.append(start_dict)

    return jsonify(start)

@app.route("/api/v1.0/start/end")
def end():

    # When given the start and the end date, calculate the TMIN, TAVG, and TMAX 
    # for dates between the start and end date inclusive.
    session = Session(engine)

    start_date = dt.datetime(2016,8,22)
    end_date = dt.datetime(2017,8,23)

    start_end_year = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()

    session.close()

    end = []
    for tobs in start_end_year:
        end_dict = {}
        end_dict["tobs"] = temperature
        end_dict["date"] = date
        end.append(end_dict)

    return jsonify(end)

if __name__ == "__main__":
    app.run(debug=True)