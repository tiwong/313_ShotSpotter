from shiny import App, render, reactive, ui
# import shinyswatch
# from shinywidgets import output_widget, register_widget
# import matplotlib.pyplot as plt
# from utils import *




app_ui = ui.page_navbar(
    # shinyswatch.theme.simplex(),
    ui.nav('Home', ui.h2('About', align = 'center'),
           ui.hr(),
           ui.h2('Data', align = 'center')),
    ui.nav('Summary', 'etc.'),
    ui.nav('Methods', 'Two-Way Fixed Effects Model'),
    ui.nav('Visualizations', 
           ui.layout_sidebar(
           ui.panel_sidebar(
               ui.input_select("select_group", "Select Level", ['Zipcodes', 'Precincts', 'Scout Car Areas (SCA)'])),
           ui.panel_main('Test'))),
    title='313 Shotspotter'
)

def server(input, output, session):
    @output
    @render.text
    def value():
        return "You choose:" + str(input.select_group())

app = App(app_ui, server)
