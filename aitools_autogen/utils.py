#
# This file contains the code for the `utils.py` module.
#
# The idea here is that we do not want to execute code, but we want to generate code.
# This is currently based on the issue that we cannot execute code in the browser
# because the signal library is not available on a background thread in a streamlit process.
#
# So this is a workaround to generate code instead of executing it, and still depends on
# the autogen library `code_utils`.
#
import ast
import glob
import json
import os
import re
import textwrap
from hashlib import md5
from typing import List
from typing import Optional
from typing import Tuple

from autogen import Agent, ConversableAgent

from aitools_autogen.config import UNKNOWN, WORKING_DIR, CODE_BLOCK_PATTERN


def extract_code(
        text: str, pattern: str = CODE_BLOCK_PATTERN,
) -> List[Tuple[str, str]]:
    """
    Extract code blocks from a text and format preambles as comments.

    This function searches for code blocks in a string of text. Each code block is expected
    to be in the format of an optional preamble followed by the code enclosed in triple
    backticks. The language of the code can be optionally specified right after the first
    set of triple backticks.

    The function returns a list of 2-tuples, each containing the language (if specified,
    otherwise an empty string) and the code. If no code blocks are detected, the function
    returns a list with a single 2-tuple containing the string "unknown" and the original text.

    Preambles are treated as follows:
    - Each line of the preamble is turned into a comment in the code block by prefixing it
      with a '#' character, unless it already starts with '#'.
    - If a line in the preamble starts with '# filename', this line is not commented out,
      and it is placed as the first line of the corresponding code block. This is meant
      to preserve a directive that might be important for the interpretation or execution
      of the code. Only the first occurrence of a '# filename' line is processed in this manner.

    Args:
        text (str): The text to extract code from.
        pattern (str, optional): The regular expression pattern for finding the
            code block. Defaults to CODE_BLOCK_PATTERN.

    Returns:
        list: A list of tuples, each containing the language and the code (with the preamble
              incorporated as comments and the '# filename' line placed first if present).
    """
    matches = re.findall(pattern, text, flags=re.DOTALL)

    result = []

    for match in matches:
        preamble, lang, code = match
        preamble_filename_line = ""
        code_filename_line = ""
        preamble_lines = []
        code_lines = []

        # Process each line in the preamble
        for line in preamble.split("\n"):
            line_stripped = line.strip()
            if line_stripped.startswith("# filename"):
                # Capture the filename line to place at the beginning of the code block
                if not preamble_filename_line:  # Only capture the first occurrence
                    preamble_filename_line = line_stripped
            else:
                # Add '#' to each line of the preamble if it doesn't start with '#'
                if line_stripped and not line_stripped.startswith("#"):
                    preamble_lines.append(f"# {line}")
                else:
                    preamble_lines.append(line)

        # Concatenate the processed preamble lines with newlines
        commented_preamble = "\n".join(preamble_lines)

        # Also look for filename inside the code block
        for line in code.split("\n"):
            line_stripped = line.strip()
            if line_stripped.startswith("# filename"):
                # Capture the filename line to place at the beginning of the code block
                if not code_filename_line:
                    code_filename_line = line_stripped
            else:
                code_lines.append(line)
        full_code_lines = "\n".join(code_lines)

        filename_line = code_filename_line or preamble_filename_line or ""
        # Concatenate the filename line (if any), the commented preamble, and the code, with newlines in between
        full_code = "\n".join(filter(None, [filename_line, commented_preamble, full_code_lines]))

        result.append((lang, full_code))

    if not result:
        result.append((UNKNOWN, text))

    return result


