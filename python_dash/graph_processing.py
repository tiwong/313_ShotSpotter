import statistics
from utils import create_all_files, get_911_data, clean_911, get_SCAs, load_911
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objs as go
import ipywidgets as widgets
from scipy.stats.mstats import winsorize

# create_all_files()

total911 = load_911('clean_updated_gunshots.csv')
total911['category'] = total911['category'].str.replace(" ", "")
shotspt_df = total911[(total911.category.str.contains(
    "SHOTSPT"))].copy()
greenlight_df = pd.read_csv('Project_Green_Light_Locations.csv')
greenlight_df = greenlight_df.dropna()

# 911 Graph


def create_911_graph():
    ss_sca_total = total911.sca.unique()

    fig = px.histogram(total911[total911.sca.isin(
        ss_sca_total)], x='sca', color='category')
    return fig


def create_911_summary():
    total_calls = len(total911)

    sca_counts = total911.groupby('sca').size()
    average_calls_per_sca = sca_counts.mean()

    category_counts = total911.groupby('category').size()
    most_calls_category = category_counts.idxmax()
    least_calls_category = category_counts.idxmin()

    most_calls_sca = sca_counts.idxmax()
    least_calls_sca = sca_counts.idxmin()

    summary_str = (
        f"Total 911 Calls: {total_calls}\n"
        f"Average Calls per SCA: {average_calls_per_sca:.2f}\n"
        f"Category with Most Calls: {most_calls_category} ({category_counts[most_calls_category]})\n"
        f"Category with Least Calls: {least_calls_category} ({category_counts[least_calls_category]})\n"
        f"SCA with Most Calls: {most_calls_sca} ({sca_counts[most_calls_sca]})\n"
        f"SCA with Least Calls: {least_calls_sca} ({sca_counts[least_calls_sca]})\n"
    )

    return summary_str


# Recanvas

