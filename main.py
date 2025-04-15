# main.py
# from src.services.config_manager import ConfigManager
from config_manager import ConfigManager
import src.const.config_const as config_const

def main():
    config_manager = ConfigManager(config_const.KAFKA_CONFIG, 
                                   config_const.KAFKA_TOPIC_DOWNLOAD_REQUESTS)
    config_manager.set_links_file_path(config_const.LINKS_FILE_PATH)
    config_manager.read_links_file_and_send()
    

    

if __name__ == "__main__":
    main() 