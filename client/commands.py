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
        "description": "Get current online players",
        "brief": "See online players",
        "help": "This command sends an RCON command to the server to retrieve the players currently online."
    }),
    "save": edict({
        "usage": "zz save",
        "description": "Save current server state",
        "brief": "Saves the server",
        "help": "Sends an RCON command to the server to save the current game state."
    }),
    "startrain": edict({
        "usage": "zz starrain [intensity]",
        "description": "Starts rain with intensity from 1 to 100. Intensity is optional",
        "brief": "Start rain on game",
        "help": "The command starts rain on the server. The intensity of the rain is an optional argument \
                represented by a number from 1 to 100, where lower numbers means lighter rains and higher \
                numbers means heavier rains. (e.g. zz start 50 - starts rain with intensity 50)."
    }),
    "stoprain": edict({
        "usage": "zz stoprain",
        "description": "Stops rain immediately",
        "brief": "Stops rain on game",
        "help": "The command sends an RCON command to stop the rain on the game."
    }),
    "checkModsNeedUpdate": edict({
        "usage": "zz checkModsNeedUpdate",
        "description": "Returns Log Messages from server if mods are updated or not",
        "brief": "Checks if Mods are Up to Date",
        "help": "A command that checks if mods are up to date. The command reads the output log from the \
                server application and redirects to the discord channel as bot messages. The logs will tell \
                whether the mods are updated or not."
    }),
    "servermsg": edict({
        "usage": 'zz servermsg "mensagem"',
        "description": "Sends a Global Message to the Server",
        "brief": "Sends a message to the server",
        "help": 'Sends a global message to the server. The message must be around quotes ("mesage") because \
                of the way arguments are handled (each space is a new argument to the command).'
    }),
    "teleport": edict({
        "usage": 'zz teleport "playerA" "playerB"',
        "description": "Teleports playerA to playerB",
        "brief": "Teleports Player A to Player B",
        "help": 'This commands teleports player A to player B. Since player names might contain spaces \
                it is strongly recommended the use of quotes around player names (e.g. "player name"). \
                (e.g. zz teleport "Hakuna Mortata" "yoshi").'
    }),
    "additem": edict({
        "usage": 'zz additem "player" itemID [number]',
        "description": "Adds item of ID itemID to inventory of player. If number is given adds the amount of items",
        "brief": "Gives Item to a Player",
        "help": 'This commands sends an RCON to the server to add an item to a player inventory. This command has \
                2 or 3 arguments. The first is the name of the player (recommended between quotes "player name"), \
                the second is the item name (check https://pzwiki.net/wiki/Items), and the third is the optional \
                number of items (if not given will add 1 item). (e.g. zz additem "KombiV8" Base.Axe 3 - adds 3 \
                axes to player KombiV8 inventory).'
    }),
}