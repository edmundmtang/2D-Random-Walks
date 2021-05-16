''' Plot the results of 2D random walks as
an animated scatterplot with trailing lines
using plotly's graph objects package

Edmund tang 4/15/2021
'''
import plotly.express as px
import plotly.graph_objs as go

import mysql.connector
import pandas as pd

cnx = mysql.connector.connect(
    host = "localhost",
    user = "root",
    password = "password",
    database = "2d_walk"
    )
cursor = cnx.cursor()
cursor.execute("SELECT `simNum`, `stepNum`, `xpos`, `ypos` FROM `trajectories` WHERE `simNum` <= 10") # using only first 10 experiments
results = cursor.fetchall()

# pull data from database
df = pd.DataFrame([[ij for ij in i] for i in results])
df.rename(columns = {0: "Simulation ID", 1: "Step Number", 2: "x position", 3: "y position"}, inplace = True)

steps = list(df[df["Simulation ID"] == 1]["Step Number"]) # step numbers from first simulation
simNums = list(df[df["Step Number"] == 0]["Simulation ID"]) # all simulation IDs

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
for simNum in simNums:
    # generate each pair of traces by simulation ID
    data_by_simNum = df[df["Simulation ID"] == simNum]
    # trace for the marker
    trace0 = go.Scatter(x=[list(data_by_simNum["x position"])[0]],
                        y=[list(data_by_simNum["y position"])[0]],
                        mode = "markers",
                        marker = dict(color = px.colors.qualitative.Plotly[simNum % len(px.colors.qualitative.Plotly)]), #https://plotly.com/python/discrete-color/
                        name = "Particle {}".format(simNum)
                        )
    # trace for the line
    trace1 = go.Scatter(x=trace0.x,
		        y=trace0.y,
		        mode = "lines",
		        line = dict(color = trace0.marker.color),
                        name = "Trajectory {}".format(simNum)
                        )
    # add traces to data
    fig_dict["data"].append(trace0); fig_dict["data"].append(trace1)

# make frames
frames = []
for i in steps:
    frame_data = []
    for simNum in simNums:
        data_by_simNum = df[df["Simulation ID"] == simNum]
        frame_mrkr_by_simNum = dict(type = "scatter", # end marker
                                    x=[list(data_by_simNum["x position"])[i]],
                                    y=[list(data_by_simNum["y position"])[i]])
        frame_data.append(frame_mrkr_by_simNum)
        frame_traj_by_simNum = dict(type = "scatter", # trajectory line
                                    x=list(data_by_simNum["x position"])[:i+1],
                                    y=list(data_by_simNum["y position"])[:i+1])
        frame_data.append(frame_traj_by_simNum)
    frame = dict(data= frame_data,
                 traces = list(range(0,len(simNums)*2)),
                 name = i)
    frames.append(frame)
                           
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

fig.write_html("rw2d_trailing_scatterplot.html")
