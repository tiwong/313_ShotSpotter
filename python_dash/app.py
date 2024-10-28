from graph_processing import create_911_summary, create_combined_map, create_greenlight_map, create_shotspotter_map, create_map, create_map_only_SS, create_recanvas_summary, create_sca_graph, create_911_graph, create_recanvas_graph, create_sca_graphs, create_sca_summary, create_weekly_graph, create_weekly_summary, get_precincts
from shiny import App, render, reactive, ui
import shinyswatch
from shinywidgets import output_widget, register_widget, render_widget
from utils import *
from pathlib import Path

# To run app - shiny run --reload --launch-browser app.py
text_dict = {}
file_names = ["recanvas", "scout_car_areas", "total_911_calls", "weekly_shotspotter_incidents", "gunshots_sca",
              "gunshots_sca_shotspotter_only", "project_greenlight", "combined_visualization", "shotspotter_locations"]


for file in file_names:
    with open("Summaries/" + file + ".html") as f:
        text_dict[file] = f.read()

with open("about.html") as f:
    about_html = f.read()

with open("head.html") as f:
    head_html = f.read()


app_ui = ui.page_navbar(
    shinyswatch.theme.simplex(),
    ui.nav('Home',
           ui.page_fluid(ui.HTML(head_html),
                         ui.output_ui("page_summary"),
                         ui.layout_sidebar(
               ui.panel_sidebar(
                    # Removed 'Project Greenlight Cameras' from dropdown menu, but all other code is still intact
                   ui.input_select("select_graph", "Select Graph", ['Combined Visualization', 'Total Number of Gunshots per SCA', 'Total Shotspotter Gunshot Calls per SCA',
                                   'Total Gunshot Calls', 'Scout Car Areas (SCA)', 'Recanvas', 'Weekly ShotSpotter Incidents', 'Shotspotter / Project Greenlight Locations']),
                   ui.panel_conditional("input.select_graph === 'Shotspotter / Project Greenlight Locations'",
                                        [ui.input_checkbox("show_greenlight", "Project Greenlight", True),
                                         ui.input_checkbox("show_shotspotter", "ShotSpotter", True)]),
                   ui.panel_conditional("input.select_graph === 'Total Gunshot Calls'",
                                        ui.output_text_verbatim("total_911_calls_summary")),
                   ui.panel_conditional("input.select_graph === 'Scout Car Areas (SCA)'",
                                        [ui.input_select("select_precinct", "Select Precinct", get_precincts()),
                                         ui.output_text_verbatim("sca_summary")]),
                   ui.panel_conditional("input.select_graph === 'Recanvas'",
                                        ui.output_text_verbatim("recanvas_summary")),
                   ui.panel_conditional("input.select_graph === 'Weekly ShotSpotter Incidents'",
                                        ui.output_text_verbatim("weekly_summary"))),
               ui.page_fluid(ui.panel_main(output_widget('render_graph'))))),
           ),
    ui.nav('About', ui.HTML(about_html)),
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

    @output
    @render.ui
    def page_summary():
        selected_graph = input.select_graph()

        if selected_graph == 'Recanvas':
            return ui.HTML(text_dict["recanvas"])
        elif selected_graph == 'Total Gunshot Calls':
            return ui.HTML(text_dict["total_911_calls"])
        elif selected_graph == 'Scout Car Areas (SCA)':
            return ui.HTML(text_dict["scout_car_areas"])
        elif selected_graph == 'Weekly ShotSpotter Incidents':
            return ui.HTML(text_dict["weekly_shotspotter_incidents"])
        elif selected_graph == 'Total Number of Gunshots per SCA':
            return ui.HTML(text_dict["gunshots_sca"])
        elif selected_graph == "Total Shotspotter Gunshot Calls per SCA":
            return ui.HTML(text_dict["gunshots_sca_shotspotter_only"])
        elif selected_graph == "Project Greenlight Cameras":
            return ui.HTML(text_dict["project_greenlight"])
        elif selected_graph == "Combined Visualization":
            return ui.HTML(text_dict["combined_visualization"])
        elif selected_graph == "Shotspotter / Project Greenlight Locations":
            return ui.HTML(text_dict["shotspotter_locations"])

    @output
    @render_widget
    def render_graph():
        selected_graph = input.select_graph()
        selected_precinct = input.select_precinct()

        # Check which datasets should be displayed
        show_greenlight = input.show_greenlight()
        show_shotspotter = input.show_shotspotter()

        print(selected_graph, selected_precinct)
        if selected_graph == 'Recanvas':
            # Render the Recanvas graph
            return create_recanvas_graph()
        elif selected_graph == 'Total Gunshot Calls':
            # Render the Total Gunshot Calls graph
            return create_911_graph()
        elif selected_graph == 'Scout Car Areas (SCA)':
            # Render the SCA graph
            return create_sca_graphs(selected_precinct)
        elif selected_graph == 'Weekly ShotSpotter Incidents':
            return create_weekly_graph()
        elif selected_graph == 'Total Number of Gunshots per SCA':
            return create_map()
        elif selected_graph == 'Total Shotspotter Gunshot Calls per SCA':
            return create_map_only_SS()
        elif selected_graph == 'Project Greenlight Cameras':
            return create_greenlight_map()
        elif selected_graph == 'Combined Visualization':
            return create_combined_map()
        elif selected_graph == 'Shotspotter / Project Greenlight Locations':
            return create_shotspotter_map(show_greenlight, show_shotspotter)

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
