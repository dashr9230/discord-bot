
from discord.ext import commands
import time,random,requests,math,discord

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

    @commands.command(aliases=["derpi","db","derpy","derpybooru"])
    @commands.cooldown(1,15,commands.BucketType.user)
    async def derpibooru(self,context,*,tags:str=""):
        tags=tags.lower()
        nsfw=context.channel.is_nsfw()
        if not tags:
            pony = random.choice(["ts", "pp", "ry", "rd", "aj", "fs", "sus", "sg", "sp", "pl", "tia",
                "tx", "pcd", "lyra", "bon", "oct", "dj", "dh", "coco", "nmm", "daybreaker", "sf"])
            tags = pony if nsfw else "safe,"+pony
        elif not nsfw:
            blacklist=["explicit","grimdark","grotesque","questionable","semi-grimdark","suggestive"]
            for word in blacklist:
                tags=tags.replace(word,"safe")
            tags="safe,"+tags

        url = "https://derpibooru.org/search.json"
        params = {"q": tags, "filter_id": 56027}
        headers = {"User-Agent": "User-Agent/1.0.0 (Discord Bot)"}
        response = requests.get(url, params=params, headers=headers)
        if response.status_code != 200:
            await context.send("ℹ | Derpibooru jelenleg nem elérhető, próbáld meg később.")
            return

        count=len(response.json()["search"])
        if 0 < count:
            pages=int(response.json()["total"] / count)
            params["page"]=random.randint(1,pages)

            response = requests.get(url, params=params, headers=headers)
            if response.status_code != 200:
                await context.send("ℹ | Derpibooru jelenleg nem elérhető, próbáld meg később.")
                return

            search=response.json()["search"]
            index=random.randint(0,len(search))

            id=search[index]['id']
            title="Derpibooru # %d" % id
            image="https:%s" % search[index]["representations"]["full"]
            description=search[index]["description"]

            tags=search[index]["tags"].split(", ")
            #artist=[a for a in t if a.find("artist:") != -1]
            creator="Ismeretlen"
            for tag in tags:
                if tag.find("artist:") != -1 or tag.find("editor:") != -1:
                    creator=tag[7:]

            embed=discord.Embed(title=title,url=url[:-11]+str(id),colour=0x3D92D0,description=description)
            embed.add_field(name="Tetszések",value=search[index]['upvotes'])
            embed.add_field(name="Nem tetszések", value=search[index]['downvotes'])
            embed.add_field(name="Pontok", value=search[index]['score'])
            embed.add_field(name="Kedvencek", value=search[index]['faves'])
            embed.add_field(name="Készítette", value=creator)
            embed.add_field(name="Feltöltötte", value=search[index]["uploader"])
            embed.set_image(url=image)

            await context.send(embed=embed)
        else:
            await context.send(f"ℹ | Nincs találat a megadott "+"keresőszavakra." if tags.count(",") else "keresőszóra." )

    @commands.command()
    @commands.cooldown(1,15,commands.BucketType.user)
    async def e621(self,context,*,tags:str=""):
        tags=tags.lower()
        if not tags:
            await context.send("ℹ | Nem adtál meg keresőszavakat.")
            return
        if not context.channel.is_nsfw():
            tags=tags.replace("rating:explicit","rating:safe")
            tags=tags.replace("rating:questionable","rating:safe")
            tags="rating:safe "+tags

        url="https://e621.net/post/index.json"
        params={"limit":100,"tags":tags}
        headers={"User-Agent": "User-Agent/1.0.0 (Discord Bot)"}
        response = requests.get(url, params=params, headers=headers)
        if response.status_code != 200:
            await context.send("ℹ | e621 jelenleg nem elérhető. Próbáld meg később.")
            return

        data=response.json()
        count=len(data)
        if count==0:
            await context.send("ℹ | Nincs találat a " +
                "keresőszavakra." if 0<tags.count(" ") else "keresőszóra.")
            return

        data=data[random.randint(0,count)]
        id=data["id"]
        title="e621 # %d" % id
        url="https://e621.net/post/show/%d" % id
        type=data["file_ext"]
        image=data["sample_url"] if type in ("jpg","png","gif") else data["preview_url"]
        description=data["description"]

        embed=discord.Embed(title=title,url=url,colour=0x453269,description=description)
        embed.add_field(name="Pontok",value=data["score"])
        embed.add_field(name="Kedvelések",value=data["fav_count"])
        embed.add_field(name="Készítette",value=", ".join(data["artist"]))
        embed.add_field(name="Feltöltötte",value=data["author"])
        embed.set_footer(text="Kép mérete: %dx%d | Fájl mérete: %d KiB | Típus: %s"
            % (data["width"],data["height"],data["file_size"],type))
        embed.set_image(url=image)

        await context.send(embed=embed)

def setup(bot):
    bot.add_cog(Uncategorized(bot))
