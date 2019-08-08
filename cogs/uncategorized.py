
from discord.ext import commands
import time,random,requests,discord,bs4,math

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

    # TODO: Jobban nekifeküdni, és néhány ellenőrzést hozzáadni.
    @commands.command(aliases=["ph"])
    @commands.cooldown(1,15,commands.BucketType.user)
    async def pornhub(self,context,*,tags:str=""):
        if not context.channel.is_nsfw():
            await context.send("ℹ | Ezt a parancsot csak NSFW csatornákban működik.")
            return
        if not tags:
            await context.send("ℹ | Nem adtál meg keresőszavakat.")
            return

        url="https://pornhub.com/"
        params={"search":""}
        headers={
            "User-Agent": "User-Agent/1.0.0 (Discord Bot)",
            "Content-Type" : "text/html; charset=UTF-8"
        }
        keywords = tags.split(" ")
        categories = []
        for keyword in keywords:
            if keyword in ("female", "gay", "male", "misc", "straight", "transgender", "uncategorizedd"):
                categories.append(keyword)
            else:
                params["search"]+=keyword+"+"

        navigate_to=url+"albums/"+"-".join(categories)
        print(params)
        response = requests.get(navigate_to,params=params,headers=headers)
        if response.status_code != 200:
            await context.send("ℹ | Pornhub jelenleg nem elérhető. Próbáld meg később.")
            return
        data=bs4.BeautifulSoup(response.content,"lxml")
        number_of_albums=data.find("div",class_="showingCounter").get_text().rsplit(" ",1)[1]
        number_of_pages=math.ceil(int(number_of_albums)/36)
        params["page"]=random.randint(1,number_of_pages)

        # Moving to a random page...
        response = requests.get(navigate_to, params=params, headers=headers)
        if response.status_code != 200:
            await context.send("ℹ | Pornhub jelenleg nem elérhető. Próbáld meg később.")
            return
        data = bs4.BeautifulSoup(response.content, "lxml")
        albums=data.find_all("div",{"class":"photoAlbumListBlock"})
        album=random.choice(albums)
        navigate_to=url+str(album.find("a")["href"][1:])

        # Inside the album
        response = requests.get(navigate_to, headers=headers)
        if response.status_code != 200:
            await context.send("ℹ | Pornhub jelenleg nem elérhető. Próbáld meg később.")
            return
        data = bs4.BeautifulSoup(response.content, "lxml")
        images=data.find_all("div",{"class":"photoAlbumListBlock"})
        image=random.choice(images)
        image=image.find("a")["href"]
        navigate_to=url+image

        # Getting the photo...
        response = requests.get(navigate_to, headers=headers)
        if response.status_code != 200:
            await context.send("ℹ | Pornhub jelenleg nem elérhető. Próbáld meg később.")
            return
        data=bs4.BeautifulSoup(response.content,"lxml")
        url=data.find("a",{"href":str(image)}).find("img")
        await context.send(url.attrs["src"])

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

def setup(bot):
    bot.add_cog(Uncategorized(bot))
