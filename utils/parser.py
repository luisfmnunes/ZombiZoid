import argparse

def parse_args():
    
    parser = argparse.ArgumentParser()
    
    parser.add_argument("-c", "--config", type=str, 
                        help="Config File Path", default="config/config.yaml")
    parser.add_argument("-D", "--debug", action="store_true",
                        help="Initialize on debug mode")
    
    return parser.parse_args()