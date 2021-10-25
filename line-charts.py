import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.express as px
from get_covid_data import Covid19

covid19 = Covid19()
daily_report = covid19.get_daily_report('09-30-2021')
time_series = covid19.get_time_series()
all_countries = time_series["Country_Region"].unique()

app = dash.Dash(__name__)

app.layout = html.Div([
    dcc.Dropdown(
        id="dropdown",
        options=[{"label": x, "value": x} 
                 for x in all_countries],
        value=["Taiwan", "Singapore", "Korea, South", "Israel"],
        multi=True
    ),
    dcc.Graph(id="line-chart"),
])

@app.callback(
    Output("line-chart", "figure"), 
    [Input("dropdown", "value")])
def update_line_chart(countries):
    mask = time_series["Country_Region"].isin(countries)
    fig = px.line(time_series[mask], 
        x="Date", y="Confirmed", color='Country_Region')
    return fig

app.run_server(debug=True)