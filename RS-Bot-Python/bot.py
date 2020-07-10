import socket
import asyncio
import urllib.request as req
import uuid
import random
import json
import time
import re
import discord, discord.utils as utils
from discord.ext import commands as cmds
from datetime import datetime as dt
import config as cfg
import timer as tm
import player as pl
import logger

bot = cmds.Bot(cfg.CMD_PREFIX)
bot.chat_formatters = ("\\","_","*","~","`",":","|")
tokens = []

log = logger.CustomLogger("botlogger",log_fname="bot.log",bot=bot)

def run_coro_safe(coro):
    try:
        future = asyncio.run_coroutine_threadsafe(coro,loop)
        return future.result(15)
    except asyncio.TimeoutError:
        log.error("Future timed out!")

async def handle_inactive():
    players = pl.get_players()
    role = utils.get(server.roles,name="Inactive")

    log.info("Handling inactive players")
    for player in players:
        if player.discord_id:
            member = utils.get(server.members,id=player.discord_id)
            last_join = dt.fromtimestamp(player.last_join) if player.last_join else None
            if last_join and (dt.now() - last_join).days >= cfg.INACTIVE_DAYS and member:
                    await bot.add_roles(member,role)
        asyncio.sleep(0.01)
        
    tm.Timer(cfg.INACTIVE_INTERVAL,handle_inactive)

@bot.event
async def on_ready():
    print("Logged in as")
    print(bot.user.name)
    print(bot.user.id)
    print("------")

    global server
    server = utils.get(bot.servers,id=cfg.SERVER_ID)
    await handle_inactive()
    
@bot.event
async def on_member_join(member):
    try:
        await bot.send_message(member,"__**Welcome to the Redstone Server's Discord!**__")
        await bot.send_message(member,"I'm the Redstone Server Bot, or RS-Bot\
 for short. I help maintain the Discord server by connecting your Minecraft account\
 to verify you and automatically update your roles. Once you have connected your\
 account, you will be able to access the rest of the Discord server.")
        await bot.send_message(member,"You can link your Minecraft account to\
 the server by typing '/discord token' on the server and then sending me that token.")
    except:
        pass

@bot.event
async def on_message(message):
    if message.content == "/discord token":
        await bot.send_message(message.channel,"You must use this command in-game!")

    try:
        if not message.channel.name:
            await on_pm(message)
    except Exception as e:
        log.error("Error in on_message: %s\n%s" % (e,message.content))

    if message.channel.id == cfg.CHATSTREAM_ID:
        await on_chat_discord(message)
        return

    await bot.process_commands(message)

@bot.event
async def on_member_update(before,after):
    try:
        player = pl.get_player_by_id(before.id)
        if before.name != after.name:
            await bot.change_nickname(member,player.name)
    except Exception as e:
        log.error("Error in on_member_update: %s" % e)

async def on_pm(message):
    token = message.content

    if token in tokens:
        tokens.remove(token)
        player = pl.get_player_by_token(token)
        if player.discord_id:
            member = utils.get(server.members,id=player.discord_id)
            try:
                await bot.remove_roles(member,*server.roles)
            except Exception as e:
                log.error("%s role issue: linked another account and failed: %s" % (member.name,e))
            
        player.discord_id = message.author.id
        player.save()   # since 7/9/2018 player's will keep their token

        member = utils.get(server.members,id=player.discord_id)

        rank_role = utils.get(server.roles,name=player.rank)
        memb_role = utils.get(server.roles,name="Linked")
        relay_role = utils.get(server.roles,name="Chat-Relay")
        
        await bot.add_roles(member,rank_role,memb_role,relay_role)
        await bot.change_nickname(member,player.name)

        try:
            await bot.send_message(message.author,"Your Discord account has been successfully linked! Thank you!")
        except:
            pass
    else:
        try:
            await bot.send_message(message.author,"Sorry, that's not a valid token! You can generate a new token on the server with /discord token")
        except:
            pass

