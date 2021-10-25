import requests
import numpy as np
import pandas as pd

class Covid19:
    def get_lookup_table(self):
        uid_iso_fips_lookup_table = pd.read_csv("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/UID_ISO_FIPS_LookUp_Table.csv")
        uid_iso_fips_lookup_table['Country_Region'] = uid_iso_fips_lookup_table['Country_Region'].str.replace('*', '', regex=False)
        uid_iso_fips_lookup_table['Combined_Key'] = uid_iso_fips_lookup_table['Combined_Key'].str.replace('*', '', regex=False)
        uid_iso_fips_lookup_table['Population'] = uid_iso_fips_lookup_table['Population'].astype('Int64')
        split_series = uid_iso_fips_lookup_table['Combined_Key'].str.split(', ')
        counties = []
        states = []
        for lst in split_series:
            if len(lst) == 1:
                counties.append(np.nan)
                states.append(np.nan)
            elif len(lst) == 2:
                counties.append(np.nan)
                states.append(lst[0])
            elif len(lst) == 3:
                counties.append(lst[0])
                states.append(lst[1])
        uid_iso_fips_lookup_table['Admin2'] = counties
        uid_iso_fips_lookup_table['Province_State'] = states
        uid_iso_fips_lookup_table = uid_iso_fips_lookup_table[['UID', 'Combined_Key',
                                                               'iso2', 'iso3',
                                                               'Country_Region', 'Province_State', 'Admin2',
                                                               'Lat', 'Long_', 'Population']]
        return uid_iso_fips_lookup_table

    def get_daily_report(self, report_date):
        self._report_date = report_date
        try:
            daily_report = pd.read_csv("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/{}.csv".format(report_date))
            daily_report['Country_Region'] = daily_report['Country_Region'].str.replace('*', '', regex=False)
            daily_report['Combined_Key'] = daily_report['Combined_Key'].str.replace('*', '', regex=False)
            daily_report = daily_report.drop(labels=['Active', 'Lat', 'Long_', 'FIPS', 'Admin2', 'Province_State', 'Country_Region'], axis=1)
            return daily_report[['Combined_Key', 'Last_Update', 'Confirmed', 'Deaths', 'Incident_Rate', 'Case_Fatality_Ratio']]
        except:
            print("Wrong format or unavailable report date: {}.".format(report_date))
            print("Expecting mm-dd-yyyy format.")
    def get_time_series(self):
        time_series_confirmed = pd.read_csv("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv")
        time_series_deathes = pd.read_csv("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv")
        #time_series_recovered = pd.read_csv("https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv")
        time_series_confirmed['Province/State'] = time_series_confirmed['Province/State'].fillna(time_series_confirmed['Country/Region'])
        time_series_deathes['Province/State'] = time_series_deathes['Province/State'].fillna(time_series_deathes['Country/Region'])
        #time_series_recovered['Province/State'] = time_series_recovered['Province/State'].fillna(time_series_recovered['Country/Region'])
        time_series_confirmed = time_series_confirmed.drop(labels=['Lat', 'Long'], axis=1)
        time_series_deathes = time_series_deathes.drop(labels=['Lat', 'Long'], axis=1)
        #time_series_recovered = time_series_recovered.drop(labels=['Lat', 'Long'], axis=1)
        time_series_confirmed_long = pd.melt(time_series_confirmed, id_vars=['Province/State', 'Country/Region'], var_name='Date', value_name='Confirmed')
        time_series_deathes_long = pd.melt(time_series_deathes, id_vars=['Province/State', 'Country/Region'], var_name='Date', value_name='Deaths')
        #time_series_recovered_long = pd.melt(time_series_recovered, id_vars=['Province/State', 'Country/Region'], var_name='Date', value_name='Recovered')
        time_series = time_series_confirmed_long
        time_series['Deaths'] = time_series_deathes_long['Deaths']
        #time_series['Recovered'] = time_series_recovered_long['Recovered']
        time_series['Date'] = pd.to_datetime(time_series['Date'])
        time_series = time_series[time_series['Date'] <= pd.to_datetime(self._report_date)]
        date_series = time_series['Date'].dt.strftime('%Y-%m-%d')
        time_series = time_series.drop('Date', axis=1)
        time_series['Date'] = pd.to_datetime(date_series)
        time_series['Country/Region'] = time_series['Country/Region'].str.replace('*', '', regex=False)
        groupby_date_country = time_series.groupby(['Date', 'Country/Region'])
        time_series = groupby_date_country[['Confirmed', 'Deaths']].sum().reset_index()
        time_series.columns = ['Date', 'Country_Region', 'Confirmed', 'Deaths']
        confirmed_shifted = time_series.groupby('Country_Region')['Confirmed'].shift(1, fill_value=0)
        deaths_shifted = time_series.groupby('Country_Region')['Deaths'].shift(1, fill_value=0)
        daily_cases = time_series['Confirmed'] - confirmed_shifted
        daily_deaths = time_series['Deaths'] - deaths_shifted
        n_cols = time_series.shape[1]
        time_series.insert(n_cols, 'Daily_Cases', daily_cases)
        n_cols = time_series.shape[1]
        time_series.insert(n_cols, 'Daily_Deaths', daily_deaths)
        return time_series