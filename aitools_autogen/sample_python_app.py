from autogen import ConversableAgent

import utils
from agents import WebPageScraperAgent

config_list = [
    {
        'model': 'gpt-4',
        'api_key': 'aitools',
        'api_base': 'http://aitools.cs.vt.edu:7860/openai/v1'
    }
]

llm_config = {
    "request_timeout": 300,
    "seed": 42,
    "config_list": config_list,
    "temperature": 0.1,
    "allow_format_str_template": True
}






agent0 = ConversableAgent("a0",
                          max_consecutive_auto_reply=0,
                          llm_config=False,
                          human_input_mode="NEVER")

scraper_agent = WebPageScraperAgent()

summary_agent = ConversableAgent("summary_agent",
                                 max_consecutive_auto_reply=6,
                                 llm_config=llm_config,
                                 human_input_mode="NEVER",
                                 code_execution_config=False,
                                 function_map=None,
                                 system_message="""You are a helpful AI assistant.
You can summarize OpenAPI specifications.  When given an OpenAPI specification, 
output a summary in bullet point form for each endpoint.
Let's make it concise in markdown format.
It should include short descriptions of parameters,
and list expected possible response status codes.
Return `None` if the OpenAPI specification is not valid or cannot be summarized.
    """)

# task = """
# I want to retrieve the Open API specification for the OpenAI API.
# https://raw.githubusercontent.com/openai/openai-openapi/master/openapi.yaml
# """

task = """
I want to retrieve the Open API specification for the US Patent Office API.
https://raw.githubusercontent.com/OAI/OpenAPI-Specification/main/examples/v3.0/uspto.yaml
"""

agent0.initiate_chat(scraper_agent, True, True, message=task)

message = agent0.last_message(scraper_agent)

agent0.initiate_chat(summary_agent, True, True, message=message)

api_description_message = agent0.last_message(summary_agent)

#api_description = api_description_message["content"]
#print(api_description)

aiohttp_client_agent = ConversableAgent("aiohttp_client_agent",
                                 max_consecutive_auto_reply=6,
                                 llm_config=llm_config,
                                 human_input_mode="NEVER",
                                 code_execution_config=False,
                                 function_map=None,
                                 system_message="""
You are a QA developer expert in Python, using the pytest framework.
You're writing an http client layer for tests for an API.

When you receive a message, you should expect that message to describe endpoints of an API.

Let's use aiohttp for our core http client layer.
All files must be generated in the api/client directory.

Write a complete implementation covering all described endpoints.
Use multiple classes in separate file names in a directory structure that makes sense.
Use aiohttp.ClientSession for the http client.
Use aiohttp.ClientResponse for the http response.

Create the aiohttp session inside a `with` block so that it is closed automatically.
The code using this generated code should not require aiohttp.

You must indicate the script type in the code block. 
Do not suggest incomplete code which requires users to modify. 
Always put `# filename: api/client/<filename>` as the first line of each code block.

Feel free to include multiple code blocks in one response. Do not ask users to copy and paste the result. 
""")

agent0.initiate_chat(aiohttp_client_agent, True, True, message=api_description_message)

llm_message = agent0.last_message(aiohttp_client_agent)["content"]
print(llm_message)

utils.save_code_files(llm_message, ".code")

print(utils.summarize_files(".code"))
