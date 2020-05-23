
from discord.ext import commands
from PIL import Image
import discord, datetime, re
import PIL, shutil, os, random

class MineBase:
    def __init__(self, member):
        self.grid = [[0 for x in range(12)] for y in range(12)]
        self.grid_show = [[0 for x in range(12)] for y in range(12)]
        self.file = f"cache/mine_{member.id}.png"
        self.tile_size = 32

        shutil.copy("assets/mine/board.png", self.file)
        self.image = Image.open(self.file)

    def __del__(self):
        self.image.close()
        try:
            os.remove(self.file)
        except:
            pass

    def generate_grid(self):
        for x in range(11):
            for y in range(11):
                self.grid_show[x][y] = 10
                n = random.randint(0,6)
                self.grid[x][y] = 9 if n == 0 else 0

        for x in range(11):
            for y in range(11):
                n = 0
                if self.grid[x][y] == 9:
                    continue
                if self.grid[x + 1][y] == 9:
                    n += 1
                if self.grid[x][y + 1] == 9:
                    n += 1
                if self.grid[x - 1][y] == 9:
                    n += 1
                if self.grid[x][y - 1] == 9:
                    n += 1
                if self.grid[x + 1][y + 1] == 9:
                    n += 1
                if self.grid[x - 1][y - 1] == 9:
                    n += 1
                if self.grid[x - 1][y + 1] == 9:
                    n += 1
                if self.grid[x + 1][y - 1] == 9:
                    n += 1
                self.grid[x][y] = n

    def modify_board(self):
        tiles = Image.open("assets/mine/tiles.png")
        if not tiles:
            return
        w = self.tile_size
        for x in range(11):
            for y in range(11):
                # left-top-right-bottom
                #print(x, y, self.grid[x][y])
                #print((self.grid[x][y] * w, 0, w, w))
                tile = tiles.crop((self.grid_show[x][y]*w, 0, self.grid_show[x][y]*w+w, w))
                self.image.paste(tile, (24+x*self.tile_size, 24+y*self.tile_size))

        self.image.save(self.file)

    def translate_move(self, move_code):
        n = ''.join(c for c in move_code if c.isdigit()) or None
        l = ''.join(c for c in move_code if c.isalpha()) or None
        return n, l

class Mine(commands.Cog):
    def __init__(self, bot):
        print("I'M loaded")
        
    @commands.command()
    async def mine(self, context, *, move: str = ""):
        test = MineBase(context.author)
        test.generate_grid()
        test.modify_board()
        with open(test.file, "rb") as fp:
            await context.send(file=discord.File(fp=fp))

        #print(move)
        #n, l = test.translate_move(move)
        #await context.send(f'-> {n}, {l}')

        del test
        """board = [[0 for x in range(12)] for y in range(12)]
        #sboard = board
        for x in range(11):
            for y in range(11):
                if random.randint(0,5) == 0:
                    board[x][y] = 9
                else:
                    board[x][y] = 0

        for x in range(11):
            for y in range(11):
                n = 0
                if board[x][y] == 9:
                    continue
                if board[x + 1][y] == 9:
                    n += 1
                if board[x][y + 1] == 9:
                    n += 1
                if board[x - 1][y] == 9:
                    n += 1
                if board[x][y - 1] == 9:
                    n += 1
                if board[x + 1][y + 1] == 9:
                    n += 1
                if board[x - 1][y - 1] == 9:
                    n += 1
                if board[x - 1][y + 1] == 9:
                    n += 1
                if board[x + 1][y - 1] == 9:
                    n += 1
                board[x][y] = n

        output = "```"
        for x in range(11):
            for y in range(11):
                output += f"{board[x][y]} "
            output += "\n"
        output += "```"
        await context.send(output)"""

def setup(bot):
    bot.add_cog(Mine(bot))