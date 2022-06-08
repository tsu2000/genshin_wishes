import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import collections

from collections import deque
from scipy.stats import binom
from scipy.stats import geom


def main(): # Main title
    st.title('Genshin Impact 5-Star Chances')
    subtitle = '### A statistical exploration of 5-Star Drop Rates in Genshin Impact'
    st.markdown(subtitle)
    
    st.markdown('This web app is for the data visualisation of the drop rates of a 5-Star Character or Weapon in the action role-playing game created by miHoYo, Genshin Impact. To observe and interact with the data visualisations, please select a banner from the box below.')

    topics = ['About',
              '5-Star Drop Rate for Permanent/Chararacter Event Banners', 
              '5-Star Drop Rate for Weapon Event Banners']

    topic = st.selectbox('Select a banner: ', topics)

    if topic == topics[0]:
        about()
    elif topic == topics[1]:
        pceb()
    elif topic == topics[2]:
        web()

        
        
        
@st.cache(allow_output_mutation = True)    
def about(): # About the app
    
    st.components.v1.html("""<a href="https://github.com/tsu2000/genshin_5star_chances" target="_blank"><img src="https://img.shields.io/static/v1?label=tsu2000&message=genshin_5star_chances
&color=blue&logo=github" alt="_blank"></a><a href="https://github.com/tsu2000/genshin_5star_chances" target="_blank"><img src="https://img.shields.io/github/stars/tsu2000/genshin_5star_chances?style=social" alt="tsu2000 - Genshin Impact 5-Star Chances"></a>""", height=28)

    st.markdown("---")
    st.markdown('### Resources used:')
    st.markdown('This web application was inspired by the following posts, and builds on the statistical models of the first post on the HoYoLAB Forums in particular.')
    st.markdown("- [**Statistical model for Genshin Impact's droprates - Post on HoYoLAB Forums by Sengalev, original by Cgg**](https://www.hoyolab.com/article/497840)")
    st.write('####')
    st.markdown('This infographic post on **Reddit** provides a simplified overview of what this app aims to illustrate that may be easier to understand for some:')
    st.markdown("- [**Soft and hard pity explained based on 24M wishes - Post on r/Genshin_Impact by u/chaos-kaizer**](https://www.reddit.com/r/Genshin_Impact/comments/o9v0c0/soft_and_hard_pity_explained_based_on_24m_wishes)")
    st.write('####')
    st.markdown("### Visit Original Source's Main Website:")
    st.markdown("- [**Genshin Wishes Official Website**](https://genshin-wishes.com) ")
    
    st.markdown("---")
                
    st.markdown('**Important Notice**: *This app is not affiliated with genshin-wishes.com or miHoYo. All technical details relating to current probability rates may be subject to change in the future. Genshin Impact and miHoYo are trademarks or registered trademarks of miHoYo. Genshin Impact © miHoYo.*')
    
    
    
    
    
    
    
