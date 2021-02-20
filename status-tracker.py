status_notification_channels = {}

import discord
import os

intents = discord.Intents.default()
intents.members = True
intents.presences = True
client = discord.Client(intents=intents)

if os.path.isfile("status-notification-channel-list.txt"):
    with open("status-notification-channel-list.txt", 'r') as f:
        while(True):
            temp1 = f.readline()[:-2]
            print(temp1)
            if not temp1: break

            temp2 = f.readline()[:-2]
            print(temp2)
            status_notification_channels[int(temp1)] = int(temp2)
else:
    f = open("status-notification-channel-list.txt", "w")
    f.close()


async def ready_message(client):
    for guild in client.guilds:
        for channel in guild.channels:
            try:
                await channel.send("I'm ready!!")
            except:
                print(f"maybe {guild.name} - {channel.name} is not a text channel")


@client.event
async def on_ready():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="member status"))
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
            with open("status-notification-channel-list.txt", "a") as f:
                f.write(str(message.guild.id)+"\n")
                f.write(str(message.channel.id)+"\n")
            await message.channel.send("done")
        else:
            await message.channel.send("There already exists a status notification channel in this server!!\nYou can not create more than one status notification channel in a server!!")

    if message.content.startswith(command_prefix+"del_status_notification_channel"):
        if not message.guild.id in status_notification_channels.keys():
            await message.channel.send("There is no status notification channel in this server!!")
        else:
            del status_notification_channels[message.guild.id]
            with open("status-notification-channel-list.txt", 'wt') as f:
                for server_id, channel_id in enumerate(status_notification_channels):
                    f.write(str(server_id)+"\n")
                    f.write(str(channel_id)+"\n")
            await message.channel.send("done")



async def notification_generate(before, after):
    notification = discord.Embed(\
        title=f"{after.name}#{after.discriminator}'s status has changed",\
        color=0xFFFF00)
    notification.set_author(name=after.name, icon_url=after.avatar_url)
    try:
        notification.add_field(name="after", value=f"status : {after.status}\n\nactivity : \n{after.activity.name}\n{after.activity.details}", inline=True)
    except:
        try:
            notification.add_field(name="after", value=f"status : {after.status}\n\nactivity : \n{after.activity.name}", inline=True)
        except:
            notification.add_field(name="after", value=f"status : {after.status}\n\nactivity : \n{after.activity}", inline=True)

    try:
        notification.add_field(name="before", value=f"status : {before.status}\n\nactivity : \n{before.activity.name}\n{before.activity.details}", inline=True)
    except:
        try:
            notification.add_field(name="before", value=f"status : {before.status}\n\nactivity : \n{before.activity.name}", inline=True)
        except:
            notification.add_field(name="before", value=f"status : {before.status}\n\nactivity : \n{before.activity}", inline=True)
    return notification


@client.event
async def on_member_update(before, after):
    if after.guild.id in status_notification_channels.keys():
        channel = client.get_channel(status_notification_channels[after.guild.id])
        await channel.send(embed=await notification_generate(before, after))





client.run(os.environ['discord-tutorial-bot-token'])
