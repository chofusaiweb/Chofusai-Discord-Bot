import os
from typing import TYPE_CHECKING

import discord
from discord import app_commands
from discord.ext import commands

from db.redis import UnarchiveClient
from src.text.error import ErrorText
from utils.finder import Finder

if TYPE_CHECKING:
    # import some original class
    from src.bot import Bot

    pass


class Thread(commands.Cog):
    def __init__(self, bot: "Bot"):
        self.bot = bot

    group = app_commands.Group(
        name="unarchive",
        description="アーカイブ自動解除機能",
        guild_ids=[int(os.environ["GUILD_ID"])],
    )

    @commands.Cog.listener("on_raw_thread_update")
    async def handle_thread_archive(self, payload: discord.RawThreadUpdateEvent):
        if payload.thread:
            thread = payload.thread
        else:
            finder = Finder(self.bot)
            thread = await finder.find_channel(payload.thread_id, discord.Thread)

        if thread.archived and not thread.locked:
            targets = await self.get_targets()
            if thread.id not in targets:
                return

            try:
                await thread.edit(archived=False)
            except discord.Forbidden as e:
                self.bot.logger.exception(ErrorText.FORBIDDEN, exc_info=e)
            except discord.HTTPException as e:
                self.bot.logger.exception(ErrorText.FAILED_TO_UNARCHIVE, exc_info=e)
            finally:
                pass
        else:
            pass
        return

    @group.command(name="on", description="アーカイブ自動解除を有効にする")
    @app_commands.guild_only()
    async def unarchive_on(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        if not isinstance(interaction.channel, discord.Thread):
            await interaction.followup.send("スレッド以外では使用できません。", ephemeral=True)
            return

        length = await self.toggle_unarchive(interaction.channel.id, on=True)

        if length == 1:
            res = "アーカイブ設定を有効にしました。"
        elif length == 0:
            res = "既にアーカイブ設定が有効になっています。"
        else:
            res = "予期せぬエラーが発生しました。"

        await interaction.followup.send(res, ephemeral=True)

    @group.command(name="off", description="アーカイブ自動解除を無効にする")
    @app_commands.guild_only()
    async def unarchive_off(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        if not isinstance(interaction.channel, discord.Thread):
            await interaction.followup.send("スレッド以外では使用できません。", ephemeral=True)
            return

        length = await self.toggle_unarchive(interaction.channel.id, on=False)

        if length == 1:
            res = "アーカイブ設定を無効にしました。"
        elif length == 0:
            res = "既にアーカイブ設定が無効になっています。"
        else:
            res = "予期せぬエラーが発生しました。"

        await interaction.followup.send(res, ephemeral=True)

    @group.command(name="status", description="このスレッドのアーカイブ自動解除の設定を表示する")
    @app_commands.guild_only()
    async def unarchive_status(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        if not isinstance(interaction.channel, discord.Thread):
            await interaction.followup.send("スレッド以外では使用できません。", ephemeral=True)
            return

        async with UnarchiveClient() as redis:
            is_already_target = await redis.is_target(interaction.channel.id)

        res = "このスレッドはアーカイブ自動解除の対象です。" if is_already_target else "このスレッドはアーカイブ自動解除の対象ではありません。"
        await interaction.followup.send(res, ephemeral=True)
        return

    @group.command(name="list", description="アーカイブ自動解除の対象のスレッドを表示する")
    @app_commands.guild_only()
    async def unarchive_list(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        async with UnarchiveClient() as redis:
            targets = await redis.get_targets()

        if not targets or targets == ():
            embed = discord.Embed(
                title="アーカイブ自動解除の対象のスレッド",
                color=discord.Color(0x3498DB),
                description="アーカイブ自動解除の対象のスレッドはありません。",
            )
        else:
            embed = discord.Embed(
                title="アーカイブ自動解除の対象スレッド",
                color=discord.Color(0x3498DB),
            )
            embed.add_field(
                name="対象スレッド",
                value="\n".join([f"<#{target}>" for target in targets]),
            )

        await interaction.followup.send(embed=embed, ephemeral=True)
        return

    async def toggle_unarchive(self, thread_id: int, on: bool):
        async with UnarchiveClient() as redis:
            if on:
                return await redis.add_target(thread_id)
            else:
                return await redis.remove_target(thread_id)

    async def get_targets(self) -> tuple[int, ...]:
        async with UnarchiveClient() as redis:
            return await redis.get_targets()


async def setup(bot: "Bot"):
    await bot.add_cog((Thread(bot)))
