import streamlit as st
import asyncio
import io
import os
import pathlib
from os.path import isfile, join
import pandas as pd
import helpers.sidebar
import helpers.util
import services.prompts
import services.llm
import helpers.util
from streamlit_ace import st_ace
from services import prompts, llm
import pyperclip

st.set_page_config(
    page_title="Generate Code",
    page_icon="📄",
    layout="wide"
)



helpers.sidebar.show()

st.write("Ducky Helps in review,debug,modify,copy code")

st.header("Review code")
st.write("copy paste the code in the box selected below ")
basic_code = st_ace(
    value="",
    language="python",
    placeholder="This is placeholder text when no code is present",
    theme="monokai",
    keybinding="vscode",
    font_size=14,
    tab_size=4,
    wrap=False,
    show_gutter=True,
    show_print_margin=True,
    auto_update=False,
    readonly=False,
    key="editor-basic"
)
st.write("Use the code editor to write code, then hit `CTRL+ENTER` to refresh the app.")
review_button = st.button("Review code")
if review_button:
    advice = st.markdown("reviewing code")
    print(basic_code)
    learning_prompt = services.prompts.review_code_prompt(code=basic_code)
    messages = llm.create_conversation_starter(learning_prompt)
    messages.append({"role": "user", "content": learning_prompt})
    asyncio.run(helpers.util.run_conversation(messages, advice))


st.header("Debugging Code")
debug_code = st_ace(
    value="",
    language="python",
    placeholder="This is placeholder text when no code is present",
    theme="monokai",
    keybinding="vscode",
    font_size=14,
    tab_size=4,
    wrap=False,
    show_gutter=True,
    show_print_margin=True,
    auto_update=False,
    readonly=False,
    key="editor-basic-debug"
)
error_ =st.text_area("Enter your Issue")
debug_button = st.button("Debug code")
if debug_button:
    advice = st.markdown("debugging code")
    learning_prompt = services.prompts.debug_code_prompt(code=debug_code,error=error_)
    messages = llm.create_conversation_starter(learning_prompt)
    messages.append({"role": "user", "content": learning_prompt})
    asyncio.run(helpers.util.run_conversation(messages, advice))



st.header("Modify Code")
code_box = st_ace(value="",
        language="python",
        placeholder="This is placeholder text when no code is present",
        theme="monokai",
        keybinding="vscode",
        font_size=14,
        tab_size=4,
        wrap=False,
        show_gutter=True,
        show_print_margin=True,
        auto_update=False,
        readonly=False,
        key="editor-basic-modify")
user_input = st.text_area("enter your response",key="userin")
s = st.button("modify")
satisf = False
if s:
    advice = st.markdown("modifying code")
    learning_prompt = services.prompts.modify_code_prompt(code=code_box,requirements=user_input)
    messages = llm.create_conversation_starter(learning_prompt)
    messages.append({"role": "user", "content": learning_prompt})
    asyncio.run(helpers.util.run_conversation(messages, advice))
    #copy to clipboard is an icon located in the top right of the highlighted code
    if st.button("Copy to Clipboard"):
        print(advice)
        if advice:
            pyperclip.copy(advice)
            st.success(f'"{advice}" copied to clipboard!')
        else:
            st.warning("Please enter some text to copy.")
reload_button = st.button("↪︎ Feedback")
if reload_button:
    # Clear the session code
    del st.session_state['userin']

st.header("Reset button")
reset_button = st.button("↪︎ Reset prompt and messages")
if reset_button:
    messages = []
    for key in st.session_state.keys():
        del st.session_state[key]










