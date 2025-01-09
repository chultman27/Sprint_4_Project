#import libraries
import streamlit as st
import plotly.express as px
import pandas as pd
from scipy import stats as st
import numpy as np
import altair as alt
import streamlit as st
import matplotlib as plt

#import data set 
uaps = pd.read_csv('ufo_sightings_scrubbed.csv', low_memory=False) 

#Write a header for the application
st.title('Sprint 4 Project: UFO/UAP Sighting Analysis')
st.header('Introduction')
st.write("""
    This project aims to creat a web application exploring some basic trends regarding global UFO sightings from 1910 to 2014. This data set was obtained from : https://mavenanalytics.io/

UFO (unidentified flying objects) or UAPs (unidentified aerial phenomena) as the are now called are terms used to describe "any apparent object in the sky that can’t be identified and classified as an object or phenomenon already known" (Petrescu, 1). While some of these can be accredited to phenomena such as weather balloons or aircrafts, others are harder to explain by conventional means. These sightings are often linked to extraterrestrials and alien life. While this topic is controversial and discussion is widespread even throughout the United States government, data does exist to support the existence of UAPs and patterns in the experiences seen. 

This study aims to:
Identify potential patterns in UAP sightings such as:
1. Places with high numbers of sightings
2. Years/ times of the year when sightings are high
3. Patterns in sightings such as the types of crafts and duration of the sightings

For the purposes of this study, we will be limiting our research to the United States (Washington D.C and Puerto Rico). We will also be using the term "UAP" moving forward as that is the current terminology used in government and media discussions.

While this information cannot prove that extraterrestrial life is behind these UAPs, understanding patterns behind them could help the public stay more vigilant and help our government know how best to monitor and study such phenomena in the future.!
""")
##Clean Data
#make all the writing lower case to avoid confusion
def convert_to_lower(df):
    for column in df.columns:
        if df[column].dtype == 'object':
            if df[column].str.contains('[A-Z]').any():
                df[column] = df[column].str.lower()
    return df
uaps = convert_to_lower(uaps)

#remove all rows that are not in the USA
print(uaps['country'].unique())
uaps_us = uaps[uaps['country'] == 'us']

#check for duplicates and drop any if they exist
dup_uaps_us = uaps_us[uaps_us.duplicated()]
uaps_us = uaps_us.drop_duplicates().reset_index()

#fix data types
#change the date/time to date time
uaps_us['datetime'] = pd.to_datetime(uaps_us['datetime'], format='%Y-%m-%d %H:%M:%S')
# change the duration in seconds to a float type
uaps_us['duration (seconds)'] = pd.to_numeric(uaps_us['duration (seconds)'], errors='coerce')

#check for missing values
#dropping missing values in 'shape' column. Only looking at sightings that have a shape category to simplify, as there already is an 'unknown' column. Do not want to lump those two together
uaps_us = uaps_us.dropna(subset=['shape'])
#missing values in 'comments' column
uaps_us['comments']= uaps_us['comments'].fillna('no_comment')

#Question 1 info
st.header('Which State Reported the Highest number of UAP sightings from 1910-2014?')

#group the rows by state and count the number of rows
uaps_state_group = uaps_us.groupby('state').size().reset_index(name='count')
#sort results in descending order
uaps_state_group = uaps_state_group.sort_values(by='count', ascending=False)
#create a graphic describing the distribution of sightings across states --> bar graph: discrete data
#create bargraph via plotly.express
fig_bar1 = px.bar(uaps_state_group, x='state', y='count', title='UAP Sightings per U.S State from 1910-2014')
fig_bar1.update_traces(marker_color='green')
fig_bar1.update_layout(
    xaxis_title='State (abbreviation)',
    yaxis_title='UAP Sighting Count',
    title_font=dict(family="Arial", size=24, color="black"),
    font=dict(family="Arial", size=14, color="black") )
#show figure in streamlit
st.plotly_chart(fig_bar1)

##Question 2 info
st.header('Which Year has the Highest Number of UAP Sightings?')

