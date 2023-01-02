from easydict import EasyDict as edict

"""
    Commands from ProjectZomboid Dedicated Server
    - name: command name
    - args: array of command possible number of arguments
"""
zz_commands = [
    edict({"name": "players", "args": [0]}),
    edict({"name": "save", "args": [0]}),
    edict({"name": "startrain", "args": [0, 1]}),
    edict({"name": "stoprain", "args": [0]}),
    # edict({"name": "showoptions", "args": [0]}),
    edict({"name": "checkModsNeedUpdate", "args": [0]}),
    edict({"name": "servermsg", "args": [1]}),
    edict({"name": "teleport", "args": [2]}),
    edict({"name": "additem", "args": [2, 3]}),
]

zz_help = {
    "players": edict({
        "usage": "zz players",
        "description": "Get current online players"
    }),
    "save": edict({
        "usage": "zz save",
        "description": "Save current server state"
    }),
    "startrain": edict({
        "usage": "zz starrain [intensity]",
        "description": "Starts rain with intensity from 1 to 100. Intensity is optional"
    }),
    "stoprain": edict({
        "usage": "zz stoprain",
        "description": "Stops rain immediately"
    }),
    "checkModsNeedUpdate": edict({
        "usage": "zz checkModsNeedUpdate",
        "description": "Returns Log Messages from server if mods are updated or not"
    }),
    "servermsg": edict({
        "usage": 'zz servermsg "mensagem"',
        "description": "Sends a Global Message to the Server"
    }),
    "teleport": edict({
        "usage": 'zz teleport "playerA" "playerB"',
        "description": "Teleports playerA to playerB"
    }),
    "additem": edict({
        "usage": 'zz additem "player" itemID [number]',
        "description": "Adds item of ID itemID to inventory of player. If number is given adds the amount of items"
    }),
}