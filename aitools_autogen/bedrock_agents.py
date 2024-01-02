import json
import traceback
from typing import List, Optional, Dict, Any, Union, Tuple

import asyncio
import boto3
from autogen import ConversableAgent, Agent, logger


class ClaudeBedrockAssistant(ConversableAgent):
    _boto3_config = boto3.session.Config(signature_version='s3v4',
                                         connect_timeout=5,
                                         read_timeout=60,
                                         max_pool_connections=5,
                                         retries={'max_attempts': 1, 'total_max_attempts': 1})

    _bedrock_east_runtime = boto3.client(
        service_name="bedrock-runtime",
        region_name="us-east-1",
        config=_boto3_config
    )

    _bedrock_west_runtime = boto3.client(
        service_name="bedrock-runtime",
        region_name="us-west-2",
        config=_boto3_config
    )

    _bedrock_llm_config = {
        "modelId": "anthropic.claude-v2",
        "contentType": "application/json",
        "accept": "*/*",
        "prompt_config": {
            "temperature": 0.1,
            "max_tokens_to_sample": 4000,
            "top_k": 120,
            "top_p": 0.5,
            "stop_sequences": ['\n\nHuman:'],
            "anthropic_version": "bedrock-2023-05-31",
        }
    }

    def __init__(self,
                 name: str = "Claude2 Assistant",
                 system_message: str = "You are an expert Python programmer.",
                 max_consecutive_auto_reply: int = 30,
                 bedrock_llm_config: Optional[Dict] = None):
        super().__init__(name=name,
                         llm_config=None,
                         system_message=system_message,
                         code_execution_config=False,
                         function_map=None,
                         human_input_mode="NEVER",
                         max_consecutive_auto_reply=max_consecutive_auto_reply)

        self._bedrock_llm_config = bedrock_llm_config or self._bedrock_llm_config
        self._reply_func_list = []
        self.register_reply([Agent, None], ClaudeBedrockAssistant.generate_bedrock_reply,
                            config=self._bedrock_llm_config)

    def generate_bedrock_reply(
            self,
            messages: Optional[List[Dict]] = None,
            sender: Optional[Agent] = None,
            config: Optional[Any] = None,
    ) -> Tuple[bool, Union[str, Dict, None]]:
        """Generate a reply using bedrock."""

        def json_escaped_string(prompt_str:str):
            # Convert the prompt string into its JSON string representation.
            # This will handle all necessary character escapes.
            escaped_prompt = json.dumps(prompt_str)

            # Remove the outer quotes added by dumps since we're inserting this string into an already quoted location.
            return escaped_prompt[1:-1]

        bedrock_config = {k: v for k, v in config.items() if k != 'prompt_config'}
        prompt_config = config.get('prompt_config')
        if bedrock_config is None or bedrock_config == {}:
            return False, None
        if messages is None:
            messages = self._oai_messages[sender]
        prompt = self._oai_system_message[0]['content']
        prompt = prompt + '\n'.join([msg['content'] for msg in messages]) if messages is not None else ''
        prompt_config['prompt'] = json_escaped_string(prompt.encode('unicode_escape').decode('utf-8'))

        # Constructing the body data structure
        body_data = {
            "prompt": f'Human: {prompt_config["prompt"]}\\n\\nAssistant:',
            "max_tokens_to_sample": prompt_config["max_tokens_to_sample"],
            "temperature": prompt_config["temperature"],
            "top_k": prompt_config["top_k"],
            "top_p": prompt_config["top_p"],
            "stop_sequences": ["\\n\\nHuman:"],
            "anthropic_version": prompt_config["anthropic_version"]
        }
        bedrock_config['body'] = json.dumps(body_data)

        try:
            print("Calling AWS Bedrock API")
            start_time = asyncio.get_event_loop().time()
            response = self._bedrock_east_runtime.invoke_model(**bedrock_config)
            end_time = asyncio.get_event_loop().time()
            print(f"Call to AWS Bedrock API took {end_time - start_time} seconds")
            completion = ClaudeBedrockAssistant.extract_bedrock_text(response)
            if completion is None:
                return False, None
            return True, completion
        except Exception as e:
            logger.error(e)
            traceback.print_exc()
            raise e

    @classmethod
    def extract_bedrock_text(cls, response) -> Optional[str]:
        response_body = json.loads(response["body"].read())
        completion = response_body.get('completion')
        if completion is None:
            return None
        return completion


if __name__ == "__main__":
    agent = ClaudeBedrockAssistant()
    boss = ConversableAgent("boss",
                            code_execution_config=False,
                            llm_config=False,
                            max_consecutive_auto_reply=0,
                            human_input_mode="NEVER")
    boss.initiate_chat(agent, True, False,
                       message="Write a bubble sort algorithm in Python.")

    print(boss.last_message(agent))