async def on_join_mc(fields,conn):
    conn.sendall(b"handling join")

    try:
        if len(fields) != 3:
            raise Exception("Too many or too few fields")
        
        uuid = fields[1]
        name = fields[2]

        player = pl.get_player(uuid)
        if not player:
            player = pl.Player(uuid,name,last_join=time.time()).save()
            return
        
        player.last_join = time.time()
        if name != player.name:
            player.name = name
        player.save()

        member = utils.get(server.members,id=player.discord_id)
        role = utils.get(server.roles,name="Inactive")
    except Exception as e:
        log.error("Error in join packet: %s" % e)

    try:
        await bot.remove_roles(member,role)
        await bot.change_nickname(member,player.name)
    except:
        pass

async def on_rank(fields,conn):
    try:
        conn.sendall(b"handling rank")
        
        if len(fields) != 3:
            raise Exception("Too many or too few fields")

        player = pl.get_player(fields[1])
        if not player:
            log.error("Invalid UUID value: %s" % fields[1])
            return
            
        rank = fields[2].replace("+","")

        try:
            if rank not in cfg.RANK_ROLES:
                rank += "s"
                if rank not in cfg.RANK_ROLES:
                    rank -= "s"
                    raise Exception("Invalid role name: %s" % rank)
            
            roles = [r for r in server.roles if r.name in cfg.RANK_ROLES]
            new_role = utils.get(roles,name=rank)
            member = utils.get(server.members,id=player.discord_id)
            if not member:
                return

            await bot.remove_roles(member,*roles)
            await asyncio.sleep(0.5)
            await bot.add_roles(member,new_role)

            player.rank = rank
            player.save()
        except Exception as e:
            log.error(e)
            
    except Exception as e:
        log.error("Error in rank packet: %s" % e)


async def on_token(fields,conn):
    try:
        if len(fields) != 4:
            conn.sendall(b"token failed, report this to staff")
            raise Exception("Too many or too few fields")

        try:
            _ = uuid.UUID(fields[1],version=4)
        except ValueError:
            log.error("Bad UUID: %s" % fields[1])
            return
                      
        player = pl.get_player(fields[1])
        if not player:
            player = pl.Player(fields[1],fields[2])
            player.save()
        
        while True:
            token = uuid.uuid4().hex[:5]
            if token not in tokens: break

        if player.token in tokens:
            tokens.remove(player.token)
            
        player.token = token
        player.rank = fields[3]
        player.save()
            
        conn.sendall(token.encode())
        tokens.append(token)
    except Exception as e:
        log.error("Error in token packet: %s" % e)

async def on_chat(fields,conn):
    try:
        conn.sendall(b"handling chat")
        
        pattern = "(\[[^\]]+\])([^\[:]+)((?:\[[^\]]+\])*): (.*)"

        message = " ".join(fields[1:])
        message = re.sub("§.","",message)
            
        message = message.replace("@everyone","@-everyone")

        channel = utils.get(server.channels,id=cfg.CHATSTREAM_ID)
        
        reg_match = re.findall(pattern,message)
        
        if len(reg_match) != 1:
            await bot.send_message(channel,message)
            return
        
        prefix,name,suffix,msg = reg_match[0]
        
        for fmt in bot.chat_formatters:
            name = name.replace(fmt,"\\" + fmt)
            msg = msg.replace(fmt,"\\" + fmt)

        fun = False      # set to True to annoy people :D
        if fun:
            player = pl.get_player_by_name(name)
            name = "<@%s>" % player.discord_id if player and player.discord_id else name
            
        suffix = "**%s**" % suffix if suffix else ""

        message = "**%s**%s%s: %s" % (prefix,name,suffix,msg)

        await bot.send_message(channel,message)

    except Exception as e:
        log.error("Error in chat packet: %s:\n%s" % (e,message))
    except AttributeError as e:
        log.error("Server has not been found yet!")

async def on_chat_discord(message):
    if message.author == bot.user:
        return

    try:
        
        player = pl.get_player_by_id(message.author.id)
        
        await bot.delete_message(message)
        msg = message.content[:256]
            
        role = utils.get(server.roles,name="Staff")
        if not role in message.author.roles:
            msg = re.sub("§.","",msg)
        
        msg = "chat %s §7%s§f: %s" % (player.uuid,player.name,msg)

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        await loop.sock_connect(sock,cfg.SERVER_ADDR)
        await loop.sock_sendall(sock,msg.encode())
        sock.close()
        
    except Exception as e:
        log.error("Chat stream error: %s" % e)
    
