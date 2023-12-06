import pandas as pd
import requests
import re


def get_911_data():
    """ PULL FROM OPEN DATA PORTAL API TO PANDAS DF """
    # Takes about 4 mins to run
    url = "https://services2.arcgis.com/qvkbeam7Wirps6zC/arcgis/rest/services/911_Calls_New/FeatureServer/0/query?where=category%20%3D%20'SHOT%20SPT'%20OR%20category%20%3D%20'SHOTS%20IP'%20OR%20category%20%3D%20'SHOTS%20JH'%20OR%20category%20%3D%20'SHOTSPT'&outFields=*&outSR=4326&f=json"
    df = pd.DataFrame()
    offset = 0

    print("Beginning 911 API data pull...")

    while True:
        response = requests.get(url, params={'resultOffset': offset})
        data = response.json().get('features')
        df = pd.concat([df, pd.json_normalize(data)],
                       axis=0, ignore_index=True)
        if len(data) < 1000:
            break
        offset += 1000

    print("Data pull complete.")

    return df


def clean_911(df, keep_shape=False):
    print("Begin Cleaning Data...")

    # Rename columns
    df.columns = ['incident_id', 'agency', 'incident_address', 'zip_code', 'priority', 'callcode', 'calldescription', 'category', 'call_timestamp', 'precinct_sca', 'respondingunit', 'officerinitiated',
                  'intaketime', 'dispatchtime', 'traveltime', 'totalresponsetime', 'time_on_scene', 'totaltime', 'neighborhood', 'block_id', 'council_district', 'longitude', 'latitude', 'shape', 'ObjectId', 'X', 'Y']

    # Drop rows w. missing values
    df.dropna(subset=['dispatchtime', 'traveltime',
              'time_on_scene', 'longitude', 'latitude'], inplace=True)
    # Drop duplicate entries
    df.drop_duplicates(subset='incident_id', inplace=True)

    # Drop miscellaneous entris
    df = df[(df.zip_code != '     ') & (df.zip_code != '0    ')]
    df = df[(df.intaketime != '0') | (df.traveltime != '0')]
    df = df[df.calldescription != 'SYSTEM TEST - SHOTSPOTTER']
    df = df[df.totalresponsetime <= 180]

    df.call_timestamp = pd.to_datetime(df.call_timestamp, unit='ms')
    df.incident_id = df.incident_id.astype('int64')
    df.zip_code = df.zip_code.astype('int64')
    df.priority = pd.to_numeric(df.priority, errors='coerce')
    df.priority.fillna(0, inplace=True)
    df.priority = df.priority.astype('int64')
    df.longitude = df.longitude.astype('float64')
    df.latitude = df.latitude.astype('float64')

    time_features = ['intaketime',
                     'dispatchtime', 'traveltime', 'totalresponsetime', 'time_on_scene',
                     'totaltime']
    df[time_features] = df[time_features].replace(
        ',', '', regex=True).astype('float64')

    df['sca'] = [re.sub('[^0-9]', '', str(x)).lstrip('0')
                 for x in df.precinct_sca]
    df['precinct'] = [x[:1] if x[:1] != '1' else x[:2] for x in df.sca]
    df = df[df.sca != '']
    df['sca'] = [x[:2] + '1' + x[2:]
                 if (x == '121') | (x == '111') else x for x in df.sca]
    df['sca'] = [x if ((len(x) == 4) | ((len(x) == 3) & (x[:1] != '1'))) else (
        x[:1] + '0' + x[1:] if len(x) == 2 else x[:2] + '0' + x[2:]) for x in df.sca]

    df['date'] = df.call_timestamp.dt.strftime('%Y-%m-%d')
    df['month'] = df.call_timestamp.dt.strftime('%Y-%m')
    df['week'] = df.call_timestamp.dt.strftime('%Y-%U')
    df['year'] = df.call_timestamp.dt.strftime('%Y')

    df.drop('precinct_sca', axis=1, inplace=True)

    if keep_shape == True:
        df.to_csv('clean_updated_gunshots.csv', index=False)
    else:
        df.drop(['shape', 'ObjectId', 'X', 'Y'], axis=1, inplace=True)
        df.to_csv('clean_updated_gunshots.csv', index=False)

    print("Data cleaning complete.")
    return df


def load_911(file_name):
    df = pd.read_csv(file_name, low_memory=False)
    df.sca = df.sca.astype('string')
    df.precinct = df.precinct.astype('string')
    df.call_timestamp = pd.to_datetime(df.call_timestamp)
    df.incident_id = df.incident_id.astype('int64')
    df.zip_code = df.zip_code.astype('int64')
    df.priority = df.priority.astype('int64')
    df.longitude = df.longitude.astype('float64')
    df.latitude = df.latitude.astype('float64')
    return df


def create_recanvas_data():
    print("Begin calculating Recanvas data...")

    df_recanvas = load_911('clean_updated_gunshots.csv')

    df_recanvas['time_difference'] = None
    df_recanvas.reset_index(drop=True, inplace=True)
    last_shotspotter = {}

    for index, row in df_recanvas.iterrows():
        if "SHOTSPOTTER" in row['calldescription'].replace(" ", "") and "RECANVAS" not in row['calldescription'].replace(" ", ""):
            last_shotspotter[index] = row['call_timestamp']
        elif "RECANVAS" in row['calldescription']:
            matching_shotspotter_timestamp = None
            for i in range(index - 1, -1, -1):
                if "SHOTSPOTTER" in df_recanvas.at[i, 'calldescription'].replace(" ", "") and "RECANVAS" not in df_recanvas.at[i, 'calldescription'].replace(" ", "") and \
                        df_recanvas.at[i, 'X'] == row['X'] and df_recanvas.at[i, 'Y'] == row['Y']:
                    matching_shotspotter_timestamp = last_shotspotter.get(i)
                    break

            if matching_shotspotter_timestamp is not None:
                time_difference = row['call_timestamp'] - \
                    matching_shotspotter_timestamp
                df_recanvas.at[index, 'time_difference'] = time_difference

    filter_df_recanvas = df_recanvas[(df_recanvas['calldescription'] == 'RECANVAS SHOTSPOTTER') | (
        df_recanvas['calldescription'] == 'RECANVASS SHOTSPOTTER')].copy()
    filter_df_recanvas = filter_df_recanvas[filter_df_recanvas['time_difference'].notna(
    )]

    filter_df_recanvas.to_csv('recanvas_filtered.csv')

    print("Recanvas Data Calculation complete.")

    return filter_df_recanvas


def create_all_files():
    clean_911(get_911_data(), True)
    create_recanvas_data()


def get_SCAs():
    sca_url = 'https://services2.arcgis.com/qvkbeam7Wirps6zC/arcgis/rest/services/DPD_SCAs/FeatureServer/0/query?outFields=*&where=1%3D1&f=geojson'
    response = requests.get(sca_url)
    sca = response.json()
    return sca
