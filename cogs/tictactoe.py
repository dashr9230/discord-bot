
import discord
import discord.ext.commands as commands
from PIL import Image, ImageOps
import requests
import os, random, asyncio

from . import utils

class TicTacToeGame(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ttts = {}

    def __del__(self):
        del self.ttts

    @commands.command(aliases=["ixox","ttt","tic","tac","toe"])
    async def tictactoe(self, context, *, message: str = ""):
        if self.ttts.get(context.guild.id):
            p = self.ttts[context.guild.id].players
            await context.send(f"Már jelenleg fut egy játék **{p['x'].name}** és **{p['o'].name}** ellen.")
            return

        if not message:
            await context.send("Nem adtál meg ellenfelet. Próbáld kihívni valamely botot.")
            return

        args = message.split(" ")
        stoopid_mode = True if "stupid" in args else False
        opponent = utils.find_member_by_name(context,args[0])
        if opponent is None:
            await context.send(f"Nem találtam **{name}** nevű tagot. Próbáld meg kihívni valamely botot.")
            return

        if opponent == context.author:
            await context.send("Magadat nem hívhatod ki TicTacToe menetre. Próbáld meg valamely botot.")
            return

        self.ttts[context.guild.id] = utils.TicTacToe(context.author, opponent)
        ttt = self.ttts[context.guild.id]

        if not opponent.bot:
            await context.send(f"**{context.author.name}** kihívott téged egy TicTacToe menetre, {opponent.mention}!",delete_after=30.0)

        buttons = {
            "1⃣": 0, "2⃣": 1, "3⃣": 2, "4⃣": 3, "5⃣": 4,
            "6⃣": 5, "7⃣": 6, "8⃣": 7, "9⃣":8,
            "🔄": -1, "❌": -2
        }
        message = None
        end_round = False
        field = -1
        while(True):
            try:
                # Ha az ellenfél egy bot, akkor kezdjen
                if ttt.players[ttt.turn].bot and not end_round:
                    last_turn = ttt.turn
                    field = ttt.get_computer_move(stoopid_mode)
                    ttt.move(field)
                    field += 1

                image = open(ttt.file, "rb")
                if image:
                    if message != None:
                        await message.delete()

                    if end_round:
                        message = await context.send(file=discord.File(image))
                    else:
                        message = await context.send(f"**{ttt.players[last_turn].name}** ({last_turn}) tett a {field}-as/-es mezőre.\nMost te következel {ttt.players[ttt.turn].mention}!"
                            if field != -1 else f"Most te következel {ttt.players[ttt.turn].mention}", file=discord.File(image))

                    image.close()

                    if end_round:
                        break

                for k, v in buttons.items():
                    if ttt.is_field_free(buttons[k]) or (buttons[k] in (-1, -2)):
                        await message.add_reaction(k)

                def check(r, m):
                    return r.emoji in buttons and m == ttt.players[ttt.turn]
                r, m = await self.bot.wait_for("reaction_add", timeout=60.0, check=check)

                if r.emoji in buttons:
                    if buttons[r.emoji] == -2:
                        await context.send(f"**{m.name}** leállította a játékot.")
                        break
                    elif buttons[r.emoji] == -1:
                        del self.ttts[context.guild.id]
                        self.ttts[context.guild.id] = utils.TicTacToe(context.author, opponent)
                        ttt = self.ttts[context.guild.id]
                        field = -1
                    else:
                        last_turn = ttt.turn
                        ttt.move(buttons[r.emoji])
                        field = buttons[r.emoji] + 1

            except utils.InvalidMove:
                await context.send(f"Érvénytelen lépés, {m.mention}!", delete_after=30.0)
            except utils.Winner:
                await context.send(f"**{ttt.players[last_turn].name}** nyerte a kört. Graturálok!")
                end_round = True
            except utils.Tie:
                await context.send("Hát ez döntetlen lett :(")
                end_round = True
            except asyncio.TimeoutError:
                await context.send("Lejárt az idő, a játék törlésre került.")
                break

        del self.ttts[context.guild.id]

def setup(bot):
    try:
        bot.add_cog(TicTacToeGame(bot))
        print("TicTacToeGame modul sikeresen betöltve.")
    except:
        print("Nem sikerült betölteni a TicTacToeGame modult.")