async def on_broadcast(fields,conn):
    try:
        conn.sendall(b"handling broadcast")

        message = " ".join(fields[1:])
        message = re.sub("§.","",message)

        if re.fullmatch(".* (joined the game|left the game)",message):
            message = "`%s`" % message
        elif re.fullmatch("[\S]* (is|has been) (now |no longer )?(afk|auto-afk'd).( Reason: .*)?",message):
            for fmt in bot.chat_formatters:
                message = message.replace(fmt,"\\" + fmt)
            message = "*%s*" % message
        
        if message.startswith("["):
            for fmt in bot.chat_formatters:
                message = message.replace(fmt,"\\" + fmt)
            prefix = re.findall("\[.*?\]",message)[0]
            message = message.replace(prefix,"**%s**" % prefix)

        channel = utils.get(server.channels,id=cfg.CHATSTREAM_ID)
        await bot.send_message(channel,message)
        
    except Exception as e:
        log.error("Error in broadcast packet: %s" % e)
        log.info(message)

async def on_online(fields,conn):
    try:
        conn.sendall(b"handling online")

        count = len(fields[1:])
        online = "\n".join(fields[1:])
        for fmt in bot.chat_formatters:
            online = online.replace(fmt,"\\" + fmt)

        channel = utils.get(server.channels,id=cfg.CHATSTREAM_ID)
        
        new_topic = "%s players in-game:\n%s" % (len(fields[1:]),online) if count else "No players in-game"
        await bot.edit_channel(channel,topic=new_topic)

    except Exception as e:
        log.error("Error in online packet: %s" % e)

@bot.command(pass_context=True,help="Flips a coin.")
async def flipcoin(ctx):
    side = "Heads!" if random.random() > 0.49 else "Tails!"
    await bot.send_message(ctx.message.channel,side)

@bot.command(pass_context=True,help="Gets random cat image.")
async def cat(ctx):
    future = loop.run_in_executor(None,req.urlretrieve,"https://cataas.com/cat/cute",cfg.DIR_PATH + "cat.gif")
    await future
    await bot.send_file(ctx.message.channel,"cat.gif")

@bot.command(pass_context=True,help="Gets random dog image.")
async def dog(ctx):
    future = loop.run_in_executor(None,req.urlopen,"https://dog.ceo/api/breeds/image/random")
    result = await future
    data = json.load(result)
    future = loop.run_in_executor(None,req.urlretrieve,data["message"],cfg.DIR_PATH + "dog.jpg")
    await future
    await bot.send_file(ctx.message.channel,"dog.jpg")

##@bot.command(pass_context=True,help="Gets random fruit image.")
##async def fruit(ctx):
##    future = loop.run_in_executor(None,req.urlretrieve,"https://source.unsplash.com/random/?{banana},{fruit}",cfg.DIR_PATH + "fruit.jpg")
##    await future
##    await bot.send_file(ctx.message.channel,"fruit.jpg")

##@bot.command(pass_context=True)
##async def play(ctx,url):
##    print("PLAYING SONG")
##    author = ctx.message.author
##    dj_role = utils.get(server.roles,name="DJ")
##    
##    if dj_role not in author.roles:
##        await bot.send_message(ctx.message.channel,"You do not have permission to use this feature!")
##        return
##    
##    vchannel = author.voice_channel
##    vc = await bot.join_voice_channel(vchannel)
##
##    player = await vc.create_ytdl_player(url)
##    player.volume = 0.6
##    player.start()

def handle_api(data,conn):
    fields = data.decode().split()
    fmt = fields[0]

    if fmt == "join":
        run_coro_safe(on_join_mc(fields,conn))
    elif fmt == "rank":
        run_coro_safe(on_rank(fields,conn))
    elif fmt == "token":
        run_coro_safe(on_token(fields,conn))
    elif fmt == "chat":
        run_coro_safe(on_chat(fields,conn))
    elif fmt == "broadcast":
        run_coro_safe(on_broadcast(fields,conn))
    elif fmt == "online":
        run_coro_safe(on_online(fields,conn))
    else:
        log.warning("Received unsupported request: %s" % fmt)

def main(_loop):
    global loop
    loop = _loop
    bot.run(cfg.TOKEN)
