import emojis
import re

from typing import List, Optional, Tuple

from discord import File, MessageReference
from discord.ext.commands import Context
from dataclasses import dataclass

from Helpers.RandomText import RandomText
from Wordle.Canvas import Canvas


@dataclass
class Echo:
    canvas: Canvas

    async def echo(self, ctx: Context) -> Tuple[Optional[str], Optional[List[File]], MessageReference]:
        content = ctx.message.clean_content
        echo_text = content.lstrip(ctx.prefix).lstrip(
            ctx.invoked_with).lstrip()
        echo_files = []

        if not echo_text:
            reference = None

            # Check if message is a reply
            if ctx.message.reference:
                reference = await ctx.channel.fetch_message(ctx.message.reference.message_id)
            else:
                # Attempt to get and echo content from last message in channel
                async for msg in ctx.channel.history(limit=1, before=ctx.message):
                    reference = msg
                    break

            if reference:
                echo_text = reference.clean_content
                echo_files = [await attachment.to_file() for attachment in reference.attachments]

        if not echo_text.strip() and not echo_files:
            x = RandomText.no_evil()
            return (x, None, None)

        # Don't draw URLs
        urls = list(set(re.findall(r'(https?://\S+)', echo_text)))
        for url in urls:
            echo_text = re.sub(f'\s*{url}', '', echo_text)

        # Replace all emojis with supported poop emoji
        echo_text = emojis.encode(
            re.sub(r':[^\s:]+:', emojis.encode(':poop:'),
                   emojis.decode(echo_text)))

        plain_text = ' '.join(urls) if urls else ''
        if echo_text:
            echo_files = [self.canvas.draw_text(
                echo_text, center=False).to_discord_file()] + echo_files

        return (plain_text, echo_files, ctx.message)
