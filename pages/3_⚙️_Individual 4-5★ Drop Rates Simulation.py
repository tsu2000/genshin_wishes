import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import altair as alt

import requests
import random
import io

from ..pity_probs import char_roll_5star, char_roll_4star, weap_roll_5star, weap_roll_4star
from streamlit_extras.badges import badge
from altair.vegalite.v4.api import LayerChart
from typing import Dict, Tuple, Any
from PIL import Image


def main():
    col1, col2, col3 = st.columns([0.045, 0.28, 0.015])
    
    with col1:
        url = 'https://github.com/tsu2000/genshin_wishes/raw/main/images/simulation_1.png'
        response = requests.get(url)
        img = Image.open(io.BytesIO(response.content))
        st.image(img, output_format = 'png')

    with col2:
        st.title('Genshin Gacha Simulation')

    with col3:
        badge(type = 'github', name = 'tsu2000/genshin_wishes', url = 'https://github.com/tsu2000/genshin_wishes')

    st.markdown('### ⚙️ &nbsp; Individual 5★ & 4★ drop rate simulation')

    st.markdown('This web app simulates the separate drop rates of 4★ and 5★ characters/weapons in Genshin Impact, according to theoretical data. Note that drop rates for 4★ items may be considered (4★ or better) in this simulation. For combined probabilities, view the other probability simulation page.')

    topics = ['5★ Drop Rate Simulation', 
              '4★ Drop Rate Simulation']

    topic = st.selectbox('Select the respective simulation:', topics)

    st.markdown('---')

    if topic == topics[0]:
        simulation_5star()
    elif topic == topics[1]:
        simulation_4star()

    
def simulation_5star():
    st.markdown('## 5★ Drop Rate Simulation')

    st.markdown('### User inputs:')

    banner_select = st.selectbox('Choose a banner:', ['Character Event/Standard Banner', 'Weapon Event Banner'])
    bt = 'character' if banner_select == 'Character Event/Standard Banner' else 'weapon'

    col1, col2 = st.columns(2)
    max_pity = 90 if bt == 'character' else 77
    with col1:
        wishes_count = st.number_input('Enter number of wishes you have:', value = 100, min_value = 1, max_value = 100000)
    with col2:
        pity_count = st.number_input('Enter current 5★ pity you are at:', value = 1, min_value = 1, max_value = max_pity)

    num_simulations = st.slider('Select number of iterations for the simulation:', value = 10000, min_value = 100, max_value = 100000)

    result = wish_simulation5(num_tries = wishes_count, pity = pity_count, n_iter = num_simulations, banner_type = bt)
        
    st.markdown('### Summary statistics') 
    st.plotly_chart(result[0], use_container_width= True)

    st.markdown(f'### Wish distribution - {{banner_select}}')
    freq_graph(result[1], wishes_count, pity_count)

    st.markdown('---')


def simulation_4star():
    st.markdown('## 4★ Drop Rate Simulation')

    st.markdown('### User inputs:')

    banner_select = st.selectbox('Choose a banner:', ['Character Event/Standard Banner', 'Weapon Event Banner'])
    bt = 'character' if banner_select == 'Character Event/Standard Banner' else 'weapon'

    col1, col2 = st.columns(2)
    max_pity = 10 if bt == 'character' else 9
    with col1:
        wishes_count = st.number_input('Enter number of wishes you have:', value = 100, min_value = 1, max_value = 100000)
    with col2:
        pity_count = st.number_input('Enter current 4★ pity you are at:', value = 1, min_value = 1, max_value = max_pity)

    num_simulations = st.slider('Select number of iterations for the simulation:', value = 10000, min_value = 100, max_value = 100000)

    result = wish_simulation4(num_tries = wishes_count, pity = pity_count, n_iter = num_simulations, banner_type = bt)
        
    st.markdown('### Summary statistics') 
    st.plotly_chart(result[0], use_container_width= True)

    st.markdown(f'### Wish distribution - {{banner_select}}')
    freq_graph(result[1], wishes_count, pity_count)

    st.markdown('---')


def get_item_count(num_tries: int, pity: int, prob_dict: Dict[int, float]) -> int:
    count = 0
    for i in range(num_tries):
        rand_val = random.random()
        if rand_val < prob_dict[pity]:
            count += 1
            pity = 1
        else:
            pity += 1

    return count


