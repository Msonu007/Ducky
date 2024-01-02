import asyncio
import streamlit as st
from streamlit import status
from asyncio import sleep

import helpers.sidebar
import helpers.util
from aitools_autogen.blueprint_generate_core_client_bedrock import CoreClientTestBlueprintBedrock
from aitools_autogen.blueprint_generate_core_client import CoreClientTestBlueprint
from aitools_autogen.blueprint_project8 import CustomBlueprintML
from aitools_autogen.config import llm_config
from aitools_autogen.utils import clear_working_dir

st.set_page_config(
    page_title="Auto Code",
    page_icon="📄",
    layout="wide"
)

# Add comments to explain the purpose of the code sections

# Show sidebar
helpers.sidebar.show()


option = st.selectbox(
    "Which blueprint you wanna use ?",
    ("Default Blueprint","Custom Blueprint")
)

if option == "Default Blueprint":
    st.session_state.blueprint = CoreClientTestBlueprint()
else:
    st.session_state.blueprint = CustomBlueprintML()


async def run_blueprint(ctr, seed: int = 42) -> str:
    await sleep(3)
    llm_config["seed"] = seed
    await st.session_state.blueprint.initiate_work(message=task)
    return st.session_state.blueprint.summary_result

blueprint_ctr, parameter_ctr = st.columns(2, gap="large")
with blueprint_ctr:
    st.markdown("# Run Blueprint")
    if option == "Custom Blueprint":
        url = st.text_input("Enter a dataset to model on:",
                        value="https://gist.githubusercontent.com/curran/a08a1080b88344b0c8a7/raw/0e7a9b0a5d22642a06d3d5b9bcbad9890c8ee534/iris.csv")
    else:
        url = st.text_input("Enter a OpenAPI Schema URL to test:",
                        value="https://raw.githubusercontent.com/OAI/OpenAPI-Specification/main/examples/v3.0/uspto.yaml")
    agents = st.button("Start the Agents!", type="primary")

with parameter_ctr:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("### Other Options")
    clear = st.button("Clear the autogen cache...&nbsp; ⚠️", type="secondary")
    seed = st.number_input("Enter a seed for the random number generator:", value=42)

dynamic_ctr = st.empty()
results_ctr = st.empty()

if clear:
    with results_ctr:
        status("Clearing the agent cache...")
    clear_working_dir("../.cache", "*")

if agents:
    with results_ctr:
        status("Running the Blueprint...")

    task = f"""
                I want to retrieve the dataset from the url {url} .
                build an end to end datascience project, use the dataset from the above link.
                You need to preprocess the dataset,remove the missing values.
                You need to perform feature engineering on the dataset provided.
                You want to train your machine learning model on your dataset.
                You want to know what the best model is for your dataset.
                Always put `# filename: api/client/<filename>` as the first line of each code block.
                """

    text = asyncio.run(run_blueprint(ctr=dynamic_ctr, seed=seed))
    st.balloons()

    with results_ctr:
        st.markdown(text)



