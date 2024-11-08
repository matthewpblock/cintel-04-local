import plotly.express as px
import seaborn as sns
from palmerpenguins import load_penguins

from shiny.express import input, ui
from shinywidgets import output_widget, render_widget, render_plotly
from shiny import render, reactive

# Set the UI to dark mode
ui.update_dark_mode("dark")

# Add a sidebar
with ui.sidebar(position="left", bg="#181818", open="open"):
    ui.h2("Sidebar")  # Sidebar header
    
    # Insert Drop-Down menu for selecting attributes
    ui.input_selectize(
        id="selected_attribute",
        label="Selected Attribute",
        choices=["bill_length_mm", "bill_depth_mm", "flipper_length_mm", "body_mass_g"],
    )

    # Insert Numeric Input field
    ui.input_numeric(id="plotly_bin_count", label="Bin Count (Plotly)", value=5)
    # Insert a slider input
    ui.input_slider(
        id="seaborn_bin_count", label="Bin Count (Seaborn)", min=3, max=21, value=7
    )

    # Insert checkbox filter for species
    ui.input_checkbox_group(
        id="selected_species_list",
        label="Species",
        choices=["Adelie", "Gentoo", "Chinstrap"],
        selected=["Adelie", "Gentoo", "Chinstrap"],
        inline=False,
    )
     # Insert checkbox filter for island
    ui.input_checkbox_group(
        id="selected_island_list",
        inline=True,
        label="Islands",
        choices=["Torgerson", "Biscoe", "Dream"],
        selected=["Torgerson", "Biscoe", "Dream"])
    
    # Inster a dividing line
    ui.hr()
    # Insert a link
    ui.a(
        "Source code on GitHub",
        href="https://github.com/matthewpblock/cintel-04-local",
        target="_blank",
    )

# Main content

# Use the built-in function to load the Palmer Penguins dataset
penguins = load_penguins()

ui.page_opts(title="Matt's Flying Penguin Block", fillable=True)  # Insert page header
with ui.layout_columns():  # Format into columns

    with ui.card():
        ui.card_header("Data Table")

        @render.data_frame
        def penguins_dt():
            return render.DataTable(filtered_data())

    with ui.card():
        ui.card_header("Data Grid")

        @render.data_frame
        def penguins_dg():
            return render.DataGrid(filtered_data())


with ui.layout_columns():  # Create a second row of columns

    with ui.card(fill=True):
        ui.card_header("Plotly Histogram")

        @render_widget
        def plot1():
            scatterplot = px.histogram(
                data_frame=filtered_data(),
                x=input.selected_attribute(),
                nbins=input.plotly_bin_count(),
            ).update_layout(
                title={"text": "Palmer Penguins", "x": 0.5},
                yaxis_title="Count",
                xaxis_title=input.selected_attribute(),
            )
            return scatterplot

    with ui.card():
        ui.card_header("Seaborn Histogram")

        @render.plot
        def plot2():
            ax = sns.histplot(
                data=filtered_data(),
                x=input.selected_attribute(),
                bins=input.seaborn_bin_count(),
            )
            ax.set_title("Palmer Penguins")
            ax.set_xlabel(input.selected_attribute())
            ax.set_ylabel("Number")
            return ax


# Insert a Plotly Scatterplot (not in a column)
with ui.card(full_screen=True):
    ui.card_header("Plotly Scatterplot: Species")

    @render_plotly
    def plotly_scatterplot():
        # Return a scatter plot using Plotly Express
        # The plot visualizes the relationship between bill length and bill depth
        # for different species and islands
        return px.scatter(
            data_frame=filtered_data(),  # Filtered data for the scatter plot
            x="bill_length_mm",          # X-axis: Bill length in millimeters
            y="bill_depth_mm",           # Y-axis: Bill depth in millimeters
            color="species",             # Color points by species
            symbol="island",             # Different symbols for different islands
            labels={                     # Custom labels for the axes and legend
                "bill_depth_mm": "Bill Depth",
                "bill_length_mm": "Bill Length",
                "species": "Species",
                "island": "Island",
            },
        )


# --------------------------------------------------------
# Reactive calculations and effects
# --------------------------------------------------------

# Add a reactive calculation to filter the data
# By decorating the function with @reactive, we can use the function to filter the data
# The function will be called whenever an input functions used to generate that output changes.
# Any output that depends on the reactive function (e.g., filtered_data()) will be updated when the data changes.


# This decorator marks the function as a reactive calculation.
# Any output that depends on the reactive function (e.g., filtered_data()) 
# will be updated when the data changes.

@reactive.calc
def filtered_data():
    # Filter the penguins DataFrame based on the selected species and islands
    isFilterMatch = penguins["species"].isin(input.selected_species_list()) & penguins["island"].isin(input.selected_island_list())
    
    # Return the filtered DataFrame
    return penguins[isFilterMatch]
