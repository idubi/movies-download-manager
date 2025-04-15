from message_hub import MessageHub
import os
import json
import const.auth_const   as auth_const
import const.config_const   as config_const


def parse_params (params):
    param_tuples = []
    for param in params.split(" "):
        if "=" in param:
            key, value = param.split("=")
            # Strip any quotes and whitespace
            key = key.strip()
            value = value.strip('"').strip()
            param_tuples.append((key, value)) 
    return param_tuples

def get_param_value(param_tuples, key, default=None):
    """
    Gets a value from param_tuples by key
    Args:
        param_tuples: List of tuples containing (key, value) pairs
        key: Key to look up
        default: Default value if key not found
    Returns:
        Value for the key or default if not found
    """
    params_dict = dict(param_tuples)
    return params_dict.get(key, default)

def validate_params (param_tuples,mandatory_parameters, error_message):
    """
    Validates the parameters in the param_tuples list.
    """
    param_keys = [key for key, _ in param_tuples]
    for mandatory_param in mandatory_parameters:
        if mandatory_param not in param_keys:
            print(f"{error_message} - Missing mandatory parameter: {mandatory_param}")
            return False
    return True

def add_default_value(param_tuples, key, default_value):
    """
    Adds a default value for a key if it doesn't exist in the param_tuples
    Args:
        param_tuples: List of tuples containing (key, value) pairs
        key: Key to check for
        default_value: Default value to add if key is missing
    Returns:
        Updated param_tuples list
    """
    if not any(k == key for k, _ in param_tuples):
        param_tuples.append((key, default_value))

     
def read_links_file(links_file_path):
    """
    Reads the links file and returns a list of download tasks.
    Each task is a dictionary containing the link, name, and folder name.
    """
    if not os.path.exists(links_file_path):
        raise FileNotFoundError(f"Links file not found: {links_file_path}")

    tasks = []
    folder_name = None

    with open(links_file_path, "r") as links_file:
        for line in links_file:
            line = line.strip()
            if not line:
                continue

            # Check if the line specifies the folder name
            if line.startswith("folder:"):
                folder_name = line.split("folder:")[1].strip()
                continue

            # Ensure a folder name has been set
            if not folder_name:
                print("Skipping links because no folder name is specified.")
                continue

            # Parse the link and name
            link, params = line.strip().split(" ",1)
            param_tuples = parse_params(params)
            add_default_value(param_tuples, "need_authentication", "False")
            # if parameter is true then add the path to authentication files
            if eval(get_param_value(param_tuples, "need_authentication","False")) :
                add_default_value(param_tuples, "cookies_path", auth_const.COOKIES_PATH)
                add_default_value(param_tuples, "raw_cookies_path", auth_const.RAW_COOKIES_PATH)

           
            if not validate_params(param_tuples,["file_name","need_authentication"] ,"Skipping invalid line: {line}"):
                continue

            params_dict = dict(param_tuples)
            

            tasks.append({"link": link, 
                         "folder_name": folder_name,
                        "name": get_param_value(param_tuples, "file_name"),
                        **params_dict,
                            })
            

    return tasks


if __name__ == "__main__":
    # Kafka configuration
    kafka_config = {
        "bootstrap.servers": "localhost:9092",  # Replace with your Kafka server
    }
    kafka_topic = "download-requests"

    # Initialize the Message Hub
    message_hub = MessageHub(kafka_config)

    # Read tasks from the links file
    # links_file_path = "./resources/links-tests.txt"
    links_file_path = config_const.LINKS_FILE_PATH
    tasks = read_links_file(links_file_path)

    # Send tasks to Kafka
    for task in tasks:
        message_hub.send_message(kafka_topic, key=task["link"], value=task)
