import dash
from dash import Dash, dcc, html, dash_table, Input, Output, State, callback_context
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas as pd

from dash_components.figures import create_state_bar, create_choropleth

cancer_data = pd.read_csv("dash_components/assets/Melanoma_states.csv")
default_year = cancer_data["Year"].min()
cancer_data['Age-Adjusted Rate'] = pd.to_numeric(cancer_data['Age-Adjusted Rate'], errors='coerce')
vitamin_data = pd.read_csv("dash_components/assets/Vitamin-D.csv")

CONVERSION_FACTOR = 10

app = dash.Dash(__name__)
def create_layout():
    fig2 = create_choropleth()
    return html.Div([
        html.H1("Sunshine: The Daily Deadly Radiation", style={"textAlign": "center"}),
        html.H3("Amelia Ubben - CS150", style={"textAlign": "center"}),
        dcc.RadioItems(
            #style={"height": "300px"},
            id = "sort-order",
            options=[
                {"label": "Highest to Lowest", "value": "asc"},
                {"label": "Lowest to Highest", "value": "desc"},
            ],
            value = "desc",
            inline=True
        ),
        dcc.Graph(id="uv-bar-graph",
                  figure=create_state_bar(order_ascending=False)),
        dcc.Input(
            id="county-input",
            type="text",
            placeholder = "Enter your county...",
            debounce = True,
            style = {"width": "50%", "marginBottom" : "20px", "marginTop" : "10px"}
        ),
        html.Div(id="county-output"),
        html.Div([
            html.H1("Melanoma: A Constant Threat"),
            dcc.Slider(
                id = "year-slider",
                min = cancer_data["Year"].min(),
                max = cancer_data["Year"].max(),
                value=default_year,
                marks={str(year): str(year) for year in sorted(cancer_data["Year"].unique())},
                step = None
            ),
            dcc.Graph(
                id="cancer-choropleth",
                figure=fig2,

            )
        ], style = {"width": "80%", "margin": "0 auto"}
        ),
        html.Div([
            html.H1("Vitamin-D from the Sun... How about Simple Diet?", style={"marginTop": "50px"}),

            html.Div([
                html.Label("Select Sun Exposure:"),
                dcc.Dropdown(
                    id = "sun-dropdown",
                    options=[
                        {"label": "15 minutes", "value": 15},
                        {"label": "30 minutes", "value": 30},
                        {"label": "40 minutes", "value": 40},
                        {"label": "50 minutes", "value": 50},
                    ],
                    value = 30,
                    clearable = False,
                ),
                html.Div(id="dropdown-output", style={"margin-top":"10px"})
            ], style = {"width":"80%", "margin": "auto"}
            ),
            dcc.Graph(
                id = "vitamin-bar", style={"height": "600px"}
            )
        ], style={"width":"80%", "margin": "0 auto"}
        )
    ])