'''
Plot the results of 2D random walk simulations

Edmund Tang 2021-04-13
'''

import rw2d
from matplotlib import pyplot
import mysql.connector
from mysql.connector import errorcode
from timer import timer

#Connect to server 
cnx = mysql.connector.connect(
        host='localhost',
	user='root',
	password='phylumSnack1738#'
	)
cursor = cnx.cursor()

#Select database
DB_name = "2D_walk"
cursor.execute("USE {}".format(DB_name))

#Plot trajectory
simNums = range(1,11)
fig = rw2d.plot_traj(simNums, cnx)
fig.show()

#Plot MSD
plot_axes = [0, 10, 0, 80]
fig = rw2d.plot_MSD(1,cnx,plot_axes)
fig.show()
