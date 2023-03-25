import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import requests
import io

from ..pity_probs import char_roll_5star, weap_roll_5star
from streamlit_extras.badges import badge
from collections import deque
from scipy.stats import binom, geom
from PIL import Image


# Main title
def main(): 
    col1, col2, col3 = st.columns([0.045, 0.28, 0.015])
    
    with col1:
        url = 'https://github.com/tsu2000/genshin_wishes/raw/main/images/gacha.png'
        response = requests.get(url)
        img = Image.open(io.BytesIO(response.content))
        st.image(img, output_format = 'png')

    with col2:
        st.title('Genshin Impact 5★ Chances')

    with col3:
        badge(type = 'github', name = 'tsu2000/genshin_wishes', url = 'https://github.com/tsu2000/genshin_wishes')
    
    st.markdown('### 🎲 &nbsp; Statistics of 5★ Drop Rates in Genshin Impact')
    
    st.markdown('This web app is for the theoretical data visualisation of the drop rates of a 5★ Character or Weapon in Genshin Impact made using the *matplotlib* library in Python. To observe and interact with the data visualisations, please select a banner from the box below.')

    topics = ['5★ Drop Rate for Permanent/Chararacter Event Banners', 
              '5★ Drop Rate for Weapon Event Banners',
              'About']

    topic = st.selectbox('Select a banner: ', topics)

    st.markdown('---')

    if topic == topics[0]:
        pceb()
    elif topic == topics[1]:
        web()
    elif topic == topics[2]:
        about()


