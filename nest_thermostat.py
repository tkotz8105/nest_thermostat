#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  nest_thermostat.py
#  Queries the Nest server via API and writes data record to SQLite Database
#
#  Copyright 2017 Tom Kotz
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
#
import os.path		#required for determining SQLite database location
import sqlite3		#database manager
import nest			#required for API to Nest devices
import datetime as dt	#required for converting Nest formatted time to usual format
from tzlocal import get_localzone	# Required to convert UTC to localtime
import time			#used for time conversion
import json
#
#
# Function to get client info for nestlog.json file for access to Nest API
def get_client_info(nestlog_json_file):
	with open(nestlog_json_file) as data_file:
		data=json.load(data_file)
		#pprint(data)
		client_info = data['nest_client_info'][0]
	data_file.close
	return client_info
#
# Function to convert UTC to local time
def cvt_to_local(my_time):
    if time.daylight:
        offsetSeconds = -(time.altzone)
    else:
        offsetSeconds = -(time.timezone)
    return my_time+offsetSeconds
#
# Function to convert Nest formatted datetime to system usable time
def convert_my_iso_8601(iso_8601, tz_info):
	assert iso_8601[-1] == 'Z'
	iso_8601 = iso_8601[:-1] + '000'
	iso_8601_dt = dt.datetime.strptime(iso_8601, '%Y-%m-%dT%H:%M:%S.%f')
	return iso_8601_dt
#
def main():
#

	sql_single = 'INSERT INTO thermostat(datetime, last_connect, online, device_serial,'+ \
	'device_name, device_where, label, mode, ambient_temperature, temperature_scale,'+ \
	'humidity, device_min_temperature, device_max_temperature, hvac_state, hvac_fan,' + \
	'hvac_emergency_heat, target_temperature, eco_temperature_high, eco_temperature_low,'+ \
	'device_is_locked, locked_temperature_low, locked_temperature_high, has_leaf,'+ \
	'device_can_heat, device_can_cool, device_has_humidifier, device_has_dehumidifier,'+ \
	'device_has_fan, device_has_hot_water_control, device_postal_code)'+ \
	' VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'
	sql_dual = 'INSERT INTO thermostat(datetime, last_connect, online, device_serial,'+ \
	'device_name, device_where, label, mode, ambient_temperature, temperature_scale,'+ \
	'humidity, device_min_temperature, device_max_temperature, hvac_state, hvac_fan,' + \
	'hvac_emergency_heat, target_temperature, target_lo_temperature, target_hi_temperature, eco_temperature_high,'+ \
	'eco_temperature_low, device_is_locked, locked_temperature_low, locked_temperature_high,'+ \
	'has_leaf, device_can_heat, device_can_cool, device_has_humidifier, device_has_dehumidifier,'+ \
	'device_has_fan, device_has_hot_water_control, device_postal_code)'+ \
	' VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'
# Get required client info for access to Nest API
	access_token_cache_file = os.path.expanduser('~')+'/nest/nest.json'
	nestlog_json_file = os.path.expanduser('~')+'/nest/nestlog.json'
	client_info=get_client_info(nestlog_json_file)
	client_id = client_info.get('client_id')
	client_secret = client_info.get('client_secret')
#
# Set file path for access to SQLite database file
	file_path=os.path.expanduser('~')+'/nest/nestlog.sdb'
#
# Access Nest API
	napi = nest.Nest(client_id=client_id, client_secret=client_secret, access_token_cache_file=access_token_cache_file)

	if napi.authorization_required:   # only required first time to get pin and create access_token_cache_file
		print('Go to ' + napi.authorize_url + ' to authorize and enter pin in JSON file')
		pin = raw_input("PIN: ")
		napi.request_token(pin)
#
	# Access advanced structure properties:
	for structure in napi.structures:
#
		# Access advanced device properties & create SQL to store Nest Thermostat Elements in SQLite DB
		for device in structure.thermostats:
			last_connect=convert_my_iso_8601(device.last_connection, get_localzone())	#convert Nest last_connection to local time
#
# Get current system time and use as time stamp for database record... convert to Epoch Time
			time_now=dt.datetime.utcnow()
			sys_time=cvt_to_local(int((dt.datetime.utcnow() - dt.datetime(1970,1,1)).total_seconds()))
#
# Convert last_connect time to Epoch time
			last_connect=cvt_to_local(int((last_connect - dt.datetime(1970,1,1)).total_seconds()))
			
#
# Open database and execute SQL statement to write Nest Thermostat data
			conn=sqlite3.connect(file_path)
			cur=conn.cursor()
			# print (sys_time, last_connect, device.online, device._serial, device.name, device.where, device.label,
				# device.mode, device.temperature, device.temperature_scale, device.humidity, device.min_temperature, device.max_temperature,
				# device.hvac_state, device.fan, device.is_using_emergency_heat, device.target, device.eco_temperature.high, device.eco_temperature.low,
				# device.is_locked, device.locked_temperature.low, device.locked_temperature.high, device.has_leaf,
				# device.can_heat, device.can_cool, device.has_humidifier, device.has_dehumidifier,
				# device.has_fan, device.has_hot_water_control, device.postal_code)

			if (device.mode == 'heat-cool'):
				target_lo=device.target[0]
				target_hi=device.target[1]
#				print (target_lo, target_hi, device.hvac_state)
				if (device.hvac_state=='heating'):
					target_temp=device.target[0]
				elif (device.hvac_state == 'cooling'):
					target_temp=device.target[1]
				elif (device.hvac_state == 'off'):
					target_split=(device.target[0]+device.target[1])/2
					if(device.temperature-10 <= target_split):
						target_temp=device.target[0]
					else:
						target_temp=device.target[1]
				sql=sql_dual
#				print (target_lo, target_hi)	
				cur.execute(sql,(sys_time, last_connect, device.online, device._serial, device.name, device.where, device.label,
					device.mode, device.temperature, device.temperature_scale, device.humidity, device.min_temperature, device.max_temperature,
					device.hvac_state, device.fan, device.is_using_emergency_heat, target_temp, target_lo, 
					target_hi, device.eco_temperature.high, device.eco_temperature.low,
					device.is_locked, device.locked_temperature.low, device.locked_temperature.high, 
					device.has_leaf, device.can_heat, device.can_cool, device.has_humidifier, 
					device.has_dehumidifier, device.has_fan, device.has_hot_water_control, device.postal_code))
			else :
				sql=sql_single
				cur.execute(sql,(sys_time, last_connect, device.online, device._serial, device.name, device.where, device.label,
					device.mode, device.temperature, device.temperature_scale, device.humidity, device.min_temperature, device.max_temperature,
					device.hvac_state, device.fan, device.is_using_emergency_heat, device.target, 
					device.eco_temperature.high, device.eco_temperature.low,
					device.is_locked, device.locked_temperature.low, device.locked_temperature.high,
					device.has_leaf, device.can_heat, device.can_cool, device.has_humidifier,
					device.has_dehumidifier, device.has_fan, device.has_hot_water_control, device.postal_code))
			conn.commit()	#Commit new record
			conn.close()	#Close Database
	return 0

if __name__ == '__main__':
	main()

