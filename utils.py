import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import requests
import re

def get_911_data():
    """ PULL FROM OPEN DATA PORTAL API TO PANDAS DF """
    # Takes about 4 mins to run
    url = "https://services2.arcgis.com/qvkbeam7Wirps6zC/arcgis/rest/services/911_Calls_New/FeatureServer/0/query?where=category%20%3D%20'SHOT%20SPT'%20OR%20category%20%3D%20'SHOTS%20IP'%20OR%20category%20%3D%20'SHOTS%20JH'%20OR%20category%20%3D%20'SHOTSPT'&outFields=*&outSR=4326&f=json"
    df = pd.DataFrame()
    offset = 0

    while True:
        response = requests.get(url, params= {'resultOffset':offset})
        data = response.json().get('features')
        df = pd.concat([df, pd.json_normalize(data)], axis = 0, ignore_index= True)
        if len(data) < 1000: 
            break
        offset += 1000

    # Cleaning
    df.columns = ['incident_id', 'agency', 'incident_address', 'zip_code', 'priority', 'callcode', 'calldescription', 'category', 'call_timestamp','precinct_sca', 'respondingunit', 'officerinitiated', 'intaketime','dispatchtime', 'traveltime', 'totalresponsetime', 'time_on_scene', 'totaltime', 'neighborhood', 'block_id', 'council_district', 'longitude', 'latitude', 'shape', 'ObjectId', 'X', 'Y']

    df.drop_duplicates(subset='incident_id', inplace=True)
    df.call_timestamp = pd.to_datetime(df.call_timestamp)
    df.X = df.X.astype('float64')
    df.Y = df.Y.astype('float64')
    df.loc[(df.zip_code == '     ') | (df.zip_code == '0    '), 'zip_code'] = '0'
    df.zip_code = df.zip_code.astype('Int64')
    df = df[df.calldescription != 'SYSTEM TEST - SHOTSPOTTER']

    time_features = ['intaketime',
       'dispatchtime', 'traveltime', 'totalresponsetime', 'time_on_scene',
       'totaltime']
    df[time_features] = df[time_features].replace(',', '', regex=True).astype('float64')

    years = df.call_timestamp.dt.isocalendar().year
    weeks = df.call_timestamp.dt.isocalendar().week

    df['week_nums'] = weeks + (years - min(years)) * 52
    df['sca']= [re.sub('[^0-9]','', str(x)) for x in df.precinct_sca]
    return df

def get_zipcodes():
    zipcodes_url = 'https://services2.arcgis.com/qvkbeam7Wirps6zC/arcgis/rest/services/ZipCodes/FeatureServer/0/query?outFields=*&where=1%3D1&f=geojson'
    response = requests.get(zipcodes_url)
    zipcodes = response.json()
    return zipcodes

def get_SCAs():
    sca_url = 'https://services2.arcgis.com/qvkbeam7Wirps6zC/arcgis/rest/services/DPD_SCAs/FeatureServer/0/query?outFields=*&where=1%3D1&f=geojson'
    response = requests.get(sca_url)
    sca = response.json()
    return sca
