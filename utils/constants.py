brain_images = {
    "no_brain": [
        "https://i1.sndcdn.com/artworks-000583301069-jy5ib2-t500x500.jpg",
        "https://i.pinimg.com/originals/6a/1c/84/6a1c843de4d7a5b5843ef63e6ba47e8b.jpg",
        "https://cdn.discordapp.com/attachments/859335247547990026/880461702355902544/Z.png"
    ],
    "small": [
        "https://thumbs.dreamstime.com/b/small-brain-fingers-close-view-male-hand-taking-human-72334857.jpg",
        "https://media.istockphoto.com/photos/xray-of-a-man-with-small-brain-inside-picture-id182163441?k=6&m=182163441&s=170667a&w=0&h=gmcvJM2LKhh37Pi9WLtXWhMwtqCRa7h98UcaWUEYJJg=",
        "https://cdn.drawception.com/drawings/Gx0YdMvYOY.png",
        "https://thumbs.dreamstime.com/b/x-ray-small-brain-black-background-41056681.jpg",
        "https://culturedecanted.files.wordpress.com/2014/06/small.jpg?w=640"
    ],
    "medium": [
        "https://img.i-scmp.com/cdn-cgi/image/fit=contain,width=425,format=auto/sites/default/files/styles/768x768/public/d8/images/methode/2020/07/10/ad89450a-c1d5-11ea-8c85-9f30eae6654e_image_hires_194031.JPG?itok=SmtqUNGR&v=1594381242",
        "https://ychef.files.bbci.co.uk/976x549/p028qsgx.jpg"
    ],
    # just like my dic-
    "big": [
        "https://i1.sndcdn.com/avatars-000597831615-6q438f-t500x500.jpg",
        "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRgERYJeiv_ozoqu2sXNlINA6PXnoa3yfuCus7fpDIZ4ka2bZG1oL0vfnWbfqN8ElQN-ZY&usqp=CAU",
        "https://www.pngitem.com/pimgs/m/523-5238503_pepe-the-frog-big-brain-hd-png-download.png"
    ]
}

from enum import Enum


YOUTUBE_TAGS = {
    "channel_name": "The name of the channel that uploaded a video!",
    "channel_id": "The ID of the channel that uploaded a video.",
    "channel_subs": "The number of subscribers to the channel.",
    "video_url": "The link to the video that was uploaded.",
    "video_id": "The ID of the video that was uploaded.",
    "video_likes": "The number of likes the video has.",
    "video_dislikes": "The number of dislikes the video has.",
    "video_views": "The number of views the video has.",
    "video_title": "The title of the video.",
}

DEFAULT_YOUTUBE_MSG = """
Yooo! **{channel_name}** just uploaded a new video! {video_url}
Go check it out!
"""
class Emojis(str, Enum):
    FIRST = "⏮️"
    PREVIOUS = "⏪"
    NEXT = "⏩"
    LAST = "⏭️"
    TRASH = "🗑️"


USER_FLAGS = {
    'staff': '<:staff:895391901778346045> Discord Staff',
    'partner': '<:partnernew:895391927271309412> Partnered Server Owner',
    'hypesquad': '<:hypesquad:895391957638070282> HypeSquad Events',
    'bug_hunter': '<:bughunter:895392105386631249> Discord Bug Hunter',
    'hypesquad_bravery': '<:bravery:895392137225584651> HypeSquad Bravery',
    'hypesquad_brilliance': '<:brilliance:895392183950131200> HypeSquad Brilliance',
    'hypesquad_balance': '<:balance:895392209564733492> HypeSquad Balance',
    'early_supporter': '<:supporter:895392239356903465> Early Supporter',
    'bug_hunter_level_2': '<:bughunter_gold:895392270369579078> Discord Bug Hunter',
    'verified_bot_developer': '<:earlybotdev:895392298895032364> Early Verified Bot Developer',
    'verified_bot': '<:verified_bot:897876151219912754> Verified Bot',
    'discord_certified_moderator': '<:certified_moderator:895393984308981930> Certified Moderator',
    'premium_since': '<:booster4:895413288219861032>'
}

COMMON_DISCRIMINATORS = ['0001', '0002', '0003', '0004', '0005', '0006', '0007', '0008', '0009',
                         '1111', '2222', '3333', '4444', '5555', '6666', '7777', '8888', '9999',
                         '1010', '2020', '3030', '4040', '5050', '6060', '7070', '8080', '9090',
                         '1001', '2002', '3003', '5004', '5005', '6006', '7007', '8008', '9009',
                         '1000', '2000', '3000', '4000', '5000', '6000', '7000', '8000', '9000',
                         '1337', '6969', '0420', '2021', '0666', '0333']