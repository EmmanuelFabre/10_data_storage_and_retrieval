#import Flask
from flask import Flask, jsonify
#import dependencies
# Python SQL toolkit and Object Relational Mapper
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, inspect, func
import numpy as np
import pandas as pd
import datetime as dt

engine = create_engine("sqlite:///hawaii.sqlite", connect_args={'check_same_thread': False})
#SQLite by default prohibits use of single connection in more than one thread. 
#Hence, add 'connect_args={'check_same_thread':False} paramter to your engine

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables (into classes)
Base.prepare(engine, reflect=True)
# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station
# Create our session (link) from Python to the DB
session = Session(engine)

# Calculate the date 1 year ago from the last data point in the database
#what is latest date available?
session.query(Measurement.date).order_by(Measurement.date.desc()).first()
# 2017-08-23

#date one year ago from lasted date available in data
year_ago = dt.datetime(2017, 8, 23) - dt.timedelta(days=365)
#print(year_ago)
# 2016-08-23

#combine both queries--last 12 months of measurement dates and precipitation
last_12_date_prcp = (session
	.query(Measurement.date, Measurement.prcp)
	.filter(Measurement.date >= year_ago)
	.order_by(Measurement.date).all())

# What are the most active stations? (i.e. what stations have the most rows)?
active_stations = (session
	.query(func.count(Measurement.station), Measurement.station)
	.group_by(Measurement.station)
	.order_by(func.count(Measurement.station).desc()))




# Using the station id from the previous query, calculate the lowest temperature recorded, 
# highest temperature recorded, and average temperature most active station?
lo_hi_avg = (session
				.query(func.min(Measurement.tobs),  func.max(Measurement.tobs), func.avg(Measurement.tobs), Measurement.station)
				.group_by(Measurement.station)
			   )


# A date string in the format %Y-%m-%d
start_date= "2017-03-21"
end_date= "2017-03-31"



#############FLASK CODE BELOW####################
#Create an app; remember to pass __name__
#__name__ represents the name of the python file.
app = Flask(__name__)

#Create the 'route' in the web server.
#define a function for to execute when people access this route.
@app.route("/")
def home():
	return(
		
		f"Welcome to the Climate Analysis API.<br/>"
		f"Available Routes:<br/>"
		f"/api/v1.0/precipitation<br/>"
		f"/api/v1.0/stations<br/>"
		f"/api/v1.0/tobs<br/>"
		f"/api/v1.0/03-21-17<br/>"
		f"/api/v1.0/03-21-17/03-31-17<br/>"
	)

@app.route("/api/v1.0/precipitation")
def precip():
	#Convert the query results to a Dictionary using date as the key and..
	#..prcp as the value.
	#Return the JSON representation of your dictionary.

#test convert query result from tuple to list
	#convert = list(np.ravel(last_12_date_prcp))

	lst = []
	for x in last_12_date_prcp:

		precip_dict = {}
		precip_dict["date"] = x.date
		precip_dict["prcp"] = x.prcp
		lst.append(precip_dict)
	return jsonify(lst)

#check out flask with orm in 10.3!!!!!!!!!!!
#check the 'variable_rule'  or 'justice_league' 'app.py file from 10.3
	#value of jsonify - type 'flask run' in terminal. Go to /jsonified..
	#..route and it returns a dictionary

@app.route("/api/v1.0/stations")
def stations():
	#Return a JSON list of stations from the dataset.

	lst_stat = []
	for y in active_stations:
		stat_dict={}
		stat_dict["station"] = y.station
		lst_stat.append(stat_dict)
	return jsonify(lst_stat)


@app.route("/api/v1.0/tobs")
def temps():
	#query for the dates and temperature observations from a year from..
	#..the last data point.
	
	last_12_date_tobs = (session
		.query(Measurement.date, Measurement.tobs)
		.filter(Measurement.date >= year_ago)
		.order_by(Measurement.date).all())
	
	#Return a JSON list of Temperature Observations (tobs) for..
	#..the previous year.
	lst_tobs = []
	for y in last_12_date_tobs:
		tobs_dict={}
		tobs_dict["tobs"] = y.tobs
		tobs_dict["date"] = y.date
		lst_tobs.append(tobs_dict)
	return jsonify(lst_tobs)

@app.route("/api/v1.0/03-21-17")
def start():
	beyond_date= (session
		.query(Measurement.date, func.min(Measurement.tobs).label("min_tobs"), func.avg(Measurement.tobs).label("avg_tobs"), func.max(Measurement.tobs).label("max_tobs"))
		.filter(Measurement.date >= start_date).all())
	lst_beyond = []
	for z in beyond_date:
		beyond_dict = {}
		beyond_dict["date"] = z.date
		beyond_dict["Min Temp"] = z.min_tobs
		beyond_dict["Avg Temp"] = z.avg_tobs
		beyond_dict["Max Temp"] = z.max_tobs
		lst_beyond.append(beyond_dict)
	return jsonify(lst_beyond)

@app.route("/api/v1.0/03-21-17/03-31-17")
def start_end():
	trip_dates= (session
		.query(func.min(Measurement.tobs).label("min_tobs"), func.avg(Measurement.tobs).label("avg_tobs"), func.max(Measurement.tobs).label("max_tobs"))
		.filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all())
	lst_dates = []
	for z in trip_dates:
		dates_dict = {}
		#dates_dict["date"] = z.date
		dates_dict["Min Temp"] = z.min_tobs
		dates_dict["Avg Temp"] = z.avg_tobs
		dates_dict["Max Temp"] = z.max_tobs
		lst_dates.append(dates_dict)
	return jsonify(lst_dates)






