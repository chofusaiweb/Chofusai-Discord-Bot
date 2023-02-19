import os
from typing import TYPE_CHECKING

import discord
from discord import app_commands
from discord.ext import commands  # type: ignore

if TYPE_CHECKING:
    # import some original class
    from src.bot import Bot

    pass


class PinMessage(commands.Cog):
    def __init__(self, bot: "Bot"):
        self.bot = bot
        self.ctx_pin_message = app_commands.ContextMenu(
            name="Pin/Unpin message",
            guild_ids=[int(os.environ["GUILD_ID"])],
            callback=self.ctx_pin_message_callback,
        )
        self.bot.tree.add_command(self.ctx_pin_message)

    async def ctx_pin_message_callback(self, interaction: discord.Interaction, message: discord.Message):
        await interaction.response.defer(ephemeral=True)

        if message.pinned:
            res = await self.pin_message(message)
        else:
            res = await self.unpin_message(message)

        await interaction.followup.send(res, ephemeral=True)
        return

    async def pin_message(self, message: discord.Message) -> str:
        try:
            await message.pin()
        except discord.Forbidden as e:
            response = "ピン留めに必要な権限がBotに与えられていません。"
            self.bot.logger.error(response, exc_info=e)
        except discord.NotFound as e:
            response = "メッセージやチャンネルが見つかりませんでした。"
            self.bot.logger.error(response, exc_info=e)
        except discord.HTTPException as e:
            response = "ピン留めに失敗しました。\n既にチャンネルに50個以上のピン留めがある可能性があります。"
            self.bot.logger.error(response, exc_info=e)
        except Exception as e:
            response = "不明なエラーが発生しました。"
            self.bot.logger.error(response, exc_info=e)
        else:
            response = "ピン留めしました。"

        return response

    async def unpin_message(self, message: discord.Message) -> str:
        try:
            await message.unpin()
        except discord.Forbidden as e:
            response = "ピン留め解除に必要な権限がBotに与えられていません。"
            self.bot.logger.error(response, exc_info=e)
        except discord.NotFound as e:
            response = "メッセージやチャンネルが見つかりませんでした。"
            self.bot.logger.error(response, exc_info=e)
        except discord.HTTPException as e:
            response = "ピン留め解除に失敗しました。"
            self.bot.logger.error(response, exc_info=e)
        except Exception as e:
            response = "不明なエラーが発生しました。"
            self.bot.logger.error(response, exc_info=e)
        else:
            response = "ピン留めを解除しました。"

        return response


async def setup(bot: "Bot"):
    await bot.add_cog((PinMessage(bot)))
