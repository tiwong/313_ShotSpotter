from shiny import App, render, reactive, ui
import shinyswatch
from shinywidgets import output_widget, register_widget, render_widget
# import matplotlib.pyplot as plt
from utils import *
from pathlib import Path
# from faicons import icon_svg

# total911 = get_911_data()
total911 = read_911_data()
ss_sca_total = total911[(total911.category == 'SHOTSPT ') | (total911.category == 'SHOT SPT')].sca.unique()

ss_sca_dict = {}
for week in total911.week.unique():
    week_df = total911[total911.week == week]
    ss_sca = week_df[(week_df.category == 'SHOTSPT ') | (week_df.category == 'SHOT SPT')].sca.unique()
    if len(ss_sca) > 0:
        ss_sca_dict.update({week: ss_sca})
ss_sca911 = total911[total911.sca.isin(ss_sca_total)]


app_ui = ui.page_navbar(
    shinyswatch.theme.simplex(),
    ui.nav('Home', ui.h2('About', align = 'center'),
           ui.hr(),
           ui.h2('Data', align = 'center')),
    ui.nav('Summary', 'etc.'),
    ui.nav('Methods', 'Two-Way Fixed Effects Model'),
    ui.nav_menu('Visualizations',
    ui.nav('Maps','HI'),
    ui.nav('Distributions',
        ui.layout_sidebar(
            ui.panel_sidebar(
            ui.input_select("select_group", "Select Level", ['Zipcodes', 'Precincts', 'Scout Car Areas (SCA)'])),
           ui.panel_main(output_widget('total911_hist'))),
           )),
    title= ui.div(
        ui.img(src = 'cod.png',
        height = 75,
        width = 75,
        style = "margin:5px 5px"),
        '313 Shotspotter'
    )
)

def server(input, output, session):
    @output
    @render_widget
    def total911_hist():
        fig = px.histogram(ss_sca911, x = 'sca', color = 'category')
        fig.update_layout(margin = {"r":0,"t":0,"l":0,"b":0})
        return fig

www_dir = Path(__file__).parent / 'www'
app = App(app_ui, server, static_assets = www_dir)