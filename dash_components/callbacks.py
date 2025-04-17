import dash
from dash import Dash, dcc, html, dash_table, Input, Output, State, callback_context
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import pandas as pd
import requests
import plotly.express as px

from dash_components.figures import create_state_bar, create_choropleth, cancer_data
from dash_components.figures import uv_data
from dash_components.layout import CONVERSION_FACTOR

uv_data_counties = pd.read_csv("dash_components/assets/uv-county.csv")
vitamin_data = pd.read_csv("dash_components/assets/Vitamin-D.csv")
vitamin_data["IU per serving"] = pd.to_numeric(vitamin_data["IU per serving"], errors='coerce')
#uv_data_counties = uv_data.groupby("STATENAME", as_index=False)["UV"].mean()
#print(vitamin_data)

CONVERSION_FACTOR = 10

app = dash.Dash()

geojson_url = "https://raw.githubusercontent.com/PublicaMundi/MappingAPI/master/data/geojson/us-states.json"
states_geojson = requests.get(geojson_url).json()

#uv stacked bar by state with radio buttons
def register_callback(app):
    @app.callback(
        Output("uv-bar-graph", "figure"),
        Input("sort-order", "value")
    )
    def update_uv_graph(sort_order):
        order_ascending = (sort_order == "asc")

        return create_state_bar(order_ascending=order_ascending)
    @app.callback(
        Output("county-output", "children"),
        Input("county-input", "value")
    )
    def update_county_output(county_value):
        if not county_value:
            return "Please enter your county"
        county_value = county_value.strip().title()
        county_row = uv_data_counties[uv_data_counties["COUNTY NAME"] == county_value]

        if county_row.empty:
            return "County not found. Please check your spelling."

        county_uv = county_row["UV"].iloc[0]
        county_name = county_row["COUNTY NAME"].iloc[0]

        threshold = 1300
        if 1300 < county_uv < 3000 :
            message = f"WARNING: {county_name}'s UV level exceeds the universal average. Take precaution on sunny days."

        if 3000 < county_uv < 4000 :
            message = f"WARNING: {county_name}'s UV level exceeds the universal average by 1700-2700. Be careful outside!"

        if 4000 < county_uv < 5000 :
            message = f"WARNING: {county_name}'s UV level exceeds the universal average by 2700-3700. Take extreme precaution when going outside!"

        if 5000 < county_uv :
            message = f"WARNING: {county_name}'s UV level exceeds the universal average by at least 3700. Avoid going outside!"

        return message
    #choropleth and slider
    @app.callback(
        Output("cancer-choropleth", "figure"),
        Input("year-slider", "value")
    )
    def update_choropleth(selected_year):
        filtered_data = cancer_data[cancer_data["Year"] == selected_year]
        custom_scale = [
            (0, "#f51414"),
            (0.5, "#c70c0c"),
            (1, "#8c0101")
        ]
        fig = px.choropleth(
            data_frame = filtered_data,
            geojson = states_geojson,
            locations = "State",
            featureidkey = "properties.name",
            color = "Age-Adjusted Rate",
            color_continuous_scale = custom_scale,
            scope = "usa",
            hover_name = "State",
            title = f"Cancer Rate by State in {selected_year}"
        )
        fig.update_geos(visible = False)
        fig.update_layout(margin={"r":0, "t":50, "l":0, "b":50})
        return fig

    #vitamin D bar graph and dropdown
    @app.callback(
        [Output("vitamin-bar", "figure"),
         Output("dropdown-output", "children")],
        Input("sun-dropdown", "value")
    )
    def update_vitamin_bar(sun_minutes):
        sun_iu = sun_minutes * CONVERSION_FACTOR

        df_sun = pd.DataFrame([{"Source": "Sun Exposure", "IU per serving": sun_iu}])
        total_food_iu = vitamin_data["IU per serving"].sum()
        df_total = pd.DataFrame([{"Source": "Total Food", "IU per serving": total_food_iu}])
        df_all = pd.concat([vitamin_data, df_total, df_sun], ignore_index=True)

        #for custom graph coloring
        def assign_color(source):
            if source == "Sun Exposure":
                return "hotpink"
            elif source == "Total Food":
                return "lightblue"
            else:
                return "blue"
        df_all["BarColor"] = df_all["Source"].apply(assign_color)

        fig3 = px.bar(
            df_all,
            x = "Source",
            y= "IU per serving",
            title="Vitamin D IU Comparison: Diet vs. UV rays",
            labels={"IU per serving": "Vitamin D (IU)"}
        )
        fig3.update_traces(marker_color= df_all["BarColor"].tolist())
        fig3.add_hline(
            y=600,
            line_dash="dash",
            line_color="black",
            annotation_text="Daily Value of Vitamin D",
            annotation_position="top"
        )

        fig3.update_layout(margin={"t": 50, "b":100})
        dropdown_message = (
            f"With {sun_minutes} minutes of sun exposure you would produce "
            f"approximately {sun_iu} IU of vitamin D."

        )
        return fig3, dropdown_message
