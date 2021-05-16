'''Quickly and simply plot the results of
2d random walks as animated scatter plots

Edmund Tang 4/14/2021
'''

import plotly.express as px
import plotly.graph_objs as go

import mysql.connector
import pandas as pd

cnx = mysql.connector.connect(
    host = "localhost",
    user = "root",
    password = "phylumSnack1738#",
    database = "2d_walk"
    )
cursor = cnx.cursor()
cursor.execute("SELECT `simNum`, `stepNum`, `xpos`, `ypos` FROM `trajectories`")
results = cursor.fetchall()

df = pd.DataFrame([[ij for ij in i] for i in results])
df.rename(columns = {0: "Simulation ID", 1: "Step Number", 2: "x position", 3: "y position"}, inplace = True)

##trace1 = go.Scatter(
##    x=df['x position'],
##    y=df['y position'],
##    text=df['Simulation ID'],
##    mode='markers'
##    )
##
##layout = go.Layout(
##    title='Trajectories of 2D Random Walks',
##    xaxis=dict(title = "x Position"),
##    yaxis=dict(title = "y Position")
##    )
##
##data = [trace1]
##fig = go.Figure(data=data, layout=layout)
##fig.show()

#animated scatterplot using plotly.express
fig1 = px.scatter(df, x="x position", y="y position", animation_frame = "Step Number", animation_group="Simulation ID",
                 hover_name="Simulation ID",
                 range_x=[-20, 20], range_y=[-20,20], width=800, height=800
                 )

fig1.layout.updatemenus[0].buttons[0].args[1]['frame']['duration'] = 50
fig1.layout.updatemenus[0].buttons[0].args[1]['transition']['duration'] = 50
fig1.show()
