import os
import json
from src.const import auth_const, config_const
from src.services.message_HUB.message_hub import MessageHub
from src.utils.config_utils import parse_params, \
                parse_params,get_param_value, \
                validate_params, add_default_value
from collections import defaultdict

class ConfigManager:
    _instance = None

    def __new__(cls, kafka_config, kafka_topic, links_file_path=None):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
            cls._instance._initialize(links_file_path, kafka_config, kafka_topic)
        else:
            if links_file_path:
                if cls._instance._validate_links_file_path(links_file_path):
                    cls._instance._links_file_path = links_file_path
                    cls._instance.read_links_file_and_send()
        return cls._instance

    def set_links_file_path(self, links_file_path):
        """
        Set the path to the links file and read it.
        """
        if self._validate_links_file_path(links_file_path):
            self._links_file_path = links_file_path
        else:
            print(f"Invalid links file path: {links_file_path}")
        return self
    

    def _initialize(self, links_file_path, kafka_config, kafka_topic):
        self._kafka_config = kafka_config
        self._kafka_topic = kafka_topic
        self.message_hub = MessageHub(kafka_config)
        self.tasks = []
        if self._validate_links_file_path(links_file_path or ""):
            self._links_file_path = links_file_path
            self.read_links_file_and_send()

    def _validate_links_file_path(self, path):
        if  not (os.path.exists(path)):
            print(f"Invalid links file path: {path}")
            return False
        return True

    def read_links_file_and_send(self):
        folder_links, folder_limits = self.parse_links_file()
        for folder, tasks in folder_links.items():
                    for task in tasks:
                        task['max_concurrent'] = folder_limits.get(folder, config_const.MAX_CONCURRENT_DOWNLOADS_PER_FOLDER)
                        self.message_hub.send_message(self._kafka_topic, key=task["link"], value=task)


    # def _read_links_file(self, path):
    #     tasks = []
    #     folder_name = None
    #     with open(path, "r") as links_file:
    #         for line in links_file:
    #             line = line.strip()
    #             if not line:
    #                 continue
    #             if line.startswith("folder:"):
    #                 folder_name = line.split("folder:")[1].strip()
    #                 continue
    #             if not folder_name:
    #                 print("Skipping links because no folder name is specified.")
    #                 continue
    #             link, params = line.strip().split(" ", 1)
    #             param_tuples = parse_params(params)
    #             add_default_value(param_tuples, "need_authentication", "False")
    #             if eval(get_param_value(param_tuples, "need_authentication", "False")):
    #                 add_default_value(param_tuples, "cookies_path", auth_const.COOKIES_PATH)
    #                 add_default_value(param_tuples, "raw_cookies_path", auth_const.RAW_COOKIES_PATH)
    #             if not validate_params(param_tuples, ["file_name", "need_authentication"], f"Skipping invalid line: {line}"):
    #                 continue
    #             params_dict = dict(param_tuples)
    #             tasks.append({
    #                 "link": link,
    #                 "folder_name": folder_name,
    #                 "name": get_param_value(param_tuples, "file_name"),
    #                 **params_dict
    #             })
    #     return tasks

    def parse_links_file(self):
        folder_links = defaultdict(list)
        folder_limits = {}
        current_folder = None
        
        with open(self._links_file_path, "r") as links_file:
            for line in links_file:
                line = line.strip()
                if not line:
                    continue

                if line.startswith("folder:"):
                    current_folder = line.split("folder:")[1].strip()
                    continue
                    
                if line.startswith("max_concurrent:"):
                    if current_folder:
                        limit = int(line.split("max_concurrent:")[1].strip())
                        folder_limits[current_folder] = min(
                            limit,
                            config_const.MAX_CONCURRENT_DOWNLOADS
                        )
                    continue

                if not current_folder:
                    print("Skipping links because no folder name is specified.")
                    continue

                # Process link and parameters
                link, params = line.strip().split(" ", 1)
                param_tuples = parse_params(params)
                add_default_value(param_tuples, "need_authentication", "False")
                
                if eval(get_param_value(param_tuples, "need_authentication", "False")):
                    add_default_value(param_tuples, "cookies_path", auth_const.COOKIES_PATH)
                    add_default_value(param_tuples, "raw_cookies_path", auth_const.RAW_COOKIES_PATH)
                
                if not validate_params(param_tuples, ["file_name", "need_authentication"], f"Skipping invalid line: {line}"):
                    continue
                
                params_dict = dict(param_tuples)
                task = {
                    "link": link,
                    "folder_name": current_folder,
                    "name": get_param_value(param_tuples, "file_name"),
                    **params_dict
                }
                folder_links[current_folder].append(task)
                
        return folder_links, folder_limits


    def __del__(self):
        if hasattr(self, "message_hub"):
            del self.message_hub
