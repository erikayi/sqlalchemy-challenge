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
        f"/api/v1.0/<start><br>"
        f"/api/v1.0/<start>/<end><br>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    
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

    session = Session(engine)

    active_station = session.query(Measurement.station, func.count(Measurement.tobs)).group_by(Measurement.station).\
                        order_by(func.count(Measurement.tobs).desc()).all()
    
    session.close()

    station_list = []
    for station in active_station:
        station_list_dict = {}
        station_list_dict["station"] = station
        station_list.append(station_list_dict)

    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():

    session = Session(engine)

    active_station = session.query(Measurement.station, func.count(Measurement.tobs)).group_by(Measurement.station).\
                        order_by(func.count(Measurement.tobs).desc()).all()

    most_active_station = active_station[0][0]

    # end_date = dt.datetime(2017,8,23)
    # begin_date = dt.datetime(2016,8,22)

    last_year = dt.date.datetime(2017,8,23) - dt.timedelta(days=365)

    temperature = session.query(Measurement.station, Measurement.tobs, Measurement.date).\
                filter(Measurement.station == most_active_station).\
                filter(Measurement.date == last_year).\
                order_by(Measurement.date).all()
    
    session.close()

   # Query the dates and temperature observations of the most active station for the last year of data.
    temp_observ = []
    for station, tobs in temperature:
        temp_observ_dict = {}
        temp_observ_dict["station"] = station
        temp_observ_dict["tobs"] = tobs
        temp_observ.append(temp_observ_dict)

    return jsonify(temp_observ)

@app.route("/api/v1.0/<start>")
def start():
    return jsonify(start)

@app.route("/api/v1.0/<start>/<end>")
def end():
    return jsonify(end)




if __name__ == "__main__":
    app.run(debug=True)