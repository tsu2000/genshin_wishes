import streamlit as st
import io
import requests

from streamlit_extras.badges import badge
from PIL import Image

def main():
    col1, col2, col3 = st.columns([0.045, 0.27, 0.035])
    
    with col1:
        url = 'https://github.com/tsu2000/genshin_wishes/raw/main/images/Genshin_Impact.png'
        response = requests.get(url)
        img = Image.open(io.BytesIO(response.content))
        st.image(img, output_format = 'png')

    with col2:
        st.title('Genshin Impact Wish Stats')

    with col3:
        badge(type = 'github', name = 'tsu2000/genshin_wishes', url = 'https://github.com/tsu2000/genshin_wishes')

    st.markdown('### 🏠 &nbsp; Statistics-Based Web Apps for wishing in Genshin Impact')
    st.markdown('Welcome to the homepage for all Streamlit-based web applications centered around wishing statistics in Genshin Impact! To start using a feature, navigate to the sidebar on the left.')

    st.markdown('---')

    st.markdown('#### Current Web Apps:')

    st.markdown('These are the web apps the site currently has:')
    st.markdown('- **5★ Probability Distributions**: Allows users to visualise comprehensive in-game drop rates as probability distributions for 5★ items.')
    st.markdown('- **4/5★ Drop Rates Simulation**: Allows users to simulate and predict their in-game 5★ **OR** 4★ drop rates separately based on provided user input, such as number of wishes, pity level, and type of banner.')
    st.markdown('- **Combined Drop Rates Simulation**: Allows users to simulate and predict their in-game **combined** 3★/4★/5★ drop rates based on provided user input, such as number of wishes, pity level, and type of banner.')

    st.markdown('---')

    st.markdown('***Disclaimer**: This application is not affiliated with Genshin Impact, HoYoVerse in any way, shape or form. Information in this app may be subject to change and inaccurate. Please visit [**Wish Counter**](https://paimon.moe/wish) for more details regarding one\'s own personal wishing history and statistics.*')

if __name__ == "__main__":
    st.set_page_config(page_title = 'Genshin Wish Stats', page_icon = '🏠')
    main()