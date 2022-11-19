import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station
#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################
# create home page route
@app.route("/")
def main():
    return (
        f"Hello! Welcome to the Home Page!<br>"
        f"List all available api routes.<br>"
        f"Precipitation for the previous year: /api/v1.0/precipitation<br>"
        f"List of stations from the dataset: /api/v1.0/stations<br>"
        f"List of temperature observations (TOBS) for the previous year: /api/v1.0/tobs<br>"
        f"Input start date (yyyy-mm-dd) to get the list of the min temperature, the avg temperature, and the max temperature for a given start date: /api/v1.0/<start><br>"
        f"Input start date (yyyy-mm-dd) and end date (yyyy-mm-dd) to get the list of the min temperature, the avg temperature, and the max temperature for a given start-end range: /api/v1.0/<start>/<end><br>"
    )


# create precipitation route of last 12 months of precipitation data
@app.route("/api/v1.0/precipitation")
def prcp():
    session = Session(engine)   
    start_date = '2016-08-23'
    sel = [Measurement.date, 
        func.sum(Measurement.prcp)]
    prcp = session.query(*sel).\
            filter(Measurement.date >= start_date).\
            group_by(Measurement.date).\
            order_by(Measurement.date).all()
   
    session.close()

    # convert results to a dictionary with date as key and prcp as value
    prcp_dict = dict(prcp)

    # return the json representation of your dictionary
    return jsonify(prcp_dict)


# create station route of a list of the stations from the dataset
@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine) 
    stations = session.query(Station.name, Station.station).all()
    session.close()
    # list all stations
    all_stations = list(np.ravel(stations))

    # return json list of stations
    return jsonify(all_stations)


# create tobs route of temp observations for most active station over last 12 months
@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    # Query the temperature observation data for the most active station for the previous year
    sel = [Measurement.date, 
        Measurement.tobs]
    tobs_station = session.query(*sel).\
            filter(Measurement.date >= '2016-08-23', Measurement.station == 'USC00519281').\
            group_by(Measurement.date).\
            order_by(Measurement.date).all()

    session.close()


    dates = []
    temps = []

    for date, temp in tobs_station:
        dates.append(date)
        temps.append(temp)
    
    station_tobs_dict = dict(zip(dates, temps))

    return jsonify(station_tobs_dict)


# create start and start/end route
@app.route("/api/v1.0/<start_date>")
def summart_start(start_date, end_date='2017-08-23'):

    session = Session(engine)
    query_result = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
    session.close()

    stats = []
    for min, avg, max in query_result:
        dict = {}
        dict["Min"] = min
        dict["Average"] = avg
        dict["Max"] = max
        stats.append(dict)

    # If the query returned non-null values return the results,
    # otherwise return an error message
    if dict['Min']: 
        return jsonify(stats)
    else:
        return jsonify({"error": f"Date not found or not formatted as YYYY-MM-DD."}), 404

@app.route("/api/v1.0/<start_date>/<end_date>")
def summary_range(start_date, end_date='2017-08-23'):

    session = Session(engine)
    query_result = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()
    session.close()

    stats = []
    for min, avg, max in query_result:
        dict = {}
        dict["Min"] = min
        dict["Average"] = avg
        dict["Max"] = max
        stats.append(dict)

    # If the query returned non-null values return the results,
    # otherwise return an error message
    if dict['Min']: 
        return jsonify(dict)
    else:
        return jsonify({"error": f"Date(s) not found, invalid date range or dates not formatted correctly."}), 404



if __name__ == "__main__":
    app.run(debug=True)