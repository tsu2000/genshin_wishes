import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import altair as alt

import requests
import random
import io

from pity_probs import char_roll_5star, char_roll_4star, weap_roll_5star, weap_roll_4star
from collections import Counter
from streamlit_extras.badges import badge
from altair.vegalite.v4.api import LayerChart
from typing import Dict, Tuple
from PIL import Image


def main():
    col1, col2, col3 = st.columns([0.045, 0.28, 0.015])
    
    with col1:
        url = 'https://github.com/tsu2000/genshin_wishes/raw/main/images/simulation_2.png'
        response = requests.get(url)
        img = Image.open(io.BytesIO(response.content))
        st.image(img, output_format = 'png')

    with col2:
        st.title('Genshin Gacha Simulation')

    with col3:
        badge(type = 'github', name = 'tsu2000/genshin_wishes', url = 'https://github.com/tsu2000/genshin_wishes')

    st.markdown('### 🦾 &nbsp; Combined 3★/4★/5★ drop rate simulation')

    st.markdown('This web app simulates the **combined** drop rates of 4★ and 5★ characters/weapons and resulting 3★ drops in Genshin Impact according to theoretical data. Note that 5★ drops override 4★ drops in this simulation, even if the 4★ pity is at guaranteed. For individual 4★ and 5★ probabilities, view the other probability simulation page. **Note:** Entering a large number of wishes in user input results in exponentially slower loading times.')

    st.markdown('---')

    st.markdown('### User inputs:')    

    banner_select = st.selectbox('Choose a banner:', ['Character Event/Standard Banner', 'Weapon Event Banner'])
    bt = 'character' if banner_select == 'Character Event/Standard Banner' else 'weapon'

    col1, col2, col3 = st.columns(3)
    max_pity_5star = 90 if bt == 'character' else 77
    max_pity_4star = 10 if bt == 'character' else 9
    with col1:
        wishes_count = st.number_input('Enter number of wishes you have:', value = 100, min_value = 1, max_value = 10000)
    with col2:
        pity_count_5star =  st.number_input('Enter current 5★ pity you are at:', value = 1, min_value = 1, max_value = max_pity_5star)
    with col3:
        pity_count_4star =  st.number_input('Enter current 4★ pity you are at:', value = 1, min_value = 1, max_value = max_pity_4star)
    num_simulations = st.slider('Select number of iterations for the simulation:', value = 10000, min_value = 100, max_value = 100000)

    final_sim = combined_freq_graph(n_iter = num_simulations, pity_4 = pity_count_4star, pity_5 = pity_count_5star, banner_type = bt, num_wishes = wishes_count)

    st.markdown(f'### Wish distribution - {banner_select}')
    st.altair_chart(final_sim[0], use_container_width = True)

    st.markdown('### DataFrame Results:')
    st.dataframe(final_sim[1], use_container_width = True)

    st.markdown('### Comprehensive summary statistics for all rarity drops:')

    def describe_rarity(star):
        df = final_sim[1][[star, 'Count']]
        result = pd.Series([x for index, row in df.iterrows() for x in [row[star]] * row['Count']])

        summary = result.describe().to_dict()

        # Find median and mode
        mode = result.mode().values[0]

        # Add median and mode to summary statistics
        summary.update({'mode': mode})
        summary_stats = pd.Series(summary).to_frame().rename(columns = {0: star})

        return summary_stats

    df = pd.concat([describe_rarity('3★'), describe_rarity('4★'), describe_rarity('5★')], axis = 1).T

    st.plotly_chart(summary_table(df), use_container_width = True)

    st.markdown('---')


def simulate_rolls(prob_4: Dict[int, float], prob_5: Dict[int, float], pity_4: int, pity_5: int, num_rolls: int) -> Tuple[int, int, int]:
    '''
    
    A function that simulates the number of 3★, 4★ and 5★ drops obtained from a specified number of gacha rolls.

    Args:
        prob_4 (Dict[int, float]): A dictionary of probabilities of 4★ items with the key being the nth pull after the previous 4★ drop and value being the probability of a 4★ drop at the nth pull.
        prob_5 (Dict[int, float]): A dictionary of probabilities of 5★ items with the key being the nth pull after the previous 5★ drop and value being the probability of a 5★ drop at the nth pull.
        pity_4 (int): The user's current number of pulls since the last 4★ drop. 
        pity_5 (int): The user's current number of pulls since the last 5★ drop. 
        num_rolls: The specified number of gacha rolls as provided by the user.

    Returns:
        Tuple[int, int, int]: A tuple consisting of the number of 3★, 4★ and 5★ drops obtained from the simulation, respectively in order.
    '''

    item3_count, item4_count, item5_count = 0, 0, 0

    for i in range(num_rolls):

        randomVal = random.random()

        if randomVal < prob_5[pity_5]:
            item5_count += 1
            pity_5 = 1

        elif randomVal < prob_4[pity_4]:
            item4_count += 1
            pity_4 = 1

        else:
            pity_4 += 1
            pity_5 += 1
            item3_count += 1
            
    return item3_count, item4_count, item5_count


