import os
from typing import TYPE_CHECKING

import discord
from discord import app_commands
from discord.ext import commands

from src.text.error import ErrorText

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
        author_name = str(interaction.user)

        if message.pinned:
            res = await self.unpin_message(author_name, message)
        else:
            res = await self.pin_message(author_name, message)

        await interaction.followup.send(res, ephemeral=True)
        return

    async def pin_message(self, author: str, message: discord.Message) -> str:
        try:
            await message.pin(reason=f"by {author}")
        except discord.Forbidden as e:
            response = ErrorText.FORBIDDEN
            self.bot.logger.error(response, exc_info=e)
        except discord.NotFound as e:
            response = ErrorText.CHANNEL_OR_MESSAGE_NOT_FOUND
            self.bot.logger.error(response, exc_info=e)
        except discord.HTTPException as e:
            response = ErrorText.FAILED_TO_PIN
            self.bot.logger.error(response, exc_info=e)
        except Exception as e:
            response = ErrorText.UNKNOWN_ERROR
            self.bot.logger.error(response, exc_info=e)
        else:
            response = "ピン留めしました。"

        return response

    async def unpin_message(self, author: str, message: discord.Message) -> str:
        try:
            await message.unpin(reason=f"by {author}")
        except discord.Forbidden as e:
            response = ErrorText.FORBIDDEN
            self.bot.logger.error(response, exc_info=e)
        except discord.NotFound as e:
            response = ErrorText.CHANNEL_OR_MESSAGE_NOT_FOUND
            self.bot.logger.error(response, exc_info=e)
        except discord.HTTPException as e:
            response = ErrorText.FAILED_TO_UNPIN
            self.bot.logger.error(response, exc_info=e)
        except Exception as e:
            response = ErrorText.UNKNOWN_ERROR
            self.bot.logger.error(response, exc_info=e)
        else:
            response = "ピン留めを解除しました。"

        return response


async def setup(bot: "Bot"):
    await bot.add_cog((PinMessage(bot)))
