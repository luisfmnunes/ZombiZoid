import re
import nextcord
import socket
from nextcord.ext import commands
from nextcord import Interaction
from rcon.source import Client as rcon_cl
from rcon.exceptions import *
from .ssh import SSHCl
from utils.logger import get_logger
from .commands import *
from functools import wraps
from .navigator import nav, By

class DiscordBot(commands.Bot):
    """
        A class that stores a discord client and bot info
    """
    def __init__(self, config, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config = config
        self.logger = get_logger()
        self.ssh_cl = SSHCl(config)
        self.ssh_server = SSHCl(config)
        
        self.server_stdio = None
        self.server_stdout = None
        self.server_stderr = None
        
        # self.nav = nav
    
    async def on_ready(self):
        self.logger.info(f"{self.user} has connected to Discord")

    # async def on_message(self, message : nextcord.message.Message):
    #     self.logger.debug(message)
    #     if not message.author == self.user:
    #         await message.channel.send("Hmm... Coquinha Gelada")
    
    async def on_command_error(self, context: commands.Context, exception: commands.errors.CommandError) -> None:
        if isinstance(exception, commands.CommandNotFound):
            await context.send("Command Not Found")
        else:
            self.logger.debug(exception)
    
    def local_run(self):
        self.run(self.config["bot_token"])

    def rcon_command(self, function):
        @wraps(function)
        def inner(*args, **kwargs):
            try:
                host, port, pwd, timeout = self.config.get("server"), self.config.get("rcon_port"), self.config.get("rcon_pwd"), self.config.get("rcon_timeout")
                rcon_client = rcon_cl(host, port, pwd, timeout)
                function(rcon_client = rcon_client)
            except (ConfigReadError, SessionTimeout, UserAbort, WrongPassword, socket.timeout) as e:
                function(exception = e)

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
    bot = DiscordBot(config, intents=intent,*args, **kwargs)
    
    @bot.slash_command(name="status", description="Returns Bot Status", guild_ids=[config["guild_id"]])
    async def status(interaction: Interaction):
        await interaction.response.send_message("Bot Loaded and Runnning")
    
    @bot.slash_command(name="running", description="Returns if the PZ Server is Runnning", guild_ids=[config["guild_id"]])
    async def running(intercation: Interaction):
        
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
        
        message = ping_pgred()
        
        await intercation.response.send_message(message)
    
    @bot.slash_command(name="restart", description="Restarts the server on runner", guild_ids=[config["guild_id"]])
    async def restart(interaction: Interaction):
        
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
            await interaction.response.send_message(f"Server Running on {proc}. Restarting...")
            # await interaction.response.send_message(kill_server())
            kill_server()
        else:
            await interaction.response.send_message("No Server Running. Initializing Server")

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
        
        bot.logger.info("Server Started")
        
    @bot.command(name="info")
    async def help(ctx: commands.Context, *args):
        command = next(iter(args), None)
        await ctx.message.add_reaction("⏳")
        if command and not command in zz_help:
            await fail_response(ctx, f"Command **{command}** Not Found")
        elif command and command in zz_help:
            message = f"Command **{command}**:\n{'-'*2} Usage: {zz_help[command].usage}\n{'-'*2} Description: {zz_help[command].description}"
            await success_response(ctx, message)
        else:
            message = ""
            for command in zz_help:
                message += f"Command **{command}**:\n{'-'*2} Usage: {zz_help[command].usage}\n{'-'*2} Description: {zz_help[command].description}\n\n"
            await success_response(ctx, message)

    @bot.command(name="log")
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
            message = "\n".join(last_lines)
            
            if not message:
                message = "No new Logs Available"
            
            await success_response(ctx, message)
        
        else:
            await fail_response(ctx, "Server not Running.")
        
    @bot.command(name="addmod")
    async def addmod(ctx: commands.Context, *args):
        
        bot.logger.debug(f"addmod. Command Arguments: {args}")
        await ctx.message.add_reaction("⏳")
        
        if len(args) != 1:
            await fail_response(ctx, "Invalid number of arguments for command addmod")
            
            return
        
        url = args[0]
        
        id_regex =              re.compile(r"id=(\d{10})")
        workshop_regex =     re.compile(r"Workshop ID: (\d{10})")
        mod_regex =          re.compile(r"Mod ID: (\w+)")
        map_regex =             re.compile(r"Map Folder: (\w+)")
        
        mod_id = id_regex.findall(url)
        if not mod_id:
            bot.logger.debug(f"Expected URL from a Steam Workshop Mod. {url}")
            await fail_response(ctx, "Invalid URL. Expect URL from a Steam Workshop Mod")
            
            return
        else:
            mod_id = next(iter(mod_id))
            
        bot.logger.debug(f"Mod ID Found: {mod_id}")
        try:
            nav.get(url)
            
            result = nav.find_element(By.ID, 'highlightContent').text
            title = nav.find_element(By.CLASS_NAME, 'workshopItemTitle').text
            
            text_mod_id = mod_regex.findall(result)
            text_workshop_id = workshop_regex.findall(result)
            map_folder = map_regex.findall(result)
            
            bot.logger.debug(f"Mod Title: {title}\nWorkshop ID: {mod_id}\nMod ID(s): {', '.join(text_mod_id)}")
            
        except Exception as e:
            bot.logger.debug(e)
            await fail_response(ctx, "Cannot Navigate URL")
            
        if map_folder:
            await fail_response(ctx, "Cannot Handle Map Mods Yet")
            
        await success_response(
            ctx,
            f"Mod Title: {title}\nWorkshop ID: {mod_id}\nMod ID(s): {', '.join(text_mod_id)}"    
        )
    
    # RCON Command Factory
    def function_builder(cmd):
        @bot.command(name=cmd.name)
        async def SendMessage(ctx: commands.Context, *args):
            bot.logger.debug(ctx.message)
            bot.logger.debug(f"Command Arguments: {args}")
            bot.logger.debug(cmd)
            await ctx.message.add_reaction("⏳")
            
            # adds double quotes to arguments that contains space
            args = [f'"{a}"' for a in args if " " in a]
            
            if len(args) not in cmd.args:
                await fail_response(ctx, f"Invalid number of arguments for command {cmd.name}")
                
                return
            
            try:                
                with rcon_cl(bot.config["server"], 
                             bot.config["rcon_port"], 
                             passwd=bot.config["rcon_pwd"], 
                             timeout=bot.config["rcon_timeout"]) as cl:
                    message = cl.run(cmd.name, *args)
                    bot.logger.debug(f"Command Response: {message.splitlines()[0]}")
                
                # specific behaviour from checkModsNeedUpdate that writes to server log
                if cmd.name == "checkModsNeedUpdate": 
                    if bot.server_stdout:
                        await ctx.send(message)
                        message = None
                        bot.server_stdout.channel.settimeout(3) # sets interval to wait for new messages
                        try:
                            for line in iter(bot.server_stdout.readline, ""):
                                if("CheckMods" in line):
                                    await ctx.send(line)
                                bot.logger.debug(line)
                        except:
                            pass
                
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
