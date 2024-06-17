from webscrapping import scrape
from llm import process_llm
import streamlit as st
from PIL import Image
from io import BytesIO
import os

def scrape_website(url):
    image_list = []
    txt = scrape(url, 'images')
    # Check and load images if any
    if os.path.exists('images'):
        images = os.listdir('images')
        for img in images:
            if img.endswith(('.jpg', '.jpeg', '.png', '.gif')):
                image = Image.open(f'images/{img}')
                image_list.append(image)
    return txt, image_list

# Function to send data to LLM function (replace with actual LLM function)
def process_with_llm(content):
    # Placeholder for LLM processing (replace with actual LLM code)
    processed_content = f"LLM processed: {content}"
    return processed_content

def main():
    st.set_page_config(
        page_title="Social Media Content Creation App",
        page_icon="🌟",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Custom CSS for styling
    st.markdown(
        """
        <style>
        .stButton > button {
            background-color: #6c63ff !important;
            color: white !important;
            font-weight: bold;
            border-radius: 5px;
            padding: 10px 20px;
            transition: all 0.3s ease;
        }
        .stButton > button:hover {
            background-color: #5248e6 !important;
            color: white !important;
        }
        .stTextInput > div > div > input {
            border-radius: 5px;
            padding: 10px;
            border-color: #6c63ff !important;
        }
        .generated-content {
            background-color: #262730;
            padding: 20px;
            border-radius: 10px;
            margin-top: 20px;
            border: 1px solid #6c63ff;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }
        .generated-content img {
            border-radius: 10px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.title('Social Media Content Creation App')
    st.markdown("<h3 style='color: #6c63ff;'>Create social media content and images</h3>", unsafe_allow_html=True)

    # Input URL
    url = st.text_input('Enter Website URL')

    # Generate content and image on button click
    if st.button('Generate Content and Image'):
        if url:
            # Scrape website for content and images
            content, image_list = scrape_website(url)

            # Send scraped content to LLM function
            processed_content,list = process_llm(content,url)
        
            image_list=image_list+list
            # Display generated content
            st.markdown("<hr>", unsafe_allow_html=True)
            st.markdown(f"<div class='generated-content'>{processed_content}</div>", unsafe_allow_html=True)

            if image_list:
                st.markdown("<hr>", unsafe_allow_html=True)
                st.write("Images found in the article url")
                st.image(image_list, width=200, caption=[f"Image {i+1}" for i in range(len(list))])
            

if __name__ == "__main__":
    main()
