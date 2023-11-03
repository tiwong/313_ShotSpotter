from graph_processing import create_sca_graph, create_911_graph, create_recanvas_graph
from shiny import App, render, reactive, ui
import shinyswatch
from shinywidgets import output_widget, register_widget, render_widget
from utils import *
from pathlib import Path

app_ui = ui.page_navbar(
    shinyswatch.theme.simplex(),
    ui.nav('Home', ui.h2('About', align='center'),
           ui.hr(),
           ui.h2('Data', align='center')),
    ui.nav('Summary', 'etc.'),
    ui.nav('Methods', 'Two-Way Fixed Effects Model'),
    ui.nav_menu('Visualizations',
                ui.nav('Maps', 'HI'),
                ui.nav('Distributions',
                       ui.layout_sidebar(
                           ui.panel_sidebar(
                               ui.input_select("select_group", "Select Level", [
                                   'Total 911 Calls', 'Scout Car Areas (SCA)', 'Recanvas',]),
                               ui.input_text("selected_sca", "Enter SCA", "812B")),
                           ui.panel_main(output_widget('render_graph'))),
                       )),
    title=ui.div(
        ui.img(src='cod.png',
               height=75,
               width=75,
               style="margin:5px 5px"),
        ui.img(src='BDL_Transparent.png',
               height=75,
               width=125,
               style="margin:5px 5px")
    )
)


def server(input, output, session):
    @output
    @render_widget
    def render_graph():
        selected_value = input.select_group()
        selected_sca = input.selected_sca()
        print(selected_value)
        if selected_value == 'Recanvas':
            # Render the Recanvas graph
            return create_recanvas_graph()
        elif selected_value == 'Total 911 Calls':
            # Render the Total 911 Calls graph
            return create_911_graph()
        elif selected_value == 'Scout Car Areas (SCA)':
            # Render the SCA graph
            return create_sca_graph(selected_sca)


www_dir = Path(__file__).parent / 'www'
app = App(app_ui, server, static_assets=www_dir)