def create_recanvas_list():
    filter_df_recanvas = load_911('recanvas_filtered.csv')

    filter_df_recanvas['time_difference'] = pd.to_timedelta(
        filter_df_recanvas['time_difference'])

    time_difference_list = (filter_df_recanvas['time_difference']).tolist()

    updated_time_list = []
    for time in time_difference_list:
        updated_time_list.append((time.days*24 + time.seconds//3600) / 24)

    updated_time_array = np.array(updated_time_list, dtype=np.float32)
    updated_time_array = winsorize(updated_time_array, (0.01, 0.3))

    return updated_time_array


def create_recanvas_graph():
    fig = px.histogram(x=create_recanvas_list(), nbins=200, labels={'x': 'Time Difference (days)', 'y': 'Frequency'},
                       title='Distribution of Time Differences')
    return fig


def create_recanvas_summary():
    updated_time_list = create_recanvas_list()

    mean = sum(updated_time_list) / len(updated_time_list)
    median = statistics.median(updated_time_list)
    mode = statistics.mode(updated_time_list)
    data_range = max(updated_time_list) - min(updated_time_list)
    q1 = statistics.quantiles(updated_time_list, n=4)[0]
    q3 = statistics.quantiles(updated_time_list, n=4)[2]

    return f"""Mean: {mean:.2f}
Median: {median:.2f}
Mode: {mode:.2f}
Range: {data_range:.2f}
Q1 (25th percentile): {q1:.2f}
Q3 (75th percentile): {q3:.2f}"""


# SCAs

def get_precincts():
    return sorted(list(set(total911['precinct'].astype('int64'))))


def get_scas_in_precinct(precinct):
    precinct_data = total911[total911['precinct'] == precinct].copy()
    scas_list = sorted(precinct_data['sca'].unique().tolist())
    return scas_list


def create_sca_graphs(precinct):
    scas = get_scas_in_precinct(precinct)
    sca_graphs = []
    for sca in scas:
        sca_graphs.append(create_sca_graph(sca))

    box = widgets.VBox(sca_graphs)
    return box


def create_sca_graph(sca):
    sca = str(sca).strip()

    sca_df = total911.copy()

    sca_data = shotspt_df[shotspt_df['sca'] == sca].copy()
    sca_data['time'] = pd.to_datetime(
        sca_data['call_timestamp'], format="%Y/%m/%d %H:%M:%S+00")

    weekly_counts_shotspt = sca_data.resample(
        'W', on='time')['category'].count()

    start_date = sca_data['time'].min()
    end_date = sca_data['time'].max()

    data_ip = sca_df[(
        sca_df['sca'] == sca) & sca_df.category.str.contains("SHOTSIP")].copy()
    data_ip['time'] = pd.to_datetime(
        data_ip['call_timestamp'], format="%Y/%m/%d %H:%M:%S+00")
    if (start_date == end_date or pd.isnull(start_date)):
        start_date = data_ip['time'].min()
        end_date = data_ip['time'].max()
    data_ip = data_ip[(
        data_ip['time'] >= start_date) & (data_ip['time'] <= end_date)]

    weekly_counts_ip = data_ip.resample('W', on='time')[
        'category'].count()

    data_jh = sca_df[(
        sca_df['sca'] == sca) & sca_df.category.str.contains("SHOTSJH")].copy()
    data_jh['time'] = pd.to_datetime(
        data_jh['call_timestamp'], format="%Y/%m/%d %H:%M:%S+00")
    data_jh = data_jh[(
        data_jh['time'] >= start_date) & (data_jh['time'] <= end_date)]

    weekly_counts_jh = data_jh.resample('W', on='time')[
        'category'].count()

    fig = go.FigureWidget(data=[
        go.Scatter(x=weekly_counts_shotspt.index,
                   y=weekly_counts_shotspt.values, name="SHOTSPT", mode="lines", line=dict(color="blue")),
        go.Scatter(x=weekly_counts_ip.index, y=weekly_counts_ip.values,
                   name="SHOTS IP", mode="lines", line=dict(color="red")),
        go.Scatter(x=weekly_counts_jh.index, y=weekly_counts_jh.values,
                   name="SHOTS JH", mode="lines", line=dict(color="green"))])

    fig.update_layout(title=f'Scout Car Area: {int(sca[len(sca) - 2:])}')
    fig.update_xaxes(showgrid=True)

    return fig


def create_sca_summary(precinct):
    scas = get_scas_in_precinct(precinct)

    summary = {
        'precinct': precinct,
        'total_calls': 0,
        'sca_summary': {}
    }

    for sca in scas:
        sca_data = total911[total911['sca'] == sca]

        total_calls_sca = len(sca_data)

        summary['total_calls'] += total_calls_sca

        category_counts = sca_data['category'].value_counts().to_dict()

        summary['sca_summary'][sca] = {
            'total_calls': total_calls_sca,
            'category_counts': category_counts
        }

    summary_str = f"Precinct {precinct} Summary:\n"
    summary_str += f"Total Calls: {summary['total_calls']}\n"

    for sca, sca_info in summary['sca_summary'].items():
        summary_str += f"SCA {sca}: Total Calls: {sca_info['total_calls']}, "
        summary_str += ', '.join([f"{cat}: {count}" for cat,
                                 count in sca_info['category_counts'].items()])
        summary_str += "\n"

    return summary_str


# Weekly shotspotter
def create_weekly_graph():
    all_shotspt = shotspt_df.copy()
    non_shotspt = total911[~(total911.category.str.contains(
        "SHOTSPT"))].copy()

    all_shotspt['time'] = pd.to_datetime(
        all_shotspt['call_timestamp'], format="%Y/%m/%d %H:%M:%S+00")
    non_shotspt['time'] = pd.to_datetime(
        non_shotspt['call_timestamp'], format="%Y/%m/%d %H:%M:%S+00")

    all_shotspt = all_shotspt.resample('W', on='time')[
        'category'].count().reset_index()
    non_shotspt = non_shotspt.resample('W', on='time')[
        'category'].count().reset_index()

    start_date = all_shotspt['time'].min()
    end_date = all_shotspt['time'].max()

    mask = (all_shotspt['time'] >= start_date) & (
        all_shotspt['time'] <= end_date)
    all_shotspt = all_shotspt.loc[mask]

    mask = (non_shotspt['time'] >= start_date) & (
        non_shotspt['time'] <= end_date)
    non_shotspt = non_shotspt.loc[mask]

    all_shotspt.columns = ['time', 'count']
    non_shotspt.columns = ['time', 'count']

    fig = go.Figure()

    fig.add_trace(go.Scatter(x=all_shotspt['time'], y=all_shotspt['count'], mode='lines',
                             name='SHOTSPT', line=dict(color='blue')))

    fig.add_trace(go.Scatter(x=non_shotspt['time'], y=non_shotspt['count'], mode='lines',
                             name='NON SHOTSPT', line=dict(color='red')))

    fig.update_layout(
        yaxis_range=[0, 500],
        title="Weekly ShotSpotter Incidents"
    )

    return fig


def create_weekly_summary():
    weekly_counts_shotspt = shotspt_df.copy()
    weekly_counts_shotspt['time'] = pd.to_datetime(
        weekly_counts_shotspt['call_timestamp'], format="%Y/%m/%d %H:%M:%S+00")
    weekly_counts_shotspt = weekly_counts_shotspt.resample('W', on='time')[
        'category'].count()

    non_shotspt = total911[~(total911.category.str.contains(
        "SHOTSPT"))].copy()

    weekly_counts_non_shotspt = non_shotspt.copy()
    weekly_counts_non_shotspt['time'] = pd.to_datetime(
        weekly_counts_non_shotspt['call_timestamp'], format="%Y/%m/%d %H:%M:%S+00")
    weekly_counts_non_shotspt = weekly_counts_non_shotspt.resample('W', on='time')[
        'category'].count()

    total_shotspt = weekly_counts_shotspt.sum()
    average_shotspt = weekly_counts_shotspt.mean()
    peak_shotspt = weekly_counts_shotspt.max()

    total_non_shotspt = weekly_counts_non_shotspt.sum()
    average_non_shotspt = weekly_counts_non_shotspt.mean()
    peak_non_shotspt = weekly_counts_non_shotspt.max()

    summary_str = f"Weekly ShotSpotter Summary:\n"
    summary_str += f"Total ShotSpotter Incidents: {total_shotspt}\n"
    summary_str += f"Average ShotSpotter Incidents per Week: {average_shotspt:.2f}\n"
    summary_str += f"Peak Week for ShotSpotter Incidents: {peak_shotspt}\n"
    summary_str += f"Total Non-ShotSpotter Incidents: {total_non_shotspt}\n"
    summary_str += f"Average Non-ShotSpotter Incidents per Week: {average_non_shotspt:.2f}\n"
    summary_str += f"Peak Week for Non-ShotSpotter Incidents: {peak_non_shotspt}\n"

    return summary_str

# Map


def create_map():
    sca = get_SCAs()
    sca_counts = total911.groupby(by=['sca']).size().to_frame().reset_index()
    sca_counts.columns = ['sca', 'shots']
    sca_counts.sort_values(by='shots')

    fig = px.choropleth_mapbox(sca_counts, geojson=sca,
                               locations='sca',
                               color='shots',
                               featureidkey="properties.Area",
                               mapbox_style='carto-positron',
                               color_continuous_scale='matter',
                               zoom=9.25,
                               center={'lat': 42.3314, 'lon': -83.0458},
                               opacity=0.85,
                               title='All Gunshots')
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    return fig


def create_map_only_SS():
    sca = get_SCAs()
    sca_counts = shotspt_df.groupby(by=['sca']).size().to_frame().reset_index()
    sca_counts.columns = ['sca', 'shots']

    sca_counts_filtered = sca_counts[sca_counts['shots'] >= 10]

    sca_counts_filtered['log_shots'] = np.log(sca_counts_filtered['shots'])

    fig = px.choropleth_mapbox(sca_counts_filtered, geojson=sca,
                               locations='sca',
                               color='log_shots',
                               featureidkey="properties.Area",
                               mapbox_style='carto-positron',
                               color_continuous_scale='matter',
                               zoom=9.25,
                               center={'lat': 42.3314, 'lon': -83.0458},
                               opacity=0.85,
                               title='All Gunshots',
                               hover_data={'shots': True, 'log_shots': False})
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    return fig


def create_greenlight_map():
    fig = px.scatter_mapbox(greenlight_df,
                            lat="latitude",
                            lon="longitude",
                            hover_name="business_name",
                            hover_data=["address", "business_type"],
                            color_discrete_sequence=["fuchsia"],
                            zoom=10,
                            height=600)

    fig.update_layout(mapbox_style="open-street-map")

    return fig


def create_combined_map():
    sca = get_SCAs()
    sca_counts = total911.groupby(by=['sca']).size().to_frame().reset_index()
    sca_counts.columns = ['sca', 'shots']
    sca_counts.sort_values(by='shots')

    fig = px.choropleth_mapbox(sca_counts, geojson=sca,
                               locations='sca',
                               color='shots',
                               featureidkey="properties.Area",
                               mapbox_style='carto-positron',
                               color_continuous_scale='matter',
                               opacity=0.5,
                               title='Gunshots and Greenlight Locations')

    sca_counts = shotspt_df.groupby(by=['sca']).size().to_frame().reset_index()
    sca_counts.columns = ['sca', 'shots']
    sca_counts.sort_values(by='shots')

    fig.add_choroplethmapbox(geojson=sca,
                             locations=sca_counts['sca'],
                             z=sca_counts['shots'],
                             featureidkey="properties.Area",
                             colorscale='Viridis',
                             marker_line_width=0)

    fig.add_scattermapbox(lat=greenlight_df["latitude"],
                          lon=greenlight_df["longitude"],
                          mode='markers',
                          marker=dict(size=6, color="green"),
                          text=greenlight_df["business_name"],
                          hoverinfo='text')

    fig.update_layout(mapbox_style="carto-positron",
                      mapbox_zoom=9.25,
                      mapbox_center={"lat": 42.3314, "lon": -83.0458},
                      margin={"r": 0, "t": 0, "l": 0, "b": 0})

    return fig
