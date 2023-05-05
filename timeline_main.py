import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from pandas import Timestamp

uploaded_file = st.file_uploader("Выберите XLSX файл", accept_multiple_files=False)
project_name = st.text_input("Установите название проекта")
if uploaded_file:
  data = pd.read_excel(uploaded_file)
    ##### DATA PREP ##### 
  df = pd.DataFrame(data)

  # project start date
  proj_start = df.Start.min()

  # number of days from project start to task start
  df['start_num'] = (df.Start-proj_start).dt.days

  # number of days from project start to end of tasks
  df['end_num'] = (df.End-proj_start).dt.days

  # days between start and end of each task
  df['days_start_to_end'] = df.end_num - df.start_num

  # days between start and current progression of each task
  df['current_num'] = (df.days_start_to_end * df.Completion)

  # create a column with the color for each department
  def color(row):
      c_dict = {'MKT':'#E64646', 'FIN':'#E69646', 'ENG':'#34D05C', 'PROD':'#34D0C3', 'IT':'#3475D0'}
      return c_dict[row['Department']]

  df['color'] = df.apply(color, axis=1)

  ##### PLOT #####
  fig, (ax, ax1) = plt.subplots(2, figsize=(16,6), gridspec_kw={'height_ratios':[6, 1]}, facecolor='#36454F')
  ax.set_facecolor('#36454F')
  ax1.set_facecolor('#36454F')
  # bars
  ax.barh(df.Task, df.current_num, left=df.start_num, color=df.color)
  ax.barh(df.Task, df.days_start_to_end, left=df.start_num, color=df.color, alpha=0.5)

  for idx, row in df.iterrows():
      ax.text(row.end_num+0.1, idx, f"{int(row.Completion*100)}%", va='center', alpha=0.8, color='w')
      ax.text(row.start_num-0.1, idx, row.Task, va='center', ha='right', alpha=0.8, color='w')


  # grid lines
  ax.set_axisbelow(True)
  ax.xaxis.grid(color='k', linestyle='dashed', alpha=0.4, which='both')

  # ticks
  xticks = np.arange(0, df.end_num.max()+1, 3)
  xticks_labels = pd.date_range(proj_start, end=df.End.max()).strftime("%m/%d")
  xticks_minor = np.arange(0, df.end_num.max()+1, 1)
  ax.set_xticks(xticks)
  ax.set_xticks(xticks_minor, minor=True)
  ax.set_xticklabels(xticks_labels[::3], color='w')
  ax.set_yticks([])

  plt.setp([ax.get_xticklines()], color='w')

  # align x axis
  ax.set_xlim(0, df.end_num.max())

  # remove spines
  ax.spines['right'].set_visible(False)
  ax.spines['left'].set_visible(False)
  ax.spines['left'].set_position(('outward', 10))
  ax.spines['top'].set_visible(False)
  ax.spines['bottom'].set_color('w')

  
  plt.suptitle(project_name, color='w')

  ##### LEGENDS #####
  legend_elements = [Patch(facecolor='#E64646', label='Marketing'),
                     Patch(facecolor='#E69646', label='Finance'),
                     Patch(facecolor='#34D05C', label='Engineering'),
                     Patch(facecolor='#34D0C3', label='Production'),
                     Patch(facecolor='#3475D0', label='IT')]

  legend = ax1.legend(handles=legend_elements, loc='upper center', ncol=5, frameon=False)
  plt.setp(legend.get_texts(), color='w')

  # clean second axis
  ax1.spines['right'].set_visible(False)
  ax1.spines['left'].set_visible(False)
  ax1.spines['top'].set_visible(False)
  ax1.spines['bottom'].set_visible(False)
  ax1.set_xticks([])
  ax1.set_yticks([])

  # Get "Today" value from sys date/ date.today()
  from datetime import date
  today = pd.Timestamp(date.today())
  today = today - proj_start

  # Get "Today" value from custom timestamp
  #today = Timestamp('2022-03-02 00:00:00') 
  #today = today - proj_start

  # plot line for today
  ax.axvline(today.days, color='w', lw=1, alpha=0.7)
  ax.text(today.days, len(df)+0.5, 'Today', ha='center', color='w')

  plt.savefig('gantt.png', facecolor='#36454F', dpi=1000)
  
  st.pyplot(plt)
