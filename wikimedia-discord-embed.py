# wikimedia-discord-embed v1.0.0
# 
#   Simple Discord bot that replaces the functionality of native
#   Wikimedia Commons embeds which have been broken since early
#   January 2026.
# 
#   When a message contains a direct Wikimedia Commons link the bot
#   retrieves the image and posts it while removing the native embed
#   from the source message.
# 
#   Native embeds appear to be broken due to Wikimedia restricting
#   clients that do not provide a conventional User-Agent. Photos
#   retrieved prior to this change are cached and unaffected.
# 
#   https://yarrie.net/wikimedia
# 
# Usage
# 
#   The bot only requires the discord.py package available from
#   pip. Set the DISCORD_TOKEN environment var and run the file.
# 
# Techincal Notes
# 
#     * Only URLs with the following scheme are recognised:
# 
#       http[s]://commons.wikimedia.org/wiki/File:
# 
#     * There's a maximum of 10 images per message due to Discord
#     restrictions.
# 
#     * Filenames and the requesting user are listed alongside images.
# 
#     * There's no error handling, raw Python errors get dumped to
#     stderr.
# 
#     * URLs do not require the scheme to be recognised.
# 
# License
# 
#   This program is licensed under CC0-1.0, marked as dedicated to the 
#   public domain, see LICENSE file.
# 
# Contributing
# 
#   Please email any feedback or patches to harry@harrystanton.com, I
#   cherish all correspondence.

import os
import io
from urllib.parse import urlparse
from urllib.request import urlopen
from urllib.request import Request

# third-party packages
import discord

# discord
if "DISCORD_TOKEN" not in os.environ:
    print("error: missing DISCORD_TOKEN environment variable", file=sys.stderr)
    exit(1)
DISCORD_TOKEN=os.environ["DISCORD_TOKEN"]

# wikimedia
USER_AGENT="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.3"
URL="https://commons.wikimedia.org/wiki/File:"

# lazy html parser to avoid importing more modules
def parse_opengraph_image(html):
    prop_i = html.index('property="og:image"')
    url_start_i = html[prop_i:].index('content="') + len('content="') + prop_i
    url_end_i = html[url_start_i:].index('"') + url_start_i
    return html[url_start_i:url_end_i]

def generate_url(filename):
    return URL+filename

def parse_url(url_raw):
    url = urlparse(url_raw)

    if url.scheme == "":
        if url_raw.startswith("commons.wikimedia.org"):
            return parse_url("https://" + url_raw)

    if url.hostname != "commons.wikimedia.org":
        return None
    if not url.path.startswith("/wiki/File:"):
        return None

    file_index = url.path.index("File:")
    return url.path[file_index+5:]

# Take a raw Wikimedia image URL, download the preview and return the
# raw image data. Has strict URL validation and returns None on an
# invalid URL.
def dl_raw_url_img(raw_url):
    # clean up url
    filename = parse_url(raw_url)
    if filename is None:
        return None
    page_url = generate_url(filename)

    # make page request for raw image url
    req = Request(page_url, data=None, headers={
        "User-Agent": USER_AGENT
    })
    
    # download the image url
    image_url = None
    with urlopen(req) as f:
        html = f.read().decode("utf-8")
        image_url = parse_opengraph_image(html)

    req = Request(image_url, data=None, headers={
        "User-Agent": USER_AGENT
    })
    with urlopen(req) as f:
        data = f.read()
        return (filename, data)

class Bot(discord.Client):
    async def on_ready(self):
        print("logged in")

    async def on_message(self, message):
        if message.author == self.user:
            return

        split = message.content.split(" ")

        filenames = []
        files = []
        for word in split:
            # dl_raw_url_img will return None on invalid URL
            res = dl_raw_url_img(word)
            if res is not None:
                filename, img_data = res

                bytes = io.BytesIO(img_data)
                d_file = discord.File(bytes, filename=filename)
                files.append(d_file)
                filenames.append("`" + filename + "`")

                if len(files) >= 10:
                    break
        if len(files) > 0:
            await message.edit(suppress=True)
            text = "\n".join(filenames) + "\n" + message.author.name
            await message.channel.send(text, files=files)

intents = discord.Intents.default()
intents.message_content = True
bot = Bot(intents=intents)
bot.run(DISCORD_TOKEN)

