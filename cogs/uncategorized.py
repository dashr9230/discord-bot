
from discord.ext import commands
import time,random

class Uncategorized(commands.Cog):
    @commands.command()
    async def ping(self,context):
        start=time.time()
        message=await context.send("ℹ | Ping?")
        end=time.time()
        result=round((end-start)*1000)

        text=random.choice(["Halló? Ki kopog?","Halló? Ki az?","Ébren vagyok!",
            "Még élek!","Még nem tűntem el!","Itt is vagyok!","Superping megérkezett!",
            "Kerestél?","Hívtál?","Valaki használja ezt meg?","Bacon pizzát?","Hagymás babot?",
            "0101!","Halló, halló!","Élek és virulok!","Áucs!"])

        await message.edit(content=f"ℹ | Pong! {text} - Tartott **{result}** ms-ig.")

def setup(bot):
    bot.add_cog(Uncategorized(bot))
