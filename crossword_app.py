import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

df = pd.read_csv('crossword.csv') #read in data
df['Week'] = pd.to_datetime(df['Week']) #set field as datetime
#indicator for solving after Thurs
df['late_week'] = ((df.Thursday == 1) | (df.Friday == 1) | (df.Saturday) | (df.Sunday)).astype(int) 

#chart of total stats by day of week
days = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday','late_week']

df_totals = df[days].describe().T[['count','mean']]
df_totals['correct'] = (df_totals['count'] * df_totals['mean']).astype(int)

df_totals = df_totals[['correct','mean']]


#get cumulative totals and running average
df_cumul = df[['WeekNum','Week']].copy()
df_cumul[days] = df.cumsum()[days]

df_running_avg = df_cumul[['WeekNum','Week']].copy()
for d in days:
    df_running_avg[d] = df_cumul[d]/df_cumul['WeekNum']

#get rolling averages
df_20 = df[days].rolling(20).mean()
df_52 = df[days].rolling(52).mean()


#STILL NEED TO ADD -- LAST 20 AVERAGES AND PCT CHANGES (MAYBE COMPARED TO THE PREVIOUS LAST 2 AVG?)
        
    
#make streamlit app
st.title('Crossword Stats')
st.write('Check out my NY Times Crossword Puzzle stats!')

st.header('Total Weeks')
st.metric('',df.shape[0])

st.header('Total Correct Puzzles')
cols = st.columns(len(days)) 
for i in range(len(days)):
    with cols[i]:
        st.metric(days[i],int(df_totals.iloc[i].correct))
        
st.header('Percetage Finished')
cols = st.columns(4) 
for i in range(4):
    with cols[i]:
        st.metric(days[i],"{:.0%}".format(df_totals.iloc[i]['mean']))
cols = st.columns(4) 
for i in range(4):
    with cols[i]:
        st.metric(days[i+4],"{:.0%}".format(df_totals.iloc[i+4]['mean']))
        

st.header('Trends Over Time')
day = st.selectbox('Pick Weekday',days)

fig, ax = plt.subplots()
ax.set_title(day+' Trends')
ax.plot(df.Week, df_running_avg[day], label='Running Average')
ax.plot(df.Week, df_20[day], label='L20 Average')
ax.plot(df.Week, df_52[day], label='L52 Average')
ax.set_ylim(0,1.1)
ax.legend(loc='best',prop={'size': 6})
plt.xticks(rotation=90)

st.pyplot(fig)
 