def _get_function_signature(function: ast.FunctionDef) -> str:
    """
    Construct the function signature from the function definition, including type annotations.

    Args:
        function (ast.FunctionDef): The function definition.

    Returns:
        str: The function signature as a string.
    """
    # Extract the function name
    func_name = function.name

    # Extract the function arguments
    args = []
    for arg in function.args.args:
        arg_name = arg.arg

        # Include type annotation if present
        if arg.annotation:
            arg_name += f": {ast.unparse(arg.annotation)}"

        args.append(arg_name)

    # Handle default values for arguments if they exist
    defaults_offset = len(args) - len(function.args.defaults)
    for i, default in enumerate(function.args.defaults):
        args[i + defaults_offset] += f"={ast.unparse(default)}"

    # Handle type annotations for return value
    return_annotation = ""
    if function.returns:
        return_annotation = f" -> {ast.unparse(function.returns)}"

    args_str = ", ".join(args)
    return f"{func_name}({args_str}){return_annotation}"


def _get_public_functions(file_path: str):
    """
    Extract the public functions and their signatures from a Python file, including those inside classes.

    Args:
        file_path (str): The path to the Python file.

    Returns:
        list: A list of strings, each representing a public function or method with its signature.
    """
    with open(file_path, "r", encoding='utf-8') as source:
        node = ast.parse(source.read())

    functions = []
    for item in node.body:
        if isinstance(item, ast.FunctionDef):
            # For top-level functions
            if not item.name.startswith("_"):
                functions.append(_get_function_signature(item))
        elif isinstance(item, ast.ClassDef):
            # For functions within classes (methods)
            for class_item in item.body:
                if (isinstance(class_item, ast.FunctionDef) or isinstance(class_item, ast.AsyncFunctionDef)) and not class_item.name.startswith("_"):
                    functions.append(f"{item.name}.{_get_function_signature(class_item)}")  # Include the class name

    return functions


def summarize_files(working_folder: str) -> str:
    """
    Summarizes each Python file's public interface in the specified folder and its subfolders.

    Args:
        working_folder (str): The path of the working folder.

    Returns:
        str: A markdown string summarizing the public interface of each Python file.
    """
    markdown_summary = ""

    for subdir, _, files in os.walk(working_folder):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(subdir, file)
                public_functions = _get_public_functions(file_path)

                # Create a relative file path to display
                relative_file_path = os.path.relpath(file_path, working_folder)

                # Add a section for this file to the markdown summary
                markdown_summary += f"## {relative_file_path}\n"

                if public_functions:
                    for signature in public_functions:
                        markdown_summary += f"- `{signature}`\n"
                else:
                    markdown_summary += "No public methods.\n"

                # Add an extra newline to separate sections
                markdown_summary += "\n"

    return markdown_summary


def save_code(
        code: str = None,
        work_dir: Optional[str] = None,
        lang: Optional[str] = "python",
) -> str:
    """
    Save the code in a working directory.
    Filenames are expected to be relative paths, and appear inside the code
    as a line starting with '# filename'.

    Args:
        code (str): The code to save.  If a filename cannot be derived from a line starting with '# filename',
            a file with a randomly generated name will be created.
            The file name must be a relative path. Relative paths are relative to the working directory.
        work_dir (Optional, str): The working directory for the code execution.
            If None, a default working directory will be used.
            The default working directory is the "code" directory under the path to this file.
            If the code is executed in the current environment, the code must be trusted.
        lang (Optional, str): The language of the code. Default is "python".

    Returns:
        str: A summary of the files in the working directory
        image: The docker image name after container run when docker is used.
    """
    filename = re.findall(r"# filename: ([^\n]+)", code)
    if not filename:
        code_hash = md5(code.encode()).hexdigest()
        # create a file with a automatically generated name
        filename = f"tmp_code_{code_hash}.{'py' if lang.startswith('python') else lang}"
    elif isinstance(filename, list):
        filename = filename[0]
    work_dir = work_dir or WORKING_DIR
    filepath = os.path.join(work_dir, filename)
    file_dir = os.path.dirname(filepath)
    print(f"Saving code to {filepath}")
    os.makedirs(file_dir, exist_ok=True)
    if code is not None:
        with open(filepath, "w", encoding="utf-8") as fout:
            fout.write(code)
    return filename

def save_code_files(llm_message: str, work_dir: Optional[str] = None) -> List[str]:
    filenames = []
    code_files = extract_code(llm_message)
    for lang, code_block in code_files:
        if lang == 'python':
            filename = save_code(code_block, work_dir)
            filenames.append(filename)
    return filenames
