#
# Copyright (C) 2024 by IamDvis@Github, < https://github.com/IamDvis >.
#
# This file is part of < https://github.com/IamDvis/DV-VIBES > project,
# and is released under the MIT License.
# Please see < https://github.com/IamDvis/DV-VIBES/blob/master/LICENSE >
#
# All rights reserved.

from ANWIVIBES.core.bot import Anwi
from ANWIVIBES.core.dir import dirr
from ANWIVIBES.core.git import git
from ANWIVIBES.core.userbot import Userbot
from ANWIVIBES.misc import dbb, heroku, sudo

from .logging import LOGGER

dirr()
git()
dbb()
sudo()
heroku()

app = Anwi()
userbot = Userbot()


from .platforms import *

Apple = AppleAPI()
Carbon = CarbonAPI()
SoundCloud = SoundAPI()
Spotify = SpotifyAPI()
Resso = RessoAPI()
Telegram = TeleAPI()
YouTube = YouTubeAPI()
