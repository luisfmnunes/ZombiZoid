from easydict import EasyDict as edict

"""
    Commands from ProjectZomboid Dedicated Server
    - name: command name
    - args: array of command possible number of arguments
"""
zz_commands = [
    edict({"name": "players", "args": [0]}),
    edict({"name": "save", "args": [0]}),
    edict({"name": "startrain", "args": [0]}),
    edict({"name": "stoprain", "args": [0]}),
    edict({"name": "showoptions", "args": [0]}),
    edict({"name": "servermsg", "args": [1]}),
    edict({"name": "additem", "args": [2]}),
]