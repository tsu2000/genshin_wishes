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
        st.title('Genshin Impact WishStats')

    with col3:
        badge(type = 'github', name = 'tsu2000/genshin_wishes', url = 'https://github.com/tsu2000/genshin_wishes')

    st.markdown("### 🏠 &nbsp; Visualising Genshin Impact's Wish & Pity System")
    st.markdown("An interactive Streamlit app that explores the drop rates and pity mechanics behind Genshin Impact's wish system. Use the sidebar to get started.")

    st.markdown('---')

    st.markdown('#### Current Features:')
    st.markdown('- 🎲 **Wish System Probabilities**: Data visualisations and statistical explanations behind the wish and pity system probability rates in Genshin Impact (for 5★ items/characters).')
    st.markdown('- 🕹️ **Drop Rate Simulator**: Customize your wish history to simulate expected outcomes based on pity count, banner type, and number of pulls.')

    st.markdown('---')

    st.markdown('***Disclaimer**: This app is not affiliated with HoYoVerse or Genshin Impact. All figures are estimates. For actual wish history and official tools, visit [**Wish Counter**](https://paimon.moe/wish).*')

if __name__ == "__main__":
    st.set_page_config(page_title = 'Genshin Impact WishStats', page_icon = '🏠')
    main()
