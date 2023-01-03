# ZombiZoid - Discord Bot

This is a discord bot to manage the Project Zomboid Dedicated Server, allowing server update using SSH Protocol, server commands run with RCON protocol and server info retrieval with discord commands.

<p align="center">
    <image src="images/discord.png" />
</p>

The main ideia of this bot was the necessity of constantly needing to manually close and update the dedicated server whenever either the game or any of the workshop mods had an update. Giving support was also a challenge since it involved giving someone admin priviledges within the game.

In order to automate the aforementioned problems and allow a centralized manager. The ZombiZoid bot implementation was designed.

The bot runs on a Linux amd64 Oracle Cloud Server and the dedicated server runs on a Linux x64 machine. The Bot connects with the dedicated server both through RCON (in-game commands calling) and SSH (dedicated server machine management) protocols.

## Tasks

The Bot currently performs the following tasks:

- Start Server By Slash Command
- Updates Server By Slash Command
- Run in-game commands (RCON) - `zz command`