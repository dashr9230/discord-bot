
# TODO: Add ability to move messages to another channel
# TODO: Add multilanguage support
# TODO: Add music player
# TODO: Add ability to log out bot
# TODO: Add ability to change command prefix
# TODO: Add Sims(?) game
# TODO: Add ban and kick command

from discord.ext import commands
from . import utils

import time,random,requests,discord,bs4,math,aiohttp

__all__=["Uncategorized"]

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

    @commands.command(aliases=["ph"])
    async def pornhub(self, context, *, keywords: str = ""):
        time_left=utils.is_on_cooldown(context, 15)
        if time_left != -1:
            await context.send(f"ℹ | Whoa, nyugi cowboy! Próbáld meg újra **{time_left} másodperc** múlva.")
            return
        if not context.channel.is_nsfw():
            await context.send("ℹ | Ez a parancs csak NSFW csatornákban működik.")
            return

        segments = []
        tags = []
        verified = False
        order = ""
        if keywords:
            keywords = keywords.lower()
            for keyword in keywords.split(" "):
                if keyword in ["seg:female","seg:gay","seg:male","seg:straight"]:
                    segments.append(keyword[4:])
                elif keyword in ["seg:transgender","seg:trans"]:
                    segments.append("transgender")
                elif keyword in ["seg:miscellaneous","seg:misc"]:
                    segments.append("misc")
                elif keyword == "verified":
                    verified = True
                elif keyword in ["o:mv","o:most_viewed"]:
                    order = "mv"
                elif keyword in ["o:mr", "o:most_recent"]:
                    order = "mr"
                elif keyword in ["o:tr","o:top_rated"]:
                    order = "tr"
                else:
                    tags.append(keyword)

        url = "https://www.pornhub.com/albums/"
        params = {}

        if not segments:
            segments.append("female")
            segments.append("straight")
            segments.append("uncategorized")
        if tags:
            params["search"] = "+".join(tags)
        if order:
            params["o"] = order
        if verified:
            params["verified"] = "1"

        message = await context.send(f"🔍 | **Pornhub** | Keresés következőre: ***{keywords}***")

        content = utils.xget(url + "-".join(segments), params)
        if content == None:
            await message.edit(content=f"ℹ | **Pornhub** | Hiba merült fel album keresés közben.")
            return

        album_contents = content.find_all("div",{"class":"photoAlbumListBlock"})
        if not album_contents:
            await message.edit(content=f"ℹ | **Pornhub** | Nincs album találat.")
            return
        album_content = random.choice(album_contents)
        album_link = url[:23] + album_content.find("a")["href"]

        content = utils.xget(album_link)
        if content == None:
            await message.edit(content=f"ℹ | **Pornhub** | Hiba merült fel kép keresése közben.")
            return

        photo_contents = content.find_all("div",{"class":"photoAlbumListBlock"})
        if not photo_contents:
            await message.edit(content=f"ℹ | **Pornhub** | Nincs fotó találat.")
            return
        photo_content = random.choice(photo_contents)

        album_title, owner = content.title.string.split(" - ")
        owner = owner.split("'")[0]
        title = f"Pornhub # {owner} Albuma"
        photo_link = photo_content.find("a")["href"]
        photo_url = photo_content.attrs["style"][23:-3]

        embed = discord.Embed(title="Megtekintés teljes méretben",
            url=url[:23]+photo_link,colour=0xFF9900,description=album_title)
        embed.set_author(name=title,url=album_link)
        embed.set_image(url=photo_url)

        await message.edit(content=None, embed=embed)

    @commands.command(aliases=["fur","fa"])
    @commands.cooldown(1,15,commands.BucketType.user)
    async def furaffinity(self,context,*,tags:str=""):
        if not tags:
            await context.send("Nem adtál meg keresőszavakat.")
            return
        url="https://www.furaffinity.net/search"
        headers={"User-Agent": "User-Agent/1.0.0 (Discord Bot)"}
        params={"q":tags}
        # TODO: configból kiolvasni a bejelentkező adatokat
        # TODO: NSFW ellenőrzés szükséges miután a bejelentkező adatok ki vannak töltve
        data={"username":"","password":""}

        # Get number of images
        response=requests.get(url,params=params,headers=headers,data=data,timeout=10)
        if response.status_code != 200:
            await context.send("Furaffinity nem elérhető")
            return

        content=bs4.BeautifulSoup(response.content,"lxml")
        result=content.find("fieldset",{"id":"search-results"}).find("legend").get_text()
        start=result.find("of ")+3
        max_finds=result[start : result.find(")",start)]
        if max_finds == "0":
            await context.send("Nincs találat a keresőszavakra.")
            return
        params["page"]=random.randint(1,math.ceil(int(max_finds)/48))

        # Grab some photo in that page
        response=requests.get(url,params=params,headers=headers,data=data,timeout=10)
        if response.status_code != 200:
            await context.send("Furaffinity nem elérhető")
            print(response.status_code)
            return

        content = bs4.BeautifulSoup(response.content, "lxml")
        figure=content.find_all("figure")
        if not figure:
            await context.send("Hiba lépett fel keresés közben.")
            return
        image=random.choice(figure)
        image=image.find("b").find("u").find("a").attrs["href"]

        await context.send(f"https://www.furaffinity.net{image}")

    @commands.command(aliases=["dan"])
    async def danbooru(self, context, *, keywords: str = ""):
        time_left = utils.is_on_cooldown(context, 15)
        if time_left != -1:
            await context.send(f"Nyugi öcskös! **{time_left}** másodperc múlva újra használhatod.")
            return

        url = "https://danbooru.donmai.us"
        params = {}

        if keywords:
            keywords = keywords.lower()
            nsfw = context.channel.is_nsfw()
            tags = [] if nsfw else ["rating:safe"]
            for keyword in keywords.split(" "):
                if not nsfw and not keyword.startswith("rating:") \
                        and not keyword.startswith("-rating:"):
                    tags.append(keyword)
            params["tags"] = " ".join(tags)
        else:
            url += "/posts/random"
            if not context.channel.is_nsfw():
                params["tags"] = "rating:safe"

        content = utils.xget(url, params)
        if content == None:
            await context.send("Hiba lépett fel poszt keresése közben.")
            return

        if keywords:
            posts_container = content.find("div",{"id":"posts-container"})
            articles = posts_container.find_all("article")
            if not articles:
                await context.send("Nincs találat?")
                return
            image = random.choice(articles)
        else:
            image = content.find("section",{"id": "image-container"})

        id = image["data-id"]
        title = "Danbooru # " + id
        url = url[:26] + "/posts/" + id
        favs = image["data-fav-count"]
        score = image["data-score"]
        ext = image["data-file-ext"]
        size = image["data-width"] + "x" + image["data-height"]
        rating = image["data-rating"]

        embed = discord.Embed(title=title,color=0x0073FF,url=url)
        embed.add_field(name="Kedvencek", value=favs)
        embed.add_field(name="Pontok", value=score)
        embed.set_footer(text="Méret %s | Fájltípus: %s | Osztályozás: %s" % (size, ext, rating))
        embed.set_image(url=image["data-large-file-url"])

        await context.send(embed=embed)

    @commands.command(aliases=["yt"])
    async def youtube(self, context, *, keywords: str = ""):
        time_left = utils.is_on_cooldown(context, 15)
        if time_left != -1:
            await context.send(f"Lassan öcskös! Újra próbálhatod **{time_left}** mp múlva.")
            return
        if not keywords:
            await context.send("Nem adtál meg keresési kulcsokat.")
            return

        query = []
        sp = "CAASAhAB"
        for keyword in keywords.split(" "):
            if not keyword:
                continue
            if keyword in ["sort_by:d","sort_by:date","sort_by:upload_date"]:
                sp = "CAISAhAB"
            elif keyword in ["sort_by:v","sort_by:views","sort_by:view_count"]:
                sp = "CAMSAhAB"
            elif keyword in ["sort_by:r","sort_by:rates","sort_by:rating"]:
                sp = "CAESAhAB"
            else:
                query.append(keyword)

        url = "https://www.youtube.com/results"
        params = {"search_query":" ".join(query), "sp": sp}

        content = utils.xget(url, params)
        if content == None:
            await context.send("Hiba lépett fel videó keresése közben.")
            return

        thumbnail_div = content.find("div",{"class":"yt-lockup-thumbnail contains-addto"})
        thumbnail_a = thumbnail_div.find("a",{"aria-hidden":"true","class":"yt-uix-sessionlink spf-link"})

        await context.send(url[:23] + thumbnail_a["href"])

    @commands.command()
    async def purge(self, context, limit: str = ""):
        if not utils.has_permission(context.author, "manage_messages"):
            await context.send("Nincs jogod üzenetek törléséhez.")
            return
        if not limit and not limit.isnumeric() and (0 > int(limit) <= 100):
            await context.send("Nem adtál meg számot, amennyit törölni szeretnél. (1-100)")
            return
        try:
            await context.channel.purge(limit=int(limit))
        except:
            await context.send("Hiba merült fel üzenetek törlése közben.")

    @commands.command()
    async def prune(self, context, *, message: str = ""):
        if not utils.has_permission(context.author, "manage_messages"):
            await context.send("Nincs jogod üzenetek törléséhez.")
            return
        if not message:
            await context.send("Nem adtál meg számot és nevet akinek az üzeneteit törölni szeretnéd.")
            return
        limit, name = message.split(" ", 1)
        if not limit.isnumeric() and (0 > int(limit) <= 100):
            await context.send("A szám nem lehet 1-nél kisebb és 100-nál nagyobb.")
            return
        member = utils.find_member(context, name)
        if member == None:
            await context.send(f"Nem találtam **{name}** nevű felhasználót.")
            return
        try:
            count = 0
            async for m in context.channel.history(limit=100):
                if m.author == member:
                    await m.delete()
                    count += 1
                if int(limit) <= count:
                    break
            await context.send(f"Törölve lett {count} üzenet {member.name}-tól/-től.")
        except:
            await context.send("Hiba merült fel üzenetek törlése közben.")

    @commands.command()
    async def report(self, context, *, message: str = ""):
        if not message:
            await context.send("Nem adtál meg üzenetet.")
            return
        # TODO: Read the webhook url from config
        url = ""
        if not url:
            await context.send("Report parancs jelenleg nem elérhető.")
            return

        async with aiohttp.ClientSession() as session:
            webhook = discord.Webhook.from_url(url, adapter=discord.AsyncWebhookAdapter(session))
            await webhook.send(message)

        await context.send("Köszönjük jelentésed!")

def setup(bot):
    bot.add_cog(Uncategorized(bot))
