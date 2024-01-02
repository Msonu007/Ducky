import asyncio

import streamlit as st
import helpers.sidebar
import helpers.util
import services.prompts
import services.llm

st.set_page_config(
    page_title="Learning Topics",
    page_icon="🎓",
    layout="wide"
)

st.header("Learning Topics")

helpers.sidebar.show()

# Add a sidebar option to select a learner level
learner_level = st.sidebar.selectbox("I'd like my answer as if I were a:",
                                     ["5 year old", "high school student", "college student", "adult", "retiree"])

response_format = st.sidebar.selectbox("I'd like my answer as a:",
                                       ["set of bullet point notes", "article", "online course syllabus"])

answer_button_sb = st.sidebar.button("Get Answer&nbsp;&nbsp;➠", type="primary", key="answer_button_sb")

st.markdown("<br>", unsafe_allow_html=True)

topic = st.text_input("What would you like to learn about?", placeholder="Ask about a software development topic here.")
answer_button = st.button("Get Answer&nbsp;&nbsp;➠", type="primary")

if answer_button or answer_button_sb:
    advice = st.markdown("### Ducky Teaching...")
    learning_prompt = services.prompts.learning_prompt(learner_level, response_format, topic)
    messages = services.llm.create_conversation_starter(services.prompts.quick_learning_system_prompt())
    messages.append({"role": "user", "content": learning_prompt})
    asyncio.run(helpers.util.run_conversation(messages, advice))

