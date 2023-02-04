import re
import nextcord
import socket
from nextcord.ext import commands
from nextcord import Interaction, Embed
from rcon.source import Client as rcon_cl
from rcon.exceptions import *
from .ssh import SSHCl
from utils.logger import get_logger
from .commands import *
from functools import wraps
from .navigator import nav, By
from .pages import EmbededModsPageSource, menus
from pretty_help import PrettyHelp
import sys
sys.path.append("..")
from db.db import ModsDB, Document, Query

class DiscordBot(commands.Bot):
    """
        A class that stores a discord client and bot info
    """
    
    def __init__(self, config, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._config = config
        self.logger = get_logger()
        
        # SSH Channels to invoke server (keeps listening) and ping commands
        self.ssh_cl = SSHCl(config)
        self.ssh_server = SSHCl(config) # SSH Channel always open to keep server running
        
        # Buffers of server invoke
        self.server_stdio = None
        self.server_stdout = None
        self.server_stderr = None
        
        # TinyDB Mods Database initialization
        self.mods = ModsDB("db/mods/mods.json", indent=4)
        
        # SSH common functions
        @self.ssh_cl.ping_command(f"pgrep -u {config['ssh_user']} {config['start_file']}")
        def ping_pgrep(streams, *args, **kwargs):
            stdout, stderr = streams
            self.logger.debug(stdout)
            self.logger.debug(stderr)
            message = None
            proc = next(iter(stdout), None)
            if len(stdout):
                message = f"Server running on proccess {proc}"
            elif stderr:
                message = f"Errors found on command: {stderr}"
            else:
                message = f"Server is not running"

            return message, proc
        
        self.pgrep = ping_pgrep
        
    
    async def on_ready(self):
        self.logger.info(f"{self.user} has connected to Discord")

    # async def on_message(self, message : nextcord.message.Message):
    #     self.logger.debug(message)
    #     if not message.author == self.user:
    #         await message.channel.send("Hmm... Coquinha Gelada")
    
    async def on_command_error(self, context: commands.Context, exception: commands.errors.CommandError) -> None:
        if isinstance(exception, commands.CommandNotFound):
            await context.message.add_reaction("\N{CROSS MARK}")
            await context.send("Command Not Found")
        else:
            self.logger.debug(exception)
    
    def local_run(self):
        self.run(self._config["bot_token"])

    def get_mod_by_url(self, url):
        id_regex =              re.compile(r"id=(\d{9,11})")
        workshop_regex =        re.compile(r"Workshop ID: (\d{9,11})")
        mod_regex =             [re.compile(r"Mod ID: (\w+)"), re.compile(r"ModID: (\w+)")]
        map_regex =             re.compile(r"Map Folder: (\w+)")
        
        mod_id = id_regex.findall(url)
        if not mod_id:
            self.logger.debug(f"Expected URL from a Steam Workshop Mod. {url}")
            
            raise ValueError(f"Expected URL from a Steam Workshop Mod. {url}")
        else:
            mod_id = next(iter(mod_id))
            
        self.logger.debug(f"Mod ID Found: {mod_id}")
        
        nav.get(url)
        
        result = nav.find_element(By.ID, 'highlightContent').text
        title = nav.find_element(By.CLASS_NAME, 'workshopItemTitle').text
        
        for reg in mod_regex:
          text_mod_id = reg.findall(result)
          if text_mod_id:
            break
        text_workshop_id = workshop_regex.findall(result)
        map_folder = map_regex.findall(result)
        
        self.logger.debug(f"Mod Title: {title}; Workshop ID: {mod_id}; Mod ID(s): {', '.join(text_mod_id)}")
        
        return text_workshop_id, title, text_mod_id, map_folder


async def fail_response(ctx: commands.Context, message: str = None):
    await ctx.message.clear_reaction("⏳")
    await ctx.message.add_reaction("\N{CROSS MARK}")
    if message:
        await ctx.send(message)

async def success_response(ctx: commands.Context, message: str = None):
    await ctx.message.clear_reaction("⏳")
    await ctx.message.add_reaction("\N{WHITE HEAVY CHECK MARK}")
    if message:
        await ctx.send(message)
    

def get_bot(config, *args, **kwargs):
    
    intent = nextcord.Intents.default()
    intent.message_content = True
    bot = DiscordBot(config, 
                     intents=intent, 
                     help_command=PrettyHelp(
                       show_index=False), 
                     *args, 
                     **kwargs)
    
    @bot.slash_command(name="status", description="Returns Bot Status", guild_ids=[config["guild_id"]])
    async def status(interaction: Interaction):
        await interaction.response.send_message("Bot Loaded and Runnning")
    
    @bot.slash_command(name="running", description="Returns if the PZ Server is Runnning", guild_ids=[config["guild_id"]])
    async def running(intercation: Interaction):
        
        await intercation.response.defer()
        @bot.ssh_cl.ping_command(f"pgrep -u {config['ssh_user']} {config['start_file']}")
        def ping_pgred(streams, *args, **kwargs):
            stdout, stderr = streams
            bot.logger.debug(stdout)
            bot.logger.debug(stderr)
            message = None
            if len(stdout):
                message = f"Server running on proccess {stdout[0]}"
            elif stderr:
                message = f"Errors found on command: {stderr}"
            else:
                message = f"Server is not running"

            return message
        try:
          message = ping_pgred()
        except:
          message = f"Failed to communicate with server {config['server']}"
        
        await intercation.followup.send(content= message)
    
    @bot.slash_command(name="restart", description="Restarts the server on runner", guild_ids=[config["guild_id"]])
    async def restart(interaction: Interaction):
        
        await interaction.response.defer()
        @bot.ssh_cl.ping_command(f"pgrep -u {config['ssh_user']} {config['start_file']}")
        def ping_pgred(streams, *args, **kwargs):
            stdout, _ = streams
            bot.logger.debug(stdout)
            return next(iter(stdout), None)
        
        proc = ping_pgred()
        
        @bot.ssh_cl.ping_command(f"kill -9 {proc}")
        def kill_server(streams, *args, **kwargs):
            stdout, _ = streams
            bot.logger.debug(stdout)
            return stdout
        
        if proc:
            await interaction.followup.send(content=f"Server Running on {proc}. Restarting...")
            # await interaction.response.send_message(kill_server())
            kill_server()
        else:
            await interaction.followup.send(content="No Server Running. Initializing Server")

        bot.server_stdio, bot.server_stdout, bot.server_stderr = bot.ssh_server.attached_command(
            "/".join([
                config["start_path"], 
                config["start_file"]
                ])
        )
        
        bot.server_stdio.close()
        
        bot.logger.info("Server Started")
        
    @bot.slash_command(name="update", description="Update Server on runner", guild_ids=[config["guild_id"]])
    async def update(interaction: Interaction):
        
        await interaction.response.defer()
        @bot.ssh_cl.ping_command(f"pgrep -u {config['ssh_user']} {config['start_file']}")
        def ping_pgred(streams, *args, **kwargs):
            stdout, _ = streams
            bot.logger.debug(stdout)
            return next(iter(stdout), None)
        
        proc = ping_pgred()
        
        @bot.ssh_cl.ping_command(f"kill -9 {proc}")
        def kill_server(streams, *args, **kwargs):
            stdout, _ = streams
            bot.logger.debug(stdout)
            return stdout
        
        if proc:
            kill_server()
        
        await interaction.send("Updating Server:")
        
        @bot.ssh_cl.ping_command(f"steamcmd +runscript {config['update_script']}")
        def update_server(streams, *args, **kwargs):
            stdout, _ = streams
            bot.logger.debug(stdout)
            return stdout

        messages = update_server()
        await interaction.send("\n".join(messages))
        bot.server_stdio, bot.server_stdout, bot.server_stderr = bot.ssh_server.attached_command(
            "/".join([
                config["start_path"], 
                config["start_file"]
                ])
        )
        
        bot.server_stdio.close()
        
        await interaction.followup.send(content="Server Updated")
        bot.logger.info("Server Started")
        
    # @bot.command(name="info")
    # async def help(ctx: commands.Context, *args):
    #     command = next(iter(args), None)
    #     await ctx.message.add_reaction("⏳")
    #     if command and not command in zz_help:
    #         await fail_response(ctx, f"Command **{command}** Not Found")
    #     elif command and command in zz_help:
    #         message = f"Command **{command}**:\n{'-'*2} Usage: {zz_help[command].usage}\n{'-'*2} Description: {zz_help[command].description}"
    #         await success_response(ctx, message)
    #     else:
    #         message = ""
    #         for command in zz_help:
    #             message += f"Command **{command}**:\n{'-'*2} Usage: {zz_help[command].usage}\n{'-'*2} Description: {zz_help[command].description}\n\n"
    #         await success_response(ctx, message)

    @bot.command(name="log",
                usage=zz_help["log"].usage,
                description=zz_help["log"].description,
                brief=zz_help["log"].brief,
                help=zz_help["log"].help)
    async def log(ctx: commands.Context, *args):
        count = 5
        if len(args):
            count = int(next(iter(args)))
        await ctx.message.add_reaction("⏳")
        if bot.server_stdout:
            bot.server_stdout.channel.settimeout(10) # sets interval to wait for new messages
            last_lines = list()
            try:
                for line in iter(bot.server_stdout.readline, ""):
                    last_lines.append(line)
                    bot.logger.debug(line)
            except:
                pass
            
            last_lines = last_lines[-count:]
            # Checks Wheter maximum Embed description size is reached
            while sum(len(line) for line in last_lines) >= 4096:
              last_lines = last_lines[1:]
            message = "".join(last_lines)
            
            if not message:
                message = "No new Logs Available"
            
            await success_response(ctx, f"Retrieved {len(last_lines)} log lines")
            if len(message) > 2000:
              embed = Embed(description=message, colour = nextcord.Colour.purple())
              await ctx.send(embed = embed)
            else:
              await ctx.send(f"```{message}```")
        
        else:
            await fail_response(ctx, "Server not Running.")
        
    @bot.command(name="add_mod",
                usage=zz_help["add_mod"].usage,
                description=zz_help["add_mod"].description,
                brief=zz_help["add_mod"].brief,
                help=zz_help["add_mod"].help)
    async def addmod(ctx: commands.Context, *args):
        
        bot.logger.debug(f"add_mod. Command Arguments: {args}")
        await ctx.message.add_reaction("⏳")
        
        if len(args) != 1:
            await fail_response(ctx, "Invalid number of arguments for command add_mod")
            return
        
        url = args[0]
        
        
        try:
            mod_id, title, text_mod_id, map_folder = bot.get_mod_by_url(url)
            mod_id = next(iter(mod_id))
        except Exception as e:
            bot.logger.debug(e)
            await fail_response(ctx, f"{e}. Cannot Navigate URL")
            return
            
        if map_folder:
            await fail_response(ctx, "Cannot Handle Map Mods Yet")
            return
        
        bot.logger.debug(f"URL Data: {mod_id} {title} {text_mod_id} {map_folder}")
        if not bot.mods.contains(doc_id=mod_id):
            bot.mods.insert(Document(
                {
                    'id': mod_id,
                    'title': title,
                    'url': url,
                    'mods': text_mod_id,
                    'map': None,
                },
                doc_id=mod_id))
        else:
            await fail_response(ctx, f"Mod {title} is already added to the server")
            return
        bot.logger.debug("Reading remote server file")
        sconfig_lines = bot.ssh_cl.read_remote_file(config["server_file"])
        mod_line = next(i for i, l in enumerate(sconfig_lines) if re.search(r"^Mods=", l))
        id_line = next(i for i, l in enumerate(sconfig_lines) if re.search(r"^WorkshopItems", l))

        bot.logger.debug("Filling remote server file with new mod data")
        if ";" in sconfig_lines[mod_line]:
            sconfig_lines[mod_line] =  ";".join([sconfig_lines[mod_line].strip()] + text_mod_id) + "\n"
            sconfig_lines[id_line] = ";".join([sconfig_lines[id_line].strip(), mod_id]) + "\n"
        else:
            sconfig_lines[mod_line] = sconfig_lines[mod_line].strip() + ";".join(text_mod_id) + "\n"
            sconfig_lines[id_line] = sconfig_lines[id_line] + mod_id + "\n"
            
        bot.ssh_cl.write_remote_file(config["server_file"], "".join(sconfig_lines))
        await success_response(
            ctx,
            f"Mod Title: {title}\nWorkshop ID: {mod_id}\nMod ID(s): {', '.join(text_mod_id)}"    
        )

    @bot.command(name="remove_mod",
                usage=zz_help["remove_mod"].usage,
                description=zz_help["remove_mod"].description,
                brief=zz_help["remove_mod"].brief,
                help=zz_help["remove_mod"].help
                )
    async def remove_mod(ctx: commands.Context, *args):
        
        bot.logger.debug(f"remove_mod. Command Arguments: {args}")
        await ctx.message.add_reaction("⏳")
        if len(args) != 1:
            await fail_response(ctx, "Wrong number of arguments for remove_mod")
            await ctx.send("Check usage with zz help remove_mod")
            return
        
        arg = next(iter(args))
        q = Query()
        
        remove_entity = bot.mods.search(q.id == arg) or bot.mods.search(q.title == arg)
        if not remove_entity:
            await fail_response(ctx, f"Unable to find {arg} id or title")
            return
        
        remove_entity = next(iter(remove_entity))

        bot.logger.debug(f"Removing Entity {remove_entity}")
        
        bot.mods.remove(doc_ids=[int(remove_entity["id"])])
        
        sconfig_lines = bot.ssh_cl.read_remote_file(config["server_file"])
        mod_line = next(i for i, l in enumerate(sconfig_lines) if re.search(r"^Mods=", l))
        id_line = next(i for i, l in enumerate(sconfig_lines) if re.search(r"^WorkshopItems", l))

        ids = [a["id"] for a in bot.mods.all()]
        mods = [name for workshop in bot.mods.all() for name in workshop["mods"]]

        bot.logger.debug(f"Writing changes to server config file")

        sconfig_lines[mod_line] = f"Mods={';'.join(mods)}\n"
        sconfig_lines[id_line] = f"WorkshopItems={';'.join(ids)}\n"

        bot.ssh_cl.write_remote_file(config["server_file"], "".join(sconfig_lines))

        await success_response(ctx, f"Removed mod {remove_entity['title']} ({remove_entity['id']})")

    @bot.command(name="list_mod",
                usage=zz_help["list_mod"].usage,
                description=zz_help["list_mod"].description,
                brief=zz_help["list_mod"].brief,
                help=zz_help["list_mod"].help)
    async def list_mod(ctx: commands.Context, *args):
        
        bot.logger.debug(f"list_mod. Command Arguments: {args}")
        await ctx.message.add_reaction("⏳")
        
        mods = bot.mods.all()
        mods = ([f"{mod['id'] or ERROR}: {mod['title'] or ERROR}" for mod in mods])
        
        if not mods:
            await fail_response(ctx, "No mods found on server")
        
        else:
            #message = ""
            await success_response(ctx, f"Total of {len(mods)} Mods on Server")
#            for mod in mods:
#              if len(message + mod) > 2000:
#                await ctx.send(message)
#                message = mod
#              else:
#                message = "\n".join([message, mod])
#            await ctx.send(message)
            pages = menus.ButtonMenuPages(
                source = EmbededModsPageSource(mods),
            )

            await pages.start(ctx)
    
    # RCON Command Factory
    def function_builder(cmd):
        @bot.command(name=cmd.name, 
                    usage=zz_help[cmd.name].usage, 
                    description=zz_help[cmd.name].description,
                    brief=zz_help[cmd.name].brief,
                    help=zz_help[cmd.name].help)
        async def SendMessage(ctx: commands.Context, *args):
            bot.logger.debug(ctx.message)
            bot.logger.debug(f"Command Arguments: {args}")
            bot.logger.debug(cmd)
            await ctx.message.add_reaction("⏳")
            
            # adds double quotes to arguments that contains space
            args = [f'"{a}"' if " " in a else f"{a}" for a in args]
            
            if len(args) not in cmd.args:
                await fail_response(ctx, f"Invalid number of arguments for command {cmd.name}")
                return
            
            try:                
                with rcon_cl(config["server"], 
                             config["rcon_port"], 
                             passwd=config["rcon_pwd"], 
                             timeout=config["rcon_timeout"]) as cl:
                    message = cl.run(cmd.name, *args)
                    bot.logger.debug(f"Command Response: {message}")
                
                # specific behaviour from checkModsNeedUpdate that writes to server log
                if cmd.name == "checkModsNeedUpdate": 
                    if bot.server_stdout:
                        await ctx.send(message)
                        message = None
                        bot.server_stdout.channel.settimeout(3) # sets interval to wait for new messages
                        try:
                            logs = list()
                            for line in iter(bot.server_stdout.readline, ""):
                                if("CheckMods" in line):
                                  # await ctx.send(line)
                                    logs.append(line)
                                    bot.logger.debug(line)
                        except Exception as e:
                            pass
                        message = f"```{''.join(logs)}```"
                await success_response(ctx)
            except Exception as e:
                bot.logger.warning(e)
                message = f"Error communicating with Project Zomboid Bilulu Server.\n{e}"
                
                await fail_response(ctx)
                
            if message:       
                await ctx.send(message)
        
        return SendMessage
        
    for cmd in zz_commands:
        function_builder(cmd)
    
    return bot
