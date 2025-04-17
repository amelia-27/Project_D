import dash
import plotly.express as px
from dash import Dash, dcc, html, dash_table, Input, Output, State, callback_context
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas as pd

from dash_components import callbacks, layout



app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.QUARTZ, dbc.icons.FONT_AWESOME],
)

#data preparation
#cancer_data = pd.read_csv("dash_components/assets/Melanoma_states.csv")
#uv_data = pd.read_csv("dash_components/assets/uv-county.csv")
#vitamin_data = pd.read_csv("dash_components/assets/Vitamin-D.csv")

#uv_data = uv_data.groupby("STATENAME", as_index=False)["UV"].mean()

app.layout = layout.create_layout()

callbacks.register_callback(app)


if __name__ == "__main__":
    app.run(debug=True)