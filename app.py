from webscrapping import scrape
import streamlit as st
st.header("Linkedin Post Generator")
st.write("enter your article url here")
st.text_input()
folder = './images'
txt = scrape(url, folder)
