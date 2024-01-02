import asyncio
from typing import Optional, Dict, List
import autogen
from autogen import ConversableAgent, Agent

from aitools_autogen.agents import WebPageScraperAgent, DatasetScaperAgent
from aitools_autogen.blueprint import Blueprint
from aitools_autogen.config import llm_config, config_list, WORKING_DIR
from aitools_autogen.utils import save_code_files, summarize_files, clear_working_dir


class CustomBlueprintML(Blueprint):
    def __init__(self, work_dir: Optional[str] = WORKING_DIR):
        super().__init__([], config_list=config_list, llm_config=llm_config)
        self._work_dir = work_dir or "code"
        self._summary_result: Optional[str] = None

    @property
    def summary_result(self) -> str | None:
        """The getter for the 'summary_result' attribute."""
        return self._summary_result

    @property
    def work_dir(self) -> str:
        """The getter for the 'work_dir' attribute."""
        return self._work_dir

    async def status(self) -> Dict[Agent, List[Dict[str, str]]]:
        return self.boss_agent.chat_messages

    async def initiate_work(self, message: str):
        clear_working_dir(self._work_dir)
        self.boss_agent = DatasetScaperAgent()

        self.coder_agent = ConversableAgent("coder_agent",
                                            max_consecutive_auto_reply=51,
                                            llm_config=llm_config,
                                            human_input_mode="NEVER",
                                            code_execution_config=False,
                                            function_map=None,
                                            system_message="""You are a helpful AI assistant.
                                        You are a python coder and a machine learning expert,you are building a datascience pipeline.
                                        Write python code for the below requirements.
                                        You have been provided with the url and dataset description .
                                        use the url to load the dataset into a dataframe and do the next steps.
                                        Lets use sklearn package for training our model.
                                        Use pandas for loading the dataset and preprocessing related tasks i.e filling missing values and one hot encoding.
                                        perform pca for feature engineering
                                        You need to perform feature engineering on the dataset provided.
                                        Train the model with different models and suggest the best model for your dataset.
                                        Do not suggest incomplete code which requires users to modify.
                                        Feel free to include multiple code blocks in one response. Do not ask users to copy and paste the result.
                                        Never shorten the response, always include all code for all files generated.
                                        Your responses will be archived to disk, so eliding code is not wanted.
                                        format the code properly and seperate the code from the comments.
                                        """
                                            )

        self.critic_agent = ConversableAgent("critic_agent",
                                             max_consecutive_auto_reply=51,
                                             llm_config=llm_config,
                                             human_input_mode="NEVER",
                                             code_execution_config=False,
                                             function_map=None,
                                             system_message=""" You are a helpful assistant highly skilled in evaluating the quality of a
                                                datascience pipeline project.
                                        You must check weather there is code for feature engineering.
                                        You must check weather there is code for handling missing values.
                                        You must check weather the feature engineering is done properly.
                                        You must check weather the model is trained and inference is done properly.
                                        Check for the above mentioned things and give the feedback and suggest improvements that can be done.
                                        Do NOT suggest code.
                                        Do NOT accept partial code with pieces elided.
                                        Based on the critique above, suggest a concrete list of actions that the coder should take to improve the code.

        """)

        """
        silent_ = False
        self.boss_agent.initiate_chat(self.dataset_scaper_agent, True, silent_, message=message)
        message = self.boss_agent.last_message(self.dataset_scaper_agent)
        self.boss_agent.initiate_chat(self.coder_agent, True, silent_, message=message)
        coder_message = self.boss_agent.last_message(self.coder_agent)
        self.coder_agent.initiate_chat(self.critic_agent, True, silent_, message=coder_message)
        critic_message = self.coder_agent.last_message(self.critic_agent)
        print(critic_message)
        print(critic_message["content"])
        print("The saved files are ",save_code_files(critic_message["content"], self.work_dir))
        self._summary_result = summarize_files(self.work_dir)
        """
        groupchat = autogen.GroupChat(agents=[self.boss_agent, self.coder_agent, self.critic_agent], messages=[],
                                      max_round=15)
        manager = autogen.GroupChatManager(groupchat=groupchat, llm_config=llm_config)
        manager.initiate_chat(self.boss_agent, True, False, message=message)

        msg_ = manager.chat_messages[self.coder_agent]
        for msg in msg_:
            print("The files coder are ", save_code_files(msg['content'], self._work_dir))

        self._summary_result = summarize_files(self._work_dir)


if __name__ == "__main__":
    blueprint = CustomBlueprintML()
    url = "https://gist.githubusercontent.com/curran/a08a1080b88344b0c8a7/raw/0e7a9b0a5d22642a06d3d5b9bcbad9890c8ee534/iris.csv"
    asyncio.run(blueprint.initiate_work(message=f"""
                I want to retrieve the dataset from a url named {url} .
                build an end to end datascience project, use the dataset from the above link.
                You need to preprocess the dataset,remove the missing values.
                You need to perform feature engineering on the dataset provided.
                You want to train your machine learning model on your dataset.
                You want to know what the best model is for your dataset.
                """))
    print(blueprint.summary_result)
