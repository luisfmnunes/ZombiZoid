import nextcord
import socket
from nextcord.ext import commands
from nextcord import Interaction
from rcon.source import Client as rcon_cl
from rcon.exceptions import *
from utils.logger import get_logger
from .commands import *

class DiscordBot(commands.Bot):
    """
        A class that stores a discord client and bot info
    """
    def __init__(self, config, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config = config
        self.logger = get_logger()
    
    async def on_ready(self):
        self.logger.info(f"{self.user} has connected to Discord")

    # async def on_message(self, message : nextcord.message.Message):
    #     self.logger.debug(message)
    #     if not message.author == self.user:
    #         await message.channel.send("Hmm... Coquinha Gelada")

    def local_run(self):
        self.run(self.config["bot_token"])


def get_bot(config, *args, **kwargs):
    
    intent = nextcord.Intents.default()
    intent.message_content = True
    bot = DiscordBot(config, intents=intent,*args, **kwargs)
    
    @bot.slash_command(name="status", description="Returns Bot Status", guild_ids=[config["guild_id"]])
    async def status(interaction: Interaction):
        await interaction.response.send_message("Bot Loaded and Runnning")
    
    # Command Factory
    def function_builder(cmd):
        @bot.command(name=cmd.name)
        async def SendMessage(ctx: commands.Context):
            bot.logger.debug(ctx.message)
            bot.logger.debug(cmd)
            try:
                await ctx.message.add_reaction("⏳")
                
                with rcon_cl(bot.config["server"], 
                             bot.config["rcon_port"], 
                             passwd=bot.config["rcon_pwd"], 
                             timeout=bot.config["rcon_timeout"]) as cl:
                    message = cl.run(cmd.name)
                    bot.logger.debug(f"Command Response: {message.splitlines()[0]}")
                
                await ctx.message.clear_reaction("⏳")
                await ctx.message.add_reaction("\N{WHITE HEAVY CHECK MARK}")
            except (ConfigReadError, SessionTimeout, UserAbort, WrongPassword, socket.timeout) as e:
                bot.logger.warning(e)
                message = "Error communicating with Project Zomboid Bilulu Server"
                
                await ctx.message.clear_reaction("⏳")
                await ctx.message.add_reaction("\N{CROSS MARK}")
                    
            await ctx.send(message)
        
        return SendMessage
        
    for cmd in zz_commands:
        function_builder(cmd)
    
    return bot