
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

    for cog in os.listdir("cogs"):
        if not cog.endswith(".py"):
            continue
        cog = cog[:-3]
        try:
            bot.load_extension(f"cogs.{cog}")
            print(f"\"{cog}\" modul sikeresen betöltve.")
        except commands.NoEntryPointError:
            print(f"Belépési pont nem található \"{cog}\" modulban.")
        except commands.ExtensionFailed as i:
            print(f"Hiba lépett fel \"{cog}\" modul lefuttatása közben.\n{i}")

    bot.run(token)

main()
