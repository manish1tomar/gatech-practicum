import AzureQuestionAnsweringKnowledgeBase as akb
import asyncio
import streamlit as st

#answer = asyncio.run(akb.getAnswer("Hi"))
#print(answer)

st.write("Hi there !! OnePal here, always happy to help. \n\nHow can I help you ?\n\nYou can ask like")
if st.button('graduation requirements'):
    st.write("Let talk about graduation requirements")
    st.write(asyncio.run(akb.getAnswer("how to graduate")))
    if st.button("english course"):
        st.write(asyncio.run(akb.getAnswer("english courses")))
    if st.button("math course"):
        answer=asyncio.run(akb.getAnswer("math courses"))
        print(answer)
        st.write("math courses are these")
    if st.button("science course"):
        st.write(asyncio.run(akb.getAnswer("science courses")))
elif st.button('academic planning advice'):
    st.write("Let talk about academic planning advice")
elif st.button('support resources'):
    st.write("Let talk about support resources")
else:
    st.write("Something else ? Type below")
    st.text_input("")