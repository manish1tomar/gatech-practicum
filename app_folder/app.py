import streamlit as st
import numpy as np
import pandas as pd
import requests

#Add title of app
st.title('FCS Chatbot OnePal')

#Add simple text
st.write("Hi there !! This is OnePal, I’m here to help!")

#user input
number = st.slider('What is your feedback on a scale of 1-5, being the highest.',1,5)
if number >= 4:
    st.write("Thanks for your feedback", number, "is great")
else:
    st.write("Thanks for your feedback", number, "means I need to learn more & improve.")

#Add a button
if st.button('Say Hello !'):
    st.write("Hi there !! This is OnePal, I’m here to help!")

#Add radio button
genre = st.radio("What do you want to talk about ?", ('Graduation Requirements', 'Career Advise', 'Support resources'))
st.write(f"Sure, lets talk about {genre}")

#Add a dropdown
contact_option = st.selectbox("How would like to be contacted ?", ('Email ','Mobile Phone ','Home Phone '))

#Add a sidebar
sd_bar = st.sidebar.selectbox("How would like to be contacted ?", ('Email','Mobile Phone','Home Phone'))

#Add text input
#st.sidebar.text_input(f'Enter your {contact_option}')
st.text_input(f'Enter your {contact_option}')

#Add a file uploader
#uploaded_file = st.file_uploader("Upload the file", type="csv")
uploaded_file = st.sidebar.file_uploader("Upload the file", type="csv")

#Line chart
#==============================================================================================================#
data = pd.DataFrame({"S.No.": list(range(1,11))
                    ,"Value": np.array(list(range(10,101,10)))})
st.line_chart(data)
#==============================================================================================================#

st.chat_message("user")
st.write("Hi there !! This is OnePal, I’m here to help!")
st.chat_input("What do you want to talk about ?")

