import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

#PANDAS WORK
df = pd.read_csv('data/crossword.csv')  # read in data
recent_week = df.tail(1)['Week'].item()  # save recent week as string
df['Week'] = pd.to_datetime(df['Week'])  # set field as datetime
#indicator for solving after Thurs
df['late_week'] = (
    (df.Thursday == 1) | (df.Friday == 1) | (df.Saturday) | (df.Sunday)
).astype(int) 

#chart of total stats by day of week
days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday',
        'Friday', 'Saturday', 'Sunday', 'late_week']

df_totals = df[days].describe().T[['count', 'mean']]
df_totals['total correct'] = (df_totals['count'] * df_totals['mean']).astype(int)

df_totals = df_totals[['total correct', 'mean']]
df_totals = df_totals.rename(columns={'mean': 'percent correct'})

#get cumulative totals and running average
df_cumul = df[['WeekNum','Week']].copy()
df_cumul[days] = df[days].cumsum()

df_running_avg = df_cumul[['WeekNum', 'Week']].copy()
for d in days:
    df_running_avg[d] = df_cumul[d]/df_cumul['WeekNum']

#get rolling averages
df_20 = df[days].rolling(20).mean()
df_52 = df[days].rolling(52).mean()

#make 20 week rolling average into a dataframe to compare current week to week - 20
df_L20 = df_20.iloc[[df_20.shape[0]-21, df_20.shape[0]-1]].T
df_L20['L20'] = df_L20[df_20.shape[0]-1]
df_L20['Comp'] = df_L20[df_20.shape[0]-21]
df_L20['percent_diff'] = df_L20['L20']/df_L20['Comp'] - 1

#get active streaks
streak_dict = {}
for day in df.columns[2:]:
    df_temp = pd.DataFrame()
    df_temp['Current'] = df[day]
    df_temp['shifted'] = df[day].shift(1)
    df_temp['StartStreak'] = df_temp['Current'] != df_temp['shifted']
    df_temp['StreakId'] = df_temp['StartStreak'].cumsum()
    
    if df_temp['Current'][df.shape[0]-1] == 1: #if streak is active
        streak_dict[day] = df_temp[df_temp['StreakId'] == df_temp['StreakId'].max()].shape[0]

    elif df_temp['Current'][df.shape[0]-1] == 0: #if streak is inactive
        streak_dict[day] = 0
    else:
        print('Error')

#STREAMLIT WORK
st.title('Crossword Stats')
st.write('Check out my progress on the NY Times Crossword Puzzle!')
st.write('Note: I have decided to stop updating the data. Consider these my final stats!')

cols = st.columns(2)
with cols[0]:
    st.metric('Total Weeks Tracked', df.shape[0])
with cols[1]:
    st.metric('Most Recent Week', recent_week)

st.table(round(df_totals[['total correct']].T, 2))
st.table(round(df_totals[['percent correct']].T, 2))
        
st.header('20 Week Moving Averages')       
cols = st.columns(4) 
for i in range(4):
    with cols[i]:
        st.metric(
            days[i], f"{df_L20.iloc[i]['L20']:.0%}", f"{df_L20.iloc[i]['percent_diff']:.0%}"
        )
cols = st.columns(4) 
for i in range(4):
    with cols[i]:
        st.metric(
            days[i+4], f"{df_L20.iloc[i+4]['L20']:.0%}", f"{df_L20.iloc[i+4]['percent_diff']:.0%}"
        )
        

st.header('Trends Over Time')
day = st.selectbox('Pick Weekday', days)

fig, ax = plt.subplots()
ax.plot(df.Week, df_running_avg[day], label='Running Average')
ax.plot(df.Week, df_20[day], label='L20 Average')
ax.plot(df.Week, df_52[day], label='L52 Average')
ax.set_ylim(0, 1.1)
ax.legend(loc='best', prop={'size': 6})
plt.xticks(rotation=90)

st.pyplot(fig)

st.header('Active Streaks')
cols = st.columns(4) 
for i in range(4):
    with cols[i]:
        st.metric(days[i], streak_dict[days[i]])
cols = st.columns(4) 
for i in range(4):
    with cols[i]:
        st.metric(days[i+4], streak_dict[days[i+4]])
