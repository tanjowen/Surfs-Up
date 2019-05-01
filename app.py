
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
# engine = create_engine("sqlite:///Resources/hawaii.sqlite")
engine = create_engine('sqlite:///Resources/hawaii.sqlite', connect_args={'check_same_thread': False}, echo=True)

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Station = Base.classes.station
Measurement = Base.classes.measurement

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
def welcome():
	"""List all routes that are available"""
	return(
		f"Available Routes:<br/><br/>"
        f"/api/v1.0/precipitation<br/>"
        f"	- List of prior year rain totals from all stations<br/><br/>"
        f"/api/v1.0/stations<br/>"
        f"	- List of stations <br/><br/>"
        f"/api/v1.0/tobs<br/>"
        f"	- List of previous year temperatures from all stations<br/><br/>"
        f"/api/v1.0/start<br/>"
        f"	- When given the start date (YYYY-MM-DD), calculates the MIN/AVG/MAX \
        temperature for all dates greater than and equal to the start date<br/><br/>"
        f"/api/v1.0/start/end<br/>"
        f"	- When given the start and the end date (YYYY-MM-DD), calculate the MIN/AVG/MAX \
        temperature for dates between the start and end date inclusive<br/><br/>"
		)


@app.route("/api/v1.0/precipitation")
def prcp():
	"""Produce a list of rain fall"""
	last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
	last_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
	rain_results = session.query(Measurement.date, Measurement.prcp).\
		filter(Measurement.date > last_year).order_by(Measurement.date).all()

	rainy_season = []
	for date, prcp in rain_results:
		data = {}
		data['date'] = date
		data['prcp'] = prcp
		rainy_season.append(data)

	return jsonify(rainy_season)


@app.route("/api/v1.0/stations")
def stations():
	"""produce a list of station names"""
	stations_names = session.query(Station.name, Station.station).all()
	stations = list(np.ravel(stations_names))

	return jsonify(stations)


@app.route("/api/v1.0/tobs")
def tobs():
	"""produce a list of all temp observations for previous year"""
	last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
	last_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
	temp = session.query(Measurement.date, Measurement.tobs).\
		filter(Measurement.date > last_year).order_by(Measurement.date).all()

	temp_results = []
	for date, tobs in temp:
		data = {}
		data['date'] = date
		data['tobs'] = tobs
		temp_results.append(data)

	return jsonify(temp_results)


@app.route("/api/v1.0/<start>")
def temp_records(start):
	"""provide the min, max, and avg for all dates after a start date"""
	start_date =  dt.datetime.strptime(start, '%Y-%m-%d')
	first_point = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), \
		func.max(Measurement.tobs)).filter(Measurement.date >= start_date).all()

	temperatures_list = list(np.ravel(first_point))

	return jsonify(temperatures_list)


@app.route("/api/v1.0/<start>/<end>")
def temp_record_start_end(start, end):
	"""provide the min, max, and avg for all dates between a start and end date"""
	start_date= dt.datetime.strptime(start, '%Y-%m-%d')
	end_date= dt.datetime.strptime(end,'%Y-%m-%d')
	final_point = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), \
		func.max(Measurement.tobs)).filter(Measurement.date >= start_date).\
		filter(Measurement.date <= end_date).all()

	temperature_list = list(np.ravel(final_point))

	return jsonify(temperature_list)


if __name__ == '__main__':
	app.run(debug=True)