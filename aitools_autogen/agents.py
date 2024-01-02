import re
from typing import Optional, List, Dict, Any, Union, Tuple
import pandas as pd
import json

import autogen
import requests
from autogen import Agent, ConversableAgent

from aitools_autogen.config import WORKING_DIR,llm_config
from aitools_autogen.utils import save_code_files


# It was at one stage interesting to play with removing the default reply functions.
# However, it just led to infinite conversations more easily.
# I'm keeping this agent here as a reminder of how I implemented it.
class CustomReplyAgent(ConversableAgent):
    def __init__(self, name: str, **kwargs):
        super().__init__(name=name if name is not None else "Custom Reply Agent", **kwargs)
        self._reply_func_list = []


class CodeLibrarianAgent(CustomReplyAgent):

    _default_librarian_config = {
        "work_dir": WORKING_DIR,
    }

    def __init__(self,
                 name: str = "Code Librarian",
                 max_consecutive_auto_reply: int = 30,
                 code_librarian_config: Optional[Dict] = None,
                 ):
        super().__init__(name=name,
                         llm_config=None,
                         system_message=None,
                         code_execution_config=False,
                         function_map=None,
                         human_input_mode="NEVER",
                         max_consecutive_auto_reply=max_consecutive_auto_reply)
        self._code_librarian_config = code_librarian_config or self._default_librarian_config
        self.register_reply([Agent, None], CodeLibrarianAgent._reply_func,
                            config=self._code_librarian_config)

    def _reply_func(
            self,
            messages: Optional[List[Dict]] = None,
            sender: Optional[Agent] = None,
            config: Optional[Any] = None,
    ) -> Tuple[bool, Union[str, Dict, None]]:
        """Generate a reply using bedrock."""

        if config is None or config == {}:
            return False, None
        if messages is None:
            messages = self._oai_messages[sender]

        for msg in messages:
            save_code_files(msg['content'], config['work_dir'])

        return True, "Files have been saved.  I'm done for now, please ask other agents to continue the group chat."

# This is a general agent with a specific name and a specific reply function.
# It scours a set of urls and gathers a dictionary of the content of each url.
# There's no cycle protection yet.
class WebScraperAgent(autogen.AssistantAgent):
    def __init__(self):
        super().__init__(name="WebScraper Agent", llm_config=None,
                         max_consecutive_auto_reply=3)
        self.register_reply([Agent, None], self._scraper_func)

    def _scraper_func(self,
                      recipient: ConversableAgent,
                      messages: Optional[List[Dict]] = None,
                      sender: Optional[Agent] = None,
                      config: Optional[Any] = None,
                      ) -> Any | Union[str, Dict, None]:
        urls = self._extract_urls(messages[0]["content"])
        if (urls is None) or (len(urls) == 0):
            return False, None
        return True, self._get_scraped_content(urls)

    # Write a function that given a str extracts a list of urls present in the string
    @staticmethod
    def _extract_urls(text):
        """
            Extracts a list of URLs from a given string.

            :param text: str, the text to search for URLs.
            :return: list, a list of URLs found in the string.
            """
        url_regex = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        urls = re.findall(url_regex, text)
        return urls

    @staticmethod
    def _get_scraped_content(urls: List[str]) -> Dict[str, Dict[str, str]]:
        result = {}
        for url in urls:
            response = requests.get(url)
            if response.status_code == 200:
                result[url] = str(response.text)
            else:
                result[url] = None
        return {"content": result}


# Sometimes you just want one web page and its content directly....
class WebPageScraperAgent(WebScraperAgent):
    def _scraper_func(self,
                      recipient: ConversableAgent,
                      messages: Optional[List[Dict]] = None,
                      sender: Optional[Agent] = None,
                      config: Optional[Any] = None,
                      ) -> Any | Union[str, Dict, None]:
        urls = self._extract_urls(messages[0]["content"])
        if (urls is None) or (len(urls) == 0):
            return False, None
        content = self._get_scraped_content(urls[0])
        if content is None:
            return False, None
        return True, content

    def _get_scraped_content(self, url: str) -> Optional[Dict[str, str]]:
        result: Optional[Dict[str, str]] = dict()
        print(self.name, "is scraping", url)
        response = requests.get(url)
        if response.status_code == 200:
            result['content'] = str(response.text)
        else:
            result = None
        return result


class DatasetScaperAgent(autogen.AssistantAgent):
    def __init__(self):
        super().__init__(name="DatasetScraperAgent", llm_config=None,
                         max_consecutive_auto_reply=51,code_execution_config=False)
        self.register_reply([Agent, None], self._scraper_func)

    @staticmethod
    def _extract_urls(text):
        """
            Extracts a list of URLs from a given string.

            :param text: str, the text to search for URLs.
            :return: list, a list of URLs found in the string.
            """
        url_regex = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        urls = re.findall(url_regex, text)
        print(text,urls)
        return urls

    def _download_dataset(self, url):
        result: Optional[Dict[str, str]] = dict()
        dataframe = pd.read_csv(url)
        json_ = dataframe.to_json()
        k = dataframe.dtypes
        print(k)
        for key in k.keys():
            k[key] = str(k[key].name)
        print(k)
        df_new = pd.DataFrame.from_dict(k).to_json()
        result["content"] = f"The dataset description is {df_new} and the dataset url is {url}"
        return result




    def _scraper_func(self,
                      recipient: ConversableAgent,
                      messages: Optional[List[Dict]] = None,
                      sender: Optional[Agent] = None,
                      config: Optional[Any] = None,
                      ) -> Any | Union[str, Dict, None]:
        url = self._extract_urls(messages[0]["content"])
        description = self._download_dataset(url[0])
        if (description is None) or (len(description) == 0):
            return False, None
        return True, description
