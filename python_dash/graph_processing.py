from utils import read_911_data
import pandas as pd
import plotly.express as px

total911 = read_911_data()


def create_911_graph():
    ss_sca_total = total911[(total911.category == 'SHOTSPT ') | (
        total911.category == 'SHOT SPT')].sca.unique()

    ss_sca_dict = {}
    for week in total911.week.unique():
        week_df = total911[total911.week == week]
        ss_sca = week_df[(week_df.category == 'SHOTSPT ') | (
            week_df.category == 'SHOT SPT')].sca.unique()
        if len(ss_sca) > 0:
            ss_sca_dict.update({week: ss_sca})
    fig = px.histogram(total911[total911.sca.isin(
        ss_sca_total)], x='sca', color='category')
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    return fig


def create_recanvas_graph():
    df_recanvas = total911.copy()
    df_recanvas['category'] = df_recanvas['category'].str.strip()
    df_recanvas['call_timestamp'] = pd.to_datetime(
        df_recanvas['call_timestamp'])
    df_recanvas = df_recanvas[df_recanvas['category'] == 'SHOTSPT']
    df_recanvas['time_difference'] = None
    df_recanvas.reset_index(drop=True, inplace=True)
    last_shotspotter = {}

    for index, row in df_recanvas.iterrows():
        if "SHOTSPOTTER" in row['calldescription'].replace(" ", "") and "RECANVAS" not in row['calldescription'].replace(" ", "") and row['calldescription'] != "SYSTEM TEST - SHOTSPOTTER":
            last_shotspotter[index] = row['call_timestamp']
        elif "RECANVAS" in row['calldescription']:
            matching_shotspotter_timestamp = None
            for i in range(index - 1, -1, -1):
                if "SHOTSPOTTER" in df_recanvas.at[i, 'calldescription'].replace(" ", "") and "RECANVAS" not in df_recanvas.at[i, 'calldescription'].replace(" ", "") and df_recanvas.at[i, 'calldescription'] != "SYSTEM TEST - SHOTSPOTTER" and \
                        df_recanvas.at[i, 'X'] == row['X'] and df_recanvas.at[i, 'Y'] == row['Y']:
                    matching_shotspotter_timestamp = last_shotspotter.get(i)
                    break

            if matching_shotspotter_timestamp is not None:
                time_difference = row['call_timestamp'] - \
                    matching_shotspotter_timestamp
                df_recanvas.at[index, 'time_difference'] = time_difference

    filtered_df = df_recanvas[(df_recanvas['calldescription'] == 'RECANVAS SHOTSPOTTER') | (
        df_recanvas['calldescription'] == 'RECANVASS SHOTSPOTTER')].copy()
    filtered_df = filtered_df[filtered_df['time_difference'].notna()]

    time_difference_list = (filtered_df['time_difference']).tolist()

    updated_time_list = []
    for time in time_difference_list:
        updated_time_list.append((time.days*24 + time.seconds//3600) / 24)

    fig = px.histogram(x=updated_time_list, nbins=200, labels={'x': 'Time Difference (days)', 'y': 'Frequency'},
                       title='Distribution of Time Differences')
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    return fig


def create_sca_graph(sca):
    sca = sca.strip()

    filtered_df = total911[(total911.category.str.contains(
        "SHOTSPT") | total911.category.str.contains("SHOT SPT"))].copy()

    sca_w_shotspotter = set(filtered_df['precinct_sca'])

    sca_df = total911[total911['precinct_sca'].isin(sca_w_shotspotter)].copy()

    sca_data = filtered_df[filtered_df['precinct_sca'] == sca].copy()
    sca_data['time'] = pd.to_datetime(
        sca_data['call_timestamp'], format="%Y/%m/%d %H:%M:%S+00")

    weekly_counts_shotspt = sca_data.resample(
        'W', on='time')['category'].count()

    start_date = sca_data['time'].min()
    end_date = sca_data['time'].max()

    non_shotspt_data_ip = sca_df[(
        sca_df['precinct_sca'] == sca) & sca_df.category.str.contains("SHOTS IP")].copy()
    non_shotspt_data_ip['time'] = pd.to_datetime(
        non_shotspt_data_ip['call_timestamp'], format="%Y/%m/%d %H:%M:%S+00")
    non_shotspt_data_ip = non_shotspt_data_ip[(
        non_shotspt_data_ip['time'] >= start_date) & (non_shotspt_data_ip['time'] <= end_date)]

    weekly_counts_non_shotspt_ip = non_shotspt_data_ip.resample('W', on='time')[
        'category'].count()

    non_shotspt_data_jh = sca_df[(
        sca_df['precinct_sca'] == sca) & sca_df.category.str.contains("SHOTS JH")].copy()
    non_shotspt_data_jh['time'] = pd.to_datetime(
        non_shotspt_data_jh['call_timestamp'], format="%Y/%m/%d %H:%M:%S+00")
    non_shotspt_data_jh = non_shotspt_data_jh[(
        non_shotspt_data_jh['time'] >= start_date) & (non_shotspt_data_jh['time'] <= end_date)]

    weekly_counts_non_shotspt_jh = non_shotspt_data_jh.resample('W', on='time')[
        'category'].count()

    fig = px.line()
    fig.add_scatter(x=weekly_counts_shotspt.index,
                    y=weekly_counts_shotspt.values, name="SHOTSPT", mode="lines", line=dict(color="blue"))
    fig.add_scatter(x=weekly_counts_non_shotspt_ip.index, y=weekly_counts_non_shotspt_ip.values,
                    name="SHOTS IP", mode="lines", line=dict(color="red"))
    fig.add_scatter(x=weekly_counts_non_shotspt_jh.index, y=weekly_counts_non_shotspt_jh.values,
                    name="SHOTS JH", mode="lines", line=dict(color="green"))

    fig.update_layout(title=sca)
    fig.update_xaxes(showgrid=True)

    return fig
