"""
Name: Hanni Chen
CS602-SN1
Data: NYC Collisions
URL: Link to your web application online (see extra credit)
Description:
This program is designed to show NYC Collision report. 
The report at a glance will be on the main page along with tables and visualizations such as crashes over hour & month, percentages of cases in each borough.
The "Details" page will allow users to filter data by year, borough, and injured type with map to take a closer look in specific case conditions.
The "search by Zipcode" page allow users to look up cases at a specific zipcode location.
"""
import pandas as pd
import streamlit as st
import numpy as np
import pydeck as pdk
import matplotlib.pyplot as plt
from PIL import Image, ImageFont, ImageDraw

# Set the pages to wide layout
st.set_page_config(layout="wide")
# Setting up Main menu image & texts
# Open an image & add the title on image
title_image = Image.open("car_crash.jpg")
title_font = ImageFont.truetype('hannahchn/Calibri Bold', 75)
title_text = """             
              NYC 2015-2017 
               Crash Report
               (Sample Data) """
image_editable = ImageDraw.Draw(title_image)
image_editable.text((50, 200), title_text, (255, 255, 255))
title_image.save("title.jpg")

MENU_Options = ["Main Page", "Details", "Search By Zipcode"]
MENU = """
    Main Menu - Report At A Glance
====================================================================   
Details - Select filters to display the data that meet the criteria 
& See filtered data on Map
====================================================================   
Search by Zipcode - See data under a zipcode
====================================================================
"""


# Read the csv file (sample data)
FILENAME = "nyc_veh_crash_sample.csv"
def read_file():
    df = pd.read_csv(FILENAME)
    return df

def annotation(bars):
    for bar in bars:
        height = bar.get_height()
        plt.annotate('{}'.format(height), xy=(bar.get_x() + bar.get_width()/2, height), xytext=(1, 4), textcoords="offset points", ha="center", size=7, weight="bold")

def glance():
    df = read_file()
    st.title("Report At A Glance")
    st.subheader("Dataset Preview")
    st.dataframe(df)

    # Extract & Sort Time
    df["NEW_TIME"] = df["DATE"] + " " + df["TIME"]
    df["NEW_TIME"] = pd.to_datetime(df["NEW_TIME"])
    sortedBy_new_time = df.sort_values(by="NEW_TIME")
    time_in_order = sortedBy_new_time["NEW_TIME"]
    st.write(f'This sample dataset includes data from {time_in_order.iloc[1]} to {time_in_order.iloc[-1]}')
    st.write(f'This sample dataset has {df.shape[0]} records')
    # Extract, Count & Sort data by Hour
    df["HOUR"] = pd.to_datetime(df['TIME'], format='%H:%M').dt.hour
    sorted_hour = df["HOUR"].value_counts().sort_index()
    # Extract, Count & Sort data by Month
    df["MONTH"] = pd.to_datetime(df['DATE'], format='%m/%d/%y').dt.month
    sorted_month = df["MONTH"].value_counts().sort_index()
    # Extract & Count Borough Data
    borough_caseCount = df["BOROUGH"].value_counts()

    # Pivot Table: Crashes happened in each Borough By Year
    df["YEAR"] = pd.to_datetime(df['DATE'], format='%m/%d/%y').dt.year
    df["CRASHES"] = 1
    borough_year = df[["BOROUGH", "YEAR", "CRASHES"]]
    pivot_table = pd.pivot_table(borough_year, index=["BOROUGH", "YEAR"], aggfunc='count', margins=True, margins_name="Total")
    col1, col2, col3 = st.beta_columns([1, 1, 1])
    with col2:
        st.subheader("Crashes Summary")
        st.dataframe(pivot_table)

    # Convert all the vehicle factors to list & combine them into one
    vehicle1_factor = df["VEHICLE 1 FACTOR"].tolist()
    vehicle2_factor = df["VEHICLE 2 FACTOR"].tolist()
    vehicle3_factor = df["VEHICLE 3 FACTOR"].tolist()
    vehicle4_factor = df["VEHICLE 4 FACTOR"].tolist()
    vehicle5_factor = df["VEHICLE 5 FACTOR"].tolist()
    factors = vehicle1_factor + vehicle2_factor + vehicle3_factor + vehicle4_factor + vehicle5_factor
    # Convert the final list back to pandas series
    all_factors = pd.Series(factors)
    # Create factors table
    st.subheader("Count of factors of all crashes")
    factors_count = all_factors.value_counts().to_frame("Count")
    cols = st.beta_columns(2)
    cols[0].table(factors_count.iloc[1:21])
    cols[1].table(factors_count.iloc[21:42])
    st.markdown("Most crashes happened due to driver inattention/distraction. So please stay focus when you drive to avoid danger!")
    st.write("\n")

    st.subheader("Visualizations")
    chart_cols = st.beta_columns(2)
    # Bar Chart : Crashes Over Hour
    fig, ax = plt.subplots()
    x_axis = sorted_hour.index
    y_axis = sorted_hour.values
    h_bar = ax.bar(x_axis, y_axis, color="olive")
    h_bar[17].set_color("m")
    plt.xlabel("Hour")
    plt.ylabel("Cases")
    plt.xticks(x_axis, rotation=45)
    plt.title("Crashes Over Hour", fontsize=20)
    annotation(h_bar)

    x = sorted_hour.index
    y = sorted_hour.values
    line = plt.twinx()
    line.plot(x, y, color="mediumpurple", marker="o", alpha=0.3)
    line.set_ylim(0, 400)
    chart_cols[0].pyplot(fig)
    explain1 = """   
    The first high peak of crashes is between 8:00 - 10:00.
    
    The second high peak of crashes is between 16:00 - 19:00.
    
    Most of crashes happened during 17:00 - 18:00
    """
    chart_cols[0].write(explain1)

    # Bar Chart: Crashes over Month
    fig, ax = plt.subplots()
    x_axis = sorted_month.index
    y_axis = sorted_month.values
    m_bar = ax.bar(x_axis, y_axis, color='royalblue')
    m_bar[0].set_color("firebrick")
    plt.xlabel("Month")
    plt.ylabel("Cases")
    plt.xticks(x_axis)
    plt.title("Crashes Over Month", fontsize=20)
    annotation(m_bar)
    chart_cols[1].pyplot(fig)
    explain2 = """   
    Most crashes happened in January.
    
    Then the number of crashes decreased gradually 
    
    until it remained relatively stable after march.
    """
    chart_cols[1].write(explain2)
    st.write("\n")

    another_cols = st.beta_columns(2)
    # Pie Chart: Percentages of Cases in Each Borough
    fig, ax = plt.subplots()
    x_axis = borough_caseCount.index
    y_axis = borough_caseCount.values
    explode = (0.1, 0, 0, 0, 0)
    ax.pie(y_axis, labels=x_axis, autopct='%.2f%%', explode=explode, shadow=True, startangle=90)
    plt.title("Percentages of Cases in Each Borough")
    another_cols[0].pyplot(fig)
    another_cols[0].write("Most crashes happened in Brooklyn.")

    # 3D Pydeck Chart to display case density
    location = df.iloc[:, 5:7].dropna()
    layer = pdk.Layer("ScatterplotLayer", data=location, get_position=["LONGITUDE", "LATITUDE"],
                      auto_highlight=True, get_radius=100, get_fill_color=[252, 92, 18], pickable=False)
    view_state = pdk.ViewState(latitude=40.730610, longitude=-73.935242,
                               zoom=8, min_zoom=5, max_zoom=30)
    another_cols[1].pydeck_chart(pdk.Deck(initial_view_state=view_state, layers=[layer]))

