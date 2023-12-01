from graph_processing import create_911_summary, create_recanvas_summary, create_sca_graph, create_911_graph, create_recanvas_graph, create_sca_graphs, create_sca_summary, create_weekly_graph, create_weekly_summary, get_precincts
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
                               ui.input_select("select_graph", "Select Graph", [
                                   'Total 911 Calls', 'Scout Car Areas (SCA)', 'Recanvas', 'Weekly Shotspotter Incidents']),
                               ui.panel_conditional("input.select_graph === 'Total 911 Calls'",
                                                    ui.output_text_verbatim("total_911_calls_summary")),
                               ui.panel_conditional("input.select_graph === 'Scout Car Areas (SCA)'",
                                                    [ui.input_select("select_precinct", "Select Precinct", get_precincts()),
                                                     ui.output_text_verbatim("sca_summary")]),
                               ui.panel_conditional("input.select_graph === 'Recanvas'",
                                                    ui.output_text_verbatim("recanvas_summary")),
                               ui.panel_conditional("input.select_graph === 'Weekly Shotspotter Incidents'",
                                                    ui.output_text_verbatim("weekly_summary"))),
                           ui.page_fluid(ui.panel_main(output_widget('render_graph')))),
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
    selected_graph = ""
    selected_precinct = 0
    show_precinct_select = False

    @output
    @render_widget
    def render_graph():
        selected_graph = input.select_graph()
        selected_precinct = input.select_precinct()

        print(selected_graph, selected_precinct)
        if selected_graph == 'Recanvas':
            # Render the Recanvas graph
            return create_recanvas_graph()
        elif selected_graph == 'Total 911 Calls':
            # Render the Total 911 Calls graph
            return create_911_graph()
        elif selected_graph == 'Scout Car Areas (SCA)':
            # Render the SCA graph
            return create_sca_graphs(selected_precinct)
        elif selected_graph == 'Weekly Shotspotter Incidents':
            return create_weekly_graph()

    @output
    @render.text
    def total_911_calls_summary():
        return create_911_summary()

    @output
    @render.text
    def sca_summary():
        selected_precinct = input.select_precinct()
        return create_sca_summary(selected_precinct)

    @output
    @render.text
    def recanvas_summary():
        return create_recanvas_summary()

    @output
    @render.text
    def weekly_summary():
        return create_weekly_summary()


www_dir = Path(__file__).parent / 'www'
app = App(app_ui, server, static_assets=www_dir)
