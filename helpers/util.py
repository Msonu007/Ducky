import io
from typing import List, Dict

import pandas
from streamlit.delta_generator import DeltaGenerator

import services.llm


async def run_conversation(messages: List[Dict[str, str]], message_placeholder: DeltaGenerator) \
        -> List[Dict[str, str]]:
    full_response = ""
    message_placeholder.markdown("Thinking...")
    chunks = services.llm.converse(messages)
    chunk = await anext(chunks, "END OF CHAT")
    while chunk != "END OF CHAT":
        print(f"Received chunk from LLM service: {chunk}")
        if chunk.startswith("EXCEPTION"):
            full_response = ":red[We are having trouble generating advice.  Please wait a minute and try again.]"
            break
        full_response = full_response + chunk
        message_placeholder.markdown(full_response + "▌")
        chunk = await anext(chunks, "END OF CHAT")
    message_placeholder.markdown(full_response)
    messages.append({"role": "assistant", "content": full_response})
    return messages


async def run_prompt(prompt: str,
                     message_placeholder: DeltaGenerator) \
        -> List[Dict[str, str]]:
    messages = services.llm.create_conversation_starter(prompt)
    messages = await run_conversation(messages, message_placeholder)
    return messages


def copy_as_csv_string(data_frame: pandas.DataFrame) -> str:
    # Convert DataFrame to CSV-like string
    csv_string_io = io.StringIO()
    data_frame.to_csv(csv_string_io, index=False, sep=',')

    # Get the CSV data from the StringIO object
    return csv_string_io.getvalue()