# Obtain summary statistics + mode:
def summary_statistics(array: pd.Series):
    summary = array.describe().to_dict()

    # Find median and mode
    mode = array.mode().values[0]

    # Add median and mode to summary statistics
    summary.update({'mode': mode})
    summary_stats = pd.Series(summary).to_frame().rename(columns = {0: 'Statistic'})

    ds = summary_stats.T

    fig = go.Figure(data = [go.Table(columnwidth = [2, 1.75],
                            header = dict(values = ['Count', 'Mean', 'Std Dev', 'Min', '25%', 'Median', '75%', 'Max', 'Mode'],
                                            fill_color = 'navy',
                                            line_color = 'black',
                                            font = dict(color = 'white', size = 14),
                                            height = 27.5),
                            cells = dict(values = [ds['count'], round(ds['mean'], 4), round(ds['std'], 4), ds['min'], ds['25%'], ds['50%'], ds['75%'], ds['max'], ds['mode']], 
                                        fill_color = 'gainsboro',
                                        line_color = 'black',
                                        align = 'right',
                                        font = dict(color = 'black', size = 14),
                                        height = 27.5))])
    fig.update_layout(height = 80, width = 700, margin = dict(l = 5, r = 5, t = 5, b = 5))
    return fig


def wish_simulation5(num_tries: int, pity: int, n_iter: int, banner_type: str) -> Tuple[Any, pd.DataFrame]:    
    if banner_type == 'weapon':
        arr5 = pd.Series([get_item_count(num_tries, pity, weap_roll_5star) for j in range(n_iter)])
        
    elif banner_type == 'character':
        arr5 = pd.Series([get_item_count(num_tries, pity, char_roll_5star) for j in range(n_iter)])

    ds5 = arr5.value_counts().keys()
    ds_v5 = arr5.value_counts()
    ds_p5 = arr5.value_counts(normalize = True)

    df5 = pd.DataFrame(data = {
        'Num_5★_pulls': ds5,
        'Count': ds_v5,
        'Proportion': ds_p5
    })

    return summary_statistics(arr5), df5.sort_index(axis = 0)
    

def wish_simulation4(num_tries: int, pity: int, n_iter: int, banner_type: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
    if banner_type == 'weapon':
        arr4 = pd.Series([get_item_count(num_tries, pity, weap_roll_4star) for j in range(n_iter)])
        
    elif banner_type == 'character':
        arr4 = pd.Series([get_item_count(num_tries, pity, char_roll_4star) for j in range(n_iter)])

    ds4 = arr4.value_counts().keys()
    ds_v4 = arr4.value_counts()
    ds_p4 = arr4.value_counts(normalize = True)

    df4 = pd.DataFrame(data = {
        'Num_4★_pulls': ds4,
        'Count': ds_v4,
        'Proportion': ds_p4
    })

    return summary_statistics(arr4), df4.sort_index(axis = 0)


def freq_graph(wish_data, num_wishes, pity) -> LayerChart:
    '''
    A function that simulates the number of 4★ or 5★ drops obtained from a specified number of gacha rolls.

    Args:
        num_wishes (int): The number of wishes a player currently plans to simulate the odds for.
        pity (int): The user's current number of pulls since the last 4★ or 5★ drop. Cannot be higher than the number of rolls for a guaranteed drop.
        n_iter (int): The specified number of iterations for the simulation to run.
        banner_type (str): The type of banner which determines its respective probability distribution. 'character' for Character Event/Standard Banner and 'weapon' for Weapon Event Banner.
        star (int): The rarity of the item drop in question.

    Returns:
        LayerChart: An altair object which is basically a bar graph showing the frequency rate of outputs totalling the number of specified iterations.
    '''

    # Obtain data from wish simulation:
    data = wish_data
    star = int(data.columns[0][4])

    # Create the Altair chart
    bars = alt.Chart(data).mark_bar().encode(
        x = 'Count',
        y = alt.Y(f'{data.columns[0]}:N', scale = alt.Scale(type = 'band')),
        tooltip = [alt.Tooltip('Count', format = 'd'), 
                alt.Tooltip('Proportion', format = '.2%')],
        color = alt.Color('Count', scale = alt.Scale(scheme = 'teals'), legend = None)
    ).properties(
        title = f"Number of {'4★ (or better)' if star == 4 else '5★'} items pulled with {num_wishes} wishes at {pity} [{star}★] pity (Simulation of n = {data['Count'].sum()})",
        width = 700
    )

    text = bars.mark_text(
        align = 'left',
        baseline = 'middle',
        dx = 15,
        fontSize = 14
    ).encode(
        text = alt.Text('Count'),
    )

    return st.altair_chart((bars + text).configure_title(
        fontSize = 15,
        offset = 15
    ).configure_axisY(
        titlePadding = 20,
    ).configure_axisX(
        titlePadding = 20
    ).configure_title(
            fontSize = 15,
            offset = 15,
            anchor = 'middle'
    ))

if __name__ == "__main__":
    st.set_page_config(page_title = 'Genshin Wish Stats', page_icon = '⚙️')
    main()