def pceb(): # Permanent/Character Event Banner
    
    st.markdown('## Permanent/Character Event Banner Statistics:')
    st.markdown('The probabilities for obtaining a 5-Star Character (in number of pulls after pity reset) are as follows: ')
    st.markdown('- **Base Rate:** Before 74 pulls - *Low chance*')
    st.markdown('- **Soft Pity:** From 74 pulls to 89 pulls - *Chance increases exponentially*')
    st.markdown('- **Hard Pity:** 90th Pull - *Guaranteed 5-Star*')
    
    st.write("##")
    
    st.markdown('What each graph means:')
    st.markdown('- **Probability Mass Function (PMF):** The base per-pull probability of obtaining a 5-Star Character on each individual pull after pity reset')
    st.markdown('- **Cumulative Distribution Function (CDF):** The **cumulative** probability of obtaining a 5-Star Character on your current pull or before that')
    st.markdown('- **Distribution of Successful Pulls:** Where 5-Star Character drops are most likely to occur between the pity reset and hard pity')
    
    st.write("###")
    
    def roll_probs(x):
        if x < 74:
            return 0.006
        elif x >= 74 and x < 90:
            return round((x - 73) * 0.06 + 0.006, 3)
        else:
            return 1
    
    roll_dict = {num: roll_probs(num) for num in range(1, 91)}
    
    
    st.markdown('### Probability Mass Function (PMF)')
    xi = st.slider('Choose number of pulls after your last 5-Star Character to see the base probability rate of getting a 5-star character at each number of pulls at your current level:', 1, 90, 30)
    
 
    #### PLOT 1 ####
    fig, ax = plt.subplots(figsize = (12, 6), dpi = 200)
    plt.style.use('seaborn-whitegrid')
    
    ax = plt.plot(roll_dict.keys(), roll_dict.values(), color = 'blue')

    # Vertical line, point and text
    plt.axvline(xi, linestyle = '--', color = 'blue')
    plt.plot(xi, roll_dict[xi], marker = 'o', color = 'black')
    plt.text(xi - 7, roll_dict[xi] + 0.025, '{} pull(s)'.format(int(xi)), fontsize = 10, color = 'blue')

    # Text box
    rxi = round(roll_dict[xi], 8)
    textstr = "\n".join([r'Base Rate of obtaining a 5-Star Character on Pull No. $\bf{%s}$:' % str(xi),
                         f'{rxi}' + ' (around ' + r"$\bf" + str(round(rxi * 100, 2)) + "\%}$" + ')'])
    props = dict(boxstyle = 'round', facecolor = 'lightcyan')
    plt.text(-1.25, 1, textstr, fontsize = 12, va = 'top', bbox = props)
        
    # Title, Axes Labels
    plt.title('Probability Mass Function (PMF) of obtaining a 5-Star Character at each pull after pity reset')
    plt.ylabel('Probability')
    plt.xlabel('Number of Pulls')

    plt.xticks(np.arange(0, 91, 10))
    st.pyplot(fig)
    #################
    
    
    # Calculating cumulative probabilities
    def prob_mul(n):
        if n == 75:
            return (1 - roll_dict[74])
        else:
            return (1 - roll_dict[n - 1]) * prob_mul(n - 1) 
    
    prob_75to89 = [binom.cdf(0, 73, 0.006) * prob_mul(x) * roll_dict[x] for x in range(75, 90)]
    prob_75to89 = np.cumsum(prob_75to89) + geom.cdf(73, 0.006) + binom.cdf(0, 73, 0.006) * roll_dict[74]
    prob_75to89_dict = {num: prob_75to89[num - 75] for num in range(75, 90)}
    
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
    
    
    st.markdown('### Cumulative Distribution Function (CDF)')
    xc = st.slider('Choose number of pulls after your last 5-Star Character to see the cumulative probabilities of getting a 5-star character within your set number of pulls:', 1, 90, 30)
    
    
    #### PLOT 2 ####
    fig, ax = plt.subplots(figsize = (12, 6), dpi = 200)
    plt.style.use('seaborn-whitegrid')

    plt.plot(roll_cum_dict.keys(), roll_cum_dict.values(), color = 'red')

    # Vertical line, point and text
    plt.axvline(xc, linestyle = '--', color = 'red')
    plt.plot(xc, roll_cum_dict[xc], marker = 'o', color = 'black')
    plt.text(xc - 7, roll_cum_dict[xc] + 0.025, '{} pull(s)'.format(int(xc)), fontsize = 10, color = 'r')

    # Horizontal line (Median Probability)
    plt.text(-3, 0.52, 'Median (50% chance of obtaining a 5-Star Character before/after horizontal line) ', fontsize = 10)
    plt.axhline(0.500, linestyle = ':', color = 'black')

    # Text box
    rxc = round(roll_cum_dict[xc], 8)
    textstr = "\n".join([r'Chance of obtaining a 5-Star Character by $\bf{%s}$ pull(s) or less:' % str(xc),
                         f'{rxc}' + ' (around ' + r"$\bf" + str(round(rxc * 100, 2)) + "\%}$" + ')'])
    props = dict(boxstyle = 'round', facecolor = 'wheat')
    plt.text(-1.25, 1, textstr, fontsize = 12, va = 'top', bbox = props)

    plt.title('Cumulative Distribution Function (CDF) of obtaining an 5-Star Character within X number of pulls')
    plt.ylabel('Cumulative Probability of getting a 5-Star Character', labelpad = 15)
    plt.xlabel('Cumulative Number of Pulls', labelpad = 10)

    plt.xticks(np.arange(0, 91, 10))
    st.pyplot(fig)
    #################

   
    ### Calculating Distribution of Successful Pulls
    
    d = deque(roll_cum_dict.values())
    d.pop()
    d.appendleft(0)
    subd = np.array(d)
    cumd = np.array(list(roll_cum_dict.values()))
    succ_pull_probs = list(cumd - subd)
    succ_pull_dict = {num: succ_pull_probs[num - 1] for num in range(1, 91)}

    
    st.markdown('### Distribution of Successful Pulls')
    xs = st.slider('Choose number of pulls after your last 5-Star Character to see how likely you are to pull a 5-star character at your current level:', 1, 90, 30)
    
    
    #### PLOT 3 ####
    fig, ax = plt.subplots(figsize = (12, 6), dpi = 200)
    plt.style.use('seaborn-whitegrid')

    plt.plot(succ_pull_dict.keys(), succ_pull_dict.values(), color = 'green')

    # Vertical line, point and text
    plt.axvline(xs, linestyle = '--', color = 'green')
    plt.plot(xs, succ_pull_dict[xs], marker = 'o', color = 'black')
    plt.text(xs - 7, succ_pull_dict[xs] + 0.0025, '{} pull(s)'.format(int(xs)), fontsize = 10, color = 'green')


    # Text box
    rxs = round(succ_pull_dict[xs], 8)
    textstr = "\n".join([r'Actual Probability of successfully obtaining a 5-Star Character on Pull No. $\bf{%s}$:' % str(xs),
                         f'{rxs}' + ' (around ' + r"$\bf" + str(round(rxs * 100, 2)) + "\%}$" + ')'])
    props = dict(boxstyle = 'round', facecolor = 'greenyellow')
    plt.text(-1.25, 0.105, textstr, fontsize = 12, va = 'top', bbox = props)

    # Title, Axes Labels
    plt.title('Distribution of Successful Pulls (Where 5-Star Characters are pulled the most)')
    plt.ylabel('Probability of getting a 5-Star Character', labelpad = 15)
    plt.xlabel('Number of Pulls', labelpad = 10)

    plt.xticks(np.arange(0, 91, 10))
    st.pyplot(fig)
    #################
    
    st.markdown("---")
    
    st.markdown('**Final Note:** These graphs do not take into account if you lose the 50/50 when pulling on the character event banner for a featured character. It only calculates your chances of getting **a** 5-Star character at the set amount of pulls after your pity resets.')

    
    
    
    
    
    
    
    
