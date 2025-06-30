from shiny import App, render, ui, reactive
from baseData import get_base_data
from mtss.sidebar import app_sidebar


df = get_base_data().to_pandas()

app_ui = ui.page_fluid(
    ui.h2("DATA DASHBOARD"),
    ui.layout_sidebar(
        app_sidebar,
        ui.output_data_frame("data_table")
    )
)


def server(input, output, session):
    @output
    @render.data_frame
    def data_table():
        return df


app = App(app_ui, server)
