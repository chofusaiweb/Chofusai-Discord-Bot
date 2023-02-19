from typing import TYPE_CHECKING

import discord
from discord.ext import commands
from dispander import dispand

if TYPE_CHECKING:
    # import some original class
    from src.bot import Bot

    pass


class Dispander(commands.Cog):
    def __init__(self, bot: "Bot"):
        self.bot = bot

    @commands.Cog.listener("on_message")
    async def on_message(self, message: discord.Message):
        if message.author.id == self.bot.user.id:  # type: ignore
            return

        embeds: list[discord.Embed] = await dispand(self.bot, message)

        if embeds:
            try:
                await message.channel.send(embeds=embeds)
            except Exception as e:
                self.bot.logger.error(e)
            return


async def setup(bot: "Bot"):
    await bot.add_cog(Dispander(bot))
