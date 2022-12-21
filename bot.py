"""
    This is the main file from the discord bot ZombiZoid
"""

import os
import yaml

from utils import logger, parser
from client.client import get_bot
    
if __name__ == "__main__":
    
    args = parser.parse_args()
    log = logger.get_logger(args.debug)
    
    with open(args.config, "r") as stream:
        try:
            config = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            log.error(f"Failed to parse file {args.config}")
            print(exc)
            exit(-1)
            
    for k,v in config.items():
        log.debug(f"{k}: {v}")
        
    bot = get_bot(config, command_prefix=["zz "])
    bot.local_run()
