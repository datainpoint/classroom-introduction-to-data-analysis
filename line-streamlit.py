import streamlit as st
import pandas as pd
import altair as alt

time_series = pd.read_csv("time_series.csv")
st.title('Covid19 Time Series Data')
selected_countries = st.multiselect('Select Countries:',
                                    time_series["Country_Region"].unique(),
                                    'Taiwan')
filtered_time_series = time_series[time_series["Country_Region"].isin(selected_countries)]
filtered_time_series["Date"] = pd.to_datetime(filtered_time_series["Date"])
chart = alt.Chart(filtered_time_series).mark_line().encode(
    x='Date',
    y='Confirmed',
    color='Country_Region',
    strokeDash='Country_Region',
)
st.altair_chart(chart, use_container_width=True)