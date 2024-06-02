# Copyright 2016-2024 Peppy Player peppy.player@gmail.com
# 
# This file is part of Peppy Player.
# 
# Peppy Player is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# Peppy Player is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with Peppy Player. If not, see <http://www.gnu.org/licenses/>.

import sys
import os
import logging
import codecs
import shutil

from configparser import ConfigParser
from util.keys import *
from urllib import request
from player.proxy import BLUETOOTH_SINK_NAME, VLC_NAME, MPD_NAME, MPV_NAME, SHAIRPORT_SYNC_NAME, RASPOTIFY_NAME
from util.collector import GENRE, ARTIST, ALBUM, TITLE, DATE, TYPE, COMPOSER, FOLDER, FILENAME
from os.path import expanduser

DEFAULT_VOLUME_LEVEL = 30
DEFAULTS = "defaults"

FOLDER_CONFIGURATION = "configuration"
FOLDER_LANGUAGES = "languages"
FOLDER_RADIO_STATIONS = "radio-stations"
FOLDER_BACKGROUNDS = "backgrounds"
FOLDER_PLAYLISTS = "playlists"

FILE_LABELS = "labels.properties"
FILE_VOICE_COMMANDS = "voice-commands.properties"
FILE_FLAG = "flag.png"
FILE_CONFIG = "config.txt"
FILE_CURRENT = "current.txt"
FILE_PLAYERS = "players.txt"
FILE_LANGUAGES = "languages.txt"
FILE_RELEASE = "release.txt"
FILE_BACKGROUND = "background.txt"

RELEASE = "release"
PRODUCT_NAME = "product.name"
EDITION_NAME = "edition.name"
RELEASE_YEAR = "year"
RELEASE_MONTH = "month"
RELEASE_DAY = "day"

SCREEN_INFO = "screen.info"
WIDTH = "width"
HEIGHT = "height"
DEPTH = "depth"
FRAME_RATE = "frame.rate"
HDMI = "hdmi"
NO_FRAME = "no.frame"
FLIP_TOUCH_XY = "flip.touch.xy"
MULTI_TOUCH = "multi.touch"

USAGE = "usage"
USE_TOUCHSCREEN = "touchscreen"
USE_MOUSE = "mouse"
USE_LIRC = "lirc"
USE_WEB = "web"
USE_STREAM_SERVER = "stream.server"
USE_BROWSER_STREAM_PLAYER = "browser.stream.player"
USE_VOICE_ASSISTANT = "voice.assistant"
USE_HEADLESS = "headless"
USE_VU_METER = "vu.meter"
USE_ALBUM_ART = "album.art"
USE_AUTO_PLAY = "auto.play"
USE_LONG_PRESS_TIME = "long.press.time.ms"
USE_DESKTOP = "desktop"
USE_CHECK_FOR_UPDATES = "check.for.updates"
USE_BLUETOOTH = "bluetooth"
USE_SAMBA = "samba"
USE_DNS_IP = "dns.ip"
USE_CLOCK_SCREENSAVER_IN_TIMER = "use.clock.screensaver.in.timer"

LOGGING = "logging"
FILE_LOGGING = "file.logging"
LOG_FILENAME = "log.filename"
APPEND = "append"
CONSOLE_LOGGING = "console.logging"
ENABLE_STDOUT = 'enable.stdout'
SHOW_MOUSE_EVENTS = 'show.mouse.events'

FILE_BROWSER = "file.browser"
AUDIO_FILE_EXTENSIONS = "audio.file.extensions"
PLAYLIST_FILE_EXTENSIONS = "playlist.file.extensions"
IMAGE_FILE_EXTENSIONS = "image.file.extensions"
FOLDER_IMAGES = "folder.images"
COVER_ART_FOLDERS = "cover.art.folders"
SHOW_EMBEDDED_IMAGES = "show.embedded.images"
ENABLE_EMBEDDED_IMAGES = "enable.embedded.images"
ENABLE_FOLDER_IMAGES = "enable.folder.images"
ENABLE_IMAGE_FILE_ICON = "enable.image.file.icon"
ENABLE_BUTTON_HOME = "enable.button.home"
ENABLE_BUTTON_CONFIG = "enable.button.config"
ENABLE_BUTTON_PLAYLIST = "enable.button.playlist"
ENABLE_BUTTON_USER = "enable.button.user"
ENABLE_BUTTON_ROOT = "enable.button.root"
ENABLE_BUTTON_PARENT = "enable.button.parent"
HIDE_FOLDER_NAME = "hide.folder.name"
IMAGE_AREA = "image.area"
IMAGE_SIZE = "image.size"
ICON_SIZE = "icon.size"
IMAGE_SIZE_WITHOUT_LABEL = "image.size.without.label"
PADDING = "padding"
LIST_VIEW_ROWS = "list.view.rows"
LIST_VIEW_COLUMNS = "list.view.columns"
ICON_VIEW_ROWS = "icon.view.rows"
ICON_VIEW_COLUMNS = "icon.view.columns"
ALIGN_BUTTON_CONTENT_X = "alignment"
SORT_BY_TYPE = "sort.by.type"
FILE_TYPES = "file.types"
WRAP_LABELS = "wrap.lines"
HORIZONTAL_LAYOUT = "horizontal.layout"
FONT_HEIGHT_PERCENT = "font.height"
USE_SWITCH = "use.switch"
DISK_SWITCH_FILE = "disks.txt"
NAS_FILE = "nas.txt"
ASCENDING = "ascending"

PLAYBACK_ORDER = "playback.order"
PLAYBACK_CYCLIC = "cyclic"
PLAYBACK_REGULAR = "regular"
PLAYBACK_SINGLE_TRACK = "detail"
PLAYBACK_SHUFFLE = "shuffle"
PLAYBACK_SINGLE_CYCLIC = "single"

WEB_SERVER = "web.server"
HTTPS = "https"
HTTP_PORT = "http.port"

STREAM_SERVER = "stream.server"
STREAM_SERVER_PORT = "stream.server.port"

PODCASTS_FOLDER = "podcasts.folder"
PODCAST_URL = "podcast.url"
PODCAST_EPISODE_NAME = "podcast.episode.name"
PODCAST_EPISODE_URL = "podcast.episode.url"
PODCAST_EPISODE_TIME = "podcast.episode.time"

FILE_PLAYLISTS_FOLDER = "file.playlists.folder"
MUSIC_FOLDER = "music.folder"

WINDOWS_MUSIC_FOLDER = "c:\music"
WINDOWS_PLAYLISTS_FOLDER = "c:\playlists"
WINDOWS_PODCASTS_FOLDER = "c:\podcasts"

YA_STREAM_ID = "ya.stream.id"
YA_STREAM_NAME = "ya.stream.name"
YA_STREAM_URL = "ya.stream.url"
YA_THUMBNAIL_PATH = "ya.stream.thumbnail.path"
YA_STREAM_TIME = "ya.stream.time"

RADIO_BROWSER_SEARCH_BY = "radio.browser.search.by"
RADIO_BROWSER_SEARCH_ITEM = "radio.browser.search.item"
RADIO_BROWSER_SEARCH_STATION_ID = "radio.browser.search.station.id"
FAVORITE_STATION_NAME = "favorite.station.name"
FAVORITE_STATION_ID = "favorite.station.id"
FAVORITE_STATION_LOGO = "favorite.station.logo"
FAVORITE_STATION_URL = "favorite.station.url"

SEARCH = "search"
FILE = "file"
FILE_TIME = "file.time"

HOME = "home"
HOME_MENU = "home.menu"
RADIO = "radio"
RADIO_BROWSER = "radio-browser"
AUDIO_FILES = "audio-files"
AUDIOBOOKS = "audiobooks"
STREAM = "stream"
PODCASTS = "podcasts"
AIRPLAY = "airplay"
SPOTIFY_CONNECT = "spotify-connect"
BLUETOOTH_SINK = "bluetooth-sink"
YA_STREAM = "ya-streams"
ARCHIVE = "archive"
JUKEBOX = "jukebox"
CATALOG = "catalog"
PAGE = "page"
ITEM = "item"
FOLDERS = "folders"

COLLECTION = "collection"
DATABASE_FILE = "database.file"
BASE_FOLDER = "base.folder"
SHOW_NUMBERS = "show.numbers"
COLLECTION_TOPIC = "topic"
TOPIC_DETAIL = "collection detail"
COLLECTION_TRACK = "collection.track"
COLLECTION_MENU = "collection.menu"
URL = "url"
FILE_NOT_FOUND = "file.not.found"

HOME_NAVIGATOR = "home.navigator"
HOME_BACK = "back"
HOME_SCREENSAVER = "screensaver"
HOME_LANGUAGE = "language"
EQUALIZER = "equalizer"
TIMER = "timer"
NETWORK = "network"
WIFI = "wi-fi"
BLUETOOTH = "bluetooth"
KEYBOARD = "keyboard"
PLAYER = "player"
ABOUT = "about"

DISK_MOUNT = "disk.mount"
MOUNT_AT_STARTUP = "mount.at.startup"
MOUNT_AT_PLUG = "mount.at.plug"
MOUNT_READ_ONLY = "mount.read.only"
MOUNT_POINT = "mount.point"
MOUNT_OPTIONS = "mount.options"

SLEEP = "sleep"
SLEEP_TIME = "sleep.time"
WAKE_UP = "wake.up"
WAKE_UP_TIME = "wake.up.time"
POWEROFF = "poweroff"
SLEEP_NOW = "sleep-now"
LOADING = "loading"

COLORS = "colors"
COLOR_WEB_BGR = "color.web.bgr" 
COLOR_DARK = "color.dark"
COLOR_DARK_LIGHT = "color.dark.light"
COLOR_MEDIUM = "color.medium"
COLOR_BRIGHT = "color.bright"
COLOR_CONTRAST = "color.contrast"
COLOR_LOGO = "color.logo"
COLOR_MUTE = "color.mute"
COLOR = "color"

ICONS = "icons"
ICONS_CATEGORY = "category"
ICONS_TYPE = "type"
ICONS_COLOR_1_MAIN = "color.1.main"
ICONS_COLOR_1_ON = "color.1.on"
ICONS_COLOR_2_MAIN = "color.2.main"
ICONS_COLOR_2_ON = "color.2.on"