# Permanent/Character Event Banner    
def pceb(): 
    st.markdown('### Permanent/Character Event Banner Statistics:')
    st.markdown('The probabilities for obtaining a 5★ Character (in number of pulls after pity reset) are as follows: ')
    st.markdown('- **Base Rate:** Before **74** pulls - *Low chance (<1%)*')
    st.markdown('- **Soft Pity:** From **74** pulls to **89** pulls - *Chance increases exponentially*')
    st.markdown('- **Hard Pity:** Your **90**th Pull - *Guaranteed 5★*')

    st.markdown('&nbsp;')
    
    st.markdown('What each graph means:')
    st.markdown('- **Base Pull Rate:** The base per-pull probability of obtaining a 5★ Character on each individual pull after pity reset')
    st.markdown('- **Cumulative Probability (CDF):** The **cumulative** probability of obtaining a 5★ Character on your current pull or before that')
    st.markdown('- **Distribution of Successful Pulls (PMF):** Where 5★ Character drops are most likely to occur between the pity reset and hard pity')

    st.markdown('---')
    
    roll_dict = char_roll_5star
    
    # Calculating cumulative probabilities
    @st.cache_data
    def prob_mul(n):
        if n == 75:
            return (1 - roll_dict[74])
        else:
            return (1 - roll_dict[n - 1]) * prob_mul(n - 1) 
    
    prob_75to89 = [binom.cdf(0, 73, 0.006) * prob_mul(x) * roll_dict[x] for x in range(75, 90)]
    prob_75to89 = np.cumsum(prob_75to89) + geom.cdf(73, 0.006) + binom.cdf(0, 73, 0.006) * roll_dict[74]
    prob_75to89_dict = {num: prob_75to89[num - 75] for num in range(75, 90)}

    @st.cache_data
    def roll_cum_probs(x):
        if x < 74:
            return geom.cdf(x, 0.006)

        elif x == 74:
            return geom.cdf(73, 0.006) + binom.cdf(0, 73, 0.006) * roll_dict[74]

        elif x >= 74 and x < 90:
            return prob_75to89_dict[x]

        else:
            return 1

    roll_cum_dict = {num: roll_cum_probs(num) for num in range(1, 91)}
    
    ### Calculating Distribution of Successful Pulls
    d = deque(roll_cum_dict.values())
    d.pop()
    d.appendleft(0)
    subd = np.array(d)
    cumd = np.array(list(roll_cum_dict.values()))
    succ_pull_probs = list(cumd - subd)
    succ_pull_dict = {num: succ_pull_probs[num - 1] for num in range(1, 91)}
    
    ### Defining plots
    def plot1():   
        #### PLOT 1 ####
        fig, ax = plt.subplots(figsize = (12, 6), dpi = 200)
        sns.set_style('whitegrid')

        ax = plt.plot(roll_dict.keys(), roll_dict.values(), color = 'blue')

        # Vertical line, point and text
        plt.axvline(xi, linestyle = '--', color = 'blue')
        plt.plot(xi, roll_dict[xi], marker = 'o', color = 'black')
        plt.text(xi - 7, roll_dict[xi] + 0.025, '{} pull(s)'.format(int(xi)), fontsize = 10, color = 'blue')

        # Text box
        rxi = round(roll_dict[xi], 8)
        textstr = "\n".join([r'Base Rate of obtaining a 5-star Character on Pull No. $\bf{%s}$:' % str(xi),
                             f'{rxi}' + ' (around ' + r"$\bf" + str(round(rxi * 100, 2)) + "\%}$" + ')'])
        props = dict(boxstyle = 'round', facecolor = 'lightcyan')
        plt.text(-1.25, 1, textstr, fontsize = 12, va = 'top', bbox = props)

        # Title, Axes Labels
        plt.title('Base Pull Rate of obtaining a 5-star Character at each pull after pity reset')
        plt.ylabel('Probability')
        plt.xlabel('Number of Pulls')

        plt.xticks(np.arange(0, 91, 10))
        return fig
        #################

    def plot2():    
        #### PLOT 2 ####
        fig, ax = plt.subplots(figsize = (12, 6), dpi = 200)
        sns.set_style('whitegrid')

        plt.plot(roll_cum_dict.keys(), roll_cum_dict.values(), color = 'red')

        # Vertical line, point and text
        plt.axvline(xc, linestyle = '--', color = 'red')
        plt.plot(xc, roll_cum_dict[xc], marker = 'o', color = 'black')
        plt.text(xc - 7, roll_cum_dict[xc] + 0.025, '{} pull(s)'.format(int(xc)), fontsize = 10, color = 'r')

        # Horizontal line (Median Probability)
        plt.text(-3, 0.52, 'Median (50% chance of obtaining a 5-star Character before/after horizontal line) ', fontsize = 10)
        plt.axhline(0.500, linestyle = ':', color = 'black')

        # Text box
        rxc = round(roll_cum_dict[xc], 8)
        textstr = "\n".join([r'Chance of obtaining a 5-star Character by $\bf{%s}$ pull(s) or less:' % str(xc),
                             f'{rxc}' + ' (around ' + r"$\bf" + str(round(rxc * 100, 2)) + "\%}$" + ')'])
        props = dict(boxstyle = 'round', facecolor = 'wheat')
        plt.text(-1.25, 1, textstr, fontsize = 12, va = 'top', bbox = props)

        plt.title(f'Cumulative Distribution Function (CDF) of obtaining an 5-star Character within {xc} number of pulls')
        plt.ylabel('Cumulative Probability of getting a 5-star Character', labelpad = 15)
        plt.xlabel('Cumulative Number of Pulls', labelpad = 10)

        plt.xticks(np.arange(0, 91, 10))
        return fig
        #################

    def plot3():   
        #### PLOT 3 ####
        fig, ax = plt.subplots(figsize = (12, 6), dpi = 200)
        sns.set_style('whitegrid')

        plt.plot(succ_pull_dict.keys(), succ_pull_dict.values(), color = 'green')

        # Vertical line, point and text
        plt.axvline(xs, linestyle = '--', color = 'green')
        plt.plot(xs, succ_pull_dict[xs], marker = 'o', color = 'black')
        plt.text(xs - 7, succ_pull_dict[xs] + 0.0025, '{} pull(s)'.format(int(xs)), fontsize = 10, color = 'green')

        # Text box
        rxs = round(succ_pull_dict[xs], 8)
        textstr = "\n".join([r'Actual Probability of successfully obtaining a 5-star Character on Pull No. $\bf{%s}$:' % str(xs),
                             f'{rxs}' + ' (around ' + r"$\bf" + str(round(rxs * 100, 2)) + "\%}$" + ')'])
        props = dict(boxstyle = 'round', facecolor = 'greenyellow')
        plt.text(-1.25, 0.105, textstr, fontsize = 12, va = 'top', bbox = props)

        # Title, Axes Labels
        plt.title('Distribution of Successful Pulls (Where 5-star Characters are pulled the most)')
        plt.ylabel('Probability of getting a 5-star Character', labelpad = 15)
        plt.xlabel('Number of Pulls', labelpad = 10)

        plt.xticks(np.arange(0, 91, 10))
        return fig
        #################
    
    ### Returning plots
    st.markdown('### Base Pull Rate')
    xi = st.slider('Choose number of pulls after your last 5★ Character to see the base probability rate of getting a 5★ character at each number of pulls at your current level:', 1, 90, 30)  
    st.pyplot(plot1())

    st.markdown('---')
    
    st.markdown('### Cumulative Probability')
    xc = st.slider('Choose number of pulls after your last 5★ Character to see the cumulative probability of getting a 5★ character within your set number of pulls:', 1, 90, 30)
    st.pyplot(plot2())

    st.markdown('---')
    
    st.markdown('### Distribution of Successful Pulls')
    xs = st.slider('Choose number of pulls after your last 5★ Character to see how likely you are to pull a 5★ character at your exact current pity:', 1, 90, 30)
    st.pyplot(plot3())
    
    st.markdown("---")