def web(): # Weapon Event Banner
    
    st.markdown('## Weapon Event Banner Statistics:')
    st.markdown('The probabilities for obtaining a 5-Star Weapon (in number of pulls after pity reset) are as follows:')
  
    st.markdown('- **Base Rate:** Before 63 pulls - *Low chance*')
    st.markdown('- **Soft Pity:** From 63 pulls to 76 pulls - *Chance increases exponentially*')
    st.markdown('- **Hard Pity:** 77th Pull - *Guaranteed 5-Star*')
    
    st.write("##")
    
    st.markdown('What each graph means:')
    st.markdown('- **Probability Mass Function (PMF):** The base per-pull probability of obtaining a 5-Star Weapon on each individual pull after pity reset')
    st.markdown('- **Cumulative Distribution Function (CDF):** The **cumulative probability** of obtaining a 5-Star Weapon on your current pull or before that')
    st.markdown('- **Distribution of Successful Pulls:** Where 5-Star Weapon drops are most likely to occur between the pity reset and hard pity')
    
    st.write("###")
    
    def roll_probs(x):
        if x < 63:
            return 0.007
        elif x >= 63 and x < 77:
            return round((x - 62) * 0.07 + 0.007, 3)
        else:
            return 1
    
    roll_dict = {num: roll_probs(num) for num in range(1, 78)}
    
    
    st.markdown('### Probability Mass Function (PMF)')
    xi = st.slider('Choose number of pulls after your last 5-Star Weapon to see the base probability rate of getting a 5-star Weapon at each number of pulls at your current level:', 1, 77, 25)
    
 
    #### PLOT 1 ####
    fig, ax = plt.subplots(figsize = (12, 6), dpi = 200)
    plt.style.use('seaborn-whitegrid')
    
    ax = plt.plot(roll_dict.keys(), roll_dict.values(), color = 'blue')

    # Vertical line, point and text
    plt.axvline(xi, linestyle = '--', color = 'blue')
    plt.plot(xi, roll_dict[xi], marker = 'o', color = 'black')
    plt.text(xi - 7, roll_dict[xi] + 0.025, '({} pulls)'.format(int(xi)), fontsize = 10, color = 'blue')

    # Text box
    rxi = round(roll_dict[xi], 8)
    textstr = "\n".join([r'Base Rate of obtaining a 5-Star Weapon on Pull No. $\bf{%s}$:' % str(xi),
                         f'{rxi}' + ' (around ' + r"$\bf" + str(round(rxi * 100, 2)) + "\%}$" + ')'])
    props = dict(boxstyle = 'round', facecolor = 'lightcyan')
    plt.text(-1.25, 1, textstr, fontsize = 12, va = 'top', bbox = props)

    # Title, Axes Labels
    plt.title('Probability Mass Function (PMF) of obtaining a 5-Star Weapon at each pull after pity reset')
    plt.ylabel('Probability')
    plt.xlabel('Number of Pulls')

    plt.xticks(np.arange(0, 81, 10))
    st.pyplot(fig)
    #################
    
    # Calculating cumulative probabilities
    def prob_mul(n):
        if n == 64:
            return (1 - roll_dict[63])
        else:
            return (1 - roll_dict[n - 1]) * prob_mul(n - 1) 
    
    prob_64to76 = [binom.cdf(0, 62, 0.007) * prob_mul(x) * roll_dict[x] for x in range(64, 77)]
    prob_64to76 = np.cumsum(prob_64to76) + geom.cdf(62, 0.007) + binom.cdf(0, 62, 0.007) * roll_dict[63]
    prob_64to76_dict = {num: prob_64to76[num - 64] for num in range(64, 77)}
    
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
    
    
    st.markdown('### Cumulative Distribution Function (CDF)')
    xc = st.slider('Choose number of pulls after your last 5-Star Weapon to see the cumulative probabilities of getting a 5-star Weapon within your set number of pulls:', 1, 77, 25)
    
    
    #### PLOT 2 ####
    fig, ax = plt.subplots(figsize = (12, 6), dpi = 200)
    plt.style.use('seaborn-whitegrid')

    plt.plot(roll_cum_dict.keys(), roll_cum_dict.values(), color = 'red')

    # Vertical line, point and text
    plt.axvline(xc, linestyle = '--', color = 'red')
    plt.plot(xc, roll_cum_dict[xc], marker = 'o', color = 'black')
    plt.text(xc - 7, roll_cum_dict[xc] + 0.025, '({} pulls)'.format(int(xc)), fontsize = 10, color = 'r')

    # Horizontal line (Median Probability)
    plt.text(-3, 0.52, 'Median (50% chance of obtaining a 5-Star Weapon before/after horizontal line) ', fontsize = 10)
    plt.axhline(0.500, linestyle = ':', color = 'black')

    # Text box
    rxc = round(roll_cum_dict[xc], 8)
    textstr = "\n".join([r'Chance of obtaining a 5-Star Weapon by $\bf{%s}$ pull(s) or less:' % str(xc),
                         f'{rxc}' + ' (around ' + r"$\bf" + str(round(rxc * 100, 2)) + "\%}$" + ')'])
    props = dict(boxstyle = 'round', facecolor = 'wheat')
    plt.text(-1.25, 1, textstr, fontsize = 12, va = 'top', bbox = props)

    plt.title('Cumulative Distribution Function (CDF) of obtaining an 5-Star Weapon within X number of pulls')
    plt.ylabel('Cumulative Probability of getting a 5-Star Weapon', labelpad = 15)
    plt.xlabel('Cumulative Number of Pulls', labelpad = 10)

    plt.xticks(np.arange(0, 81, 10))
    st.pyplot(fig)
    #################
    
    
    ### Calculating Distribution of Successful Pulls
    
    d = deque(roll_cum_dict.values())
    d.pop()
    d.appendleft(0)
    subd = np.array(d)
    cumd = np.array(list(roll_cum_dict.values()))
    succ_pull_probs = list(cumd - subd)
    succ_pull_dict = {num: succ_pull_probs[num - 1] for num in range(1, 78)}

    
    st.markdown('### Distribution of Successful Pulls')
    xs = st.slider('Choose number of pulls after your last 5-Star Weapon to see how likely you are to pull a 5-Star Weapon at your current level:', 1, 77, 25)
    
    
    #### PLOT 3 ####
    fig, ax = plt.subplots(figsize = (12, 6), dpi = 200)
    plt.style.use('seaborn-whitegrid')

    plt.plot(succ_pull_dict.keys(), succ_pull_dict.values(), color = 'green')

    # Vertical line, point and text
    plt.axvline(xs, linestyle = '--', color = 'green')
    plt.plot(xs, succ_pull_dict[xs], marker = 'o', color = 'black')
    plt.text(xs - 7, succ_pull_dict[xs] + 0.0025, '({} pulls)'.format(int(xs)), fontsize = 10, color = 'green')

    # Text box
    rxs = round(succ_pull_dict[xs], 8)
    textstr = "\n".join([r'Actual Probability of successfully obtaining a 5-Star Weapon on Pull No. $\bf{%s}$:' % str(xs),
                         f'{rxs}' + ' (around ' + r"$\bf" + str(round(rxs * 100, 2)) + "\%}$" + ')'])
    props = dict(boxstyle = 'round', facecolor = 'greenyellow')
    plt.text(-1.25, 0.115, textstr, fontsize = 12, va = 'top', bbox = props)

    # Title, Axes Labels
    plt.title('Distribution of Successful Pulls (Where 5-Star Weapons are pulled the most)')
    plt.ylabel('Probability of getting a 5-Star Weapon', labelpad = 15)
    plt.xlabel('Number of Pulls', labelpad = 10)

    plt.xticks(np.arange(0, 81, 10))
    st.pyplot(fig)
    #################
    
    st.markdown("---")
    
    st.markdown('**Final Note:** These graphs do not take into account if you lose the 50/50 when pulling on the weapon event banner for a featured event weapon. It only calculates your chances of getting **a** 5-Star Weapon at the set amount of pulls after your pity resets.')
    


    
if __name__ == "__main__":
    main()

