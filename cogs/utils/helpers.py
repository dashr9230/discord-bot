
import requests,bs4,time

commands={}

def xget(url,params=None,**args):
    try:
        headers = {
            "User-Agent": "User-Agent/1.0.0 (Discord Bot)",
            "Content-Type": "text/html; charset=UTF-8"
        }
        response=requests.get(url,params,headers=headers,timeout=10,**args)
        if response.status_code != 200:
            return None
        return bs4.BeautifulSoup(response.text,"html.parser")
    except:
        return None

def is_on_cooldown(context,retry_after:float):
    command=context.command.name
    now=time.time()
    if commands.get(command)==None:
        commands[command]=now
        return -1
    elif retry_after<=(now-commands[command]):
        del commands[command]
        return -1
    return int(retry_after-(now-commands[command]))

def remstr(source, start, end):
    pass
