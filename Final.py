"""
Name: Victoria Saintil
CS230: Section 3
Data: New England Airports
URL: Link to your web application on Streamlit Cloud (if posted)

Description: This data analysis utilizes data collected from various airports in the New England Area.
Using the filters to the left, you are bale to refine the data based on type and location.
"""
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import pydeck as pdk
import plotly.express as px
import csv


# Load and cache the data then read it into a dictionary if file exists
@st.cache_data
def load_data():
    try:
        file= open('new_england_airports.csv', mode='r')
        reader = csv.DictReader(file)
        rows = [row for row in reader]

        if not rows:
            raise ValueError("The dataset is empty.")

        # Code for reading csv file into a dictionary based on code from ChatGPT.
        # See section 1 of accompanying document.

        # Convert rows to a Pandas DataFrame
        data = pd.DataFrame(rows)

        # Make sure required columns exist
        required_columns = ['longitude_deg', 'latitude_deg', 'elevation_ft']
        if not all(col in data.columns for col in required_columns):
            raise ValueError("The dataset is missing required columns for mapping.")

        # change number columns to proper types
        numeric_columns = ['latitude_deg', 'longitude_deg', 'elevation_ft']
        for col in numeric_columns:
            data[col] = pd.to_numeric(data[col], errors='coerce')

        return data.dropna()
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()  # Return an empty DataFrame if an error occurs


# Helper functions
def filter_data(data1, airport_type="all", location="all"):
    if airport_type != "all":
        data1 = data1[data1['type'] == airport_type]
    if location != "all":
        data1 = data1[data1['iso_region'] == location]  # Assuming 'iso_region' contains location info
    return data1


# Matplotlib Bar Chart
def plot_bar_chart(data2):
    if data2.empty:
        st.warning("No data available for the selected filters.")
    else:
        type_counts = data2['type'].value_counts()
        fig, ax = plt.subplots(figsize=(10, 6))
        type_counts.plot(kind='bar', color='purple', ax=ax)
        ax.set_title("Number of Airports by Type")
        ax.set_xlabel("Airport Type")
        ax.set_ylabel("Count")
        st.pyplot(fig)

#Plotly Bar chart idea came from ChatGPT. See section 2 of accompanying document.

#Used the Plotly website to help understand how to use the package properly. url: https://plotly.com/python/getting-started/
def plot_chart(data3):
    if data3.empty:
        st.warning("No data available for the selected filters.")
    else:
        # Count the number of airports by type
        type_counts = data3['type'].value_counts().reset_index()
        type_counts.columns = ['Airport Type', 'Count']

        # Create a bar chart
        fig = px.bar(type_counts, x='Airport Type', y='Count',
                     color='Airport Type', title="Number of Airports by Type",
                     labels={'Airport Type': 'Airport Type', 'Count': 'Number of Airports'})

        # Custom layout
        fig.update_layout(
            xaxis_title="Airport Type",
            yaxis_title="Number of Airports",
            template="plotly_dark",
            showlegend=False
        )

        # Display chart in Streamlit
        st.plotly_chart(fig)


# Load data
data = load_data()

# Streamlit App
#Added a background image to the website! reference: https://www.youtube.com/watch?v=pyWqw5yCNdo
page_bg_img = """
<style>
[data-testid="stAppViewContainer"]{
background-image: url("https://image.cnbcfm.com/api/v1/image/108066493-1732216796010-gettyimages-1726532680-61035_14_rsb200120_011.jpeg?v=1732216825&w=1858&h=1045&vtcrop=y");
background-size: cover;
}
[data-testid="stHeader"] {
background: rgba(0,0,0,0);
}
</style>
"""

st.markdown(page_bg_img, unsafe_allow_html=True)
st.title("New England Airports Explorer")
st.sidebar.header("Filters")

# Create sidebar widgets that allow filtering through the data to display various outcomes
airport_type = st.sidebar.selectbox("Select Airport Type", ["all"] + list(data['type'].unique()), key="airport_type")
location = st.sidebar.selectbox("Select Location", ["all"] + list(data['iso_region'].unique()), key="location")

if data.empty:
    st.error("The dataset is empty. Unable to display data or charts.")
else:
    # Filtered Data
    filtered_data = filter_data(data, airport_type, location)
    if filtered_data.empty:
        st.warning("No data available for the selected filters.")
    else:
        st.write(f"Displaying {len(filtered_data)} airports: In this chart, you are able to see all the airports that are listed in the CSV file."
                 f" You are able to list each column in ascending or descending order.")
        st.dataframe(filtered_data)

        # Displays the top 5 elevated airports in the New England Area
        top_5 = filtered_data.nlargest(5, 'elevation_ft')
        st.subheader("Top 5 Airports by Elevation")
        st.write("\nThis chart shows you the 5 highest airports based on their elevation")
        st.dataframe(top_5)

        # Matplotlib Bar Chart
        st.subheader("Airports by Type (Matplotlib)")
        st.write("\nThis is a basic chart that displays the airports by type and displays the data.")
        plot_bar_chart(filtered_data)

        # Map that displays the location of the airports on a charted map
        if 'longitude_deg' in filtered_data.columns and 'latitude_deg' in filtered_data.columns:
            filtered_data = filtered_data.dropna(subset=['longitude_deg', 'latitude_deg'])
            st.subheader("Airport Locations")
            st.write("\nThis map shows where each airport is using their latitude and longitude."
                         )
            st.pydeck_chart(pdk.Deck(
                initial_view_state=pdk.ViewState(latitude=42, longitude=-71, zoom=6),
                layers=[
                    pdk.Layer(
                        "ScatterplotLayer",
                        data=filtered_data,
                        get_position=["longitude_deg", "latitude_deg"],
                        get_radius=1000,
                        get_color=[255, 0, 0],
                    ),
                ],
            ))
        else:
            st.error("Required columns for mapping (latitude_deg, longitude_deg) are missing.")

        # Plotly Bar Chart to display a more advanced version of the first bar chart
        st.subheader("Airports by Type (Plotly)")
        st.write("This chart is a more advanced version of the first bar chart."
                     " Using this chart, you are able to hover over each bar to get the exact amount "
                     "and type without using the the labels on the x and y axis")
        plot_chart(filtered_data)
