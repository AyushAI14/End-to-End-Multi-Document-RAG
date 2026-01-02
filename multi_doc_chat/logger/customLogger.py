import logging
from datetime import datetime
import os
import structlog # structured (JSON) logging

class CustomLogger:
    def __init__(self,dir='logs'):
        """
        This is a Initializing function 
        arg : dir that contain default value 'log'
        """
        # creating dir
        self.log_dir = os.path.join(os.getcwd(),dir)
        os.makedirs(self.log_dir,exist_ok=True)
        
        # creating files
        log_filename = f"{datetime.now().strftime('%m_%d_%Y_%H_%M_%S')}.log"
        self.log_file_path = os.path.join(self.log_dir,log_filename)
        
    def get_logger(self,name=__file__):
        logger_name = os.path.basename(self.log_file_path)
        
        #handlers
        file_handler = logging.FileHandler(self.log_file_path)
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(logging.Formatter("%(message)s"))

        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.INFO)
        stream_handler.setFormatter(logging.Formatter("%(message)s"))

        # global logging config
        logging.basicConfig(
            level=logging.INFO,
            format="%(message)s",
            handlers=[stream_handler, file_handler]
        )
        
        structlog.configure(
                    processors=[
                        structlog.processors.TimeStamper(fmt="iso", utc=True, key="timestamp"),
                        structlog.processors.add_log_level,
                        structlog.processors.EventRenamer(to="event"),
                        structlog.processors.JSONRenderer()
                    ],
                    logger_factory=structlog.stdlib.LoggerFactory(),
                    cache_logger_on_first_use=True,
                )
        
        return structlog.get_logger(logger_name)