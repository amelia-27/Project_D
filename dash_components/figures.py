import dash
import plotly.express as px
from dash import Dash, dcc, html, dash_table, Input, Output, State, callback_context
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas as pd
import requests

uv_data = pd.read_csv("dash_components/assets/uv-county.csv")
vitamin_data = pd.read_csv("dash_components/assets/Vitamin-D.csv")
cancer_data = pd.read_csv("dash_components/assets/Melanoma_states.csv")
cancer_data['Age-Adjusted Rate'] = pd.to_numeric(cancer_data['Age-Adjusted Rate'], errors='coerce')

uv_data = uv_data.groupby("STATENAME", as_index=False)["UV"].mean()

default_year = cancer_data["Year"].min()
initial_cancer_df = cancer_data[cancer_data["Year"] == default_year]

#Stacked Bar UV by State
def create_state_bar(order_ascending = True):
    sorted_data = uv_data.sort_values("UV", ascending=order_ascending)
    fig = px.bar(
        data_frame = sorted_data,
        x = "UV",
        y= "STATENAME",
        orientation = "h",
        title = "Average UV Levels by State (Wh/m²)",
        labels = {"UV": "UV", "STATENAME": "State"}
    )
    fig.update_layout(
        height = 1000,
        xaxis=dict(
            range=[0,8000],
            tickvals=[1300, 4000, 6000],
            ticktext = ["Universal average", "High", "Very Exposed to UV"]
        ),
        yaxis=dict(
            automargin=True
        )
    )
    return fig

def create_choropleth(selected_year=None):
    if selected_year is None:
        selected_year = cancer_data["Year"].min()
    filtered_data = cancer_data[cancer_data["Year"] == selected_year]
    #import here again?
    geojson_url = "https://raw.githubusercontent.com/PublicaMundi/MappingAPI/master/data/geojson/us-states.json"
    states_geojson = requests.get(geojson_url).json()
    custom_scale = [
        (0, "#f51414"),
        (0.5, "#c70c0c"),
        (1, "#8c0101")
    ]
    fig2 = px.choropleth(
        data_frame = initial_cancer_df,
        geojson = states_geojson,
        locations = "State",
        featureidkey = "properties.name",
        color = "Age-Adjusted Rate",
        color_continuous_scale = custom_scale,
        scope="usa",
        hover_name = "State",
        title = f"Melanoma of the Skin by Case Rate in {default_year}"
    )
    fig2.update_geos(visible=False)
    fig2.update_layout(margin={"r":0, "t": 50, "l": 0, "b": 50})
    return fig2