def clear_working_dir(work_dir: Optional[str] = None, filename_wildcard: str = '*.py') -> None:
    """
    Clears all .py files from the specified working directory.
    If no directory is specified, the WORKING_DIR constant is used.

    After removing a .py file, if no other files are present in the directory,
    it removes the directory itself.

    Args:
        work_dir (Optional[str], optional): The directory to clear .py files from. Defaults to None.

    Returns:
        None
    """
    work_dir = work_dir or WORKING_DIR  # If work_dir is None, use WORKING_DIR

    if os.path.exists(work_dir) and os.path.isdir(work_dir):
        # Find all .py files in the working directory and subdirectories
        python_files = glob.glob(os.path.join(work_dir, '**', filename_wildcard), recursive=True)

        for file_path in python_files:
            try:
                os.remove(file_path)  # Delete the file
                print(f"Deleted {file_path}")  # Optional: printing confirmation

                # Get the directory where the file was located
                dir_path = os.path.dirname(file_path)

                # Check if the directory is empty
                if not os.listdir(dir_path):
                    # Remove the empty directory
                    os.removedirs(dir_path)
                    print(f"Removed directory {dir_path}")

            except Exception as e:
                print(f"Could not delete {file_path} due to {e}")  # Handle exceptions during file or directory deletion
    else:
        print("The specified path does not exist or it is not a directory")



def _print_formatted_field(field_name, obj):
    # Define the fixed width for the field name and the indentation for the object string
    field_width = 30
    indent = " " * 4


    if isinstance(obj, dict):
        print(f"{field_name:<{field_width}}: ")
        try:
            item_str = json.dumps(obj, indent=4)
        except TypeError:
            # Handle non-serializable objects
            item_str = str(obj)
        print(textwrap.indent(item_str, indent))

    # Check if object is a list
    elif isinstance(obj, list):
        # Print the field name with fixed width
        print(f"{field_name:<{field_width}}: ")
        # Print each dictionary in the list on its own row
        for i, item in enumerate(obj):
            if isinstance(item, dict):
                # Convert the dict to a JSON string with indentation
                try:
                    item_str = json.dumps(item, indent=4)
                except TypeError:
                    # Handle non-serializable objects
                    item_str = str(item)
                # If it's not the first item, add an extra newline for separation
                # if i > 0:
                #     print()
                # Print the dictionary with indentation
                print(textwrap.indent(item_str, indent))
            else:
                # For non-dict items in the list, print them with indentation
                print(textwrap.indent(str(item), indent))
    else:
        # Handle other objects (not lists)
        if isinstance(obj, dict):
            obj_str = json.dumps(obj, indent=4)
        else:
            obj_str = str(obj)
        print(f"{field_name:<{field_width}}: {obj_str}")
        #print(textwrap.indent(obj_str, indent))


def print_conversable_agent_state(agent: Agent):
    _print_formatted_field("_name", agent._name)
    if isinstance(agent, ConversableAgent):
        _print_formatted_field("human_input_mode", agent.human_input_mode)
        _print_formatted_field("_code_execution_config", agent._code_execution_config)
        _print_formatted_field("_max_consecutive_auto_reply", agent._max_consecutive_auto_reply)
        _print_formatted_field("_consecutive_auto_reply_counter", agent._consecutive_auto_reply_counter)
        _print_formatted_field("_max_consecutive_auto_reply_dict", agent._max_consecutive_auto_reply_dict)
        _print_formatted_field("_is_termination_msg", agent._is_termination_msg)
        _print_formatted_field("_function_map", agent._function_map)
        _print_formatted_field("_default_auto_reply", agent._default_auto_reply)
        _print_formatted_field("_reply_func_list", agent._reply_func_list)
        _print_formatted_field("reply_at_receive", agent.reply_at_receive)
        _print_formatted_field("_oai_system_message", agent._oai_system_message)
        _print_formatted_field("_oai_messages", agent._oai_messages)
        #print_formatted_field("llm_config",agent.llm_config)

