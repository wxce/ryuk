import discord
import requests
from colorthief import ColorThief
import math
import random

blocks = [" ", ".", ":", "|"]


def role_from_mention(guild, text, default=None):
    text = text.strip("<>@&#!")
    try:
        role = guild.get_role(int(text))
        return role
    except ValueError:
        return default


def user_from_mention(getfrom, text, default=None):
    text = text.strip("<>@!#")
    try:
        if isinstance(getfrom, discord.Client):
            user = getfrom.get_user(int(text))
        elif isinstance(getfrom, discord.Guild):
            user = getfrom.get_member(int(text))
        else:
            return default
        if user is None:
            return default
        return user
    except ValueError:
        return default


def channel_from_mention(guild, text, default=None):
    text = text.strip("<>#!@")
    try:
        channel = guild.get_channel(int(text))
        if channel is None:
            return default
        return channel
    except ValueError:
        return default


def get_color(url):
    if url.strip() == "":
        return None
    try:
        r = requests.get(url)
        if r.status_code == 200:
            with open('downloads/album_art.png', 'wb') as f:
                for chunk in r:
                    f.write(chunk)
        else:
            return None

        color_thief = ColorThief('downloads/album_art.png')
        dominant_color = color_thief.get_color(quality=1)

        return to_hex(dominant_color)
    except Exception as e:
        print(e)
        return None


def to_hex(rgb):
    r, g, b = rgb

    def clamp(x):
        return max(0, min(x, 255))

    return "{0:02x}{1:02x}{2:02x}".format(clamp(r), clamp(g), clamp(b))


def get_xp(level):
    a = 0
    for x in range(1, level):
        a += math.floor(x + 300 * math.pow(2, (x / 7)))
    return math.floor(a / 4)


def get_level(xp):
    i = 1
    while get_xp(i + 1) < xp:
        i += 1
    return i


def xp_to_next_level(level):
    return get_xp(level + 1) - get_xp(level)


def xp_from_message(message):
    words = message.content.split(" ")
    eligible_words = 0
    for x in words:
        if len(x) > 1:
            eligible_words += 1
    xp = eligible_words + 10 * len(message.attachments)
    return xp


def cap(data, floor, height, steps):
    highest = max(data)
    if highest < floor:
        highest = floor

    piece = (highest / steps) / height

    new_list = []
    for i in range(len(data)):
        new_item = round(data[i] / piece)
        new_list.append(new_item)
    return new_list


def generate_graph(data, height, floor=100):
    steps = len(blocks) - 1
    data = cap(data, floor, height, steps)
    nums = [str(i).zfill(2) for i in range(len(data))]
    rows = []
    for row in reversed(range(height)):
        this_row = ""
        for i in range(len(data)):
            rem = data[i] - (row * steps)
            if rem < 0:
                rem = 0
            elif rem > steps:
                rem = steps
            this_row += blocks[rem]
        rows.append(this_row)

    number_row = []
    for z in range(2):
        this_row = ""
        for number in nums:
            this_row += number[z]
        number_row.append(this_row)

    return rows, number_row


def useragent():
    __useragents = ["Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.5; en-US; rv:1.9.1b3) Gecko/20090305 Firefox/3.1b3 GTB5",
                    "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.5; ko; rv:1.9.1b2) Gecko/20081201 Firefox/3.1b2",
                    "Mozilla/5.0 (X11; U; SunOS sun4u; en-US; rv:1.9b5) Gecko/2008032620 Firefox/3.0b5",
                    "Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.8.1.12) Gecko/20080214 Firefox/2.0.0.12",
                    "Mozilla/5.0 (Windows; U; Windows NT 5.1; cs; rv:1.9.0.8) Gecko/2009032609 Firefox/3.0.8",
                    "Mozilla/5.0 (X11; U; OpenBSD i386; en-US; rv:1.8.0.5) Gecko/20060819 Firefox/1.5.0.5",
                    "Mozilla/5.0 (Windows; U; Windows NT 5.0; es-ES; rv:1.8.0.3) Gecko/20060426 Firefox/1.5.0.3",
                    "Mozilla/5.0 (Windows; U; WinNT4.0; en-US; rv:1.7.9) Gecko/20050711 Firefox/1.0.5",
                    "Mozilla/5.0 (Windows; Windows NT 6.1; rv:2.0b2) Gecko/20100720 Firefox/4.0b2",
                    "Mozilla/5.0 (X11; Linux x86_64; rv:2.0b4) Gecko/20100818 Firefox/4.0b4",
                    "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.2) Gecko/20100308 Ubuntu/10.04 (lucid) Firefox/3.6 GTB7.1",
                    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:2.0b7) Gecko/20101111 Firefox/4.0b7",
                    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:2.0b8pre) Gecko/20101114 Firefox/4.0b8pre",
                    "Mozilla/5.0 (X11; Linux x86_64; rv:2.0b9pre) Gecko/20110111 Firefox/4.0b9pre",
                    "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:2.0b9pre) Gecko/20101228 Firefox/4.0b9pre",
                    "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:2.2a1pre) Gecko/20110324 Firefox/4.2a1pre",
                    "Mozilla/5.0 (X11; U; Linux amd64; rv:5.0) Gecko/20100101 Firefox/5.0 (Debian)",
                    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:6.0a2) Gecko/20110613 Firefox/6.0a2",
                    "Mozilla/5.0 (X11; Linux i686 on x86_64; rv:12.0) Gecko/20100101 Firefox/12.0",
                    "Mozilla/5.0 (Windows NT 6.1; rv:15.0) Gecko/20120716 Firefox/15.0a2",
                    "Mozilla/5.0 (X11; Ubuntu; Linux armv7l; rv:17.0) Gecko/20100101 Firefox/17.0",
                    "Mozilla/5.0 (Windows NT 6.1; rv:21.0) Gecko/20130328 Firefox/21.0",
                    "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:22.0) Gecko/20130328 Firefox/22.0",
                    "Mozilla/5.0 (Windows NT 5.1; rv:25.0) Gecko/20100101 Firefox/25.0",
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:25.0) Gecko/20100101 Firefox/25.0",
                    "Mozilla/5.0 (Windows NT 6.1; rv:28.0) Gecko/20100101 Firefox/28.0",
                    "Mozilla/5.0 (X11; Linux i686; rv:30.0) Gecko/20100101 Firefox/30.0",
                    "Mozilla/5.0 (Windows NT 5.1; rv:31.0) Gecko/20100101 Firefox/31.0",
                    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:33.0) Gecko/20100101 Firefox/33.0",
                    "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0",
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:58.0) Gecko/20100101 Firefox/58.0"]
    return random.choice(__useragents)
