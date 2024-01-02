import asyncio
import streamlit as st
from asyncio import sleep

import utils
from aitools_autogen.blueprint_generate_core_client_bedrock import CoreClientTestBlueprintBedrock
from aitools_autogen.blueprint_project8 import CustomBlueprintML
from config import llm_config

st.set_page_config(
    page_title="Streamlit Using Agents",
    page_icon="🕵️‍♂️",
)

st.toast("Welcome to a test of Streamlit with Agents!", icon="🕵️‍♂️")

if st.session_state.get("blueprint", None) is None:
    st.session_state.blueprint = CustomBlueprintML()


async def run_blueprint(ctr, seed: int = 42, task: str = "") -> str:
    await sleep(3)
    llm_config["seed"] = seed
    await st.session_state.blueprint.initiate_work(message=task)
    ctr.markdown(st.session_state.blueprint.summary_result)
    return st.session_state.blueprint.summary_result

blueprint_ctr, parameter_ctr = st.columns(2, gap="large")
with blueprint_ctr:
    st.markdown("# Run Blueprint")
    url = st.text_input("Enter a OpenAPI Schema URL to test:",
                        value="https://raw.githubusercontent.com/OAI/OpenAPI-Specification/main/examples/v3.0/uspto.yaml")
    agents = st.button("Start the Agents!", type="primary")

with parameter_ctr:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("### Other Options")
    clear = st.button("Clear the autogen cache...&nbsp; ⚠️", type="secondary")
    seed = st.number_input("Enter a seed for the random number generator:", value=42)

status_ctr = st.empty()
results_ctr = st.empty()

if clear:
    with status_ctr:
        st.status("Clearing the agent cache...")
    utils.clear_working_dir("../.cache", "*")

if agents:
    with status_ctr:
        st.status("Running the Blueprint...")

    
    task = f"""I want to retrieve the dataset from the
                {url}
            """

    text = asyncio.run(run_blueprint(ctr=results_ctr, seed=seed, task=task, ))
    st.balloons()

    with status_ctr:
        st.markdown("## Blueprint Results")

