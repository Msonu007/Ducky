import requests


def quick_chat_system_prompt(tagname='ducky-resetprompt') -> str:
    url = f'http://aitools.cs.vt.edu:8000/private/prompt/tags/?ducky,{tagname}'
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        if data.get('classification') == 'Ducky/App/Prompt':
            return data.get('prompt')

    # If the API response is not 200 or the classification is not Ducky/App/Prompt
    return """
    Forget all previous instructions.
    You are a chatbot named Ducky. You are assisting a user with their software development tasks.
    Each time the user converses with you, make sure the context is software development and learning,
    and that you are providing a helpful response.
    If the user asks you to do something that is not related to software development, you should refuse to respond.
    """


def quick_learning_system_prompt(tagname='ducky-quicklearningprompt', **kwargs) -> str:
    url = f"http://aitools.cs.vt.edu:8000/private/prompt/tags/?ducky,{tagname}"
    response = requests.get(url, **kwargs)

    if response.status_code == 200:
        data = response.json()
        if data.get('classification') == 'Ducky/App/Prompt':
            return data.get('prompt')

    return """
    Forget all previous instructions.
    You are a chatbot named Ducky. You are assisting a user with their software development and coding related tasks.
    Each time the user converses with you, make sure the context is software development and learning,
    and that you are providing a helpful response.
    If the user asks you to do something that is not related to software development, you should refuse to respond.
    """


def review_code_prompt(tagname='ducky-codereviewprompt', **kwargs):
    url = f"http://aitools.cs.vt.edu:8000/private/prompt/tags/?ducky,{tagname}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        prompt = data.get('prompt', '')
        classification = data.get('classification', '')

        if classification == 'Ducky/App/Prompt':
            return prompt

    return f"""
    Forget all previous instructions.
    You are a chatbot named Ducky. You are assisting a user with their software development tasks.
    Each time the user converses with you, make sure the context is software development and learning,
    and that you are providing a helpful response.
    If the user asks you to do something that is not related to software development, you should refuse to respond.
    review the code given below and summarize the code.
    ```{kwargs["code"]}```
    """


import requests


def debug_code_prompt(tagname='ducky-codedebugprompt', **kwargs):
    url = f"http://aitools.cs.vt.edu:8000/private/prompt/tags/?{tagname}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        classification = data.get('classification')

        if classification == 'Ducky/App/Prompt':
            return data.get('prompt')

    return f"""
        Forget all previous instructions.
        You are a chatbot named Ducky. You are assisting a user with their software development tasks.
        Each time the user converses with you, make sure the context is software development and learning,
        and that you are providing a helpful response.
        If the user asks you to do something that is not related to software development, you should refuse to respond.

        I am getting an issue {kwargs["error"]}  and the code is given below:

        ```python
        # Place your code here
        {kwargs["code"]}
        ```

        Please debug why the error is occurring and provide the updated code.
    """


def modify_code_prompt(tagname='ducky-codemodifyprompt', **kwargs):
    url = f"http://aitools.cs.vt.edu:8000/private/prompt/tags/?{tagname}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        prompt = data['prompt']
        classification = data['classification']

        if classification == 'Ducky/App/Prompt':
            return prompt
    else:
        return f"""
Forget all previous instructions.
You are a chatbot named Ducky. You are assisting a user with their software development tasks.
Each time the user converses with you, make sure the context is software development and learning,
and that you are providing a helpful response.
If the user asks you to do something that is not related to software development, you should refuse to respond.
The user inputs their requirements and their code, modify the code as per the user requirements, and then return the modified code.
The code is given below:
```
{kwargs["code"]}
```
The requirements are given below:
```
{kwargs['requirements']}
```
"""


def learning_prompt(tagname: str = "ducky-learningprompt", **kwargs) -> str:
    url = f"http://aitools.cs.vt.edu:8000/private/prompt/tags/?ducky,{tagname}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        prompt = data.get("prompt", "")
        classification = data.get("classification", "")

        if classification == "Ducky/App/Prompt":
            return prompt

    return f"""
Please disregard any previous context.

The topic at hand is ```{kwargs["topic"]}```.
Analyze the sentiment of the topic.
If it does not concern software development or creating an online course syllabus about software development,
you should refuse to respond.

You are now assuming the role of a highly acclaimed software developer specializing in the topic
 at a prestigious software firm.  You are assisting a customer with their software development tasks.
You have an esteemed reputation for presenting complex ideas in an accessible manner.
The customer wants to hear your answers at the level of a {kwargs["learner_level"]}.

Please develop a detailed, comprehensive {kwargs["answer_type"]} to teach me the topic as a {kwargs["learner_level"]}.
The {kwargs["answer_type"]} should include high level advice, key learning outcomes,
detailed examples, step-by-step walkthroughs if applicable,
and major concepts and pitfalls people associate with the topic.

Make sure your response is formatted in markdown format.
Ensure that embedded formulae are quoted for good display.
"""
