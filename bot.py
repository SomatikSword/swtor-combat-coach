import discord
from discord.ext import commands

from config import DISCORD_TOKEN


intents = discord.Intents.default()
intents.message_content = True


bot = commands.Bot(
    command_prefix="!",
    intents=intents
)


@bot.event
async def on_ready():
    print(f"Бот {bot.user} запущен!")


@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")


async def load_cogs():

    try:
        await bot.load_extension("cogs.analyze")
        print("Analyze Cog загружен")

    except Exception as e:
        print("Ошибка загрузки cog:")
        print(e)


async def main():
    async with bot:
        await load_cogs()
        await bot.start(DISCORD_TOKEN)


import asyncio
asyncio.run(main())