def details():
    df = read_file()
    df.rename(columns={'LATITUDE':'lat', 'LONGITUDE':'lon'}, inplace=True)
    df["YEAR"] = pd.to_datetime(df['DATE'], format='%m/%d/%y').dt.year
    # Find unique values for each filter, sort & put into list
    year_list = ['Choose:'] + list(np.sort(df["YEAR"].unique()))
    y_filter = st.sidebar.selectbox("filter - Year", year_list)

    borough_list = ['Choose:'] + list(df["BOROUGH"].unique())
    del borough_list[2]
    b_filter = st.sidebar.selectbox("filter - Borough", borough_list)

    injuredType_list = ["Choose:", "Persons Injured", "Persons Killed"]
    it_filter = st.sidebar.selectbox("filter - Injured Type", injuredType_list)

    # Filter & display filtered data
    filter_data = df.iloc[:, :]
    if y_filter != "Choose:":
        filter_data = filter_data[filter_data["YEAR"] == y_filter]
    if b_filter != "Choose:":
        filter_data = filter_data[filter_data["BOROUGH"] == b_filter]
    if it_filter == "Persons Injured":
        filter_data = filter_data[filter_data["PERSONS INJURED"] == 1]
    if it_filter == "Persons Killed":
        filter_data = filter_data[filter_data["PERSONS KILLED"] == 1]

    st.write(f"After filtered, there are {len(filter_data)} matches found.")
    st.dataframe(filter_data)
    st.subheader("See Filtered Data on Map")
    st.map(filter_data[['lat', 'lon']].dropna())

def search():
    df = read_file()
    zip_search = st.text_input("Please enter the zipcode you want to search:")
    zip_list = list(df["ZIP CODE"].unique())
    del zip_list[1]
    if zip_search == "":
        st.write("Zipcode List:", zip_list)
    else:
        zip_search = int(zip_search)
        searched_data = df.groupby(["ZIP CODE"]).get_group(zip_search)
        st.dataframe(searched_data)
        st.write(f"Based on your search, there are {len(searched_data)} matches found")
    # Clickable text link to the original dataset
    st.markdown("To explore more on the original dataset: [Click Here](https://www.kaggle.com/nypd/vehicle-collisions)")

def main():
    df = read_file()
    # Center the title image
    col1, col2, col3 = st.beta_columns([1, 3, 1])
    with col2:
        st.image("title.jpg")
    # Use expander as page navigation
    nav = st.beta_expander("Page Navigation")
    nav.text(MENU)
    selection = nav.selectbox("Please select the page you want to go:", MENU_Options)

    if selection == "Main Page":
        glance()
    if selection == "Details":
        details()
    if selection == "Search By Zipcode":
        search()

main()
