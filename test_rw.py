'''
Run a set of simulations, calculate squared
displacement, and mean squared displacements

Edmund Tang 2021-04-13
'''

import rw2d
import mysql.connector
from mysql.connector import errorcode
from timer import timer

overall_timer = timer()
overall_timer.start()

#Connect to server & select database
cnx = mysql.connector.connect(
        host='localhost',
	user='root',
	password='password',
        database = "2D_walk"
	)
cursor = cnx.cursor()

###experiment parameters
##steps = 512
##dt = 0.1
##
##simNums = []
##t = timer()
##
###perform experiments
##for _ in range(10):
##    t.start()
##    simNum = rw2d.RW_sim(steps,dt,cnx)
##    t.stop()
##
##    #calculate squared displacement
##    t.start()
##    simNum = rw2d.calc_SD(simNum,cnx)
##    t.stop()
##
##    simNums.append(simNum)
##    
###calculate MSD
##t.start()
##set_id = rw2d.calc_MSD(simNums,cnx)
##t.stop()


#calculate MSD for particular cases

###testing combination of different data set sizes
##simNums = [10, 13]
##set_id = rw2d.calc_MSD(simNums,cnx)

#testing filtering by experiment parameter
simLen = 512
cursor.execute("SELECT `simNum` FROM `experiments` WHERE simLen = {}".format(simLen))
result = cursor.fetchall()
simNums = [item[0] for item in result]
set_id = rw2d.calc_MSD(simNums, cnx)











cnx.close()
overall_timer.stop()


