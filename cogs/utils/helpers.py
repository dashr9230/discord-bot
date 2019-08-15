
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

def has_permission(member, permission: str):
    for role in member.roles:
        attr = getattr(role.permissions, permission, None)
        if attr != None and attr == True:
            return True
    return False

def find_member(context, name: str, case_sensitive = False):
    cs = case_sensitive
    name = name if cs else name.lower()
    for m in context.guild.members:
        d = [str(m.id)]
        if m.nick:
            d.append(m.nick)
        d.append(m.name if cs else m.name.lower())
        d.append(m.display_name if cs else m.display_name.lower())
        d.append(m.mention)
        for i in d:
            if i.find(name) != -1:
                return m
    return None