def simulation(num_iter: int, banner_type: str, start_pity_4: int, start_pity_5: int, wish_count: int) -> pd.DataFrame:

    if banner_type == 'character':
        prob_4, prob_5 = char_roll_4star, char_roll_5star
        
    elif banner_type == 'weapon':
        prob_4, prob_5 = weap_roll_4star, weap_roll_5star

    char_sim = [simulate_rolls(prob_4, prob_5, start_pity_4, start_pity_5, wish_count) for j in range(num_iter)]

    data_list = [(f'{str(k[0])}/{str(k[1])}/{str(k[2])}', k[0], k[1], k[2], v) for k, v in Counter(char_sim).items()]

    df = pd.DataFrame(data_list, columns = ['3★/4★/5★', '3★', '4★', '5★', 'Count'])
    df['Prob'] = df['Count'] / df['Count'].sum()

    return df


def combined_freq_graph(n_iter: int, pity_4: int, pity_5: int, banner_type: str, num_wishes: int) -> LayerChart:
    '''
    A function that simulates the number of 3★, 4★ and 5★ drops obtained from a specified number of gacha rolls.

    Args:
        n_iter (int): The specified number of iterations for the simulation to run.
        pity_4 (int): The user's current number of pulls since the last 4★ drop. Cannot be higher than the number of rolls for a guaranteed drop.
        pity_5 (int): The user's current number of pulls since the last 5★ drop. Cannot be higher than the number of rolls for a guaranteed drop.
        banner_type (str): The type of banner which determines its respective probability distribution. 'character' for Character Event/Standard Banner and 'weapon' for Weapon Event Banner.
        num_wishes (int): The number of wishes a player currently plans to simulate the odds for.

    Returns:
        LayerChart: An altair object which is basically a bar graph showing the frequency rate of outputs totalling the number of specified iterations.
    '''

    source = simulation(n_iter, banner_type, pity_4, pity_5, num_wishes)

    bars = alt.Chart(source).mark_bar().encode(
        x = 'Count',
        y = alt.Y('3★/4★/5★', sort = alt.EncodingSortField('Count', op='sum', order='descending')),
        tooltip = [alt.Tooltip('Count', format = 'd'), 
                alt.Tooltip('Prob', format = '.2%')],
        color = alt.Color('Prob', scale = alt.Scale(scheme = 'blues'), legend = None)
    ).properties(
        title = f"Number of 3★/4★/5★ drops with {source.loc[0][['3★', '4★', '5★']].sum()} wishes - (Simulation of n = {source['Count'].sum()})"
    )

    text = bars.mark_text(
        align = 'center',
        baseline = 'middle',
        dx = 15
    ).encode(
        text = alt.Text('Count', format = 'd')
    )

    chart = (bars + text).configure_title(
        fontSize = 15,
        offset = 15,
        anchor = 'middle'
    ).configure_axisY(
        titlePadding = 20,
    ).configure_axisX(
        titlePadding = 20
    )

    # Show the chart
    return chart, source


def summary_table(data: pd.DataFrame):
    fig = go.Figure(data = [go.Table(columnwidth = [2, 1.75],
                            header = dict(values = ['Rarity', 'Count', 'Mean', 'Std Dev', 'Min', '25%', 'Median', '75%', 'Max', 'Mode'],
                                            fill_color = ['maroon', 'navy'],
                                            line_color = 'black',
                                            font = dict(color = 'white', size = 14),
                                            height = 27.5),
                            cells = dict(values = [data.index, data['count'], round(data['mean'], 4), round(data['std'], 4), data['min'], data['25%'], data['50%'], data['75%'], data['max'], data['mode']], 
                                        fill_color = ['mistyrose', 'gainsboro'],
                                        line_color = 'black',
                                        align = ['center', 'right'],
                                        font = dict(color = 'black', size = 14),
                                        height = 27.5))])
    fig.update_layout(height = 120, width = 700, margin = dict(l = 5, r = 5, t = 5, b = 5))
    return fig


if __name__ == "__main__":
    st.set_page_config(page_title = 'Genshin Wish Stats', page_icon = '🦾')
    main()
