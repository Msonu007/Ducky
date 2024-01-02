import asyncio
import time
from services.llm import converse


#
# In this test, we expect to receive chunks almost immediately and spread over time.
# If this test is NOT working, we wait for a bit then receive the chunks all at once.
#

async def chat(messages):
    print("Called chat")
    full_response = ""
    chunks = converse(messages)
    chunk_index = 0
    start_time = time.time()
    chunk = await anext(chunks, "END OF CHAT")
    print(f"Chat receives partial response {chunk}")
    while chunk != "END OF CHAT":
        print(f"Chat: Chunk {chunk_index} received in {time.time() - start_time} seconds")
        chunk_index = chunk_index + 1
        full_response += chunk
        chunk = await anext(chunks, "END OF CHAT")

    print(full_response)
    messages.append({"role": "assistant", "content": full_response})
    return messages


async def main():
    messages = await chat([{"role": "user", "content": "Tell me a 200 words story."}])


if __name__ == '__main__':
    asyncio.run(main())
