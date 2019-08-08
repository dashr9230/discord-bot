
from discord.ext import commands

class Uncategorized(commands.Cog):
    pass

def setup(bot):
    bot.add_cog(Uncategorized(bot))