BACKGROUND = "background"
BACKGROUND_DEFINITIONS = "background.definitions"
BGR_TYPE = "bgr.type"
BGR_TYPE_IMAGE = "image"
BGR_TYPE_COLOR = "color"
SCREEN_BGR_COLOR = "screen.bgr.color"
SCREEN_BGR_NAMES = "screen.bgr.names"
HEADER_BGR_OPACITY = "header.bgr.opacity"
MENU_BGR_OPACITY = "menu.bgr.opacity"
FOOTER_BGR_OPACITY = "footer.bgr.opacity"
WEB_SCREEN_BGR_OPACITY = "web.screen.bgr.opacity"
WEB_SCREEN_COLOR = "web.screen.color"
WEB_BGR_NAMES = "web.bgr.names"

BGR_FILENAME = "filename"
BLUR_RADIUS = "blur.radius"
WEB_BGR_BLUR_RADIUS = "web.bgr.blur.radius"
OVERLAY_COLOR = "overlay.color"
OVERLAY_OPACITY = "overlay.opacity"

HEADER_BGR_COLOR = "header.bgr.color"
MENU_BGR_COLOR = "menu.bgr.color"
FOOTER_BGR_COLOR = "footer.bgr.color"
WEB_BGR = "web.bgr"
WEB_BGR_COLOR = "web.bgr.color"

FONT_SECTION = "font"
FONT_KEY = "font.name"

PLAYER_SCREEN = "player.screen"
TOP_HEIGHT_PERCENT = "top.height"
BOTTOM_HEIGHT_PERCENT = "bottom.height"
BUTTON_HEIGHT_PERCENT = "button.height"
POPUP_WIDTH_PERCENT = "popup.width"
IMAGE_LOCATION = "image.location"
LOCATION_CENTER = "center"
LOCATION_LEFT = "left"
LOCATION_RIGHT = "right"
ENABLE_ORDER_BUTTON = "enable.order.button"
ENABLE_INFO_BUTTON = "enable.info.button"
SHOW_TIME_SLIDER = "show.time.slider"

SCRIPTS = "scripts"
SCRIPT_PLAYER_START = "script.player.start"
SCRIPT_PLAYER_STOP = "script.player.stop"
SCRIPT_SCREENSAVER_START = "script.screensaver.start"
SCRIPT_SCREENSAVER_STOP = "script.screensaver.stop"
SCRIPT_TIMER_START = "script.timer.start"
SCRIPT_TIMER_STOP = "script.timer.stop"

GPIO = "gpio"
USE_PLAYER_BUTTONS = "use.player.buttons"
BUTTON_TYPE = "button.type"
USE_MENU_BUTTONS = "use.menu.buttons"
USE_ROTARY_ENCODERS = "use.rotary.encoders"
BUTTON_LEFT = "button.left"
BUTTON_RIGHT = "button.right"
BUTTON_UP = "button.up"
BUTTON_DOWN = "button.down"
BUTTON_SELECT = "button.select"
BUTTON_VOLUME_UP = "button.volume.up"
BUTTON_VOLUME_DOWN = "button.volume.down"
BUTTON_MUTE = "button.mute"
BUTTON_PLAY_PAUSE = "button.play.pause"
BUTTON_NEXT = "button.next"
BUTTON_PREVIOUS = "button.previous"
BUTTON_HOME = "button.home"
BUTTON_POWEROFF = "button.poweroff"
ROTARY_VOLUME_UP = "rotary.encoder.volume.up"
ROTARY_VOLUME_DOWN = "rotary.encoder.volume.down"
ROTARY_VOLUME_MUTE = "rotary.encoder.volume.mute"
ROTARY_NAVIGATION_LEFT = "rotary.encoder.navigation.left"
ROTARY_NAVIGATION_RIGHT = "rotary.encoder.navigation.right"
ROTARY_NAVIGATION_SELECT = "rotary.encoder.navigation.select"
ROTARY_JITTER_FILTER = "rotary.encoder.jitter.filter"
BUTTON_MENU_1 = "button.menu.1"
BUTTON_MENU_2 = "button.menu.2"
BUTTON_MENU_3 = "button.menu.3"
BUTTON_MENU_4 = "button.menu.4"
BUTTON_MENU_5 = "button.menu.5"
BUTTON_MENU_6 = "button.menu.6"
BUTTON_MENU_7 = "button.menu.7"
BUTTON_MENU_8 = "button.menu.8"
BUTTON_MENU_9 = "button.menu.8"
BUTTON_MENU_10 = "button.menu.10"

I2C = "i2c"
I2C_INPUT_ADDRESS = "i2c.input.address"
I2C_OUTPUT_ADDRESS = "i2c.output.address"
I2C_GPIO_INTERRUPT = "i2c.gpio.interrupt"

DSI_DISPLAY_BACKLIGHT = "display.backlight"
USE_DSI_DISPLAY = "use.display.backlight"
SCREEN_BRIGHTNESS = "screen.brightness"
SCREENSAVER_BRIGHTNESS = "screensaver.brightness"
SCREENSAVER_DISPLAY_POWER_OFF = "screensaver.display.power.off"
SLEEP_NOW_DISPLAY_POWER_OFF = "sleep.now.display.power.off"
BACKLIGHTER = "backlighter"

VOLUME_CONTROL = "volume.control"
VOLUME_CONTROL_TYPE = "type"
VOLUME_CONTROL_TYPE_PLAYER = "player"
VOLUME_CONTROL_TYPE_AMIXER = "amixer"
VOLUME_CONTROL_TYPE_HARDWARE = "hardware"
AMIXER_CONTROL = "amixer.control"
AMIXER_SCALE = "amixer.scale"
AMIXER_SCALE_LINEAR = "linear"
AMIXER_SCALE_LOGARITHM = "logarithm"
INITIAL_VOLUME_LEVEL = "initial.volume.level"
MAXIMUM_LEVEL = "maximum.level"

LANGUAGES_MENU = "languages.menu"

SCREENSAVER_MENU = "screensaver.menu"
SCREENSAVER_DELAY = "screensaver.delay"
CLOCK = "clock"
LOGO = "logo"
SLIDESHOW = "slideshow"
VUMETER = "peppymeter"
WEATHER = "peppyweather"
SPECTRUM = "spectrum"
LYRICS = "lyrics"
PEXELS = "pexels"
MONITOR = "monitor"
HOROSCOPE = "horoscope"
STOCK = "stock"
RANDOM = "random"
GENERATED_IMAGE = "generated.img."
FILE_INFO = "file-info"
ACTIVE_SAVERS = "active.savers"
DISABLED_SAVERS = "disabled.savers"

CURRENT = "current"
MODE = "mode"
LANGUAGE = "language"

PLAYER_SETTINGS = "player.settings"
VOLUME = "volume"
MUTE = "mute"
PAUSE = "pause"

FILE_PLAYBACK = "file.playback"
CURRENT_FILE_PLAYBACK_MODE = "file.playback.mode"
CURRENT_FOLDER = "folder"
CURRENT_FILE_PLAYLIST = "file.playlist"
CURRENT_FILE = "file"
CURRENT_TRACK_TIME = "track.time"
CURRENT_FILE_PLAYLIST_INDEX = "file.playlist.index"

COLLECTION_PLAYBACK = "collection.playback"
COLLECTION_TOPIC = "collection.topic"
COLLECTION_FOLDER = "collection.folder"
COLLECTION_FILE = "collection.file"
COLLECTION_URL = "collection.url"
COLLECTION_TRACK_TIME = "collection.track.time"

BROWSER_SITE = "site"
BROWSER_BOOK_TITLE = "book.title"
BROWSER_BOOK_URL = "book.url"
BROWSER_IMAGE_URL = "image.url"
BROWSER_TRACK_FILENAME = "book.track.filename"
BROWSER_BOOK_TIME = "book.time"

SCREENSAVER = "screensaver"
NAME = "name"
DELAY = "delay"
KEY_SCREENSAVER_DELAY_1 = "delay.1"
KEY_SCREENSAVER_DELAY_3 = "delay.3"
KEY_SCREENSAVER_DELAY_OFF = "delay.off"

STATIONS = "stations"
CURRENT_STATIONS = "current.stations" 

AUDIO = "audio"
PLAYER_NAME = "player.name"
PLAYERS = "players"

SERVER_FOLDER = "server.folder"
SERVER_START_COMMAND = "server.start.command"
SERVER_STOP_COMMAND = "server.stop.command"
CLIENT_NAME = "client.name"
STREAM_CLIENT_PARAMETERS = "stream.client.parameters"
STREAM_SERVER_PARAMETERS = "stream.server.parameters"

HOST = "host"
PORT = "port"

MPD = "mpdsocket"
VLC = "vlcclient"
MPV = "mpvclient"

CURRENT_PLAYER_MODE = "current.player.mode"
MODES = [RADIO, RADIO_BROWSER, AUDIO_FILES, AUDIOBOOKS, STREAM, PODCASTS, AIRPLAY, SPOTIFY_CONNECT, \
         COLLECTION, BLUETOOTH_SINK, YA_STREAM, JUKEBOX, ARCHIVE, CATALOG]
ORDERS = [PLAYBACK_CYCLIC, PLAYBACK_REGULAR, PLAYBACK_SINGLE_TRACK, PLAYBACK_SHUFFLE, PLAYBACK_SINGLE_CYCLIC]

CENTER = "center"
SAMPLE_RATE = "sample.rate"
FILE_SIZE = "file.size"
CHANNELS = "channels"
BITS_PER_SAMPLE = "bits.per.sample"
BIT_RATE = "bit.rate"
BYTES = "bytes"
HZ = "hz"
KBPS = "kbps"
CODEC = "codec"
STATION = "station"
SONG = "song"
ARTIST = "artist"

VOICE_ASSISTANT_LANGUAGE_CODES = "voice-assistant-language-codes"

SELECT_COUNTRY = "select.country"
SELECT_LANGUAGE = "select.language"

