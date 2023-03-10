# Client

The [client](client.py) is the core application of this bot, it contains the bot object instatiation as well as all attributes and commands behaviours.

## Mods DataBase

The mods database is composed by a TinyDB which is a document oriented databased, representing a lightweight solution for small databases in order to run os low specs cloud environments.

## Commands

The Bot is built-in with a batch of commands of two categories, slash commands and prefix commands. Slash Commands are usually comands related to the bot and dedicated server machine management, while prefix commands are in-game commands launched with RCON protocol and mod related commands.

## Slash Commands

<p align="center">
    <image src="../images/slashcommands.png" />
</p>

Slash commands are usually used for bot management and control. Thus in Zombizoid these are responsible for high level management applications, such as restarting, updating or checking if the server is online.

- /restart - This command restarts the Zomboid Dedicated Server on the server machine.
- /running - This command verifies if a Zomboid Dedicated Server Instance is running on the server machine
- /status - This command returns the status of the Bot Application, checking if everying is in order
- /update - This command invokes steamcmd on the Server Machine to update the Zomboid Dedicated Server Files

## Prefix Commands (zz Commands)

This section covers the in-games commands, also denominated zz commands due to the prefix of the bot. Here are some of the following commands:

- ### zz help

This is the main command in order to explore the other implemented commands, their syntax and the expected behaviour.

- ### zz add_mod

One of the main features of zombizoid bot is to automatically web scrap steam workshop pages, extract the crucial info required by the Zomboid Dedicated Server initialization file, and automatically add the given mod to the server. In order for changes to be applied the server must be restarted.

- ### zz list_mod

Don't know which mods are currently installed in the Server? No worries! This command gives an interactive Discord Embbed that displays ALL the server's mods.

- ### zz checkModsNeedUpdate

One problem every Zomboid player might have faces when playing on modded servers are the incompatible versions of the player's client and the dedicated server. This command checks if any mods needs update, and if positive allows the player to restart the server instance in order to forward the mods' updates.

- ### zz log

Want to Retrieve the latest info from Zomboid Dedicated Server Console? The log zz commands allow it to be done. Since Discord has Character Limits, if the logs surpass this limitation, only the possible incoming logs will be sent.

- ### zz players

More of a team player and only want to join the server when your friends are being bitten?? Then check if any friends are playing first with this command.

There are other zz commands available which are mostly related with in-game behaviours, so if you wanna check all available commands, resort to the first zz command of this list.