# Weapon Event Banner
def web(): 
    st.markdown('### Weapon Event Banner Statistics:')
    st.markdown('The probabilities for obtaining a 5★ Weapon (in number of pulls after pity reset) are as follows:')
  
    st.markdown('- **Base Rate:** Before **63** pulls - *Low chance (<1%)*')
    st.markdown('- **Soft Pity:** From **63** pulls to **76** pulls - *Chance increases exponentially*')
    st.markdown('- **Hard Pity:** Your **77**th Pull - *Guaranteed 5★*')

    st.markdown('&nbsp;')
    
    st.markdown('What each graph means:')
    st.markdown('- **Base Pull Rate:** The base per-pull probability of obtaining a 5★ Weapon on each individual pull after pity reset')
    st.markdown('- **Cumulative Probability (CDF):** The **cumulative probability** of obtaining a 5★ Weapon on your current pull or before that')
    st.markdown('- **Distribution of Successful Pulls (PMF):** Where 5★ Weapon drops are most likely to occur between the pity reset and hard pity')
    
    st.markdown('---')
    
    roll_dict = weap_roll_5star
    
    # Calculating cumulative probabilities
    @st.cache_data
    def prob_mul(n):
        if n == 64:
            return (1 - roll_dict[63])
        else:
            return (1 - roll_dict[n - 1]) * prob_mul(n - 1) 
    
    prob_64to76 = [binom.cdf(0, 62, 0.007) * prob_mul(x) * roll_dict[x] for x in range(64, 77)]
    prob_64to76 = np.cumsum(prob_64to76) + geom.cdf(62, 0.007) + binom.cdf(0, 62, 0.007) * roll_dict[63]
    prob_64to76_dict = {num: prob_64to76[num - 64] for num in range(64, 77)}
    
    @st.cache_data
    def roll_cum_probs(x):
        if x < 63:
            return geom.cdf(x, 0.007)

        elif x == 63:
            return geom.cdf(62, 0.007) + binom.cdf(0, 62, 0.007) * roll_dict[63]

        elif x >= 64 and x < 77:
            return prob_64to76_dict[x]

        else:
            return 1

    roll_cum_dict = {num: roll_cum_probs(num) for num in range(1, 78)}
    
    ### Calculating Distribution of Successful Pulls  
    d = deque(roll_cum_dict.values())
    d.pop()
    d.appendleft(0)
    subd = np.array(d)
    cumd = np.array(list(roll_cum_dict.values()))
    succ_pull_probs = list(cumd - subd)
    succ_pull_dict = {num: succ_pull_probs[num - 1] for num in range(1, 78)}
    
    ### Defining plots
    def plot4():    
        #### PLOT 4 ####
        fig, ax = plt.subplots(figsize = (12, 6), dpi = 200)
        sns.set_style('whitegrid')

        ax = plt.plot(roll_dict.keys(), roll_dict.values(), color = 'blue')

        # Vertical line, point and text
        plt.axvline(xi, linestyle = '--', color = 'blue')
        plt.plot(xi, roll_dict[xi], marker = 'o', color = 'black')
        plt.text(xi - 7, roll_dict[xi] + 0.025, '({} pulls)'.format(int(xi)), fontsize = 10, color = 'blue')

        # Text box
        rxi = round(roll_dict[xi], 8)
        textstr = "\n".join([r'Base Rate of obtaining a 5-star Weapon on Pull No. $\bf{%s}$:' % str(xi),
                             f'{rxi}' + ' (around ' + r"$\bf" + str(round(rxi * 100, 2)) + "\%}$" + ')'])
        props = dict(boxstyle = 'round', facecolor = 'lightcyan')
        plt.text(-1.25, 1, textstr, fontsize = 12, va = 'top', bbox = props)

        # Title, Axes Labels
        plt.title('Base Pull Rate of obtaining a 5-star Weapon at each pull after pity reset')
        plt.ylabel('Probability')
        plt.xlabel('Number of Pulls')

        plt.xticks(np.arange(0, 81, 10))
        return fig
        #################

    def plot5():    
        #### PLOT 2 ####
        fig, ax = plt.subplots(figsize = (12, 6), dpi = 200)
        sns.set_style('whitegrid')

        plt.plot(roll_cum_dict.keys(), roll_cum_dict.values(), color = 'red')

        # Vertical line, point and text
        plt.axvline(xc, linestyle = '--', color = 'red')
        plt.plot(xc, roll_cum_dict[xc], marker = 'o', color = 'black')
        plt.text(xc - 7, roll_cum_dict[xc] + 0.025, '({} pulls)'.format(int(xc)), fontsize = 10, color = 'r')

        # Horizontal line (Median Probability)
        plt.text(-3, 0.52, 'Median (50% chance of obtaining a 5-star Weapon before/after horizontal line) ', fontsize = 10)
        plt.axhline(0.500, linestyle = ':', color = 'black')

        # Text box
        rxc = round(roll_cum_dict[xc], 8)
        textstr = "\n".join([r'Chance of obtaining a 5-star Weapon by $\bf{%s}$ pull(s) or less:' % str(xc),
                             f'{rxc}' + ' (around ' + r"$\bf" + str(round(rxc * 100, 2)) + "\%}$" + ')'])
        props = dict(boxstyle = 'round', facecolor = 'wheat')
        plt.text(-1.25, 1, textstr, fontsize = 12, va = 'top', bbox = props)

        plt.title(f'Cumulative Distribution Function (CDF) of obtaining an 5-star Weapon within {xc} number of pulls')
        plt.ylabel('Cumulative Probability of getting a 5-star Weapon', labelpad = 15)
        plt.xlabel('Cumulative Number of Pulls', labelpad = 10)

        plt.xticks(np.arange(0, 81, 10))
        return fig
        #################

    def plot6():    
        #### PLOT 6 ####
        fig, ax = plt.subplots(figsize = (12, 6), dpi = 200)
        sns.set_style('whitegrid')

        plt.plot(succ_pull_dict.keys(), succ_pull_dict.values(), color = 'green')

        # Vertical line, point and text
        plt.axvline(xs, linestyle = '--', color = 'green')
        plt.plot(xs, succ_pull_dict[xs], marker = 'o', color = 'black')
        plt.text(xs - 7, succ_pull_dict[xs] + 0.0025, '({} pulls)'.format(int(xs)), fontsize = 10, color = 'green')

        # Text box
        rxs = round(succ_pull_dict[xs], 8)
        textstr = "\n".join([r'Actual Probability of successfully obtaining a 5★ Weapon on Pull No. $\bf{%s}$:' % str(xs),
                             f'{rxs}' + ' (around ' + r"$\bf" + str(round(rxs * 100, 2)) + "\%}$" + ')'])
        props = dict(boxstyle = 'round', facecolor = 'greenyellow')
        plt.text(-1.25, 0.115, textstr, fontsize = 12, va = 'top', bbox = props)

        # Title, Axes Labels
        plt.title('Distribution of Successful Pulls (Where 5-star Weapons are pulled the most)')
        plt.ylabel('Probability of getting a 5-star Weapon', labelpad = 15)
        plt.xlabel('Number of Pulls', labelpad = 10)

        plt.xticks(np.arange(0, 81, 10))
        return fig
        #################
        
    ### Returning plots
    st.markdown('### Base Pull Rate')
    xi = st.slider('Choose number of pulls after your last 5★ Weapon to see the base probability rate of getting a 5★ Weapon at each number of pulls at your current level:', 1, 77, 25)
    st.pyplot(plot4())

    st.markdown('---')
    
    st.markdown('### Cumulative Probability')
    xc = st.slider('Choose number of pulls after your last 5★ Weapon to see the cumulative probability of getting a 5★ Weapon within your set number of pulls:', 1, 77, 25)
    st.pyplot(plot5())

    st.markdown('---')

    st.markdown('### Distribution of Successful Pulls')
    xs = st.slider('Choose number of pulls after your last 5★ Weapon to see how likely you are to pull a 5★ Weapon at your exact current pity:', 1, 77, 25)
    st.pyplot(plot6())

    st.markdown("---")


# About the app   
def about(): 
    st.markdown('### Resources used:')
    st.markdown('This web application builds on the statistical models from the following social media posts:')
    st.markdown("- [**Statistical model for Genshin Impact's droprates - Post on HoYoLAB Forums by Sengalev, original by Cgg**](https://www.hoyolab.com/article/497840)")
    st.markdown('This infographic post on **Reddit** provides a simplified overview of what this app aims to illustrate that may be easier to understand for some:')
    st.markdown("- [**Soft and hard pity explained based on 24M wishes - Post on r/Genshin_Impact by u/chaos-kaizer**](https://www.reddit.com/r/Genshin_Impact/comments/o9v0c0/soft_and_hard_pity_explained_based_on_24m_wishes)")
    st.markdown("### Visit Genshin-Wishes Main Website:")
    st.markdown("- [**Genshin Wishes Official Website**](https://genshin-wishes.com)")
    st.markdown("---")
    st.markdown('**Important Notice**: *This app is not affiliated with genshin-wishes.com or HoYoVerse. All technical details relating to current probability rates may be subject to change in the future.*')    


if __name__ == "__main__":
    st.set_page_config(page_title = 'Genshin Wish Stats', page_icon = '🎲')
    main()