class Config(object):
    """ Read configuration files and prepare dictionary """
    
    def __init__(self):
        """ Initializer """

        self.screen_rect = None
        self.config = {RELEASE: self.load_release()}
        self.load_config(self.config)
        self.load_languages(self.config)
        self.load_players(self.config)
        self.load_current(self.config)
        self.load_background_definitions(self.config)
        self.load_switch_config(self.config)
        self.load_nas_config(self.config)

        self.init_lcd()
        self.pygame_screen = self.get_pygame_screen()
        sys.setrecursionlimit(10**6) # required to truncate long button labels
        
    def load_languages(self, config):
        """ Load all languages configurations
        
        :param config: configuration object
        """
        config_file = ConfigParser()
        config_file.optionxform = str

        try:
            path = os.path.join(os.getcwd(), FOLDER_LANGUAGES, FILE_LANGUAGES)
            config_file.read(path, encoding=UTF8)
        except Exception as e:
            logging.error(e)
            os._exit(0)
            
        if config_file.sections():
            if len(config_file.sections()) > 15:
                self.exit("Only 12 languages are supported.")
        else:
            self.exit("No sections found in file: " + FILE_LANGUAGES)
        
        # languages menu
        items = config_file.items(LANGUAGES_MENU)
        languages = dict(items)
        lang_dict = {}
        for key in languages.keys():
            v = languages[key]
            if v == "True":
                lang_dict[key] = True
            else:
                lang_dict[key] = False

        config[LANGUAGES_MENU] = lang_dict

        # language codes
        for section in config_file.sections()[1:3]:
            section_map = {}
            for (k, v) in config_file.items(section):
                section_map[k] = v
            config[section] = section_map

        # languages
        s = config_file.sections()
        sections = []
        for section in s[3:]:
            if config[LANGUAGES_MENU][section]:
                sections.append(section)

        languages = []

        for section in sections:
            language = {NAME: section}

            translations = {}
            for (k, v) in config_file.items(section):
                translations[k] = v
            language[TRANSLATIONS] = translations
            languages.append(language)
        
            path = os.path.join(os.getcwd(), FOLDER_LANGUAGES, section)
            if os.path.isdir(path):
                files = [FILE_LABELS, FILE_VOICE_COMMANDS, FILE_FLAG]
                self.check_files(path, files)
                p = os.path.join(path, FOLDER_RADIO_STATIONS) 
                if not os.path.isdir(p):
                    language[RADIO_MODE_ENABLED] = False                    
                else:
                    station_folders = self.get_radio_stations_folders(p)
                    if station_folders:
                        language[KEY_STATIONS] = station_folders
                        language[RADIO_MODE_ENABLED] = True             
            else:
                self.exit("Folder was not found: " + path)
                
        config[KEY_LANGUAGES] = languages

    def load_background_definitions(self, config):
        """ Load background definitions
        
        :param config: configuration object
        """
        config_file = ConfigParser()
        config_file.optionxform = str

        try:
            path = os.path.join(os.getcwd(), FOLDER_BACKGROUNDS, FILE_BACKGROUND)
            config_file.read(path, encoding=UTF8)
        except Exception as e:
            logging.error(e)
            os._exit(0)
            
        sections = config_file.sections()
        if not sections:
            self.exit("No sections found in file: " + FILE_BACKGROUND)

        config[BACKGROUND] = self.get_background_config(config_file)

        backgrounds = {}

        for section in sections[1:]:
            try:
                bgr = {BGR_FILENAME: config_file.get(section, BGR_FILENAME)}
                bgr[WEB_BGR_BLUR_RADIUS] = config_file.getint(section, WEB_BGR_BLUR_RADIUS)
            except:
                bgr = {}
            bgr[BLUR_RADIUS] = config_file.getint(section, BLUR_RADIUS)
            bgr[OVERLAY_COLOR] = self.get_color_tuple(config_file.get(section, OVERLAY_COLOR))
            bgr[OVERLAY_OPACITY] = 255 - config_file.getint(section, OVERLAY_OPACITY)
            backgrounds[section] = bgr
                        
        config[BACKGROUND_DEFINITIONS] = backgrounds

    def get_background_config(self, config_file=None):
        """ Load background configuration file

        :param config_file: the background config file
        """
        if config_file == None:
            config_file = ConfigParser()
            path = os.path.join(os.getcwd(), FOLDER_BACKGROUNDS, FILE_BACKGROUND)
            config_file.read(path, encoding=UTF8)

        c = {BGR_TYPE : config_file.get(BACKGROUND, BGR_TYPE)}

        color = self.get_color_tuple(config_file.get(BACKGROUND, SCREEN_BGR_COLOR))
        c[WEB_BGR_COLOR] = color
        c[SCREEN_BGR_COLOR] = (color[0], color[1], color[2])

        c[SCREEN_BGR_NAMES] = self.get_list(config_file, BACKGROUND, SCREEN_BGR_NAMES)
        c[WEB_BGR_NAMES] = self.get_list(config_file, BACKGROUND, WEB_BGR_NAMES)
        c[HEADER_BGR_OPACITY] = config_file.getint(BACKGROUND, HEADER_BGR_OPACITY)
        c[MENU_BGR_OPACITY] = config_file.getint(BACKGROUND, MENU_BGR_OPACITY)
        c[FOOTER_BGR_OPACITY] = config_file.getint(BACKGROUND, FOOTER_BGR_OPACITY)
        color = self.config[COLORS][COLOR_DARK_LIGHT]
        c[HEADER_BGR_COLOR] = (color[0], color[1], color[2], c[HEADER_BGR_OPACITY])
        c[FOOTER_BGR_COLOR] = (color[0], color[1], color[2], c[FOOTER_BGR_OPACITY])
        color = self.config[COLORS][COLOR_DARK]
        c[WEB_SCREEN_BGR_OPACITY] = config_file.getint(BACKGROUND, WEB_SCREEN_BGR_OPACITY)
        c[MENU_BGR_COLOR] = (color[0], color[1], color[2], c[MENU_BGR_OPACITY])
        color = c[SCREEN_BGR_COLOR]
        c[WEB_SCREEN_COLOR] = (color[0], color[1], color[2], c[WEB_SCREEN_BGR_OPACITY])
        
        return c

    def load_switch_config(self, conf=None):
        """ Load disk power switch configuration file

        :param conf: the main config file
        """
        if not conf[USE_SWITCH]:
            return

        config_file = ConfigParser()
        config_file.optionxform = str

        try:
            path = os.path.join(os.getcwd(), KEY_SWITCH, DISK_SWITCH_FILE)
            config_file.read(path, encoding=UTF8)
        except Exception as e:
            logging.debug(e)
            return
            
        sections = config_file.sections()
        disks = []
        
        for section in sections:
            disk = {}
            num = int(section[section.rfind(".") + 1 :])
            disk[KEY_INDEX] = num
            disk[BIT_ADDRESS] = 128 >> (num - 1)
            for (k, v) in config_file.items(section):
                if k == KEY_POWER_ON:
                    v = v == "True"
                disk[k] = v
            disks.append(disk)

        conf[KEY_SWITCH] = disks

    def save_switch_config(self):
        """ Save power switch configuration (disks.txt) """

        if not self.config[USE_SWITCH]:
            return

        try:
            disks = self.config[KEY_SWITCH]
        except:
            return

        config_parser = ConfigParser()
        config_parser.optionxform = str
        path = os.path.join(os.getcwd(), KEY_SWITCH, DISK_SWITCH_FILE)
        config_parser.read(path, encoding=UTF8)

        for disk in disks:
            key = "disk." + str(disk[KEY_INDEX])
            config_parser.set(key, NAME, disk[NAME])
            config_parser.set(key, KEY_POWER_ON, str(disk[KEY_POWER_ON]))

        with codecs.open(path, 'w', UTF8) as file:
            config_parser.write(file)

    def load_nas_config(self, conf=None):
        """ Load NAS configuration file

        :param conf: the main config file
        """
        config_file = ConfigParser()
        config_file.optionxform = str

        try:
            path = os.path.join(os.getcwd(), KEY_NAS, NAS_FILE)
            config_file.read(path, encoding=UTF8)
        except Exception as e:
            logging.debug(e)
            return
            
        sections = config_file.sections()
        nases = []
        
        for section in sections:
            nas = {}
            for (k, v) in config_file.items(section):
                nas[k] = v
            nases.append(nas)

        conf[KEY_NAS] = nases

    def save_nas_config(self):
        """ Save NAS configuration (nas.txt) """

        try:
            nases = self.config[KEY_NAS]
        except:
            return

        config_parser = ConfigParser()
        config_parser.optionxform = str
        path = os.path.join(os.getcwd(), KEY_NAS, NAS_FILE)
        config_parser.read(path, encoding=UTF8)
        sections = config_parser.sections()
        for section in sections:
            config_parser.remove_section(section)

        for i, nas in enumerate(nases):
            section = KEY_NAS + "." + str(i + 1)
            config_parser.add_section(section)
            config_parser.set(section, KEY_NAME, nas[KEY_NAME])
            config_parser.set(section, KEY_IP_ADDRESS, nas[KEY_IP_ADDRESS])
            config_parser.set(section, KEY_FOLDER, nas[KEY_FOLDER])
            config_parser.set(section, KEY_FILESYSTEM, nas[KEY_FILESYSTEM])
            config_parser.set(section, KEY_USERNAME, nas[KEY_USERNAME])
            config_parser.set(section, KEY_PASSWORD, nas[KEY_PASSWORD])
            config_parser.set(section, KEY_MOUNT_OPTIONS, nas[KEY_MOUNT_OPTIONS])

        with codecs.open(path, 'w', UTF8) as file:
            config_parser.write(file)

    def save_background_config(self, parameters):
        """ Save backgrounds file (background.txt) 
        
        :param parameters: parameters to save
        """

        config_file = ConfigParser()
        path = os.path.join(os.getcwd(), FOLDER_BACKGROUNDS, FILE_BACKGROUND)
        config_file.read(path, encoding=UTF8)
        exclude_keys = [WEB_BGR_COLOR, HEADER_BGR_COLOR, FOOTER_BGR_COLOR, MENU_BGR_COLOR, WEB_SCREEN_COLOR]

        keys = list(parameters.keys())
        for key in keys:
            if key in exclude_keys:
                continue
            if isinstance(parameters[key], list):
                v = ",".join(map(str, parameters[key]))
            else:
                v = str(parameters[key])
            
            config_file.set(BACKGROUND, key, v)

        with codecs.open(path, 'w', UTF8) as file:
            config_file.write(file)

    def get_radio_stations_folders(self, path):
        """ Get all radio station folders in specified folder
        
        :param path: path to search for station folders
        
        :return: list of folders
        """
        parent_folder = next(os.walk(path))[1]
        if parent_folder:
            p = os.path.join(path, parent_folder[0])
            child_folders = next(os.walk(p))[1]
            return {parent_folder[0]: sorted(child_folders)}
        return None

    def check_files(self, path, files):
        """ Check that specified files exist. Exit if doesn't exist
        
        :param files: list of files
        """
        msg = "File doesn't exist: " 
        for f in files:              
            p = os.path.join(path, f)
            if not os.path.exists(p):
                self.exit(msg + p)
        
    def exit(self, msg):
        """ Exit with provided message
        
        :param msg: message to output before exit
        """
        logging.error(msg)
        os._exit(0)

    def load_release(self, local=True):
        """ Load and parse release file release.txt.
        Create dictionary entry for each property in the file.
        
        :param config: configuration object
        :param online: True - read local file, False - read from github
        :return: dictionary containing all properties from the release.txt file
        """
        parser = ConfigParser()

        if local:
            parser.read(FILE_RELEASE)
        else:
            link = "https://raw.githubusercontent.com/project-owner/Peppy/master/release.txt"
            req = request.Request(link)
            try:
                r = request.urlopen(req)
                parser.read_string(r.read().decode('utf-8'))
            except Exception as e:
                logging.debug(e)
                return None

        c = {PRODUCT_NAME: parser.get(RELEASE, PRODUCT_NAME)}
        c[EDITION_NAME] = parser.get(RELEASE, EDITION_NAME)
        c[RELEASE_YEAR] = parser.getint(RELEASE, RELEASE_YEAR)
        c[RELEASE_MONTH] = parser.getint(RELEASE, RELEASE_MONTH)
        c[RELEASE_DAY] = parser.getint(RELEASE, RELEASE_DAY)

        return c

    def load_config(self, config, include_classes=True):
        """ Load and parse configuration file config.txt.
        Create dictionary entry for each property in the file.
        
        :param config: configuration object
        :param include_classes: include classes as properties e.g. Backlight

        :return: dictionary containing all properties from the config.txt file
        """
        linux_platform = True
        if "win" in sys.platform:
            linux_platform = False
        config[LINUX_PLATFORM] = linux_platform
        
        config_file = ConfigParser()
        path = os.path.join(os.getcwd(), FOLDER_CONFIGURATION, FILE_CONFIG)
        config_file.read(path)
    
        c = {WIDTH : config_file.getint(SCREEN_INFO, WIDTH)}
        c[HEIGHT] = config_file.getint(SCREEN_INFO, HEIGHT)
        c[DEPTH] = config_file.getint(SCREEN_INFO, DEPTH)
        c[FRAME_RATE] = config_file.getint(SCREEN_INFO, FRAME_RATE)
        c[HDMI] = config_file.getboolean(SCREEN_INFO, HDMI)
        c[NO_FRAME] = config_file.getboolean(SCREEN_INFO, NO_FRAME)
        c[FLIP_TOUCH_XY] = config_file.getboolean(SCREEN_INFO, FLIP_TOUCH_XY)
        c[MULTI_TOUCH] = config_file.getboolean(SCREEN_INFO, MULTI_TOUCH)
        config[SCREEN_INFO] = c
        self.screen_rect = pygame.Rect(0, 0, c[WIDTH], c[HEIGHT])

        config[AUDIO_FILE_EXTENSIONS] = self.get_list(config_file, FILE_BROWSER, AUDIO_FILE_EXTENSIONS)
        config[PLAYLIST_FILE_EXTENSIONS] = self.get_list(config_file, FILE_BROWSER, PLAYLIST_FILE_EXTENSIONS)
        config[IMAGE_FILE_EXTENSIONS] = self.get_list(config_file, FILE_BROWSER, IMAGE_FILE_EXTENSIONS)
        config[ENABLE_IMAGE_FILE_ICON] = config_file.getboolean(FILE_BROWSER, ENABLE_IMAGE_FILE_ICON)

        config[ENABLE_BUTTON_HOME] = config_file.getboolean(FILE_BROWSER, ENABLE_BUTTON_HOME)
        config[ENABLE_BUTTON_CONFIG] = config_file.getboolean(FILE_BROWSER, ENABLE_BUTTON_CONFIG)
        config[ENABLE_BUTTON_PLAYLIST] = config_file.getboolean(FILE_BROWSER, ENABLE_BUTTON_PLAYLIST)
        config[ENABLE_BUTTON_USER] = config_file.getboolean(FILE_BROWSER, ENABLE_BUTTON_USER)
        config[ENABLE_BUTTON_ROOT] = config_file.getboolean(FILE_BROWSER, ENABLE_BUTTON_ROOT)
        config[ENABLE_BUTTON_PARENT] = config_file.getboolean(FILE_BROWSER, ENABLE_BUTTON_PARENT)

        config[FOLDER_IMAGES] = self.get_list(config_file, FILE_BROWSER, FOLDER_IMAGES)
        config[COVER_ART_FOLDERS] = self.get_list(config_file, FILE_BROWSER, COVER_ART_FOLDERS)
        config[SHOW_EMBEDDED_IMAGES] = self.get_list(config_file, FILE_BROWSER, SHOW_EMBEDDED_IMAGES)
        config[ENABLE_FOLDER_IMAGES] = config_file.getboolean(FILE_BROWSER, ENABLE_FOLDER_IMAGES)
        config[ENABLE_EMBEDDED_IMAGES] = config_file.getboolean(FILE_BROWSER, ENABLE_EMBEDDED_IMAGES)
        config[HIDE_FOLDER_NAME] = config_file.getboolean(FILE_BROWSER, HIDE_FOLDER_NAME)
        config[IMAGE_AREA] = config_file.getint(FILE_BROWSER, IMAGE_AREA)
        config[IMAGE_SIZE] = config_file.getint(FILE_BROWSER, IMAGE_SIZE)
        config[ICON_SIZE] = config_file.getint(FILE_BROWSER, ICON_SIZE)
        config[IMAGE_SIZE_WITHOUT_LABEL] = config_file.getint(FILE_BROWSER, IMAGE_SIZE_WITHOUT_LABEL)
        config[PADDING] = config_file.getint(FILE_BROWSER, PADDING)
        config[LIST_VIEW_ROWS] = config_file.getint(FILE_BROWSER, LIST_VIEW_ROWS)
        config[LIST_VIEW_COLUMNS] = config_file.getint(FILE_BROWSER, LIST_VIEW_COLUMNS)
        config[ICON_VIEW_ROWS] = config_file.getint(FILE_BROWSER, ICON_VIEW_ROWS)
        config[ICON_VIEW_COLUMNS] = config_file.getint(FILE_BROWSER, ICON_VIEW_COLUMNS)
        config[ALIGN_BUTTON_CONTENT_X] = config_file.get(FILE_BROWSER, ALIGN_BUTTON_CONTENT_X)
        config[SORT_BY_TYPE] = config_file.getboolean(FILE_BROWSER, SORT_BY_TYPE)
        config[FILE_TYPES] = self.get_list(config_file, FILE_BROWSER, FILE_TYPES)
        config[ASCENDING] = config_file.getboolean(FILE_BROWSER, ASCENDING)
        config[WRAP_LABELS] = config_file.getboolean(FILE_BROWSER, WRAP_LABELS)
        config[HORIZONTAL_LAYOUT] = config_file.getboolean(FILE_BROWSER, HORIZONTAL_LAYOUT)
        config[FONT_HEIGHT_PERCENT] = config_file.getint(FILE_BROWSER, FONT_HEIGHT_PERCENT)
        config[USE_SWITCH] = config_file.getboolean(FILE_BROWSER, USE_SWITCH)

        c = {USE_LIRC : config_file.getboolean(USAGE, USE_LIRC)}
        c[USE_TOUCHSCREEN] = config_file.getboolean(USAGE, USE_TOUCHSCREEN)
        c[USE_MOUSE] = config_file.getboolean(USAGE, USE_MOUSE)
        c[USE_WEB] = config_file.getboolean(USAGE, USE_WEB)
        c[USE_STREAM_SERVER] = config_file.getboolean(USAGE, USE_STREAM_SERVER)
        c[USE_BROWSER_STREAM_PLAYER] = config_file.getboolean(USAGE, USE_BROWSER_STREAM_PLAYER)
        c[USE_VOICE_ASSISTANT] = config_file.getboolean(USAGE, USE_VOICE_ASSISTANT)
        c[USE_HEADLESS] = config_file.getboolean(USAGE, USE_HEADLESS)
        c[USE_VU_METER] = config_file.getboolean(USAGE, USE_VU_METER)
        c[USE_ALBUM_ART] = config_file.getboolean(USAGE, USE_ALBUM_ART)
        c[USE_AUTO_PLAY] = config_file.getboolean(USAGE, USE_AUTO_PLAY)
        c[USE_LONG_PRESS_TIME] = config_file.getint(USAGE, USE_LONG_PRESS_TIME)
        c[USE_DESKTOP] = config_file.getboolean(USAGE, USE_DESKTOP)
        c[USE_CHECK_FOR_UPDATES] = config_file.getboolean(USAGE, USE_CHECK_FOR_UPDATES)
        c[USE_BLUETOOTH] = config_file.getboolean(USAGE, USE_BLUETOOTH)
        c[USE_SAMBA] = config_file.getboolean(USAGE, USE_SAMBA)
        c[USE_DNS_IP] = config_file.get(USAGE, USE_DNS_IP)
        c[USE_CLOCK_SCREENSAVER_IN_TIMER] = config_file.getboolean(USAGE, USE_CLOCK_SCREENSAVER_IN_TIMER)
        config[USAGE] = c
        
        if not config_file.getboolean(LOGGING, ENABLE_STDOUT):
            sys.stdout = os.devnull
            sys.stderr = os.devnull
        
        c[FILE_LOGGING] = config_file.getboolean(LOGGING, FILE_LOGGING)
        c[LOG_FILENAME] = config_file.get(LOGGING, LOG_FILENAME)
        c[APPEND] = config_file.getboolean(LOGGING, APPEND)
        c[CONSOLE_LOGGING] = config_file.getboolean(LOGGING, CONSOLE_LOGGING)
        c[ENABLE_STDOUT] = config_file.getboolean(LOGGING, ENABLE_STDOUT)
        config[FILE_LOGGING] = c[FILE_LOGGING]
        config[LOG_FILENAME] = c[LOG_FILENAME]
        config[APPEND] = c[APPEND]
        config[SHOW_MOUSE_EVENTS] = config_file.getboolean(LOGGING, SHOW_MOUSE_EVENTS)
        config[CONSOLE_LOGGING] = c[CONSOLE_LOGGING]
        
        log_handlers = []
        if c[FILE_LOGGING]:
            if c[APPEND]:
                file_mode = "a"
            else:
                file_mode = "w"

            try:
                fh = logging.FileHandler(filename=c[LOG_FILENAME], mode=file_mode)
                log_handlers.append(fh)
            except:
                pass
        if c[CONSOLE_LOGGING]:
            log_handlers.append(logging.StreamHandler(sys.stdout))            
        if len(log_handlers) > 0:
            logging.basicConfig(
                level=logging.NOTSET, 
                format='[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s',
                handlers=log_handlers
            )
        else:
            logging.disable(logging.CRITICAL)
        
        c = {
            HTTP_PORT : config_file.get(WEB_SERVER, HTTP_PORT),
            HTTPS: config_file.getboolean(WEB_SERVER, HTTPS)
        }
        config[WEB_SERVER] = c
        
        c = {STREAM_SERVER_PORT : config_file.get(STREAM_SERVER, STREAM_SERVER_PORT)}
        config[STREAM_SERVER] = c
        
        config[MUSIC_FOLDER] = self.get_folder(config_file, MUSIC_FOLDER, WINDOWS_MUSIC_FOLDER, linux_platform)
        config[FILE_PLAYLISTS_FOLDER] = self.get_folder(config_file, FILE_PLAYLISTS_FOLDER, WINDOWS_PLAYLISTS_FOLDER, linux_platform)
        config[PODCASTS_FOLDER] = self.get_folder(config_file, PODCASTS_FOLDER, WINDOWS_PODCASTS_FOLDER, linux_platform)

        show_numbers = False
        try:
            show_numbers = config_file.getboolean(COLLECTION, SHOW_NUMBERS)
        except:
            pass

        c = {
            DATABASE_FILE: config_file.get(COLLECTION, DATABASE_FILE),
            BASE_FOLDER: config_file.get(COLLECTION, BASE_FOLDER),
            SHOW_NUMBERS: show_numbers
        }
        config[COLLECTION] = c        

        c = {RADIO: config_file.getboolean(HOME_MENU, RADIO)}
        c[RADIO_BROWSER] = config_file.getboolean(HOME_MENU, RADIO_BROWSER)
        c[AUDIO_FILES] = config_file.getboolean(HOME_MENU, AUDIO_FILES)
        c[AUDIOBOOKS] = config_file.getboolean(HOME_MENU, AUDIOBOOKS)
        c[STREAM] = config_file.getboolean(HOME_MENU, STREAM)
        c[PODCASTS] = config_file.getboolean(HOME_MENU, PODCASTS)
        c[AIRPLAY] = config_file.getboolean(HOME_MENU, AIRPLAY)
        c[SPOTIFY_CONNECT] = config_file.getboolean(HOME_MENU, SPOTIFY_CONNECT)
        c[COLLECTION] = config_file.getboolean(HOME_MENU, COLLECTION)
        c[BLUETOOTH_SINK] = config_file.getboolean(HOME_MENU, BLUETOOTH_SINK)
        c[YA_STREAM] = config_file.getboolean(HOME_MENU, YA_STREAM)
        c[JUKEBOX] = config_file.getboolean(HOME_MENU, JUKEBOX)
        c[ARCHIVE] = config_file.getboolean(HOME_MENU, ARCHIVE)
        c[CATALOG] = config_file.getboolean(HOME_MENU, CATALOG)
        config[HOME_MENU] = c

        c = {EQUALIZER: config_file.getboolean(HOME_NAVIGATOR, EQUALIZER)}
        c[TIMER] = config_file.getboolean(HOME_NAVIGATOR, TIMER)
        c[NETWORK] = config_file.getboolean(HOME_NAVIGATOR, NETWORK)
        c[HOME_BACK] = config_file.getboolean(HOME_NAVIGATOR, HOME_BACK)
        c[HOME_SCREENSAVER] = config_file.getboolean(HOME_NAVIGATOR, HOME_SCREENSAVER)
        c[HOME_LANGUAGE] = config_file.getboolean(HOME_NAVIGATOR, HOME_LANGUAGE)
        c[PLAYER] = config_file.getboolean(HOME_NAVIGATOR, PLAYER)
        c[ABOUT] = config_file.getboolean(HOME_NAVIGATOR, ABOUT)
        config[HOME_NAVIGATOR] = c
        
        c = {GENRE: config_file.getboolean(COLLECTION_MENU, GENRE)}
        c[ARTIST] = config_file.getboolean(COLLECTION_MENU, ARTIST)
        c[ALBUM] = config_file.getboolean(COLLECTION_MENU, ALBUM)
        c[TITLE] = config_file.getboolean(COLLECTION_MENU, TITLE)
        c[DATE] = config_file.getboolean(COLLECTION_MENU, DATE)
        c[TYPE] = config_file.getboolean(COLLECTION_MENU, TYPE)
        c[COMPOSER] = config_file.getboolean(COLLECTION_MENU, COMPOSER)
        c[FOLDER] = config_file.getboolean(COLLECTION_MENU, FOLDER)
        c[FILENAME] = config_file.getboolean(COLLECTION_MENU, FILENAME)
        config[COLLECTION_MENU] = c

        c = {MOUNT_AT_STARTUP: config_file.getboolean(DISK_MOUNT, MOUNT_AT_STARTUP)}
        c[MOUNT_AT_PLUG] = config_file.getboolean(DISK_MOUNT, MOUNT_AT_PLUG)
        c[MOUNT_READ_ONLY] = config_file.getboolean(DISK_MOUNT, MOUNT_READ_ONLY)
        c[MOUNT_POINT] = config_file.get(DISK_MOUNT, MOUNT_POINT)
        c[MOUNT_OPTIONS] = config_file.get(DISK_MOUNT, MOUNT_OPTIONS)
        config[DISK_MOUNT] = c

        c = {COLOR_WEB_BGR : self.get_color_tuple(config_file.get(COLORS, COLOR_WEB_BGR))}
        c[COLOR_DARK] = self.get_color_tuple(config_file.get(COLORS, COLOR_DARK))
        c[COLOR_MEDIUM] = self.get_color_tuple(config_file.get(COLORS, COLOR_MEDIUM))
        c[COLOR_DARK_LIGHT] = self.get_color_tuple(config_file.get(COLORS, COLOR_DARK_LIGHT))
        c[COLOR_BRIGHT] = self.get_color_tuple(config_file.get(COLORS, COLOR_BRIGHT))
        c[COLOR_CONTRAST] = self.get_color_tuple(config_file.get(COLORS, COLOR_CONTRAST))
        c[COLOR_LOGO] = self.get_color_tuple(config_file.get(COLORS, COLOR_LOGO))
        c[COLOR_MUTE] = self.get_color_tuple(config_file.get(COLORS, COLOR_MUTE))
        config[COLORS] = c

        c = {ICONS_TYPE : config_file.get(ICONS, ICONS_TYPE)}
        c[ICONS_CATEGORY] = config_file.get(ICONS, ICONS_CATEGORY)
        c[ICONS_COLOR_1_MAIN] = self.get_color_tuple(config_file.get(ICONS, ICONS_COLOR_1_MAIN))
        c[ICONS_COLOR_1_ON] = self.get_color_tuple(config_file.get(ICONS, ICONS_COLOR_1_ON))
        t = config_file.get(ICONS, ICONS_COLOR_2_MAIN)
        if t:
            c[ICONS_COLOR_2_MAIN] = self.get_color_tuple(t)
        t = config_file.get(ICONS, ICONS_COLOR_2_ON)
        if t:
            c[ICONS_COLOR_2_ON] = self.get_color_tuple(t)
        config[ICONS] = c
            
        config[FONT_KEY] = config_file.get(FONT_SECTION, FONT_KEY)

        c = {TOP_HEIGHT_PERCENT: float(config_file.get(PLAYER_SCREEN, TOP_HEIGHT_PERCENT))}
        if c[TOP_HEIGHT_PERCENT] > 30.0:
            c[TOP_HEIGHT_PERCENT] = 30.0
        c[BOTTOM_HEIGHT_PERCENT] = float(config_file.get(PLAYER_SCREEN, BOTTOM_HEIGHT_PERCENT))
        if c[BOTTOM_HEIGHT_PERCENT] > 30.0:
            c[BOTTOM_HEIGHT_PERCENT] = 30.0
        c[BUTTON_HEIGHT_PERCENT] = float(config_file.get(PLAYER_SCREEN, BUTTON_HEIGHT_PERCENT))
        if c[BUTTON_HEIGHT_PERCENT] > 45.0:
            c[BUTTON_HEIGHT_PERCENT] = 45.0
        c[POPUP_WIDTH_PERCENT] = float(config_file.get(PLAYER_SCREEN, POPUP_WIDTH_PERCENT))
        if c[POPUP_WIDTH_PERCENT] > 25.0:
            c[POPUP_WIDTH_PERCENT] = 25.0
        c[IMAGE_LOCATION] = config_file.get(PLAYER_SCREEN, IMAGE_LOCATION)
        c[ENABLE_ORDER_BUTTON] = config_file.getboolean(PLAYER_SCREEN, ENABLE_ORDER_BUTTON)
        c[ENABLE_INFO_BUTTON] = config_file.getboolean(PLAYER_SCREEN, ENABLE_INFO_BUTTON)
        c[SHOW_TIME_SLIDER] = config_file.getboolean(PLAYER_SCREEN, SHOW_TIME_SLIDER)
        config[PLAYER_SCREEN] = c

        c = {}
        c[SCRIPT_PLAYER_START] = config_file.get(SCRIPTS, SCRIPT_PLAYER_START)
        c[SCRIPT_PLAYER_STOP] = config_file.get(SCRIPTS, SCRIPT_PLAYER_STOP)
        c[SCRIPT_SCREENSAVER_START] = config_file.get(SCRIPTS, SCRIPT_SCREENSAVER_START)
        c[SCRIPT_SCREENSAVER_STOP] = config_file.get(SCRIPTS, SCRIPT_SCREENSAVER_STOP)
        c[SCRIPT_TIMER_START] = config_file.get(SCRIPTS, SCRIPT_TIMER_START)
        c[SCRIPT_TIMER_STOP] = config_file.get(SCRIPTS, SCRIPT_TIMER_STOP)
        config[SCRIPTS] = c

        c = {}
        c[USE_PLAYER_BUTTONS] = config_file.getboolean(GPIO, USE_PLAYER_BUTTONS)
        c[BUTTON_TYPE] = config_file.get(GPIO, BUTTON_TYPE)
        c[USE_MENU_BUTTONS] = config_file.getboolean(GPIO, USE_MENU_BUTTONS)
        c[USE_ROTARY_ENCODERS] = config_file.getboolean(GPIO, USE_ROTARY_ENCODERS)
        c[BUTTON_LEFT] = config_file.get(GPIO, BUTTON_LEFT)
        c[BUTTON_RIGHT] = config_file.get(GPIO, BUTTON_RIGHT)
        c[BUTTON_UP] = config_file.get(GPIO, BUTTON_UP)
        c[BUTTON_DOWN] = config_file.get(GPIO, BUTTON_DOWN)
        c[BUTTON_SELECT] = config_file.get(GPIO, BUTTON_SELECT)
        c[BUTTON_VOLUME_UP] = config_file.get(GPIO, BUTTON_VOLUME_UP)
        c[BUTTON_VOLUME_DOWN] = config_file.get(GPIO, BUTTON_VOLUME_DOWN)
        c[BUTTON_MUTE] = config_file.get(GPIO, BUTTON_MUTE)
        c[BUTTON_PLAY_PAUSE] = config_file.get(GPIO, BUTTON_PLAY_PAUSE)
        c[BUTTON_NEXT] = config_file.get(GPIO, BUTTON_NEXT)
        c[BUTTON_PREVIOUS] = config_file.get(GPIO, BUTTON_PREVIOUS)
        c[BUTTON_HOME] = config_file.get(GPIO, BUTTON_HOME)
        c[BUTTON_POWEROFF] = config_file.get(GPIO, BUTTON_POWEROFF)
        c[ROTARY_VOLUME_UP] = config_file.get(GPIO, ROTARY_VOLUME_UP)
        c[ROTARY_VOLUME_DOWN] = config_file.get(GPIO, ROTARY_VOLUME_DOWN)
        c[ROTARY_VOLUME_MUTE] = config_file.get(GPIO, ROTARY_VOLUME_MUTE)
        c[ROTARY_NAVIGATION_LEFT] = config_file.get(GPIO, ROTARY_NAVIGATION_LEFT)
        c[ROTARY_NAVIGATION_RIGHT] = config_file.get(GPIO, ROTARY_NAVIGATION_RIGHT)
        c[ROTARY_NAVIGATION_SELECT] = config_file.get(GPIO, ROTARY_NAVIGATION_SELECT)
        c[ROTARY_JITTER_FILTER] = config_file.get(GPIO, ROTARY_JITTER_FILTER)
        c[BUTTON_MENU_1] = config_file.get(GPIO, BUTTON_MENU_1)
        c[BUTTON_MENU_2] = config_file.get(GPIO, BUTTON_MENU_2)
        c[BUTTON_MENU_3] = config_file.get(GPIO, BUTTON_MENU_3)
        c[BUTTON_MENU_4] = config_file.get(GPIO, BUTTON_MENU_4)
        c[BUTTON_MENU_5] = config_file.get(GPIO, BUTTON_MENU_5)
        c[BUTTON_MENU_6] = config_file.get(GPIO, BUTTON_MENU_6)
        c[BUTTON_MENU_7] = config_file.get(GPIO, BUTTON_MENU_7)
        c[BUTTON_MENU_8] = config_file.get(GPIO, BUTTON_MENU_8)
        c[BUTTON_MENU_9] = config_file.get(GPIO, BUTTON_MENU_9)
        c[BUTTON_MENU_10] = config_file.get(GPIO, BUTTON_MENU_10)
        config[GPIO] = c

        c = {}
        try:
            c[I2C_INPUT_ADDRESS] = int(config_file.get(I2C, I2C_INPUT_ADDRESS), 0)
        except:
            c[I2C_INPUT_ADDRESS] = None
        try:
            c[I2C_OUTPUT_ADDRESS] = int(config_file.get(I2C, I2C_OUTPUT_ADDRESS), 0)
        except:
            c[I2C_OUTPUT_ADDRESS] = None
        try:
            c[I2C_GPIO_INTERRUPT] = int(config_file.get(I2C, I2C_GPIO_INTERRUPT))
        except:
            c[I2C_GPIO_INTERRUPT] = None
        config[I2C] = c

        c = {}
        c[USE_DSI_DISPLAY] = config_file.getboolean(DSI_DISPLAY_BACKLIGHT, USE_DSI_DISPLAY)
        c[SCREEN_BRIGHTNESS] = config_file.get(DSI_DISPLAY_BACKLIGHT, SCREEN_BRIGHTNESS)
        c[SCREENSAVER_BRIGHTNESS] = config_file.get(DSI_DISPLAY_BACKLIGHT, SCREENSAVER_BRIGHTNESS)
        c[SCREENSAVER_DISPLAY_POWER_OFF] = config_file.getboolean(DSI_DISPLAY_BACKLIGHT, SCREENSAVER_DISPLAY_POWER_OFF)
        c[SLEEP_NOW_DISPLAY_POWER_OFF] = config_file.getboolean(DSI_DISPLAY_BACKLIGHT, SLEEP_NOW_DISPLAY_POWER_OFF)
        config[DSI_DISPLAY_BACKLIGHT] = c
        if self.config[DSI_DISPLAY_BACKLIGHT][USE_DSI_DISPLAY] and include_classes:
            config[BACKLIGHTER] = None
            try:
                from rpi_backlight import Backlight
                config[BACKLIGHTER] = Backlight()
            except:
                pass

        c = {}
        c[VOLUME_CONTROL_TYPE] = config_file.get(VOLUME_CONTROL, VOLUME_CONTROL_TYPE)
        if not config[LINUX_PLATFORM] or config[USAGE][USE_BLUETOOTH]:
            c[VOLUME_CONTROL_TYPE] = VOLUME_CONTROL_TYPE_PLAYER

        c[AMIXER_CONTROL] = config_file.get(VOLUME_CONTROL, AMIXER_CONTROL)
        c[AMIXER_SCALE] = config_file.get(VOLUME_CONTROL, AMIXER_SCALE)
        try:
            c[INITIAL_VOLUME_LEVEL] = config_file.getint(VOLUME_CONTROL, INITIAL_VOLUME_LEVEL)
        except:
            pass
        try:
            c[MAXIMUM_LEVEL] = config_file.getint(VOLUME_CONTROL, MAXIMUM_LEVEL)
        except:
            c[MAXIMUM_LEVEL] = 100
        config[VOLUME_CONTROL] = c
            
        c = {CLOCK: config_file.getboolean(SCREENSAVER_MENU, CLOCK)}
        c[LOGO] = config_file.getboolean(SCREENSAVER_MENU, LOGO)
        c[SLIDESHOW] = config_file.getboolean(SCREENSAVER_MENU, SLIDESHOW)
        c[VUMETER] = config_file.getboolean(SCREENSAVER_MENU, VUMETER)
        c[WEATHER] = config_file.getboolean(SCREENSAVER_MENU, WEATHER)
        c[SPECTRUM] = config_file.getboolean(SCREENSAVER_MENU, SPECTRUM)
        c[LYRICS] = config_file.getboolean(SCREENSAVER_MENU, LYRICS)
        c[PEXELS] = config_file.getboolean(SCREENSAVER_MENU, PEXELS)
        c[MONITOR] = config_file.getboolean(SCREENSAVER_MENU, MONITOR)
        c[HOROSCOPE] = config_file.getboolean(SCREENSAVER_MENU, HOROSCOPE)
        c[STOCK] = config_file.getboolean(SCREENSAVER_MENU, STOCK)
        c[RANDOM] = config_file.getboolean(SCREENSAVER_MENU, RANDOM)          
        config[SCREENSAVER_MENU] = c

        c = {DELAY: config_file.get(SCREENSAVER_DELAY, DELAY)}
        config[SCREENSAVER_DELAY] = c

    def get_folder(self, config_file, property_name, default_folder, linux_platform):
        """ Get folder name

        :param config_file: configuration file
        :param property_name: parameter name
        :param default_folder: default folder name
        :param linux_platform: True - Linux, False - Windows

        :return: folder name
        """
        folder = config_file.get(FOLDERS, property_name)

        if not folder:
            return expanduser("~")

        if os.path.exists(folder):
            return folder

        if linux_platform:
            return expanduser("~")
        else:
            return default_folder

    def load_players(self, config):
        """ Loads and parses configuration file players.txt.
        Creates dictionary entry for each property in the file.
        
        :param config: configuration object
        :return: dictionary containing all properties from the players.txt file
        """
        config_file = ConfigParser()
        path = os.path.join(os.getcwd(), FOLDER_CONFIGURATION, FILE_PLAYERS)
        config_file.read(path)

        if config[LINUX_PLATFORM]:
            platform = LINUX_PLATFORM
        else:
            platform = WINDOWS_PLATFORM

        c = {PLAYER_NAME : config_file.get(AUDIO, PLAYER_NAME)}
        player_name = c[PLAYER_NAME]
        current_player = self.get_player_config(player_name, platform, config_file)
        c.update(current_player)
        config[AUDIO] = c

        config[PLAYERS] = self.get_players(config_file)

    def get_player_config(self, player_name, platform, config_file):
        section_name = player_name + "." + platform
        c = {}

        try:
            c[SERVER_FOLDER] = config_file.get(section_name, SERVER_FOLDER)
        except:
            pass

        c[SERVER_START_COMMAND] = config_file.get(section_name, SERVER_START_COMMAND)

        try:
            c[SERVER_STOP_COMMAND] = config_file.get(section_name, SERVER_STOP_COMMAND)
        except:
            c[SERVER_STOP_COMMAND] = None

        try:
            c[CLIENT_NAME] = config_file.get(section_name, CLIENT_NAME)
        except:
            c[CLIENT_NAME] = None
        
        try:
            c[STREAM_CLIENT_PARAMETERS] = config_file.get(section_name, STREAM_CLIENT_PARAMETERS)
        except:
            pass

        try:
            c[STREAM_SERVER_PARAMETERS] = config_file.get(section_name, STREAM_SERVER_PARAMETERS)
        except:
            pass

        return c

    def get_players(self, config_file_parser=None):
        """ Get players settings

        :param config_file_parser: config file parser

        :return: dictionary with players settings
        """
        if config_file_parser:
            config_file = config_file_parser
        else:
            config_file = ConfigParser()
            path = os.path.join(os.getcwd(), FOLDER_CONFIGURATION, FILE_PLAYERS)
            config_file.read(path)

        players = {AUDIO: {PLAYER_NAME: config_file.get(AUDIO, PLAYER_NAME)}}
        players[AUDIO][PLAYER_NAME] = config_file.get(AUDIO, PLAYER_NAME)
        players[VLC_NAME + "." + LINUX_PLATFORM] = self.get_player_config(VLC_NAME, LINUX_PLATFORM, config_file)
        players[VLC_NAME + "." + WINDOWS_PLATFORM] = self.get_player_config(VLC_NAME, WINDOWS_PLATFORM, config_file)
        players[MPD_NAME + "." + LINUX_PLATFORM] = self.get_player_config(MPD_NAME, LINUX_PLATFORM, config_file)
        players[MPD_NAME + "." + WINDOWS_PLATFORM] = self.get_player_config(MPD_NAME, WINDOWS_PLATFORM, config_file)
        players[MPV_NAME + "." + LINUX_PLATFORM] = self.get_player_config(MPV_NAME, LINUX_PLATFORM, config_file)
        players[MPV_NAME + "." + WINDOWS_PLATFORM] = self.get_player_config(MPV_NAME, WINDOWS_PLATFORM, config_file)
        players[SHAIRPORT_SYNC_NAME + "." + LINUX_PLATFORM] = self.get_player_config(SHAIRPORT_SYNC_NAME, LINUX_PLATFORM, config_file)
        players[RASPOTIFY_NAME + "." + LINUX_PLATFORM] = self.get_player_config(RASPOTIFY_NAME, LINUX_PLATFORM, config_file)
        players[BLUETOOTH_SINK_NAME + "." + LINUX_PLATFORM] = self.get_player_config(BLUETOOTH_SINK_NAME, LINUX_PLATFORM, config_file)
        players[BLUETOOTH_SINK_NAME + "." + WINDOWS_PLATFORM] = self.get_player_config(BLUETOOTH_SINK_NAME, WINDOWS_PLATFORM, config_file)

        return players

    def save_players(self, parameters):
        """ Save players file (players.txt) """

        config_parser = ConfigParser()
        config_parser.optionxform = str
        path = os.path.join(os.getcwd(), FOLDER_CONFIGURATION, FILE_PLAYERS)
        config_parser.read(path, encoding=UTF8)

        keys = list(parameters.keys())
        for key in keys:
            if key == "current.player.type":
                continue
            params = parameters[key]
            for t in params.items():
                config_parser.set(key, t[0], str(t[1]))

        with codecs.open(path, 'w', UTF8) as file:
            config_parser.write(file)

    def is_current_file_corrupted(self):
        """ Check if current.txt corrupted by comparing it with the default file

        :return: True - corrupted, False - not corrupted
        """
        config_file = ConfigParser()
        config_file.optionxform = str
        path = os.path.join(os.getcwd(), FOLDER_CONFIGURATION, FILE_CURRENT)
        config_file.read(path, encoding=UTF8)

        default_config_file = ConfigParser()
        default_config_file.optionxform = str
        path_to_default_file = os.path.join(os.getcwd(), FOLDER_CONFIGURATION, DEFAULTS, FILE_CURRENT)
        default_config_file.read(path_to_default_file, encoding=UTF8)

        sections = config_file.sections()

        if not sections:
            return True

        default_sections = default_config_file.sections()

        for s in default_sections:
            section = config_file[s]
            default_section = default_config_file[s]
            keys = section.keys()
            default_keys = default_section.keys()
            if len(keys) != len(default_keys):
                return True

        return False

    def set_default_file(self, filename):
        """ Replace the file by the default one

        :param filename:
        """
        path_to_file = os.path.join(os.getcwd(), FOLDER_CONFIGURATION, filename)
        path_to_default_file = os.path.join(os.getcwd(), FOLDER_CONFIGURATION, DEFAULTS, filename)
        try:
            shutil.copyfile(path_to_default_file, path_to_file)
        except Exception as e:
            logging.error(e)

    def load_current(self, config):
        """ Loads and parses configuration file current.txt.
        Creates dictionary entry for each property in the file.
        
        :param config: configuration object
        :return: dictionary containing all properties from the current.txt file
        """
        if self.is_current_file_corrupted():
            self.set_default_file(FILE_CURRENT)

        config_file = ConfigParser()
        config_file.optionxform = str
        path = os.path.join(os.getcwd(), FOLDER_CONFIGURATION, FILE_CURRENT)
        config_file.read(path, encoding=UTF8)
        
        m = config_file.get(CURRENT, MODE)
        c = {MODE : m}
        
        initial_language = None
        lang = config_file.get(CURRENT, LANGUAGE)
        
        if not lang:
            initial_language = config[KEY_LANGUAGES][0]
            lang = initial_language[NAME]
        else:
            languages = config[KEY_LANGUAGES]
            language_name_found = False
            for language in languages:
                if language[NAME] == lang:
                    initial_language = language
                    language_name_found = True
                    break
            if not language_name_found:
                logging.error("Language is not supported: " + lang)
                lang = languages[0]["name"]
                logging.debug("Set " + lang + " as the current language")
                            
        c[LANGUAGE] = lang        
        c[STREAM] = 0
        
        try:
            c[STREAM] = config_file.getint(CURRENT, STREAM)
        except:
            pass
        
        try:
            c[EQUALIZER] = self.get_equalizer(config_file.get(CURRENT, EQUALIZER))
        except:
            pass
        
        config[CURRENT] = c
        
        s = config_file.get(SCREENSAVER, NAME)
        if not s: s = "slideshow"
        c = {NAME: s}
        config[SCREENSAVER] = c

        volume_level = None

        try:
            volume_level = config[VOLUME_CONTROL][INITIAL_VOLUME_LEVEL]
        except:
            pass
        
        if not volume_level:
            try:
                volume_level = config_file.getint(PLAYER_SETTINGS, VOLUME)
            except:
                pass

        if not volume_level:
            volume_level = DEFAULT_VOLUME_LEVEL

        if volume_level > config[VOLUME_CONTROL][MAXIMUM_LEVEL]:
            volume_level = config[VOLUME_CONTROL][MAXIMUM_LEVEL]

        c = {VOLUME: volume_level}
        
        c[MUTE] = False
        c[PAUSE] = False

        s = config_file.get(PLAYER_SETTINGS, PLAYBACK_ORDER)
        if not s:
            s = PLAYBACK_CYCLIC

        c[PLAYBACK_ORDER] = s

        config[PLAYER_SETTINGS] = c
        
        c = {CURRENT_FOLDER: config_file.get(FILE_PLAYBACK, CURRENT_FOLDER)}
        c[CURRENT_FILE_PLAYLIST] = config_file.get(FILE_PLAYBACK, CURRENT_FILE_PLAYLIST)
        c[CURRENT_FILE] = config_file.get(FILE_PLAYBACK, CURRENT_FILE)
        c[CURRENT_TRACK_TIME] = config_file.get(FILE_PLAYBACK, CURRENT_TRACK_TIME)
        c[CURRENT_FILE_PLAYBACK_MODE] = config_file.get(FILE_PLAYBACK, CURRENT_FILE_PLAYBACK_MODE)
        if config_file.get(FILE_PLAYBACK, CURRENT_FILE_PLAYLIST_INDEX):
            c[CURRENT_FILE_PLAYLIST_INDEX] = int(config_file.get(FILE_PLAYBACK, CURRENT_FILE_PLAYLIST_INDEX))
        else:
            c[CURRENT_FILE_PLAYLIST_INDEX] = ""
        config[FILE_PLAYBACK] = c

        c = {COLLECTION_TOPIC: config_file.get(COLLECTION_PLAYBACK, COLLECTION_TOPIC)}
        c[COLLECTION_FOLDER] = config_file.get(COLLECTION_PLAYBACK, COLLECTION_FOLDER)
        c[COLLECTION_FILE] = config_file.get(COLLECTION_PLAYBACK, COLLECTION_FILE)
        c[COLLECTION_URL] = config_file.get(COLLECTION_PLAYBACK, COLLECTION_URL)
        c[COLLECTION_TRACK_TIME] = config_file.get(COLLECTION_PLAYBACK, COLLECTION_TRACK_TIME)
        config[COLLECTION_PLAYBACK] = c
        
        c = {PODCAST_URL: config_file.get(PODCASTS, PODCAST_URL)}
        c[PODCAST_EPISODE_NAME] = config_file.get(PODCASTS, PODCAST_EPISODE_NAME)
        c[PODCAST_EPISODE_URL] = config_file.get(PODCASTS, PODCAST_EPISODE_URL)
        c[PODCAST_EPISODE_TIME] = config_file.get(PODCASTS, PODCAST_EPISODE_TIME)
        config[PODCASTS] = c

        c = {YA_STREAM_ID: config_file.get(YA_STREAM, YA_STREAM_ID)}
        c[YA_STREAM_NAME] = config_file.get(YA_STREAM, YA_STREAM_NAME)
        c[YA_STREAM_URL] = self.cleanup_url(config_file, YA_STREAM, YA_STREAM_URL)
        c[YA_THUMBNAIL_PATH] = self.cleanup_url(config_file, YA_STREAM, YA_THUMBNAIL_PATH)
        c[YA_STREAM_TIME] = config_file.get(YA_STREAM, YA_STREAM_TIME)
        config[YA_STREAM] = c

        c = {FAVORITE_STATION_NAME: config_file.get(RADIO_BROWSER, FAVORITE_STATION_NAME)}
        c[FAVORITE_STATION_ID] = config_file.get(RADIO_BROWSER, FAVORITE_STATION_ID)
        c[FAVORITE_STATION_LOGO] = config_file.get(RADIO_BROWSER, FAVORITE_STATION_LOGO)
        c[FAVORITE_STATION_URL] = config_file.get(RADIO_BROWSER, FAVORITE_STATION_URL)

        config[RADIO_BROWSER] = c

        c = {ITEM: config_file.get(JUKEBOX, ITEM)}
        c[PAGE] = config_file.get(JUKEBOX, PAGE)
        config[JUKEBOX] = c

        c = {ITEM: config_file.get(ARCHIVE, ITEM)}
        c[FILE] = config_file.get(ARCHIVE, FILE)
        c[FILE_TIME] = config_file.get(ARCHIVE, FILE_TIME)
        config[ARCHIVE] = c

        for language in config[KEY_LANGUAGES]:
            n = language[NAME]
            k = STATIONS + "." + n
            try:
                config[k] = self.get_section(config_file, k)
            except:
                config[k] = {}
        
        c = {BROWSER_BOOK_TITLE: config_file.get(AUDIOBOOKS, BROWSER_BOOK_TITLE)}
        c[BROWSER_BOOK_URL] = config_file.get(AUDIOBOOKS, BROWSER_BOOK_URL)
        c[BROWSER_IMAGE_URL] = config_file.get(AUDIOBOOKS, BROWSER_IMAGE_URL)
        c[BROWSER_TRACK_FILENAME] = config_file.get(AUDIOBOOKS, BROWSER_TRACK_FILENAME)
        c[BROWSER_BOOK_TIME] = config_file.get(AUDIOBOOKS, BROWSER_BOOK_TIME)        
        c[BROWSER_SITE] = config_file.get(AUDIOBOOKS, BROWSER_SITE)
        config[AUDIOBOOKS] = c
        
        c = {SLEEP_TIME: config_file.get(TIMER, SLEEP_TIME)}
        c[WAKE_UP_TIME] = config_file.get(TIMER, WAKE_UP_TIME)
        try:
            c[SLEEP] = config_file.getboolean(TIMER, SLEEP)
        except:
            c[SLEEP] = False
        try:
            c[WAKE_UP] = config_file.getboolean(TIMER, WAKE_UP)
        except:
            c[WAKE_UP] = False
        try:
            c[POWEROFF] = config_file.getboolean(TIMER, POWEROFF)
        except:
            c[POWEROFF] = False                   
        config[TIMER] = c

    def cleanup_url(self, conf, section, property):
        """ Replace double %% by single %

        :param conf: config file parser
        :param section: section name
        :param property: property name

        :return: processed URL
        """
        url = ""

        url = conf.get(section, property)
        if url and "%%" in url:
            url = url.replace("%%", "%")

        return url

    def get_list(self, c, section_name, property_name):
        """ Return property which contains comma separated values
        
        :param section_name: section name in the configuration file (string enclosed between [])
        :param property_name: property name        
        :return: list of values defined as comma separated properties 
        """
        a = c.get(section_name, property_name).split(",")
        return list(map(str.strip, a))

    def get_section(self, config_file, section_name):
        """ Return property file section specified by name
        
        :param config_file: parsed configuration file
        :section_name: section name in the configuration file (string enclosed between [])        
        :return: dictionary with properties from specified section 
        """
        c = config_file[section_name]
        d = r = {}
        for i in c.items():
            k = i[0]
            if k == CURRENT_STATIONS:
                try:                
                    d[k] = i[1]
                except:
                    d[k] = ""
            else:
                try:
                    d[k] = int(i[1])
                except:
                    d[k] = 0
        return r

    def get_color_tuple(self, s):
        """ Convert string with comma separated colors into tuple with integer number for each color
        
        :param s: input string (e.g. "10,20,30" for RGB)        
        :return: tuple with colors (e.g. (10,20,30))
        """
        a = s.split(",")
        return tuple(int(e) for e in a)
    
    def get_equalizer(self, s):
        """ Convert comma separated values into list
        
        :param s: input string        
        :return: frequency list
        """
        a = s[1 : -1].split(",")
        return list(int(e) for e in a)
    
    def save_current_settings(self):
        """ Save current configuration object (self.config) into current.txt file """ 
              
        config_parser = ConfigParser()
        config_parser.optionxform = str
        path = os.path.join(os.getcwd(), FOLDER_CONFIGURATION, FILE_CURRENT)
        config_parser.read(path, encoding=UTF8)
        
        a = b = c = e = f = g = h = i = j = k = m = n = stations_changed = None
        
        if self.config[USAGE][USE_AUTO_PLAY]:        
            c = self.save_section(FILE_PLAYBACK, config_parser)
            i = self.save_section(COLLECTION_PLAYBACK, config_parser)

            keys = self.config.keys()
            s = STATIONS + "."
            stations_changed = False
            for key in keys:
                if key.startswith(s):
                    z = self.save_section(key, config_parser)
                    if z: stations_changed = True
            
            f = self.save_section(AUDIOBOOKS, config_parser)
            h = self.save_section(PODCASTS, config_parser)
            j = self.save_section(YA_STREAM, config_parser)
            k = self.save_section(JUKEBOX, config_parser)
            m = self.save_section(ARCHIVE, config_parser)
            n = self.save_section(RADIO_BROWSER, config_parser)

        a = self.save_section(CURRENT, config_parser)
        b = self.save_section(PLAYER_SETTINGS, config_parser)
        e = self.save_section(SCREENSAVER, config_parser)
        g = self.save_section(TIMER, config_parser)
        
        if a or b or c or e or f or g or h or i or j or k or m or n or stations_changed:
            path = os.path.join(os.getcwd(), FOLDER_CONFIGURATION, FILE_CURRENT)
            with codecs.open(path, 'w', UTF8) as file:
                config_parser.write(file)
                
    def save_section(self, name, config_parser):
        """ Save configuration file section
        
        :param name: section name
        :param config_parser: configuration parser
        """
        content = None
        try:
            content = self.config[name]
        except KeyError:
            pass
        
        if not content: return None
        
        sections = config_parser.sections()
        if name not in sections:
            config_parser.add_section(name)
        
        for t in content.items():
            try:
                s = t[1]
                if isinstance(s, str) and "%" in s:
                    s = s.replace("%", "%%")
                config_parser.set(name, t[0], str(s))
            except Exception as e:
                logging.error(e)
                return 0
            
        return 1

    def load_config_parameters(self, include_classes=True):
        """ Load configuration parameters

        :param include_classes: include classes as properties e.g. Backlight

        :return: dictionary of parameters
        """
        params = {RELEASE: self.load_release()}
        self.load_config(params, include_classes)
        self.load_languages(params)
        self.load_players(params)
        self.load_current(params)

        return params

    def save_config_parameters(self, parameters):
        """ Save configuration file (config.txt) """

        config_parser = ConfigParser()
        config_parser.optionxform = str
        path = os.path.join(os.getcwd(), FOLDER_CONFIGURATION, FILE_CONFIG)
        config_parser.read(path, encoding=UTF8)

        keys = list(parameters.keys())
        for key in keys:
            if key == LANGUAGES_MENU:
                continue
            params = parameters[key]
            for t in params.items():
                if isinstance(t[1], list):
                    color = ",".join(map(str, t[1]))
                    config_parser.set(key, t[0], color)
                else:
                    config_parser.set(key, t[0], str(t[1]))

        with codecs.open(path, 'w', UTF8) as file:
            config_parser.write(file)

        self.save_languages_menu_config_parameters(parameters)

    def save_languages_menu_config_parameters(self, parameters):
        """ Save languages menu parameters in file languages.txt """

        config_parser = ConfigParser()
        config_parser.optionxform = str
        path = os.path.join(os.getcwd(), FOLDER_LANGUAGES, FILE_LANGUAGES)
        config_parser.read(path, encoding=UTF8)
        params = parameters[LANGUAGES_MENU]

        for t in params.items():
            config_parser.set(LANGUAGES_MENU, t[0], str(t[1]))

        with codecs.open(path, 'w', UTF8) as file:
            config_parser.write(file)

    def get_pygame_screen(self):
        """ Initialize Pygame screen
        
        :return: pygame display object which is used as drawing context
        """
        w = self.config[SCREEN_INFO][WIDTH]
        h = self.config[SCREEN_INFO][HEIGHT]
        d = self.config[SCREEN_INFO][DEPTH]
        
        if self.config[USAGE][USE_HEADLESS]:
            os.environ["SDL_VIDEODRIVER"] = "dummy"
            os.environ["DISPLAY"] = ":0"
            pygame.display.init()
            pygame.font.init()
            return pygame.display.set_mode((1,1), pygame.DOUBLEBUF, d)
        
        pygame.display.init()
        pygame.font.init()
            
        if self.config[LINUX_PLATFORM]:
            pygame.mouse.set_visible(False)
        else:            
            pygame.display.set_caption("Peppy")
        
        if self.config[SCREEN_INFO][HDMI]:
            if self.config[SCREEN_INFO][NO_FRAME]:
                return pygame.display.set_mode((w, h), pygame.NOFRAME)
            else:
                return pygame.display.set_mode((w, h))
        else:
            if self.config[SCREEN_INFO][NO_FRAME]:
                return pygame.display.set_mode((w, h), pygame.DOUBLEBUF | pygame.NOFRAME, d)
            else:
                return pygame.display.set_mode((w, h), pygame.DOUBLEBUF, d)
        
    def init_lcd(self):
        """ Initialize touch-screen """
        
        if not self.config[USAGE][USE_TOUCHSCREEN] or self.config[USAGE][USE_HEADLESS] or not self.config[LINUX_PLATFORM]:
            return
        
        if os.path.exists("/dev/fb1"):
            os.environ["SDL_FBDEV"] = "/dev/fb1"
        elif os.path.exists("/dev/fb0"):
            os.environ["SDL_FBDEV"] = "/dev/fb0"
            
        if self.config[USAGE][USE_MOUSE]:
            if os.path.exists("/dev/input/touchscreen"):
                os.environ["SDL_MOUSEDEV"] = "/dev/input/touchscreen"
            else:
                os.environ["SDL_MOUSEDEV"] = "/dev/input/event0"
            os.environ["SDL_MOUSEDRV"] = "TSLIB"
