# Import the dependencies.
from flask import Flask, jsonify
import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")


# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)
Base.classes.keys()

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
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
    for station,count in active_station:
        station_list_dict = {}
        station_list_dict["station"] = station
        station_list_dict["count"] = count
        station_list.append(station_list_dict)

    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():

    
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
                    


@app.route("/api/v1.0/start")
def start():

    session = Session(engine)

    start_date = dt.datetime(2016,8,22)

    start_year = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                 filter(Measurement.date >= start_date).all()

    session.close()

    start = []
    for tobs,date in start_year:
        start_dict = {}
        start_dict["tobs"] = tobs
        start_dict["date"] = date
        start.append(start_dict)

    return jsonify(start)

@app.route("/api/v1.0/start/end")
def end():

    session = Session(engine)

    start_date = dt.datetime(2016,8,22)
    end_date = dt.datetime(2017,8,23)

    start_end_year = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()

    session.close()

    end = []
    for tobs,date in start_end_year:
        end_dict = {}
        end_dict["tobs"] = tobs
        end_dict["date"] = date
        end.append(end_dict)

    return jsonify(end)

if __name__ == "__main__":
    app.run(debug=True)
