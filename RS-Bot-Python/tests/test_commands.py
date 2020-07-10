@bot.command(pass_context=True)
async def add_roles(ctx):
    author = ctx.message.author
    content = ctx.message.content.split()
    if author == bot.user:
        return

    try:
        member = utils.get(server.members,name=content[1])
        roles = [utils.get(server.roles,name=r) for r in content[2].split(",")]
        
    except:
        await bot.send_message(ctx.message.channel,\
                               "Invalid syntax, try: `!add_roles <name> <role1,..>`")
        return

    await bot.add_roles(member,*roles)

@bot.command(pass_context=True)
async def remove_roles(ctx):
    author = ctx.message.author
    content = ctx.message.content.split()
    if author == bot.user:
        return

    try:
        member = utils.get(server.members,name=content[1])
        roles = [utils.get(server.roles,name=r) for r in content[2].split(",")]
        
    except:
        await bot.send_message(ctx.message.channel,\
                               "Invalid syntax, try: `!remove_roles <name> <role1,..>`")
        return

    await bot.remove_roles(member,*roles)
    
@bot.command(pass_context=True)
async def nick(ctx):
    author = ctx.message.author
    content = ctx.message.content.split()
    if author == bot.user:
        return

    try:
        member,nick = utils.get(server.members,name=content[1]),content[2]
        await bot.change_nickname(member,nick)
        await bot.send_message(ctx.message.channel,\
                               "%s's nickname has been set to %s" % (member.name,nick))
        
    except:
        await bot.send_message(ctx.message.channel,\
                               "Invalid syntax, try: `!nick <name> <nickname>`")
        return

