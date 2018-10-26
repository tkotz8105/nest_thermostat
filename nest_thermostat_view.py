#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  nest_thermostat_db_py
#  Creates the database, table, and view for the Nest Thermostat database
#  The program nest_thermostat.py program queries the Nest server via API and writes data record to SQLite Database
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

import sqlite3
import os.path

def createDB(file_path):

	if os.path.exists(file_path):
		print ('Database Exists at ',file_path)
	else:
		fileDirectory = os.path.dirname(file_path)
		if not os.path.exists(fileDirectory):
			try:
				os.makedirs(fileDirectory)
			except OSError:
				print ('No permission to create ', fileDirectory)
		timeout = 5
		# Open, then immediately close the database.
		conn = sqlite3.connect(file_path, timeout=timeout)
		print (file_path,' database created')
		conn.close()
	return

def createTable(file_path):

	conn = sqlite3.connect(file_path)
	cur = conn.cursor()
	cur.execute('CREATE TABLE thermostat ('+ \
			'datetime INT, last_connect INT, online TEXT, device_serial TEXT, device_name TEXT,	device_where TEXT, label TEXT,'+ \
			'mode TEXT, ambient_temperature INT, temperature_scale TEXT, humidity INT, device_min_temperature INT, device_max_temperature INT,'+ \
			'hvac_state TEXT, hvac_fan TEXT, hvac_emergency_heat TEXT, target_temperature INT, eco_temperature_high INT, eco_temperature_low INT,'+ \
			'device_is_locked TEXT, locked_temperature_low INT, locked_temperature_high INT, has_leaf TEXT,'+ \
			'device_can_heat TEXT, device_can_cool TEXT, device_has_humidifier TEXT, device_has_dehumidifier TEXT,'+ \
			'device_has_fan TEXT, device_has_hot_water_control TEXT, device_postal_code TEXT)')
	print ('Table thermostat created in', file_path, ' database')
	conn.close()
	return

def createView(file_path):

	conn = sqlite3.connect(file_path)
	cur = conn.cursor()
	cur.execute('CREATE VIEW V_Thermostat AS SELECT datetime(datetime,'+\
				"'"+'unixepoch'+"'"+'),DATETIME(last_connect,'+"'"+'unixepoch'+"'"+'),'+ \
				'ambient_temperature,humidity,hvac_state,hvac_fan,target_temperature,'+ \
				'target_lo_temperature, target_hi_temperature FROM thermostat')
	print ('View V_thermostat created in', file_path, ' database')
	conn.close()
	return

def addColumn(file_path):

	conn = sqlite3.connect(file_path)
	cur = conn.cursor()
	cur.execute('ALTER TABLE thermostat ADD COLUMN target_lo_temperature INT')
	cur.execute('ALTER TABLE thermostat ADD COLUMN target_hi_temperature INT')
	print ('Column(s) added in', file_path, ' database')
	conn.close()
	return
	
def getSchema(file_path):
	conn = sqlite3.connect(file_path)
	cur = conn.cursor()
	masterQuery = "select * from sqlite_master"
	cur.execute(masterQuery)
	tableList = cur.fetchall()
	for table in tableList:
		print("Database Object Type: %s"%(table[0]))
		print("Database Object Name: %s"%(table[1]))
		print("Table Name: %s"%(table[2]))
		print("Root page: %s"%(table[3]))
		print("**SQL Statement**: %s"%(table[4]))
	return

def dropView(file_path):
	conn = sqlite3.connect(file_path)
	cur = conn.cursor()
	cur.execute('DROP VIEW V_Thermostat')
	print ('View Dropped in', file_path, ' database')
	conn.close()
	return

def main():
	file_path=os.path.expanduser('~')+'/nest/nestlog.sdb'
	# createDB(file_path)
	# createTable(file_path)
	dropView(file_path)	
	createView(file_path)
	#addColumn(file_path)
	getSchema(file_path)
	return 0

if __name__ == '__main__':
	main()