#which year was the number of sightings highest?
#create year column
uaps_us['year'] = uaps_us['datetime'].dt.year
#groupby by year and count which year is the highest 
uaps_year_group = uaps_us.groupby('year').size().reset_index(name='count')
#sort results in descending order
uaps_year_group = uaps_year_group.sort_values(by='count', ascending=False)

#making a histogram of data
#make sure df is sort chronologcally
uaps_year_group['year'] = pd.to_numeric(uaps_year_group['year'])
uaps_year_group = uaps_year_group.sort_values(by='year')

#histogram
uaps_years = px.histogram(uaps_year_group, 
                   x='year', 
                   y='count', 
                   histfunc='sum',  
                   title='UAP Sightings by Year',
                   labels={'year': 'Year', 'count': 'Number of Sightings'})  

#clean up histogram
uaps_years.update_traces(marker=dict(color='lightgreen', line=dict(width=2, color='black')))
uaps_years.update_layout(
    bargap=0.1,  
    xaxis_type='category',  
    xaxis_tickangle=-45  
)
#show figure in streamlit
st.plotly_chart(uaps_years)

st.write("""The range of years from this data set with the overall highest UAP sightings was from 2003-2013 (excluding 2006), with the peak number of sightings being in 2012. These are the top ten years with the highest number of sightings overall. It is interesting to note that 2014 was not the highest on this list, indicating some sort of drop in sightings at this point. How much of this trend is due to increased UAP activity or better methods of tracking and recording sightings is unclear.""")

#Question 2 info
st.header('How does the Length of Sightings (in seconds) Change Over Time?')

#remove rows without exact number of seconds for duration
print(uaps_us['duration (hours/min)'].unique())
#dont need values with "or less, or more,  -, so far, ~, over, +"
#While we are assuming that all of these are approximations due to the sources being eye witnesses, ones with a range or very general timeline will be excluded from this analyisis
import re  
#terms to exclude
terms_to_exclude = ["or less", "or more", "-", "so far", "~", "over", "+"]
#escape special characters in the terms using re.escape
escaped_terms = [re.escape(term) for term in terms_to_exclude]
#create a regular expression pattern to match any of the escaped terms
pattern = '|'.join(escaped_terms)
#filter the DataFrame by removing rows where the 'duration (hours/min)' contains any of the terms
uaps_us_cleaned = uaps_us[~uaps_us['duration (hours/min)'].str.contains(pattern, case=False, na=False)]

#create a scatterplot for the data

#removing outlier values to visualize the main trends
Q1 = uaps_us_cleaned['duration (seconds)'].quantile(0.25)
Q3 = uaps_us_cleaned['duration (seconds)'].quantile(0.75)
IQR = Q3 - Q1

# Define outlier bounds (1.5 times the IQR above Q3 or below Q1)
lower_bound = Q1 - 1.5 * IQR
upper_bound = Q3 + 1.5 * IQR

# Filter out the outliers
filtered_data = uaps_us_cleaned[(uaps_us_cleaned['duration (seconds)'] >= lower_bound) & 
                           (uaps_us_cleaned['duration (seconds)'] <= upper_bound)]

# Create the scatterplot with filtered data
fig = px.scatter(filtered_data, x='year', y='duration (seconds)', 
                 title='UAP Sightings Duration Over Time (Outliers Removed)',
                 labels={'year': 'Year', 'duration (seconds)': 'Duration (seconds)'})
st.plotly_chart(fig)

st.write("""There is no visible trend in the duration of a UAP sighting through time. """)

##write conclusion
st.header('Conclusion')
st.write("""
In the United States from 1910-1949, thousands of UAP cases were documented across the country. A majority of these cases were recorded in California and in the summer months of June-August. The most likely time to see a UAP is between 8-10 pm with sightings lasting anywhere between less than a second to multiple hours. There does not seem to be a trend in the duration of sightings through time.

I believe the largest potential issue in this data set is the reliance on eyewitness testimony. Data could be skewed given different recording methods, number of witnessess, time of recording, etc. However that does not mean it does not give valuable insight into where and when these UAPs will be seen in the future. Information from this study could help the U.S government and other researchers track potential movements, focus areas of UAP studies, and develop methods for efficient response time to unidentified aerial phenomena.
""")

