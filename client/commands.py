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
        "usage": "",
        "description": "Get current online players",
        "brief": "See online players",
        "help": "This command sends an RCON command to the server to retrieve the players currently online."
    }),
    "save": edict({
        "usage": "",
        "description": "Save current server state",
        "brief": "Saves the server",
        "help": "Sends an RCON command to the server to save the current game state."
    }),
    "startrain": edict({
        "usage": "[intensity]",
        "description": "Starts rain with intensity from 1 to 100. Intensity is optional",
        "brief": "Start rain on game",
        "help": """The command starts rain on the server. The intensity of the rain is an optional argument represented by a number from 1 to 100, where lower numbers means lighter rains and higher numbers means heavier rains. 

                Example: zz start 50 """
    }),
    "stoprain": edict({
        "usage": "",
        "description": "Stops rain immediately",
        "brief": "Stops rain on game",
        "help": "The command sends an RCON command to stop the rain on the game."
    }),
    "checkModsNeedUpdate": edict({
        "usage": "",
        "description": "Returns Log Messages from server if mods are updated or not",
        "brief": "Checks if Mods are Up to Date",
        "help": """A command that checks if mods are up to date. The command reads the output log from the server application and redirects to the discord channel as bot messages. The logs will tell whether the mods are updated or not."""
    }),
    "servermsg": edict({
        "usage": '"mensagem"',
        "description": "Sends a Global Message to the Server",
        "brief": "Sends a message to the server",
        "help": """Sends a global message to the server. The message must be around quotes ("mesage") because of the way arguments are handled (each space is a new argument to the command)."""
    }),
    "teleport": edict({
        "usage": '"playerA" "playerB"',
        "description": "Teleports playerA to playerB",
        "brief": "Teleports Player A to Player B",
        "help": """This commands teleports player A to player B. Since player names might contain spaces it is strongly recommended the use of quotes around player names (e.g. "player name"). 

                Example: zz teleport "Hakuna Mortata" "yoshi" """
    }),
    "additem": edict({
        "usage": '"player" itemID [number]',
        "description": "Adds item of ID itemID to inventory of player. If number is given adds the amount of items",
        "brief": "Gives Item to a Player",
        "help": """This commands sends an RCON to the server to add an item to a player inventory. This command has 2 or 3 arguments: 
                   - The first is the name of the player (recommended between quotes "player name")
                   - The second is the item name (check https://pzwiki.net/wiki/Items)
                   - [Optional] The third is the optional number of items (if not given will add 1 item) 

                   Example: zz additem "KombiV8" Base.Axe 3 
                   - The above adds 3 axes to player KombiV8 inventory. """
    }),
    "log": edict({
        "usage": "[lines]",
        "description": "Returns Server last Log Messages",
        "brief": "Gets Server Logs",
        "help": """This command gets the last [lines] log messages and prints back at the called discord channel.
                    The number of messages [lines] is optional and if not given will return 5 messages.
                    This command may take long if the server is initializing because it keeps listening to the server and only timesout after 10 seconds without arrival of new messages.
                    After this commands is called the output buffer of the server is consumed therefore it won't be able to retrieve back previous messages.
                    
                    Example: zz log 10
                    - The above example returns 10 last Log Messages, if exists else returns all the lines available"""
    }),
    "add_mod": edict({
        "usage": "url",
        "description": "Adds a mod from Steam Workshop from URL",
        "brief": "Adds a Mod to server",
        "help": """This commands receives a URL from a Steam Workshop Mod and adds it to the server.
                    The URL must be a valid Steam Workshop Mod URL else it returns an error.
                    In case of mods already added to server, the command informs mod already added.
                    **ATTENTION**: The Server must be restarted in order for changes take effect (download mod files).
                    
                    Example: zz add_mod https://steamcommunity.com/sharedfiles/filedetails/?id=2200148440
                    - The example above adds Brita's Weapon Pack mod"""
    }),
    "remove_mod": edict({
        "usage": "mod ID || mod Title",
        "description": "Removes a mod from the server with ID or Title",
        "brief":"Removes a mod from the server",
        "help":"""This command removes a mod from the server initialization file.
                The removal can be done either by giving the mod ID or mod Title.
                Both information are obtained from the zz list_mod command.
                
                Examples: 
                - zz remove_mod 2745691230
                - zz remove_mod "Title of the mod" """
    }),
    "list_mod": edict({
        "usage": "",
        "description": "Returns an Interactive List of Mods",
        "brief": "Returns a List of Added Mods",
        "help": """The command returns an interactive list with multiple pages of the mods added to the server and inserted on Database.
                    If the server is reseted, the new initialization file may be Unsynchronized with the Database."""
    })
}
