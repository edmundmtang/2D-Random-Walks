'''2-Dimensional Random Walk

A set of functions to simulate random walks in two dimensions

Changelog
2021/01/17 - base version
2021/04/11 - mySQL incorporation

Edmund Tang 2021/04/11
'''

import numpy
from numpy import random
from matplotlib import pyplot
import os
import mysql.connector
from timer import timer
from mysql.connector import errorcode

def RW_sim(steps, dt, cnx):
        '''function that generates a list of
        x-positions and a list of y-positions
        and commits them to a database.
        Returns simulation ID number.'''

        cursor = cnx.cursor()
        #create experiment entry in database
        ins_stmt = "INSERT INTO `experiments` (`simLen`, `stepSize`) VALUES (%s, %s)"
        ins_data = (steps, dt)
        cursor.execute(ins_stmt, ins_data)
        #determine new simulation ID
        newSimNum = cursor.lastrowid
        print("\nSimulation ID: {}".format(newSimNum))
        print("Simulation Length: {}\nTime Step Size: {}".format(steps,dt))
        print("Running simulation...")
        
        RW_iter = RW_step(dt) #create iterator
        iter(RW_iter)
        #create initial trajectory entry in database for this experiment
        ins_stmt = """INSERT INTO `trajectories` (`simNum`, `stepNum`, `xpos`, `ypos`)
                      VALUES (%s, %s, %s, %s)"""
        step = 0
        ins_data = (newSimNum, step, RW_iter.pos[0], RW_iter.pos[1])
        cursor.execute(ins_stmt, ins_data)
        for _ in range(steps):
                next(RW_iter)
                step += 1
                ins_data = (newSimNum, step, RW_iter.pos[0], RW_iter.pos[1])
                cursor.execute(ins_stmt,ins_data)
        cnx.commit()
        print("Simulation complete!")        
        return newSimNum

class RW_step:
	'''iterator that yields positions in a random walk
	assuming a non-dimensionalized diffusivity of 4/3'''

	def __init__(self,dt):
		self.dt = dt

	def __iter__(self):
		self.pos = [0, 0] #initial position is [0, 0]
		return self

	def __next__(self): #apply change in position
		dt = self.dt
		dx = (8*dt/3)**(1/2)*random.normal()
		dy = (8*dt/3)**(1/2)*random.normal()
		self.pos[0] += dx
		self.pos[1] += dy

def calc_SD(simNum, cnx):
        '''function that uses trajectory data from
        a database to calculate the squared
        displacement of a particle'''

        cursor = cnx.cursor()
        #check that simulation exists
        cursor.execute("SELECT COUNT(*) FROM `experiments` WHERE simNum = {}".format(simNum))
        simExist = cursor.fetchone()[0]
        if simExist == 0:
                print("\nSimulation (simNum = {}) does not exist.".format(simNum))
                print("Halting calculation of squared displacements.")
                return
        #check that calculation was not already performed
        cursor.execute("SELECT COUNT(*) FROM `sq_displacements` WHERE simNum = {}".format(simNum))
        sqDispCount = cursor.fetchone()[0]
        if sqDispCount != 0:
                print("\nSquared displacements have previously been calculated for simNum = {}.".format(simNum))
        else:
                print("\nCalculating squared displacements for simNum = {}...".format(simNum))
                cursor.execute("SELECT COUNT(*) FROM `trajectories` WHERE simNum = {}".format(simNum))
                result = cursor.fetchone()
                simLen = result[0]

                # first squared displacement is zero by definition, we skip calculating this
                ins_stmt = ("""INSERT INTO `sq_displacements` (`simNum`, `stepSize`, `sd`)
                               VALUES (%s, %s, %s)""")
                ins_data = (simNum, 0, 0)
                cursor.execute(ins_stmt, ins_data)

                for i in range(1,simLen):
                        for j in range(simLen-i):
                                #first position
                                step1 = j
                                cursor.execute("SELECT `xpos`, `ypos` FROM `trajectories` WHERE `simNum` = {} AND `stepNum` = {}".format(simNum,step1))
                                pos1 = cursor.fetchone()
                                #second position
                                step2 = j+i
                                cursor.execute("SELECT `xpos`, `ypos` FROM `trajectories` WHERE `simNum` = {} AND `stepNum` = {}".format(simNum,step2))
                                pos2 = cursor.fetchone()
                                #calculate displacement
                                dx = pos2[0] - pos1[0]
                                dy = pos2[1] - pos1[1]
                                #calculate squared displacement
                                sd = dx**2 + dy**2
                                #insert results to db
                                ins_data = (simNum, i, sd)
                                cursor.execute(ins_stmt, ins_data)
                print("Square displacements calculations complete!")
        cnx.commit()
        return simNum

