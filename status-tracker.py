import discord
import os


SAVE_CHANNEL_ID = int(os.environ['save-channel-id'])


status_notification_channels = {}



intents = discord.Intents.default()
intents.members = True
intents.presences = True
client = discord.Client(intents=intents)


async def get_save(save_channel_id):
    status_notification_channels = {}
    try:
        save_channel = client.get_channel(save_channel_id)
        channels = await save_channel.history(limit=1).flatten()
        channels = channels[0].content
        print(channels)
        for channel in channels.split("\n"):
            print(channel)
            c = channel.split(":")
            status_notification_channels[int(c[0])] = int(c[1])
    except:
        pass
    print(status_notification_channels)
    return status_notification_channels


async def save(save_channel_id, channels):
    save_channel = client.get_channel(save_channel_id)
    try:
        await save_channel.send("\n".join([str(g)+":"+str(c) for g, c in channels.items()]))
    except:
        pass

async def ready_message(client):
    for guild in client.guilds:
        for channel in guild.channels:
            if channel.id != SAVE_CHANNEL_ID:
                try:
                    await channel.send("I'm ready!!")
                except:
                    print(f"maybe {guild.name} - {channel.name} is not a text channel")


@client.event
async def on_ready():
    global status_notification_channels
    status_notification_channels = await get_save(SAVE_CHANNEL_ID)
    await ready_message(client)


command_prefix = "!"

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith(command_prefix+'hello'):
        await message.channel.send('Hello!')

    if message.content.startswith(command_prefix+"members"):
        for member in message.guild.members:
            try:
                await message.channel.send(f"{member.name} : {member.status}, {member.activity.name}")
            except:
                await message.channel.send(f"{member.name} : {member.status}")

    if message.content.startswith(command_prefix+"set_status_notification_channel"):
        if not message.guild.id in status_notification_channels.keys():
            status_notification_channels[message.guild.id] = message.channel.id
            await save(SAVE_CHANNEL_ID, status_notification_channels)
            await message.channel.send("done")
        else:
            await message.channel.send("There already exists a status notification channel in this server!!\nYou can not create more than one status notification channel in a server!!")

    if message.content.startswith(command_prefix+"del_status_notification_channel"):
        if not message.guild.id in status_notification_channels.keys():
            await message.channel.send("There is no status notification channel in this server!!")
        else:
            del status_notification_channels[message.guild.id]
            await save(SAVE_CHANNEL_ID, status_notification_channels)
            await message.channel.send("done")



async def notification_generate(before, after):
    notification = discord.Embed(\
        title=f"{after.name}#{after.discriminator}'s status has changed",\
        color=0xFFFF00)
    notification.set_author(name=after.name, icon_url=after.avatar_url)
    try:
        notification.add_field(name="after", value=f"status : {after.status}\n\nactivity : \n{after.activity.name}\n{after.activity.details}", inline=True)
        notification.add_field(name="before", value=f"status : {before.status}\n\nactivity : \n{after.activity.name}\n{after.activity.details}", inline=True)
    except:
        try:
            notification.add_field(name="after", value=f"status : {after.status}\n\nactivity : \n{after.activity.name}", inline=True)
            notification.add_field(name="before", value=f"status : {before.status}\n\nactivity : \n{after.activity.name}", inline=True)
        except:
            notification.add_field(name="after", value=f"status : {after.status}\n\nactivity : \n{after.activity}", inline=True)
            notification.add_field(name="before", value=f"status : {before.status}\n\nactivity : \n{after.activity}", inline=True)
    return notification


@client.event
async def on_member_update(before, after):
    if after.guild.id in status_notification_channels.keys():
        channel = client.get_channel(status_notification_channels[after.guild.id])
        await channel.send(embed=await notification_generate(before, after))





client.run(os.environ['discord-tutorial-bot-token'])
