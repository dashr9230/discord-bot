
from discord.ext import commands
import configparser,os

bot=commands.Bot(command_prefix="!")

@bot.event
async def on_ready():
    print(f"A bot elindult {bot.user.name} néven. (ID:{bot.user.id})")

def main():
    config=configparser.ConfigParser()
    config.read("discord-bot.dev.cfg" if os.path.isfile("discord-bot.dev.cfg") else "discord-bot.cfg")
    token=config.get("bot","token",fallback="")
    if token == "":
        print("discord-bot.cfg konfigurációs fájl nem található vagy token kulcs hiányzik.")
        return
    bot.run(token)

main()