def calc_MSD(simNums, cnx):
        '''function that takes a list of simulation IDs
        and computes MSD based on those simulations.
        Computes mean and standard deviation for each time
        step, but cannot recognize differing time step
        sizes nor experimental parameters.'''

        cursor = cnx.cursor()
        #create new msd set entry
        cursor.execute("INSERT INTO `msdSetMeta` (`setdatetime`, `simCount`) VALUES (NOW(), {})".format(len(simNums)))
        setNum = cursor.lastrowid
        cnx.commit()
        print("\nSet ID reserved for setNum = {}".format(setNum))
        print("Calculating MSD...")
        #determine maximum dataset length
        maxLen = 0
        for simNum in simNums:
                #create entry recording aggregation contribution
                cursor.execute("SELECT COUNT(*) FROM `experiments` WHERE simNum = {}".format(simNum))
                if cursor.fetchone()[0] == 0:
                        print("A selected experiment does not exist (simNum = {})".format(simNum))
                        print("Halting calculation of MSD.")
                        #delete partially complete entries
                        cursor.execute("DELETE FROM `msdsets` WHERE setNum = {}".format(setNum))
                        cursor.execute("DELETE FROM `msdSetMeta` WHERE setNum = {}".format(setNum))
                        return
                #print("Adding simNum = {} to set (setNum = {})".format(simNum, setNum))
                ins_stmt = "INSERT INTO `msdSets` (`setNum`, `simNum`) VALUES (%s, %s)"
                ins_data = (setNum, simNum)
                cursor.execute(ins_stmt,ins_data)
                cnx.commit()
                
        for simNum in simNums:
                cursor.execute("SELECT MAX(`stepSize`) FROM `sq_displacements` WHERE simNum = {}".format(simNum)) #find largest step for a particular simulation
                result = cursor.fetchone()
                sdLen = result[0]
                try:
                        maxLen = max(sdLen,maxLen) #compare simulation's max to running max
                except:
                        print("No squared-displacement data is available for simNum = {}.".format(simNum))
                        print("This simulation will not be included in calculation.")

        for i in range(maxLen+1): #here i is the step size
                #print("Calculating msd and st.dev for step = {}".format(i))
                sdList = [] #initialize list of squared displacements
                #pick out all SDs for a particular step size
                for simNum in simNums:
                        cursor.execute("SELECT `sd` FROM `sq_displacements` WHERE simNum = {} AND stepSize = {}".format(simNum,i))
                        result = cursor.fetchall()
                        sub_sdList = [item for t in result for item in t] #format list
                        sdList += sub_sdList
                msd = numpy.mean(sdList)
                stdev = numpy.std(sdList)
                sd_count = len(sdList) #number of data points used in determining msd
                ins_stmt = """INSERT INTO `MSDs` (`setNum`,`stepNum`,`msd`,`stdev`,`sdCount`)
                              VALUES (%s, %s, %s, %s, %s)"""
                ins_data = (setNum, i, msd, stdev, sd_count)
                cursor.execute(ins_stmt,ins_data)
        cnx.commit()
        print("MSD calculation complete!")
        return setNum

def plot_MSD(setNum, cnx, plot_axes, errorBarType = False, output_name = 'msd.png'):
        '''function that plots the MSD and st.dev of a set of
        random walk simulations by pulling data from a database'''

        cursor = cnx.cursor()

        #pull simulation timeStep information
        cursor.execute("""SELECT `stepSize` from `experiments`
                        WHERE simNum = (SELECT `simNum` FROM `msdSets`
                        WHERE `setNum` = {} LIMIT 1)""".format(setNum)) #pick dt from a component experiment
        result = cursor.fetchone()
        if result == None:
                print("The selected MSD set (setNum = {}) does not exist".format(setNum))
                print("No figure will be generated.")
                return
        dt = result[0]

        #generate simulation's times list
        cursor.execute("SELECT `stepNum` FROM `MSDs` where setNum = {}".format(setNum))
        result = cursor.fetchall()
        t = [dt*item for t in result for item in t] #take steps and convert to time

        #pull simulation's msd and st.dev data
        cursor.execute("SELECT `msd`, `stdev`, `sdcount` FROM `MSDs` WHERE setNum = {}".format(setNum))
        result = cursor.fetchall()
        msd = [item[0] for item in result]
        if errorBarType == "stdev":
                errorBar = [item[1] for item in result]
        elif errorBarType == "sterr":
                errorBar = [item[1]/(item[2]**0.5) for item in result]
        elif errorBarType == "msderr":
                cursor.execute("SELECT `simCount` FROM `msdsetmeta`WHERE setNum = {}".format(setNum))
                result2 = cursor.fetchone()[0]
                errorBar = [item[1]/(result2**0.5) for item in result]
        else:
                errorBar = [0 for item in result]
        fig = pyplot.figure()
        pyplot.errorbar(t,msd,errorBar)
        pyplot.axis(plot_axes)
        pyplot.xlabel('t')
        pyplot.ylabel('MSD')
        pyplot.grid(True)

        pyplot.savefig(output_name)
        return fig

def plot_traj(simNums, cnx, output_name = 'trajectory.png'):
        '''function that plots the 2D trajectory of multiple
        random walks by pulling data from a database'''

        cursor = cnx.cursor()
        fig = pyplot.figure()
        for simNum in simNums:
                #pull trajectory data
                cursor.execute("SELECT `xpos` FROM `trajectories` where simNum = {}".format(simNum))
                result = cursor.fetchall()
                x = [item for t in result for item in t]
                cursor.execute("SELECT `ypos` FROM `trajectories` where simNum = {}".format(simNum))
                result = cursor.fetchall()
                y = [item for t in result for item in t]
                #plot trajectory
                pyplot.plot(x,y)
                
        pyplot.grid()
        pyplot.xlabel('x')
        pyplot.ylabel('y')
        pyplot.gca().set_aspect('equal')
        pyplot.savefig(output_name)
        return fig
