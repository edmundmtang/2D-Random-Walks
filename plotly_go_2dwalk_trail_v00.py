''' Plot the results of 2D random walks as
an animated scatterplot with trailing lines
using plotly's graph objects package

Edmund tang 4/15/2021
'''
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

# pull data from database
df = pd.DataFrame([[ij for ij in i] for i in results])
df.rename(columns = {0: "Simulation ID", 1: "Step Number", 2: "x position", 3: "y position"}, inplace = True)

df = df[df["Simulation ID"] != 13] # skipping experiment 13

steps = list(df[df["Simulation ID"] == 1]["Step Number"])

# make figure
fig_dict = {
    "data": [],
    "layout": {},
    "frames": []
}

# fill in most of layout
fig_dict["layout"]["xaxis"] = {"range": [-20, 20], "title": "x Position"}
fig_dict["layout"]["yaxis"] = {"range": [-20, 20], "title": "y Position"}
fig_dict["layout"]["hovermode"] = "closest"
fig_dict["layout"]["width"] = 900
fig_dict["layout"]["height"] = 900
fig_dict["layout"]["updatemenus"] = [
    {
        "buttons": [
            {
                "args": [None, {"frame": {"duration": 0, "redraw": False},
                                "fromcurrent": True, "transition": {"duration": 5,
                                                                    "easing": "quadratic-in-out"}}],
                "label": "Play",
                "method": "animate"
            },
            {
                "args": [[None], {"frame": {"duration": 0, "redraw": False},
                                  "mode": "immediate",
                                  "transition": {"duration": 0}}],
                "label": "Pause",
                "method": "animate"
            }
        ],
        "direction": "left",
        "pad": {"r": 10, "t": 87},
        "showactive": True,
        "type": "buttons",
        "x": 0.1,
        "xanchor": "right",
        "y": 0,
        "yanchor": "top"
    }
]

sliders_dict = {
    "active": 0,
    "yanchor": "top",
    "xanchor": "left",
    "currentvalue": {
        "font": {"size": 20},
        "prefix": "Step:",
        "visible": True,
        "xanchor": "right"
    },
    "transition": {"duration": 50, "easing": "cubic-in-out"},
    "pad": {"b": 10, "t": 50},
    "len": 0.9,
    "x": 0.1,
    "y": 0,
    "steps": []
}

# make data
simNum = 1

data_by_simNum = df[df["Simulation ID"] == 1]

trace0 = go.Scatter(x=[data_by_simNum["x position"][0]],
                    y=[data_by_simNum["y position"][0]],
                    mode = "markers",
                    name = "Simulation 1"
                    )

trace1 = go.Scatter(x=[data_by_simNum["x position"][0]],
                    y=[data_by_simNum["y position"][0]],
                    mode = "lines"
                    )

fig_dict["data"] = [trace0, trace1]

# make frames

frames = [dict(data= [dict(type="scatter",
                           x=df["x position"][:i+1],
                           y=df["y position"][:i+1]),
                      dict(type="scatter",
                           x=df["x position"][:i+1],
                           y=df["y position"][:i+1])],
               traces = [0, 1],
               name = i,
               ) for i in range(0,len(steps))]
                           
fig_dict["frames"] = frames

# slider frames
for step in steps:  
    slider_step = {"args": [
        [step],
        {"frame": {"duration": 50, "redraw": False},
         "mode": "immediate",
         "transition": {"duration": 50}}
    ],
        "label": step,
        "method": "animate"}
    sliders_dict["steps"].append(slider_step)


fig_dict["layout"]["sliders"] = [sliders_dict]

fig = go.Figure(fig_dict)

fig.show()

fig.write_html("test.html")
