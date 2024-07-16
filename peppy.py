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

import os
import sys
import subprocess
import pygame
import importlib
import time
import logging
import socket

from datetime import datetime
from threading import RLock, Thread
from subprocess import Popen
from event.dispatcher import EventDispatcher
from player.proxy import Proxy, MPD_NAME, SHAIRPORT_SYNC_NAME, RASPOTIFY_NAME, BLUETOOTH_SINK_NAME
from player.player import Player
from screensaver.screensaverdispatcher import ScreensaverDispatcher
from ui.state import State
from ui.screen.radiogroup import RadioGroupScreen
from ui.screen.home import HomeScreen
from ui.screen.language import LanguageScreen
from ui.screen.saver import SaverScreen
from ui.screen.about import AboutScreen
from ui.screen.black import BlackScreen
from ui.player.radioplayer import RadioPlayerScreen
from ui.player.streamplayer import StreamPlayerScreen
from ui.browser.radio import RadioBrowserScreen
from ui.browser.stream import StreamBrowserScreen
from ui.browser.file import FileBrowserScreen
from ui.player.fileplayer import FilePlayerScreen
from ui.screen.equalizer import EqualizerScreen
from ui.screen.timer import TimerScreen
from ui.layout.borderlayout import BorderLayout
from ui.screen.screen import PERCENT_TOP_HEIGHT, PERCENT_TITLE_FONT
from util.config import *
from util.util import Util, LABELS, PLAYER_RUNNING, PLAYER_SLEEPING
from util.keys import *
from ui.player.bookplayer import BookPlayer
from ui.screen.booktrack import BookTrack
from ui.screen.bookgenre import BookGenre
from ui.screen.bookgenrebooks import BookGenreBooks
from ui.screen.booknew import BookNew
from websiteparser.loyalbooks.loyalbooksparser import LoyalBooksParser
from websiteparser.loyalbooks.constants import *
from websiteparser.siteparser import BOOK_URL, FILE_NAME
from util.volumecontrol import VolumeControl
from ui.screen.podcasts import PodcastsScreen
from ui.screen.podcastepisodes import PodcastEpisodesScreen
from ui.player.podcastplayer import PodcastPlayerScreen
from ui.player.airplayplayer import AirplayPlayerScreen
from ui.player.spotifyconnect import SpotifyConnectScreen
from ui.screen.network import NetworkScreen
from ui.screen.wifi import WiFiScreen
from ui.screen.bluetooth import BluetoothScreen
from ui.screen.keyboard import KeyboardScreen
from ui.screen.collection import CollectionScreen
from ui.screen.topic import TopicScreen
from ui.screen.topicdetail import TopicDetailScreen
from ui.screen.latinabc import LatinAbcScreen
from ui.screen.collectionplayer import CollectionPlayerScreen
from ui.screen.collectionbrowser import CollectionBrowserScreen
from ui.screen.info import InfoScreen
from ui.screen.switch import SwitchScreen
from ui.screen.imageviewer import ImageViewer
from ui.player.bluetoothsink import BluetoothSinkScreen
from ui.screen.yastream import YaStreamScreen
from ui.player.yaplaylistplayer import YaPlaylistPlayerScreen
from ui.player.yasearchplayer import YaSearchPlayerScreen
from ui.browser.yaplaylist import YaPlaylistScreen
from ui.browser.yasearch import YaSearchScreen
from ui.browser.archivefiles import ArchiveFilesBrowserScreen
from ui.browser.archiveitems import ArchiveItemsBrowserScreen
from subprocess import Popen, check_output
from ui.browser.jukebox import JukeboxBrowserScreen
from ui.player.archiveplayer import ArchivePlayerScreen
from util.fileutil import FILE_PLAYLIST
from ui.browser.browser import BrowserScreen
from ui.browser.search import RadioSearchScreen
from ui.player.radiobrowserplayer import RadioBrowserPlayerScreen
from ui.screen.searchby import SearchByScreen
from ui.browser.favorites import FavoritesScreen
from ui.screen.catalog import CatalogScreen
from ui.browser.catalogbase import CatalogBase
from ui.browser.catalogalbumtracks import CatalogAlbumTracks
from ui.player.catalogplayer import CatalogPlayerScreen
from ui.browser.cataloggenres import CatalogGenres
from ui.browser.cataloggenreartists import CatalogGenreArtists
from util.serviceutil import SERVICE_QOBUZ, SERVICE_DEEZER, SERVICE_SPOTIFY

class Peppy(object):
    """ Main class """
    
    lock = RLock()
    def __init__(self):
        """ Initializer """

        self.util = Util()
        self.config = self.util.config
        self.util.connected_to_internet = self.check_internet_connectivity()
        self.util.init_utilities()
        
        self.use_web = self.config[USAGE][USE_WEB]
        self.players = {}
        self.volume_control = VolumeControl(self.util)

        self.voice_assistant = None
        if self.config[USAGE][USE_VOICE_ASSISTANT]:
            language = self.util.get_voice_assistant_language_code(self.config[CURRENT][LANGUAGE])
            if language:
                try:
                    from voiceassistant.voiceassistant import VoiceAssistant
                    self.voice_assistant = VoiceAssistant(self.util)
                    self.voice_assistant.start()
                except Exception as e:
                    logging.debug(e)

        self.player_screens = {
            KEY_PLAY_SITE: self.go_site_playback,
            KEY_STATIONS: self.go_stations,
            KEY_PLAY_FILE: self.go_file_playback,
            STREAM: self.go_stream,
            KEY_PODCAST_PLAYER: self.go_podcast_player,
            KEY_AIRPLAY_PLAYER: self.go_airplay,
            KEY_SPOTIFY_CONNECT_PLAYER: self.go_spotify_connect,
            KEY_BLUETOOTH_SINK_PLAYER: self.go_bluetooth_sink,
            KEY_PLAY_COLLECTION: self.go_collection_playback,
            KEY_YA_PLAYLIST_PLAYER: self.go_ya_playlist_player,
            KEY_YA_SEARCH_PLAYER: self.go_ya_search_player,
            KEY_JUKEBOX_BROWSER: self.go_jukebox,
            KEY_ARCHIVE_PLAYER: self.go_archive,
            KEY_RADIO_BROWSER_PLAYER: self.go_radio_browser_player,
            KEY_CATALOG_NEW_RELEASE_PLAYER: self.go_catalog_new_release_player,
            KEY_CATALOG_BESTSELLER_PLAYER: self.go_catalog_bestseller_player,
            KEY_CATALOG_GENRE_PLAYER: self.go_catalog_genre_player
        }

        try:
            self.util.switch_util.switch_power()
        except:
            pass

        if self.config[LINUX_PLATFORM]:
            from util.diskmanager import DiskManager
            from util.nasmanager import NasManager
            self.disk_manager = DiskManager(self)
            self.nas_manager = NasManager(self)

            if self.config[DISK_MOUNT][MOUNT_AT_STARTUP]:
                self.disk_manager.mount_all_usb_disks()
                self.nas_manager.mount_all_nases()
            if self.config[DISK_MOUNT][MOUNT_AT_PLUG]:
                self.disk_manager.start_observer()

        self.util.samba_util.start_sharing()

        if self.config[DSI_DISPLAY_BACKLIGHT][USE_DSI_DISPLAY] and self.config[BACKLIGHTER]:
            screen_brightness = int(self.config[DSI_DISPLAY_BACKLIGHT][SCREEN_BRIGHTNESS])
            self.config[BACKLIGHTER].brightness = screen_brightness
            if self.config[BACKLIGHTER].power == False:
                self.config[BACKLIGHTER].power = True

        if self.config[LINUX_PLATFORM] and self.config[USAGE][USE_BLUETOOTH]:
            bluetooth_util = self.util.get_bluetooth_util()
            if self.config[CURRENT][MODE]:
                if self.config[CURRENT][MODE] == BLUETOOTH_SINK:
                    bluetooth_util.connect_bluetooth_sink()
                else:
                    bluetooth_util.connect_device(remove_previous=False)
        
        s = self.config[SCRIPTS][SCRIPT_PLAYER_START]
        if s != None and len(s.strip()) != 0:
            self.util.run_script(s)
        
        layout = BorderLayout(self.util.screen_rect)
        layout.set_percent_constraints(PERCENT_TOP_HEIGHT, PERCENT_TOP_HEIGHT, 0, 0)
        self.config[MAXIMUM_FONT_SIZE] = int((layout.TOP.h * PERCENT_TITLE_FONT)/100.0)
        
        try:
            values = self.config[CURRENT][EQUALIZER]
            if values:
                self.util.set_equalizer(values)
        except:
            pass            

        if self.use_web:
            try:
                f = open(os.devnull, 'w')
                sys.stdout = sys.stderr = f
                from web.server.webserver import WebServer
                self.web_server = WebServer(self.util, self)
            except Exception as e:
                logging.debug(e)
                self.use_web = False

        self.screensaver_dispatcher = ScreensaverDispatcher(self.util, self.web_server)
        
        about = AboutScreen(self.util)
        about.add_listener(self.go_home)
        self.screens = {KEY_ABOUT : about}
        self.current_player_screen = None
        self.initial_player_name = self.config[AUDIO][PLAYER_NAME]
        self.current_audio_file = None
        
        if self.config[AUDIO][PLAYER_NAME] == MPD_NAME:
            self.start_audio()
            if self.config[USAGE][USE_VU_METER]:
                self.util.load_screensaver(VUMETER)
        else:
            if self.config[USAGE][USE_VU_METER]:
                self.util.load_screensaver(VUMETER)
            self.start_audio()        
                
        if self.use_web:
            self.screensaver_dispatcher.add_start_listener(self.web_server.start_screensaver_to_json)
            self.screensaver_dispatcher.add_stop_listener(self.web_server.stop_screensaver_to_json)
               
        self.event_dispatcher = EventDispatcher(self.screensaver_dispatcher, self.util, self.volume_control)        
        self.current_screen = None
        self.current_mode = self.config[CURRENT][MODE]

        disabled_modes = self.util.get_disabled_modes()
        if self.current_mode in disabled_modes:
            self.go_home(None)
            return
        
        if not self.config[CURRENT][MODE] or not self.config[USAGE][USE_AUTO_PLAY]:
            if self.config[CURRENT][MODE] == JUKEBOX:
                self.go_jukebox(None)
            else:
                self.go_home(None)
        elif self.config[CURRENT][MODE] == RADIO and self.config[HOME_MENU][RADIO]:
            state = State()
            state.source = INIT
            self.go_stations(state)
        elif self.config[CURRENT][MODE] == AUDIO_FILES and self.config[HOME_MENU][AUDIO_FILES]:
            state = State()
            state.folder = self.config[FILE_PLAYBACK][CURRENT_FOLDER].replace('\\\\', '\\')
            state.file_name = self.config[FILE_PLAYBACK][CURRENT_FILE]
            state.url = state.folder + os.sep + state.file_name
            state.playback_mode = self.config[FILE_PLAYBACK][CURRENT_FILE_PLAYBACK_MODE]
            if self.config[FILE_PLAYBACK][CURRENT_FILE_PLAYBACK_MODE] == FILE_PLAYLIST:
                state.url = state.folder + os.sep + self.config[FILE_PLAYBACK][CURRENT_FILE_PLAYLIST]
                state.playlist_track_number = self.config[FILE_PLAYBACK][CURRENT_FILE_PLAYLIST_INDEX]
            self.wait_for_file(state.url)
            self.go_file_playback(state)
        elif self.config[CURRENT][MODE] == STREAM and self.config[HOME_MENU][STREAM]:
            self.go_stream()
        elif self.config[CURRENT][MODE] == AUDIOBOOKS and self.config[HOME_MENU][AUDIOBOOKS]:
            state = State()
            state.name = self.config[AUDIOBOOKS][BROWSER_BOOK_TITLE]
            state.book_url = self.config[AUDIOBOOKS][BROWSER_BOOK_URL]
            state.img_url = self.config[AUDIOBOOKS][BROWSER_IMAGE_URL]
            state.file_name = self.config[AUDIOBOOKS][BROWSER_TRACK_FILENAME]
            state.source = INIT
            self.go_site_playback(state)
        elif self.config[CURRENT][MODE] == PODCASTS and self.config[HOME_MENU][PODCASTS]:
            state = State()
            state.podcast_url = self.config[PODCASTS][PODCAST_URL]
            state.name = self.config[PODCASTS][PODCAST_EPISODE_NAME]
            state.url = self.config[PODCASTS][PODCAST_EPISODE_URL]
            state.episode_time = self.config[PODCASTS][PODCAST_EPISODE_TIME]
            state.source = INIT
            self.go_podcast_player(state)
        elif self.config[CURRENT][MODE] == AIRPLAY and self.config[HOME_MENU][AIRPLAY]:
            self.reconfigure_player(SHAIRPORT_SYNC_NAME)
            self.go_airplay()
        elif self.config[CURRENT][MODE] == SPOTIFY_CONNECT and self.config[HOME_MENU][SPOTIFY_CONNECT]:
            self.reconfigure_player(RASPOTIFY_NAME)
            self.go_spotify_connect()
        elif self.config[CURRENT][MODE] == COLLECTION and self.config[HOME_MENU][COLLECTION]:
            state = State()
            state.topic = self.config[COLLECTION_PLAYBACK][COLLECTION_TOPIC]
            state.folder = self.config[COLLECTION_PLAYBACK][COLLECTION_FOLDER]
            state.file_name = self.config[COLLECTION_PLAYBACK][COLLECTION_FILE]
            state.url = self.config[COLLECTION_PLAYBACK][COLLECTION_URL]
            state.track_time = self.config[COLLECTION_PLAYBACK][COLLECTION_TRACK_TIME]
            state.source = INIT
            self.wait_for_file(state.url)
            self.go_collection_playback(state)
        elif self.config[CURRENT][MODE] == BLUETOOTH_SINK and self.config[HOME_MENU][BLUETOOTH_SINK]:
            self.reconfigure_player(BLUETOOTH_SINK_NAME)
            self.go_bluetooth_sink()
        elif self.config[CURRENT][MODE] == YA_STREAM and self.config[HOME_MENU][YA_STREAM]:
            state = State()
            state.id = self.config[YA_STREAM][YA_STREAM_ID]
            state.l_name = self.config[YA_STREAM][YA_STREAM_NAME]
            state.url = self.config[YA_STREAM][YA_STREAM_URL]
            state.image_path = self.config[YA_STREAM][YA_THUMBNAIL_PATH]
            state.time = self.config[YA_STREAM][YA_PLAYLIST_TIME]
            state.source = INIT
            self.go_ya_playlist_player(state)
        elif self.config[CURRENT][MODE] == JUKEBOX and self.config[HOME_MENU][JUKEBOX]:
            state = State()
            state.source = INIT
            self.go_jukebox(state)
        elif self.config[CURRENT][MODE] == ARCHIVE and self.config[HOME_MENU][ARCHIVE]:
            state = State()
            state.item = self.config[ARCHIVE][ITEM]
            state.file = self.config[ARCHIVE][FILE]
            state.file_time = self.config[ARCHIVE][FILE_TIME]
            state.source = INIT
            self.go_archive(state)
        elif self.config[CURRENT][MODE] == RADIO_BROWSER and self.config[HOME_MENU][RADIO_BROWSER]:
            state = State()
            state.id = self.config[RADIO_BROWSER][FAVORITE_STATION_ID]
            state.name = state.l_name = state.comparator_item = self.config[RADIO_BROWSER][FAVORITE_STATION_NAME]
            state.url = self.config[RADIO_BROWSER][FAVORITE_STATION_URL]
            state.image_path = self.config[RADIO_BROWSER][FAVORITE_STATION_LOGO]
            state.index = 0
            state.source = INIT
            self.go_radio_browser_player(state)
        else:
            self.go_home(None)
        
        self.player_state = PLAYER_RUNNING
        self.run_timer_thread = False   
        self.start_timer_thread()

    def wait_for_file(self, url):
        """ Wait for the file which can be unavailable at the moment after switching the hard drive on
        Makes 6 attempts 5 seconds each

        :param url: the file URL
        """
        attempts = 6
        timeout = 5
        for _ in range(attempts):
            file_available = os.path.exists(url)
            if file_available:
                logging.debug("File {} is available".format(url))
                break
            else:
                logging.debug("File {} is unavailable".format(url))
                time.sleep(timeout)
                continue

    def check_internet_connectivity(self):
        """ Exit if Internet is not available after 3 attempts 3 seconds each """

        attempts = 3
        timeout = 3
        for n in range(attempts):
            internet_available = self.is_internet_available(timeout)
            if internet_available:
                break
            else:
                if n == (attempts - 1):
                    logging.error("Internet is not available")
                    return False
                else:
                    time.sleep(timeout)
                    continue
        return True
    
    def is_internet_available(self, timeout):
        """ Check that Internet is available. The solution was taken from here:
        https://stackoverflow.com/questions/3764291/checking-network-connection

        :param timeout: request timeout
        :return: True - Internet available, False - not available
        """
        dns_server = self.config[USAGE][USE_DNS_IP].strip()
        dns_server_port = 53
        
        try:
            socket.setdefaulttimeout(timeout)
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((dns_server, dns_server_port))
            return True
        except Exception as e:
            logging.error("Connection error: {0}".format(e))
            return False
            
    def start_audio(self):
        """ Starts audio server and client """
        
        if self.config[AUDIO][PLAYER_NAME] in self.players.keys():
            self.player = self.players[self.config[AUDIO][PLAYER_NAME]]
            if hasattr(self.player, "proxy"):
                self.player.proxy.start()
                self.player.start_client()
            self.volume_control.set_player(self.player)
            return

        folder = None
        try:
            folder = self.config[AUDIO][SERVER_FOLDER]
        except:
            pass
        
        start_cmd = None
        try:
            start_cmd = self.config[AUDIO][SERVER_START_COMMAND]
        except:
            pass
        
        stream_server_parameters = None
        if self.config[USAGE][USE_STREAM_SERVER]:
            try:
                stream_server_parameters = self.config[AUDIO][STREAM_SERVER_PARAMETERS]
            except:
                pass

        stream_client_parameters = None
        try:
            stream_client_parameters = self.config[AUDIO][STREAM_CLIENT_PARAMETERS]
        except:
            pass
        
        if stream_client_parameters:
            if start_cmd:
                start_cmd = start_cmd + " " + stream_client_parameters
            else:
                start_cmd = stream_client_parameters
        
        client_name = self.config[AUDIO][CLIENT_NAME]
        linux = self.config[LINUX_PLATFORM]
        stop_cmd = self.config[AUDIO][SERVER_STOP_COMMAND]

        self.proxy = Proxy(client_name, linux, folder, start_cmd, stop_cmd, self.config[PLAYER_SETTINGS][VOLUME], stream_server_parameters)
        self.proxy_process = self.proxy.start()
        logging.debug("Audio Server Started")
        
        p = "player." + client_name
        try:
            m = importlib.import_module(p)
        except Exception as e:
            logging.debug(e)
        n = client_name.title()
        player = getattr(m, n)()
        player.set_platform(linux)
        player.set_player_mode(self.config[CURRENT][MODE])
        player.set_proxy(self.proxy_process, self.proxy)
        player.set_util(self.util)

        if self.config[VOLUME_CONTROL][VOLUME_CONTROL_TYPE] == VOLUME_CONTROL_TYPE_PLAYER:
            player.set_player_volume_control(True)
        else:
            player.set_player_volume_control(False)

        player.start_client()

        if self.config[PLAYER_SETTINGS][PAUSE]:
            player.pause()

        self.players[self.config[AUDIO][PLAYER_NAME]] = player
        self.player = player
        self.volume_control.set_player(player)
    
    def start_timer_thread(self):
        """ Start timer thread """
        
        if not self.config[HOME_NAVIGATOR][TIMER] or self.run_timer_thread:
            return
        
        sleep_selected = self.config[TIMER][SLEEP] and len(self.config[TIMER][SLEEP_TIME]) > 0
        poweroff_selected = self.config[TIMER][POWEROFF] and len(self.config[TIMER][SLEEP_TIME]) > 0
        
        if not sleep_selected and not poweroff_selected:
            return
        
        self.run_timer_thread = True
        self.timer_thread = Thread(target=self.timer_thread)
        self.timer_thread.start()

    def timer_thread(self):
        """ Timer thread function """
        
        while self.run_timer_thread:
            time.sleep(2)
            
            with self.lock:
                sleep_selected = self.config[TIMER][SLEEP]
                poweroff_selected = self.config[TIMER][POWEROFF]
                wake_up_selected = self.config[TIMER][WAKE_UP]            
                sleep_time = self.config[TIMER][SLEEP_TIME] + "00"
                wake_up_time = self.config[TIMER][WAKE_UP_TIME] + "00"
                
            current_time = datetime.now().strftime("%H%M%S")
            
            if sleep_selected:
                if wake_up_selected and self.player_state == PLAYER_SLEEPING and self.is_time_in_range(current_time, wake_up_time):
                    self.wake_up()
                    with self.lock:
                        self.player_state = PLAYER_RUNNING
                if not self.is_time_in_range(current_time, sleep_time):
                    continue                
                if self.player_state == PLAYER_RUNNING:
                    self.sleep()                
            elif poweroff_selected:
                if not self.is_time_in_range(current_time, sleep_time):
                    continue          
                logging.debug("poweroff")
                self.run_timer_thread = False
                self.shutdown()
    
    def is_time_in_range(self, t1, t2):
        """ Check if provided time (t1) is in range of 4 seconds (t1)
        
        :param t1: current time
        :param t2: time to compare to
        
        :return: True - time in range, False - time out of range
        """
        current_h_m = t1[0:4]
        current_sec = t1[4:]
        
        if current_h_m != t2[0:4]:
            return False

        if int(current_sec) < 3:
            return True
        else:
            return False
    
    def sleep(self, state=None):
        """ Go to sleep mode
        
        :param state: button state object
        """
        if self.player_state == PLAYER_SLEEPING:
            return

        logging.debug("sleep")
        with self.lock:
            self.player_state = PLAYER_SLEEPING
        self.player.stop()
        
        if self.screensaver_dispatcher.saver_running:
            self.screensaver_dispatcher.cancel_screensaver()

        self.screensaver_dispatcher.current_delay = 0      

        if self.config[USAGE][USE_CLOCK_SCREENSAVER_IN_TIMER]:
            self.screensaver_dispatcher.start_screensaver(CLOCK)
        else:
            self.go_black()

        if self.config[DSI_DISPLAY_BACKLIGHT][USE_DSI_DISPLAY] and self.config[DSI_DISPLAY_BACKLIGHT][SLEEP_NOW_DISPLAY_POWER_OFF]:
            self.config[BACKLIGHTER].power = False

        self.util.run_script(self.config[SCRIPTS][SCRIPT_TIMER_START])
        
    def wake_up(self, state=None):
        """ Wake up from sleep mode
        
        :param state: button state object
        """
        if self.player_state == PLAYER_RUNNING:
            return

        logging.debug("wake up")
        self.player_state = PLAYER_RUNNING
        self.player.resume_playback()
        self.set_current_screen(self.previous_screen_name)
        self.screensaver_dispatcher.delay_counter = 0
        self.screensaver_dispatcher.current_delay = self.screensaver_dispatcher.get_delay()
        if self.use_web:
            self.web_server.redraw_web_ui()

        if self.config[DSI_DISPLAY_BACKLIGHT][USE_DSI_DISPLAY] and self.config[DSI_DISPLAY_BACKLIGHT][SLEEP_NOW_DISPLAY_POWER_OFF]:
            self.config[BACKLIGHTER].power = True

        self.util.run_script(self.config[SCRIPTS][SCRIPT_TIMER_STOP])
        
    def exit_current_screen(self):
        """ Complete action required to exit screen """
                
        with self.lock:
            cs = self.current_screen
            if cs and self.screens and self.screens[cs]:
                self.screens[cs].exit_screen()
                
    def set_mode(self, state):
        """ Set current mode (e.g. Radio, Language etc)
        
        :param state: button state
        """
        self.store_current_track_time(self.current_screen)
        state.source = "home"
        mode = state.genre
        
        if self.current_mode != mode:
            self.player.stop()
            if self.current_mode == AIRPLAY or self.current_mode == SPOTIFY_CONNECT or self.current_mode == BLUETOOTH_SINK:
                self.reconfigure_player(self.initial_player_name)
                if self.current_mode == BLUETOOTH_SINK:
                    bluetooth_util = self.util.get_bluetooth_util()
                    bluetooth_util.disconnect_bluetooth_sink()

            self.current_mode = mode
            self.player.set_player_mode(mode)
            state.change_mode = True
        else:
            state.change_mode = False

        if mode == RADIO: self.go_stations(state)
        elif mode == RADIO_BROWSER: self.go_radio_browser_player(state)
        elif mode == AUDIO_FILES: self.go_file_playback(state)
        elif mode == STREAM: self.go_stream(state)
        elif mode == AUDIOBOOKS: self.go_audiobooks(state)
        elif mode == PODCASTS: self.go_podcast_player(state)
        elif mode == AIRPLAY:
            self.reconfigure_player(SHAIRPORT_SYNC_NAME)
            self.go_airplay(state)
        elif mode == SPOTIFY_CONNECT:
            self.reconfigure_player(RASPOTIFY_NAME)
            self.go_spotify_connect(state)
        elif mode == BLUETOOTH_SINK:
            self.reconfigure_player(BLUETOOTH_SINK_NAME)
            bluetooth_util = self.util.get_bluetooth_util()
            bluetooth_util.connect_bluetooth_sink()
            self.go_bluetooth_sink(state)
        elif mode == COLLECTION: self.go_collection(state)
        elif mode == YA_STREAM: self.go_ya_stream(state)
        elif mode == JUKEBOX: self.go_jukebox(state)
        elif mode == ARCHIVE: self.go_archive(state)
        elif mode == CATALOG: self.go_catalog(state)

        self.config[CURRENT][MODE] = mode
        
    def go_player(self, state):
        """ Go to the current player screen
        
        :param state: button state
        """ 
        try:
            state.source = GO_PLAYER
            self.player_screens[self.current_player_screen](state)
        except:
            pass
        
    def go_favorites(self, state):
        """ Go to the favorites screen
        
        :param state: button state
        """ 
        state.source = KEY_FAVORITES
        self.go_stations(state)

    def go_radio_browser_favorites(self, state):
        """ Go to the radio browser favorites screen

        :param state: button state
        """
        state.source = KEY_FAVORITES
        favorite_id = self.config[RADIO_BROWSER].get(FAVORITE_STATION_ID, None)
        if not favorite_id:
            self.go_favorites_screen(state)
        else:
            self.go_radio_browser_player(state)

    def get_current_screen(self, key, state=None):
        """ Return current screen by name
        
        :param key: screen name
        """ 
        s = None
        self.exit_current_screen()
        try:
            if self.screens and self.screens[key]:
                s = self.screens[key]
                self.set_current_screen(key, state=state)
        except KeyError:
            pass
        return s

    def add_screen_observers(self, screen):
        """ Add web obervers to the provided screen
        
        :param screen: screen for observers
        """
        screen.add_screen_observers(self.web_server.update_web_ui, self.web_server.redraw_web_ui)

    def go_home(self, state):
        """ Go to the Home Screen
        
        :param state: button state
        """        
        if self.get_current_screen(KEY_HOME): return
        
        listeners = self.get_home_screen_listeners()
        home_screen = HomeScreen(self.util, listeners)
        self.screens[KEY_HOME] = home_screen
        self.set_current_screen(KEY_HOME)
        
        if self.use_web:
            self.add_screen_observers(home_screen)
    
    def go_language(self, state):
        """ Go to the Language Screen
        
        :param state: button state
        """
        if self.get_current_screen(LANGUAGE): return

        listeners = {KEY_HOME: self.go_home, KEY_PLAYER: self.go_player}
        language_screen = LanguageScreen(self.util, self.change_language, listeners)
        self.screens[LANGUAGE] = language_screen
        self.set_current_screen(LANGUAGE)

        if self.use_web:
            self.add_screen_observers(language_screen)
    
    def change_language(self, state):
        """ Change current language and go to the Home Screen
        
        :param state: button state
        """
        if state.name != self.config[CURRENT][LANGUAGE]:
            self.config[LABELS].clear()

            try:
                stations = self.screens[KEY_STATIONS]
                if stations:
                    self.player.remove_player_listener(stations.screen_title.set_text)
            except KeyError:
                pass

            self.config[CURRENT][LANGUAGE] = state.name            
            self.config[LABELS] = self.util.get_labels()

            try:
                self.screensaver_dispatcher.current_screensaver.set_util(self.util)
            except:
                pass

            self.config[AUDIOBOOKS][BROWSER_BOOK_URL] = ""
            self.config[AUDIOBOOKS][BROWSER_IMAGE_URL] = ""
            self.screens = {k : v for k, v in self.screens.items() if k == KEY_ABOUT}
            self.current_screen = None
            
            if self.config[USAGE][USE_VOICE_ASSISTANT]:
                language = self.util.get_voice_assistant_language_code(state.name)
                if language and self.voice_assistant != None:
                    self.voice_assistant.change_language()
                           
        self.go_home(state)
        self.player.stop()
        
    def go_file_browser(self, state=None):
        """ Go to the File Browser Screen
        
        :param state: button state
        """
        if self.get_current_screen(AUDIO_FILES): return
        
        file_player = self.screens[KEY_PLAY_FILE]

        listeners = {}
        listeners[KEY_HOME] = self.go_home
        listeners[KEY_PLAY_FILE] = self.go_file_playback
        listeners[GO_BACK] = file_player.restore_current_folder
        listeners[KEY_SWITCH] = self.go_switch
        listeners[KEY_IMAGE_VIEWER] = self.go_image_viewer
        
        file_browser_screen = FileBrowserScreen(self.util, self.player.get_current_playlist, self.player.load_playlist, listeners)
        
        file_player.add_play_listener(file_browser_screen.file_menu.select_item)
        file_player.recursive_notifier = file_browser_screen.file_menu.change_folder
        
        file_browser_screen.file_menu.add_playlist_size_listener(file_player.set_playlist_size)
        file_browser_screen.file_menu.add_play_file_listener(file_player.play_button.draw_default_state)
        
        self.player.add_player_listener(file_browser_screen.file_menu.update_playlist_menu)        
        
        self.screens[AUDIO_FILES] = file_browser_screen
        self.set_current_screen(AUDIO_FILES)
        
        if self.use_web:
            self.add_screen_observers(file_browser_screen)

    def go_image_viewer(self, state=None):
        """ Go to the Image Viewer Screen
        
        :param state: button state
        """
        if self.get_current_screen(KEY_IMAGE_VIEWER, state):
            return
        
        listeners = {}
        listeners[KEY_HOME] = self.go_home
        listeners[KEY_BACK] = self.go_file_browser
        
        image_viewer_screen = ImageViewer(self.util, listeners)
        self.screens[KEY_IMAGE_VIEWER] = image_viewer_screen
        self.set_current_screen(KEY_IMAGE_VIEWER, state=state)
        
        if self.use_web:
            self.add_screen_observers(image_viewer_screen)

    def go_switch(self, state):
        """ Go to the Switch Screen

        :param state: button state
        """
        if self.get_current_screen(KEY_SWITCH): return

        listeners = {KEY_HOME: self.go_home, KEY_BACK: self.go_back, KEY_PLAYER: self.go_player}
        switch_screen = SwitchScreen(self.util, listeners)
        self.screens[KEY_SWITCH] = switch_screen

        if hasattr(self, "disk_manager"):
            switch_screen.menu.add_listener(self.disk_manager.poweroff_by_disk_name)

        self.set_current_screen(KEY_SWITCH)

        if self.use_web:
            self.add_screen_observers(switch_screen)

    def go_collection_browser(self, state=None):
        """ Go to the File Browser Screen
        
        :param state: button state
        """
        self.exit_current_screen()

        name = COLLECTION_TRACK
        if self.get_current_screen(name, state=state): return

        listeners = {}
        listeners[KEY_HOME] = self.go_home
        listeners[COLLECTION] = self.go_collection
        listeners[COLLECTION_TOPIC] = self.go_topic
        listeners[TOPIC_DETAIL] = self.go_topic_detail
        listeners[KEY_PLAY_COLLECTION] = self.go_collection_playback
        listeners[KEY_BACK] = self.go_back
        listeners[KEY_PLAYER] = self.go_player
        
        s = CollectionBrowserScreen(self.util, listeners)
        self.screens[name] = s
        self.set_current_screen(name, state=state)

        file_player = self.screens[KEY_PLAY_COLLECTION]
        file_player.add_play_listener(s.set_current)
        
        if self.use_web:
            self.add_screen_observers(s)

    def go_file_playback(self, state=None):
        """ Go to the File Player Screen
        
        :param state: button state
        """
        self.deactivate_current_player(KEY_PLAY_FILE)

        try:
            if self.screens[KEY_PLAY_FILE]:
                if hasattr(state, "name") and (state.name == KEY_HOME or state.name == KEY_BACK):
                    self.set_current_screen(KEY_PLAY_FILE, True)
                else:
                    self.set_current_screen(name=KEY_PLAY_FILE, state=state)
                self.current_player_screen = KEY_PLAY_FILE
                return
        except Exception as e:
            pass

        if self.config[FILE_PLAYBACK][CURRENT_FILE_PLAYBACK_MODE] == FILE_PLAYLIST:
            self.config[FILE_PLAYBACK][CURRENT_FILE] = self.config[FILE_PLAYBACK][CURRENT_FILE]
            self.config[FILE_PLAYBACK][CURRENT_FILE_PLAYLIST_INDEX] = int(self.config[FILE_PLAYBACK][CURRENT_FILE_PLAYLIST_INDEX])
        else:
            if getattr(state, "url", None):
                tokens = state.url.split(os.sep)
                self.config[FILE_PLAYBACK][CURRENT_FILE] = tokens[len(tokens) - 1]
        
        listeners = self.get_play_screen_listeners()
        listeners[AUDIO_FILES] = self.go_file_browser
        listeners[KEY_SEEK] = self.player.seek
        screen = FilePlayerScreen(
            listeners,
            self.util,
            self.player.get_current_playlist,
            self.volume_control,
            show_order=self.config[PLAYER_SCREEN][ENABLE_ORDER_BUTTON],
            show_info=self.config[PLAYER_SCREEN][ENABLE_INFO_BUTTON]
        )
        self.screens[KEY_PLAY_FILE] = screen
        self.current_player_screen = KEY_PLAY_FILE
        screen.load_playlist = self.player.load_playlist
        
        self.player.add_player_listener(screen.screen_title.set_text)
        self.player.add_player_listener(screen.time_control.set_track_info)
        self.player.add_player_listener(screen.update_arrow_button_labels)
        self.player.add_end_of_track_listener(screen.end_of_track)
        
        screen.add_play_listener(self.screensaver_dispatcher.change_image)
        screen.add_play_listener(self.screensaver_dispatcher.change_image_folder)

        f = getattr(state, "file_name", None)
        if f == None and state != None:
            state.file_name = self.config[FILE_PLAYBACK][CURRENT_FILE]
            
        self.set_current_screen(KEY_PLAY_FILE, state=state)
        state = State()
        state.cover_art_folder = screen.center_button.state.cover_art_folder
        self.screensaver_dispatcher.change_image_folder(state)
        
        if self.use_web:
            update = self.web_server.update_web_ui
            redraw = self.web_server.redraw_web_ui
            start = self.web_server.start_time_control_to_json
            stop = self.web_server.stop_time_control_to_json
            title_to_json = self.web_server.title_to_json
            screen.add_screen_observers(update, redraw, start, stop, title_to_json)
            self.web_server.add_player_listener(screen.time_control)
            self.player.add_player_listener(self.web_server.update_player_listeners)

    def go_file_info(self, state):
        """ Go to the File Info Screen

        :param state: button state
        """
        try:
            self.screens[KEY_FILE_INFO]
            self.set_current_screen(name=KEY_FILE_INFO, state=state)
            return
        except:
            pass

        labels = [
            self.config[LABELS][GENRE],
            self.config[LABELS][ARTIST],
            self.config[LABELS][ALBUM],
            self.config[LABELS][DATE],
            self.config[LABELS][FILE_SIZE],
            self.config[LABELS][SAMPLE_RATE],
            self.config[LABELS][CHANNELS],
            self.config[LABELS][BITS_PER_SAMPLE],
            self.config[LABELS][BIT_RATE]
        ]
        meta_keys = [
            Player.FILENAME, GENRE, ARTIST, ALBUM, DATE,
            Player.FILESIZE, Player.SAMPLE_RATE, Player.CHANNELS, Player.BITS_PER_SAMPLE, Player.BITRATE
        ]
        units = {
            Player.FILESIZE: self.config[LABELS][BYTES],
            Player.SAMPLE_RATE: self.config[LABELS][HZ],
            Player.BITRATE: self.config[LABELS][KBPS]
        }

        screen = InfoScreen(KEY_FILE_INFO, self.util, self.go_back, labels, meta_keys, units, 14, 4, self.util.get_file_metadata)
        self.screens[KEY_FILE_INFO] = screen
        self.set_current_screen(name=KEY_FILE_INFO, state=state)

        if self.use_web:
            screen.add_screen_observer(self.web_server.redraw_web_ui)

    def go_radio_info(self, state):
        """ Go to the Radio Info Screen

        :param state: button state
        """
        try:
            self.screens[KEY_RADIO_INFO]
            self.set_current_screen(name=KEY_RADIO_INFO, state=state)
            return
        except:
            pass

        labels = [
            self.config[LABELS][GENRE],
            self.config[LABELS][ARTIST],
            self.config[LABELS][SONG],
            self.config[LABELS][SAMPLE_RATE],
            self.config[LABELS][CHANNELS],
            self.config[LABELS][BIT_RATE],
            self.config[LABELS][CODEC]
        ]
        meta_keys = [
            Player.STATION,
            GENRE,
            ARTIST,
            SONG,
            Player.SAMPLE_RATE,
            Player.CHANNELS,
            Player.BITRATE,
            Player.CODEC
        ]
        units = {
            Player.BITRATE: self.config[LABELS][KBPS],
            Player.SAMPLE_RATE: self.config[LABELS][HZ]
        }

        screen = InfoScreen(KEY_RADIO_INFO, self.util, self.go_back, labels, meta_keys, units, 12, 3, self.screens[KEY_STATIONS].get_station_metadata)
        self.screens[KEY_RADIO_INFO] = screen
        self.set_current_screen(name=KEY_RADIO_INFO, state=state)

        if self.use_web:
            screen.add_screen_observer(self.web_server.redraw_web_ui)

    def go_collection_playback(self, state=None):
        """ Go to the Collection Player Screen
        
        :param state: button state
        """
        self.deactivate_current_player(KEY_PLAY_COLLECTION)

        if hasattr(state, "folder") and hasattr(state, "source") and state.source != INIT:
            self.config[COLLECTION_PLAYBACK][COLLECTION_FOLDER] = os.path.join(self.config[COLLECTION][BASE_FOLDER], state.folder)
            self.config[COLLECTION_PLAYBACK][COLLECTION_FILE] = state.file_name
            self.config[COLLECTION_PLAYBACK][COLLECTION_URL] = state.url

        try:
            if self.screens[KEY_PLAY_COLLECTION]:
                if hasattr(state, "name") and (state.name == KEY_HOME or state.name == KEY_BACK or state.name == KEY_PLAYER):
                    self.set_current_screen(KEY_PLAY_COLLECTION, True)
                else:
                    self.set_current_screen(name=KEY_PLAY_COLLECTION, state=state)
                self.current_player_screen = KEY_PLAY_COLLECTION
                return
        except:
            pass

        listeners = self.get_play_screen_listeners()
        listeners[AUDIO_FILES] = self.go_collection_browser
        listeners[KEY_SEEK] = self.player.seek
        screen = CollectionPlayerScreen(listeners, self.util, self.player.get_current_playlist, self.volume_control)
        self.screens[KEY_PLAY_COLLECTION] = screen
        self.current_player_screen = KEY_PLAY_COLLECTION
        screen.load_playlist = self.player.load_playlist
        
        self.player.add_player_listener(screen.screen_title.set_text)
        self.player.add_player_listener(screen.time_control.set_track_info)
        self.player.add_player_listener(screen.update_arrow_button_labels)
        self.player.add_end_of_track_listener(screen.end_of_track)
        
        screen.add_play_listener(self.screensaver_dispatcher.change_image)
        screen.add_play_listener(self.screensaver_dispatcher.change_image_folder)

        self.set_current_screen(KEY_PLAY_COLLECTION, state=state)
        state = State()
        state.cover_art_folder = screen.center_button.state.cover_art_folder
        self.screensaver_dispatcher.change_image_folder(state)
        
        if self.use_web:
            update = self.web_server.update_web_ui
            redraw = self.web_server.redraw_web_ui
            start = self.web_server.start_time_control_to_json
            stop = self.web_server.stop_time_control_to_json
            title_to_json = self.web_server.title_to_json
            screen.add_screen_observers(update, redraw, start, stop, title_to_json)
            self.web_server.add_player_listener(screen.time_control)
            self.player.add_player_listener(self.web_server.update_player_listeners)

    def go_site_playback(self, state=None):
        """ Go to the Site Player Screen
        
        :param state: button state
        """
        self.deactivate_current_player(KEY_PLAY_SITE)
        name = KEY_PLAY_SITE
        s = State()
        s.name = state.name
        s.file_name = getattr(state, FILE_NAME, None)
        a = getattr(state, "source", None)
        if a:
            s.source = a
        else: 
            s.source = INIT
        
        if getattr(state, BOOK_URL, None):
            self.config[AUDIOBOOKS][BROWSER_BOOK_URL] = s.book_url = state.book_url 
        
        try:
            if self.screens[name]:
                if getattr(state, "source", None) == BOOK_MENU:
                    s.name = state.name
                else:
                    s.name = self.config[AUDIOBOOKS][BROWSER_BOOK_TITLE]

                self.set_current_screen(name, state=s)
                self.current_player_screen = name
                return
        except:
            pass

        listeners = self.get_play_screen_listeners()
        listeners[KEY_SEEK] = self.player.seek
        listeners[AUDIO_FILES] = self.go_book_track_screen       
        
        if not getattr(state, BOOK_URL, None):
            self.go_site_news_screen(state)
            return
        
        self.config[AUDIOBOOKS][BROWSER_BOOK_URL] = state.book_url
        if hasattr(state, "img_url"):
            self.config[AUDIOBOOKS][BROWSER_IMAGE_URL] = state.img_url
        self.config[AUDIOBOOKS][BROWSER_BOOK_TITLE] = state.name
        s = BookPlayer(listeners, self.util, self.get_parser(), self.volume_control)
        
        self.player.add_player_listener(s.time_control.set_track_info)            
        self.player.add_player_listener(s.update_arrow_button_labels)
        self.player.add_end_of_track_listener(s.end_of_track)         
        s.add_play_listener(self.screensaver_dispatcher.change_image)

        if self.use_web:
            update = self.web_server.update_web_ui
            redraw = self.web_server.redraw_web_ui
            start = self.web_server.start_time_control_to_json
            stop = self.web_server.stop_time_control_to_json
            title_to_json = self.web_server.title_to_json
            s.add_screen_observers(update, redraw, start, stop, title_to_json)
            self.web_server.add_player_listener(s.time_control)
            self.player.add_player_listener(self.web_server.update_player_listeners)
        
        s.name = name
        state.source = INIT
        self.screens[name] = s
        self.current_player_screen = KEY_PLAY_SITE
        self.set_current_screen(name, state=state) 

    def go_book_track_screen(self, state):
        """ Go to the Book Tracks Screen
        
        :param state: button state
        """
        listeners = self.get_site_navigator_listeners()
        self.exit_current_screen()        
        name = KEY_BOOK_TRACK_SCREEN
        try:
            if self.screens[name]:
                self.set_current_screen(name)
                return
        except:
            pass
        
        d = self.get_book_menu_settings()
        s = BookTrack(self.util, listeners, self.go_site_playback, d)
        ps = self.screens[KEY_PLAY_SITE]
        ps.add_play_listener(s.track_menu.select_track)
        
        self.screens[name] = s
        self.set_current_screen(name)
        
        if self.use_web:
            self.add_screen_observers(s)
    
    def go_site_news_screen(self, state):
        """ Go to the Site New Books Screen
        
        :param state: button state
        """
        listeners = self.get_site_navigator_listeners()
        self.exit_current_screen()        
        name = self.config[AUDIOBOOKS][BROWSER_SITE] + ".new.books.screen"
        try:
            if self.screens[name]:
                self.set_current_screen(name)
                return
        except:
            pass
        
        d = self.get_book_menu_settings()
        parser = self.get_parser()
        parser.news_parser.page_url_prefix = TOP_100
        parser.language_url = d[4]
        s = BookNew(self.util, listeners, self.go_site_playback, parser, d)
        self.screens[name] = s
        self.set_current_screen(name)
        
        if self.use_web:
            self.add_screen_observers(s)
            
        s.turn_page()
    
    def get_book_menu_settings(self, show_author=True, show_genre=True):
        """ Return book menu settings for defined parameters
        
        :param show_author: flag indicating if authors button should be included
        :param show_genre: flag indicating if genre button should be included
        """
        rows = BOOKS_ROWS
        columns = BOOKS_COLUMNS
        show_genre = False
        return [rows, columns, show_author, show_genre, self.get_language_url()]
    
    def go_site_genre_screen(self, state):
        """ Go to the Site Genres Screen
        
        :param state: button state
        """
        site = self.config[AUDIOBOOKS][BROWSER_SITE]
        
        if site + ".genre.screen" == self.current_screen:
            return
              
        name = site + ".genre.books"
        try:
            if self.screens[name] and self.current_screen != name:
                cs = self.screens[name]
                cs.set_current(state) 
                self.set_current_screen(name, state=state)
                return
        except:
            pass
        
        listeners = self.get_site_navigator_listeners()
        self.exit_current_screen()
        name = site + ".genre.screen"
        try:
            if self.screens[name]:
                self.set_current_screen(name)
                return
        except:
            pass
        
        constants = None
        base_url = None
        constants = LOYALBOOKS_GENRE
        base_url = GENRE_URL
        d = self.get_book_menu_settings()    
        s = BookGenre(self.util, listeners, self.go_site_books_by_genre, constants, base_url, d)
        self.screens[name] = s
        self.set_current_screen(name)
        
        if self.use_web:
            self.add_screen_observers(s)

    def go_site_books_by_genre(self, state):
        """ Go to the Genre Books Screen
        
        :param state: button state
        """
        listeners = self.get_site_navigator_listeners()
        self.exit_current_screen()  
        site = self.config[AUDIOBOOKS][BROWSER_SITE]      
        name = site + ".genre.books"
        try:
            if self.screens[name]:                
                self.set_current_screen(name, state=state)                
                cs = self.screens[name]
                cs.set_current(state)                 
                return
        except:
            pass
        
        parser = self.get_parser()
        parser.genre_books_parser.base_url = BASE_URL
        parser.genre_books_parser.page_url_prefix = PAGE_PREFIX
        d = self.get_book_menu_settings(show_genre=False)
        s = BookGenreBooks(self.util, listeners, state.name, self.go_site_playback, state.genre, parser, d)
        self.screens[name] = s
        self.set_current_screen(name)
        
        if self.use_web:
            self.add_screen_observers(s)
            
        s.turn_page() 
    
    def get_site_navigator_listeners(self):
        """ Return site navigator listeners """
        
        listeners = {}
        listeners[GO_USER_HOME] = self.go_site_news_screen
        listeners[GO_ROOT] = self.go_site_news_screen
        listeners[GO_TO_PARENT] = self.go_site_genre_screen
        listeners[GO_PLAYER] = self.go_player
        listeners[GO_BACK] = self.go_back
        listeners[KEY_HOME] = self.go_home
        return listeners 
    
    def get_home_screen_listeners(self):
        """ Return home screen listeners """
        
        listeners = {}
        listeners[KEY_MODE] = self.set_mode
        listeners[KEY_BACK] = self.go_back
        listeners[SCREENSAVER] = self.go_savers
        listeners[LANGUAGE] = self.go_language
        listeners[KEY_PLAYER] = self.go_player
        listeners[KEY_ABOUT] = self.go_about
        listeners[EQUALIZER] = self.go_equalizer
        listeners[TIMER] = self.go_timer
        listeners[NETWORK] = self.go_network
        return listeners

    def get_play_screen_listeners(self):
        """ Player screen listeners getter """
        
        listeners = {}
        listeners[KEY_HOME] = self.go_home
        listeners[KEY_SHUTDOWN] = self.shutdown
        listeners[KEY_PLAY_PAUSE] = self.play_pause
        listeners[KEY_SET_VOLUME] = self.set_volume
        listeners[KEY_SET_CONFIG_VOLUME] = self.set_config_volume
        listeners[KEY_SET_SAVER_VOLUME] = self.screensaver_dispatcher.change_volume
        listeners[KEY_MUTE] = self.mute
        listeners[KEY_PLAY] = self.player.play
        listeners[KEY_STOP] = self.player.stop
        listeners[SCREENSAVER] = self.screensaver_dispatcher.start_screensaver

        if self.config[CURRENT][MODE] == RADIO:
            listeners[KEY_INFO] = self.go_radio_info
        else:
            listeners[KEY_INFO] = self.go_file_info

        return listeners
    
    def go_stream(self, state=None):
        """ Go to the Stream Screen
        
        :param state: button state
        """
        self.deactivate_current_player(STREAM)
        
        stream_player_screen = None
        try:
            stream_player_screen = self.screens[STREAM]    
        except:
            pass

        if stream_player_screen != None:
            stream_player_screen.set_current(state)
            self.get_current_screen(STREAM, state)
            return
        
        listeners = self.get_play_screen_listeners()
        listeners[KEY_GENRES] = self.go_genres
        listeners[KEY_STREAM_BROWSER] = self.go_stream_browser
        stream_player_screen = StreamPlayerScreen(self.util, listeners, self.volume_control)
        stream_player_screen.play()

        self.screens[STREAM] = stream_player_screen
        self.set_current_screen(STREAM, False, state)

        self.player.add_player_listener(stream_player_screen.screen_title.set_text)
        stream_player_screen.add_change_logo_listener(self.screensaver_dispatcher.change_image)
        if self.config[USAGE][USE_ALBUM_ART]:
            self.player.add_player_listener(stream_player_screen.show_album_art) 

        if stream_player_screen.center_button:
            self.screensaver_dispatcher.change_image(stream_player_screen.center_button.state)

        if self.use_web:
            update = self.web_server.update_web_ui
            redraw = self.web_server.redraw_web_ui
            title_to_json = self.web_server.title_to_json
            stream_player_screen.add_screen_observers(update, redraw, title_to_json)

    def go_podcasts(self, state=None):
        """ Go to the Podcasts Screen
        
        :param state: button state
        """
        if self.get_current_screen(PODCASTS): return
        
        try:
            if self.screens[PODCASTS]:
                self.set_current_screen(PODCASTS, state=state)
                return
        except:
            pass
        
        listeners = {}
        listeners[KEY_HOME] = self.go_home
        listeners[KEY_PLAYER] = self.go_podcast_player
        listeners[GO_BACK] = self.go_back
        listeners[KEY_PODCAST_EPISODES] = self.go_podcast_episodes
        podcasts_screen = PodcastsScreen(self.util, listeners)
        self.screens[PODCASTS] = podcasts_screen
        if self.use_web:
            self.add_screen_observers(podcasts_screen)
        self.set_current_screen(PODCASTS)
    
    def go_podcast_episodes(self, state):
        """ Go to the podcast episodes screen
        
        :param state: button state
        """
        url = getattr(state, "podcast_url", None)
               
        if url != None:
            self.config[PODCASTS][PODCAST_URL] = url
            
        try:
            if self.screens[KEY_PODCAST_EPISODES]:
                self.set_current_screen(KEY_PODCAST_EPISODES, state=state)
                return
        except:
            if state and hasattr(state, "name") and len(state.name) == 0:
                self.go_podcasts(state)
                return
        
        listeners = {}
        listeners[KEY_HOME] = self.go_home
        listeners[PODCASTS] = self.go_podcasts
        listeners[GO_BACK] = self.go_back
        listeners[KEY_PLAYER] = self.go_podcast_player
        screen = PodcastEpisodesScreen(self.util, listeners, state)
        self.screens[KEY_PODCAST_EPISODES] = screen
        
        podcast_player = self.screens[KEY_PODCAST_PLAYER]
        podcast_player.add_play_listener(screen.turn_page)
        if self.use_web:
            self.add_screen_observers(screen)
        self.set_current_screen(KEY_PODCAST_EPISODES, state=state)

    def go_podcast_player(self, state):
        """ Go to the podcast player screen
        
        :param state: button state
        """
        self.deactivate_current_player(KEY_PODCAST_PLAYER)
        try:
            if self.screens[KEY_PODCAST_PLAYER]:
                if getattr(state, "name", None) and (state.name == KEY_HOME or state.name == KEY_BACK):
                    self.set_current_screen(KEY_PODCAST_PLAYER)
                else:
                    if getattr(state, "source", None) == None:                    
                        state.source = RESUME
                    self.set_current_screen(name=KEY_PODCAST_PLAYER, state=state)
                self.current_player_screen = KEY_PODCAST_PLAYER
                return
        except:
            pass
        
        if state.name != PODCASTS:
            self.config[PODCASTS][PODCAST_EPISODE_NAME] = state.name
            
        if hasattr(state, "file_name"):
            self.config[PODCASTS][PODCAST_EPISODE_URL] = state.file_name
        elif hasattr(state, "url"):
            self.config[PODCASTS][PODCAST_EPISODE_URL] = state.url
        
        listeners = self.get_play_screen_listeners()
        listeners[AUDIO_FILES] = self.go_podcast_episodes
        listeners[KEY_SEEK] = self.player.seek
        screen = PodcastPlayerScreen(listeners, self.util, self.player.get_current_playlist, self.volume_control)
        self.screens[KEY_PODCAST_PLAYER] = screen
        screen.load_playlist = self.player.load_playlist
        
        self.player.add_player_listener(screen.time_control.set_track_info)
        self.player.add_player_listener(screen.update_arrow_button_labels)
        self.player.add_end_of_track_listener(screen.end_of_track)
        
        screen.add_play_listener(self.screensaver_dispatcher.change_image)
        screen.add_play_listener(self.screensaver_dispatcher.change_image_folder)
        
        self.set_current_screen(KEY_PODCAST_PLAYER, state=state)
        self.current_player_screen = KEY_PODCAST_PLAYER
        state = State()
        state.cover_art_folder = screen.center_button.state.cover_art_folder
        self.screensaver_dispatcher.change_image_folder(state)
        
        if self.use_web:
            update = self.web_server.update_web_ui
            redraw = self.web_server.redraw_web_ui
            start = self.web_server.start_time_control_to_json
            stop = self.web_server.stop_time_control_to_json
            title_to_json = self.web_server.title_to_json
            screen.add_screen_observers(update, redraw, start, stop, title_to_json)
            screen.add_loading_listener(redraw)
            self.web_server.add_player_listener(screen.time_control)
            self.player.add_player_listener(self.web_server.update_player_listeners)

    def go_ya_stream(self, state):
        """ Go to the YA Stream Screen

        :param state: button state
        """
        if self.config.get(KEY_YA_STREAM_CURRENT_PLAYER, None) == KEY_YA_SEARCH_PLAYER:
            self.go_ya_search_player(state)
            return
        elif self.config.get(KEY_YA_STREAM_CURRENT_PLAYER, None) == KEY_YA_PLAYLIST_PLAYER:
            self.go_ya_playlist_player(state)
            return

        if self.get_current_screen(KEY_YA_STREAM): return

        listeners = {}
        listeners[KEY_HOME] = self.go_home
        listeners[KEY_BACK] = self.go_back
        listeners[KEY_PLAYER] = self.go_player
        listeners[KEY_SEARCH_BY_NAME] = self.go_ya_search_browser
        listeners[KEY_PLAYLISTS] = self.go_ya_playlist_browser

        ya_stream_screen = YaStreamScreen(self.util, listeners)
        self.screens[KEY_YA_STREAM] = ya_stream_screen
        self.set_current_screen(KEY_YA_STREAM)

        if self.use_web:
            self.add_screen_observers(ya_stream_screen)

    def go_ya_search_keyboard(self, state=None, max_text_length=64, min_text_length=0):
        """ Go to the Keyboard Screen

        :param state: button state
        :param max_text_length: maximum text length
        """
        s = self.get_current_screen(KEY_SEARCH_YA_STREAM_KEYBOARD)
        if state:
            search_by = getattr(state, "search_by", None)
        else:
            search_by = None
        if s:
            title = getattr(state, "title", None)
            if title and title != s.screen_title.text:
                s.screen_title.set_text(title)
                s.input_text.set_text("")
                s.keyboard.text = ""
                s.keyboard.search_by = search_by
                s.keyboard.callback = state.callback
            return

        listeners = {}
        listeners[KEY_HOME] = self.go_home
        listeners[KEY_PLAYER] = self.go_ya_playlist_player
        listeners[KEY_BACK] = self.go_back
        listeners[KEY_CALLBACK] = state.callback
        title = self.config[LABELS][KEY_ENTER_QUERY]
        keyboard_screen = KeyboardScreen(title, self.util, listeners, False, max_text_length=max_text_length, min_text_length=min_text_length, search_by=search_by)
        self.screens[KEY_SEARCH_YA_STREAM_KEYBOARD] = keyboard_screen

        if self.use_web:
            self.add_screen_observers(keyboard_screen)

        self.set_current_screen(KEY_SEARCH_YA_STREAM_KEYBOARD)

    def go_ya_search_browser(self, state):
        """ Go to the YA Stream Browser Screen

        :param state: button state
        """
        if self.screens.get(KEY_YA_STREAM_SEARCH_BROWSER, None) == None:
            if getattr(state, KEY_CALLBACK_VAR, None) == None or getattr(state, "source", None) == KEY_SEARCH_BY_NAME:
                state.callback = self.go_ya_search_browser
                self.go_ya_search_keyboard(state)
                return

        if self.get_current_screen(KEY_YA_STREAM_SEARCH_BROWSER, state=state):
            return

        listeners = {}
        listeners[KEY_HOME] = self.go_home
        listeners[KEY_PLAYLISTS] = self.go_ya_playlist_browser
        listeners[KEY_SEARCH_YA_STREAM_KEYBOARD] = self.go_ya_search_keyboard
        listeners[KEY_CALLBACK] = self.go_ya_search_browser
        listeners[KEY_PLAYER] = self.go_player
        listeners[YA_STREAM] = self.go_ya_search_player

        stream_browser_screen = YaSearchScreen(self.util, listeners)
        self.screens[KEY_YA_STREAM_SEARCH_BROWSER] = stream_browser_screen
        stream_browser_screen.go_player = self.go_ya_search_player

        if self.use_web:
            self.add_screen_observers(stream_browser_screen)
            redraw = self.web_server.redraw_web_ui
            stream_browser_screen.add_loading_listener(redraw)

        self.set_current_screen(KEY_YA_STREAM_SEARCH_BROWSER, state=state)

    def go_ya_search_player(self, state):
        """ Go to the YA Search player screen

        :param state: button state
        """
        self.deactivate_current_player(KEY_YA_SEARCH_PLAYER)

        try:
            if self.screens[KEY_YA_SEARCH_PLAYER]:
                if getattr(state, "name", None) and (state.name == KEY_HOME or state.name == KEY_BACK):
                    self.set_current_screen(KEY_YA_SEARCH_PLAYER)
                else:
                    source = getattr(state, "source", None)
                    if source == None or self.current_player_screen != KEY_YA_SEARCH_PLAYER:
                        if source != KEY_YA_STREAM_SEARCH_BROWSER:
                            state.source = RESUME
                    self.set_current_screen(name=KEY_YA_SEARCH_PLAYER, state=state)
                self.current_player_screen = KEY_YA_SEARCH_PLAYER
                return
        except:
            pass

        listeners = self.get_play_screen_listeners()
        listeners[AUDIO_FILES] = self.go_ya_search_browser
        listeners[KEY_SEEK] = self.player.seek
        screen = YaSearchPlayerScreen(listeners, self.util, self.player.get_current_playlist, self.volume_control)
        self.screens[KEY_YA_SEARCH_PLAYER] = screen
        screen.load_playlist = self.player.load_playlist

        if self.screens.get(KEY_YA_STREAM_SEARCH_BROWSER, None):
            browser_screen =  self.screens[KEY_YA_STREAM_SEARCH_BROWSER]
            screen.add_track_change_listener(browser_screen.handle_track_change)

        self.player.add_player_listener(screen.time_control.set_track_info)
        self.player.add_player_listener(screen.update_arrow_button_labels)
        self.player.add_end_of_track_listener(screen.end_of_track)

        screen.add_play_listener(self.screensaver_dispatcher.change_image)
        screen.add_play_listener(self.screensaver_dispatcher.change_image_folder)

        if self.use_web:
            update = self.web_server.update_web_ui
            redraw = self.web_server.redraw_web_ui
            start = self.web_server.start_time_control_to_json
            stop = self.web_server.stop_time_control_to_json
            title_to_json = self.web_server.title_to_json
            screen.add_screen_observers(update, redraw, start, stop, title_to_json)
            screen.add_loading_listener(redraw)
            self.web_server.add_player_listener(screen.time_control)
            self.player.add_player_listener(self.web_server.update_player_listeners)

        self.set_current_screen(KEY_YA_SEARCH_PLAYER, state=state)
        self.current_player_screen = KEY_YA_SEARCH_PLAYER

    def go_ya_playlist_browser(self, state):
        """ Go to the YA Stream Browser Screen

        :param state: button state
        """
        if self.get_current_screen(KEY_YA_STREAM_PLAYLIST_BROWSER, state=state):
            return

        listeners = {}
        listeners[KEY_HOME] = self.go_home
        listeners[KEY_YA_STREAM_SEARCH_BROWSER] = self.go_ya_search_browser
        listeners[KEY_PLAYER] = self.go_player
        listeners[YA_STREAM] = self.go_ya_playlist_player

        stream_browser_screen = YaPlaylistScreen(self.util, listeners)
        self.screens[KEY_YA_STREAM_PLAYLIST_BROWSER] = stream_browser_screen
        stream_browser_screen.go_player = self.go_ya_playlist_player
        self.set_current_screen(KEY_YA_STREAM_PLAYLIST_BROWSER)

        if self.use_web:
            self.add_screen_observers(stream_browser_screen)

    def go_ya_playlist_player(self, state):
        """ Go to the YA Stream player screen

        :param state: button state
        """
        self.deactivate_current_player(KEY_YA_PLAYLIST_PLAYER)

        try:
            if self.screens[KEY_YA_PLAYLIST_PLAYER]:
                if getattr(state, "name", None) and (state.name == KEY_HOME or state.name == KEY_BACK):
                    self.set_current_screen(KEY_YA_PLAYLIST_PLAYER)
                else:
                    if getattr(state, "source", None) == None or self.current_player_screen != KEY_YA_PLAYLIST_PLAYER:
                        state.source = RESUME
                    self.set_current_screen(name=KEY_YA_PLAYLIST_PLAYER, state=state)
                self.current_player_screen = KEY_YA_PLAYLIST_PLAYER
                return
        except:
            pass

        listeners = self.get_play_screen_listeners()
        listeners[AUDIO_FILES] = self.go_ya_playlist_browser
        listeners[KEY_SEEK] = self.player.seek
        screen = YaPlaylistPlayerScreen(listeners, self.util, self.player.get_current_playlist, self.volume_control)
        self.screens[KEY_YA_PLAYLIST_PLAYER] = screen
        screen.load_playlist = self.player.load_playlist

        self.player.add_player_listener(screen.time_control.set_track_info)
        self.player.add_player_listener(screen.update_arrow_button_labels)
        self.player.add_end_of_track_listener(screen.end_of_track)

        screen.add_play_listener(self.screensaver_dispatcher.change_image)
        screen.add_play_listener(self.screensaver_dispatcher.change_image_folder)

        state.source = INIT
        state.id = self.config[YA_STREAM][YA_STREAM_ID]

        if self.use_web:
            update = self.web_server.update_web_ui
            redraw = self.web_server.redraw_web_ui
            start = self.web_server.start_time_control_to_json
            stop = self.web_server.stop_time_control_to_json
            title_to_json = self.web_server.title_to_json
            screen.add_screen_observers(update, redraw, start, stop, title_to_json)
            screen.add_loading_listener(redraw)
            self.web_server.add_player_listener(screen.time_control)
            self.player.add_player_listener(self.web_server.update_player_listeners)

        self.set_current_screen(KEY_YA_PLAYLIST_PLAYER, state=state)
        self.current_player_screen = KEY_YA_PLAYLIST_PLAYER

    def go_jukebox(self, state):
        """ Go to the Jukebox screen

        :param state: button state
        """
        if self.get_current_screen(KEY_JUKEBOX_BROWSER, state=state):
            return

        listeners = {
            KEY_HOME: self.go_home,
            KEY_SHUTDOWN: self.shutdown,
            KEY_MUTE: self.mute,
            KEY_VOLUME_DOWN: self.volume_down,
            KEY_VOLUME_UP: self.volume_up
        }
        screen = JukeboxBrowserScreen(self.util, listeners, self.player)
        self.screens[KEY_JUKEBOX_BROWSER] = screen
        self.set_current_screen(KEY_JUKEBOX_BROWSER)

        if self.use_web:
            self.add_screen_observers(screen)

    def go_audiobooks(self, state=None):
        """ Go to the Audiobooks Screen
        
        :param state: button state
        """
        listeners = self.get_play_screen_listeners()
        listeners[KEY_SEEK] = self.player.seek        
        self.exit_current_screen()
        s = State()
        s.source = INIT
        s.book_url = self.config[AUDIOBOOKS][BROWSER_BOOK_URL]
        s.img_url = self.config[AUDIOBOOKS][BROWSER_IMAGE_URL]
        s.name = self.config[AUDIOBOOKS][BROWSER_BOOK_TITLE]
        self.config[AUDIOBOOKS][BROWSER_SITE] = LOYALBOOKS
        s.language_url = self.get_language_url()
        state = State()
        self.screensaver_dispatcher.change_image_folder(state)
        
        try:
            s.source = RESUME
            if getattr(state, "file_name", None) == None:
                s.file_name = self.config[AUDIOBOOKS][BROWSER_TRACK_FILENAME]
        except:
            pass
            
        if not self.config[AUDIOBOOKS][BROWSER_BOOK_URL]:
            self.go_site_news_screen(s)
            self.current_player_screen = None
        else:
            self.go_site_playback(s)
    
    def go_airplay(self, state=None):
        """ Go airplay screen

        :param state: button state
        """
        self.deactivate_current_player(KEY_AIRPLAY_PLAYER)
        try:
            if self.screens[KEY_AIRPLAY_PLAYER]:
                self.player.add_player_listener(self.screens[KEY_AIRPLAY_PLAYER].handle_metadata)
                if getattr(state, "name", None) and (state.name == KEY_HOME or state.name == KEY_BACK):
                    self.set_current_screen(KEY_AIRPLAY_PLAYER)
                else:
                    if getattr(state, "source", None) == None:
                        state.source = RESUME
                    self.set_current_screen(name=KEY_AIRPLAY_PLAYER, state=state)
                self.current_player_screen = KEY_AIRPLAY_PLAYER
                return
        except:
            pass

        listeners = self.get_play_screen_listeners()
        next = getattr(self.player, "next", None)
        previous = getattr(self.player, "previous", None)
        d = self.screensaver_dispatcher.change_image
        screen = AirplayPlayerScreen(listeners, self.util, self.player.get_current_playlist, self.volume_control, d, next, previous)
        self.player.add_player_listener(screen.handle_metadata)
        screen.play_button.add_listener("pause", self.player.pause)
        screen.play_button.add_listener("play", self.player.play)

        self.screens[KEY_AIRPLAY_PLAYER] = screen
        self.set_current_screen(KEY_AIRPLAY_PLAYER, state=state)

        if self.use_web:
            update = self.web_server.update_web_ui
            redraw = self.web_server.redraw_web_ui
            title_to_json = self.web_server.title_to_json
            screen.add_screen_observers(update, redraw, None, None, title_to_json)
            screen.add_loading_listener(redraw)
            self.player.add_player_listener(self.web_server.update_player_listeners)

        screen.custom_button.start_listeners = []
        screen.custom_button.label_listeners = []
        screen.custom_button.press_listeners = []
        screen.custom_button.release_listeners = []

        screen.center_button.label_listeners = []
        screen.center_button.press_listeners = []
        screen.center_button.release_listeners = []

    def go_spotify_connect(self, state=None):
        """ Go spotify connect screen

        :param state: button state
        """
        self.deactivate_current_player(KEY_SPOTIFY_CONNECT_PLAYER)
        try:
            if self.screens[KEY_SPOTIFY_CONNECT_PLAYER]:
                if getattr(state, "name", None) and (state.name == KEY_HOME or state.name == KEY_BACK):
                    self.set_current_screen(KEY_SPOTIFY_CONNECT_PLAYER)
                else:
                    if getattr(state, "source", None) == None:
                        state.source = RESUME
                    self.set_current_screen(name=KEY_SPOTIFY_CONNECT_PLAYER, state=state)
                self.current_player_screen = KEY_SPOTIFY_CONNECT_PLAYER
                return
        except:
            pass

        listeners = self.get_player_screen_disabled_listeners()

        screen = SpotifyConnectScreen(listeners, self.util, self.volume_control)
        self.screens[KEY_SPOTIFY_CONNECT_PLAYER] = screen
        self.set_current_screen(KEY_SPOTIFY_CONNECT_PLAYER, state=state)

        if self.use_web:
            update = self.web_server.update_web_ui
            redraw = self.web_server.redraw_web_ui
            screen.add_screen_observers(update, redraw, None, None, None)
            screen.add_loading_listener(redraw)
            self.player.add_player_listener(self.web_server.update_player_listeners)

        self.disable_player_screen_buttons(screen)

    def go_archive(self, state):
        """ Go to the Archive player screen

        :param state: button state
        """
        self.deactivate_current_player(KEY_ARCHIVE_PLAYER)

        try:
            if self.screens[KEY_ARCHIVE_PLAYER]:
                if getattr(state, "name", None) and (state.name == KEY_HOME or state.name == KEY_BACK):
                    self.set_current_screen(KEY_ARCHIVE_PLAYER)
                else:
                    if getattr(state, "source", None) == None or self.current_player_screen != KEY_ARCHIVE_PLAYER:
                        state.source = RESUME
                    self.set_current_screen(name=KEY_ARCHIVE_PLAYER, state=state)
                self.current_player_screen = KEY_ARCHIVE_PLAYER
                return
        except:
            pass

        listeners = self.get_play_screen_listeners()
        listeners[AUDIO_FILES] = self.go_archive_files_browser
        listeners[KEY_SEEK] = self.player.seek
        screen = ArchivePlayerScreen(listeners, self.util, self.volume_control)
        self.screens[KEY_ARCHIVE_PLAYER] = screen
        screen.load_playlist = self.player.load_playlist

        self.player.add_player_listener(screen.time_control.set_track_info)
        self.player.add_player_listener(screen.update_arrow_button_labels)
        self.player.add_end_of_track_listener(screen.end_of_track)

        screen.add_play_listener(self.screensaver_dispatcher.change_image)
        screen.add_play_listener(self.screensaver_dispatcher.change_image_folder)

        state.item = self.config[ARCHIVE][ITEM]
        state.file = self.config[ARCHIVE][FILE]
        state.file_time = self.config[ARCHIVE][FILE_TIME]
        state.source = INIT

        self.set_current_screen(KEY_ARCHIVE_PLAYER, state=state)
        self.current_player_screen = KEY_ARCHIVE_PLAYER

        if self.use_web:
            update = self.web_server.update_web_ui
            redraw = self.web_server.redraw_web_ui
            start = self.web_server.start_time_control_to_json
            stop = self.web_server.stop_time_control_to_json
            title_to_json = self.web_server.title_to_json
            screen.add_screen_observers(update, redraw, start, stop, title_to_json)
            screen.add_loading_listener(redraw)
            self.web_server.add_player_listener(screen.time_control)
            self.player.add_player_listener(self.web_server.update_player_listeners)

    def get_player_screen_disabled_listeners(self):
        """ Get disabled listeners for such screens as Spotify-Connect and Bluetooth Sink

        :return: the dictionary with disabled player screen listeners except home and shutdown
        """
        listeners = {}

        listeners[KEY_HOME] = self.go_home
        listeners[KEY_SHUTDOWN] = self.shutdown
        listeners[KEY_PLAY_PAUSE] = None
        listeners[KEY_STOP] = None
        listeners[SCREENSAVER] = None
        listeners[KEY_SET_VOLUME] = None
        listeners[KEY_SET_CONFIG_VOLUME] = None
        listeners[KEY_SET_SAVER_VOLUME] = None
        listeners[KEY_MUTE] = None
        listeners[KEY_PLAY] = None

        return listeners

    def disable_player_screen_buttons(self, screen):
        """ Disable player screen buttons

        :param screen: the player screen
        """
        screen.play_button.start_listeners = []
        screen.play_button.press_listeners = []
        screen.play_button.release_listeners = []

        screen.custom_button.start_listeners = []
        screen.custom_button.label_listeners = []
        screen.custom_button.press_listeners = []
        screen.custom_button.release_listeners = []

        screen.left_button.label_listeners = []
        screen.left_button.press_listeners = []
        screen.left_button.release_listeners = []

        screen.right_button.label_listeners = []
        screen.right_button.press_listeners = []
        screen.right_button.release_listeners = []

        screen.center_button.label_listeners = []
        screen.center_button.press_listeners = []
        screen.center_button.release_listeners = []

        screen.volume = None

    def go_bluetooth_sink(self, state=None):
        """ Go Bluetooth Sink screen

        :param state: button state
        """
        self.deactivate_current_player(KEY_BLUETOOTH_SINK_PLAYER)

        try:
            if self.screens[KEY_BLUETOOTH_SINK_PLAYER]:
                if getattr(state, "name", None) and (state.name == KEY_HOME or state.name == KEY_BACK):
                    self.set_current_screen(KEY_BLUETOOTH_SINK_PLAYER)
                else:
                    if getattr(state, "source", None) == None:
                        state.source = RESUME
                    self.set_current_screen(name=KEY_BLUETOOTH_SINK_PLAYER, state=state)
                self.current_player_screen = KEY_BLUETOOTH_SINK_PLAYER
                return
        except:
            pass

        listeners = self.get_player_screen_disabled_listeners()

        screen = BluetoothSinkScreen(listeners, self.util, self.volume_control)
        self.screens[KEY_BLUETOOTH_SINK_PLAYER] = screen
        self.set_current_screen(KEY_BLUETOOTH_SINK_PLAYER, state=state)

        if self.use_web:
            update = self.web_server.update_web_ui
            redraw = self.web_server.redraw_web_ui
            screen.add_screen_observers(update, redraw, None, None, None)
            screen.add_loading_listener(redraw)
            self.player.add_player_listener(self.web_server.update_player_listeners)

        self.disable_player_screen_buttons(screen)

    def go_collection(self, state):
        """ Go to the Collection Screen
        
        :param state: button state
        """
        url = self.config[COLLECTION_PLAYBACK][COLLECTION_URL]
        source = getattr(state, "source", None)        
        if url and source != KEY_NAVIGATOR:
            state = State()
            state.topic = self.config[COLLECTION_PLAYBACK][COLLECTION_TOPIC]
            state.folder = self.config[COLLECTION_PLAYBACK][COLLECTION_FOLDER]
            state.file_name = self.config[COLLECTION_PLAYBACK][COLLECTION_FILE]
            state.url = self.config[COLLECTION_PLAYBACK][COLLECTION_URL]
            state.track_time = self.config[COLLECTION_PLAYBACK][COLLECTION_TRACK_TIME]
            self.go_collection_playback(state)
            return
        
        if self.get_current_screen(COLLECTION): return

        listeners = {}
        listeners[KEY_HOME] = self.go_home
        listeners[KEY_BACK] = self.go_back
        listeners[KEY_PLAYER] = self.go_player
        listeners[COLLECTION] = self.go_topic

        collection_screen = CollectionScreen(self.util, listeners)
        self.screens[COLLECTION] = collection_screen
        self.set_current_screen(COLLECTION)
        
        if self.use_web:
            self.add_screen_observers(collection_screen)

    def stop_catalog_playback(self, new_mode):
        """ Stop current catalog player

        :param new_mode: new catalog mode
        """
        if new_mode == self.config.get(KEY_CURRENT_CATALOG_MODE, None):
            return

        current_player = getattr(self, "current_player_screen", None)
        if current_player != None and "catalog" in current_player:
            catalog_player_screen = self.screens.get(self.current_player_screen, None)
            if catalog_player_screen:
                catalog_player_screen.stop()

    def go_catalog(self, state):
        """ Go to the Catalog Screen

        :param state: button state
        """
        if self.get_current_screen(KEY_CATALOG): return

        listeners = {}
        listeners[KEY_HOME] = self.go_home
        listeners[KEY_BACK] = self.go_back
        listeners[KEY_PLAYER] = self.go_player
        listeners[KEY_CATALOG_NEW_ALBUMS] = self.go_catalog_new_release_albums
        listeners[KEY_CATALOG_BESTSELLERS] = self.go_catalog_bestseller_albums
        listeners[KEY_CATALOG_GENRES] = self.go_catalog_genres
        listeners[KEY_CATALOG_ARTISTS] = self.go_catalog_search_artist
        listeners[KEY_CATALOG_ALBUMS] = self.go_catalog_search_album
        listeners[KEY_CATALOG_TRACK] = self.go_catalog_search_track

        catalog_screen = CatalogScreen(self.util, listeners)
        self.screens[KEY_CATALOG] = catalog_screen
        self.set_current_screen(KEY_CATALOG)

        if self.use_web:
            self.add_screen_observers(catalog_screen)

    def go_catalog_new_release_albums(self, state):
        """ Go to the Catalog New Release Albums Screen

        :param state: button state
        """
        state.source = KEY_CATALOG_NEW_ALBUMS
        self.stop_catalog_playback(KEY_CATALOG_NEW_ALBUMS)
        self.config[KEY_CURRENT_CATALOG_MODE] = KEY_CATALOG_NEW_ALBUMS

        setattr(state, KEY_CATALOG_SERVICE, (KEY_CATALOG_ALBUM_SERVICE, SERVICE_QOBUZ))

        if self.get_current_screen(KEY_CATALOG_NEW_ALBUMS, state=state): return

        listeners = {}
        listeners[KEY_HOME] = self.go_home
        listeners[KEY_BACK] = self.go_back
        listeners[KEY_PLAYER] = self.go_catalog_new_release_player
        listeners[KEY_CATALOG] = self.go_catalog
        listeners[KEY_DETAILS] = self.go_catalog_new_release_tracks

        release_screen = CatalogBase(self.util, KEY_CATALOG_NEW_ALBUMS, listeners, self.config[LABELS][KEY_NEW_ALBUMS])
        self.screens[KEY_CATALOG_NEW_ALBUMS] = release_screen

        if self.use_web:
            self.add_screen_observers(release_screen)
            redraw = self.web_server.redraw_web_ui
            release_screen.add_loading_listener(redraw)

        self.set_current_screen(KEY_CATALOG_NEW_ALBUMS)

    def go_catalog_new_release_tracks(self, state):
        """ Go to the Catalog Album Tracks Screen

        :param state: button state
        """
        setattr(state, KEY_CATALOG_SERVICE, (KEY_CATALOG_TRACK_SERVICE, SERVICE_QOBUZ))

        if self.get_current_screen(KEY_CATALOG_NEW_RELEASE_TRACKS, state=state): return

        listeners = {}
        listeners[KEY_HOME] = self.go_home
        listeners[KEY_BACK] = self.go_back
        listeners[KEY_PLAYER] = self.go_catalog_new_release_player
        listeners[KEY_CATALOG] = self.go_catalog
        listeners[KEY_DETAILS] = self.go_catalog_new_release_player

        custom_nav_button = ("album", self.go_catalog_new_release_albums)
        release_screen = CatalogAlbumTracks(self.util, KEY_CATALOG_NEW_RELEASE_TRACKS, listeners, state.name, custom_nav_button)
        self.screens[KEY_CATALOG_NEW_RELEASE_TRACKS] = release_screen

        if self.use_web:
            self.add_screen_observers(release_screen)
            redraw = self.web_server.redraw_web_ui
            release_screen.add_loading_listener(redraw)

        self.set_current_screen(KEY_CATALOG_NEW_RELEASE_TRACKS, state=state)

    def go_catalog_new_release_player(self, state):
        """ Go to the Catalog New Release player screen

        :param state: button state
        """
        if getattr(state, "source", None) == None:
            return

        if self.current_player_screen != KEY_CATALOG_NEW_RELEASE_PLAYER:
            self.deactivate_current_player(KEY_CATALOG_NEW_RELEASE_PLAYER)

        try:
            if self.screens[KEY_CATALOG_NEW_RELEASE_PLAYER]:
                if getattr(state, "name", None) and (state.name == KEY_HOME or state.name == KEY_BACK):
                    self.set_current_screen(KEY_CATALOG_NEW_RELEASE_PLAYER)
                else:
                    if getattr(state, "source", None) == None:
                        state.source = RESUME
                    self.set_current_screen(name=KEY_CATALOG_NEW_RELEASE_PLAYER, state=state)
                self.current_player_screen = KEY_CATALOG_NEW_RELEASE_PLAYER
                return
        except:
            pass

        listeners = self.get_play_screen_listeners()
        listeners[KEY_CATALOG_TRACK] = self.go_catalog_new_release_tracks
        listeners[KEY_SEEK] = self.player.seek
        listeners[AUDIO_FILES] = self.go_catalog_new_release_tracks
        listeners[YA_STREAM] = self.go_ya_search_browser
        screen = CatalogPlayerScreen(listeners, self.util, self.volume_control)
        self.screens[KEY_CATALOG_NEW_RELEASE_PLAYER] = screen

        if self.screens.get(KEY_CATALOG_NEW_RELEASE_TRACKS, None):
            tracks_screen =  self.screens[KEY_CATALOG_NEW_RELEASE_TRACKS]
            screen.add_track_change_listener(tracks_screen.handle_track_change)
            tracks_screen.add_album_change_listener(screen.stop)

        self.player.add_player_listener(screen.time_control.set_track_info)
        self.player.add_player_listener(screen.update_arrow_button_labels)
        self.player.add_end_of_track_listener(screen.end_of_track)

        screen.add_play_listener(self.screensaver_dispatcher.change_image)
        screen.add_play_listener(self.screensaver_dispatcher.change_image_folder)

        self.set_current_screen(KEY_CATALOG_NEW_RELEASE_PLAYER, state=state)
        self.current_player_screen = KEY_CATALOG_NEW_RELEASE_PLAYER

        if self.use_web:
            update = self.web_server.update_web_ui
            redraw = self.web_server.redraw_web_ui
            start = self.web_server.start_time_control_to_json
            stop = self.web_server.stop_time_control_to_json
            title_to_json = self.web_server.title_to_json
            screen.add_screen_observers(update, redraw, start, stop, title_to_json)
            screen.add_loading_listener(redraw)
            self.web_server.add_player_listener(screen.time_control)
            self.player.add_player_listener(self.web_server.update_player_listeners)

    def go_catalog_bestseller_albums(self, state):
        """ Go to the Catalog Bestseller Albums Screen

        :param state: button state
        """
        state.source = KEY_CATALOG_BESTSELLERS
        self.stop_catalog_playback(KEY_CATALOG_BESTSELLERS)
        self.config[KEY_CURRENT_CATALOG_MODE] = KEY_CATALOG_BESTSELLERS

        setattr(state, KEY_CATALOG_SERVICE, (KEY_CATALOG_ALBUM_SERVICE, SERVICE_QOBUZ))

        if self.get_current_screen(KEY_CATALOG_BESTSELLERS, state=state): return

        listeners = {}
        listeners[KEY_HOME] = self.go_home
        listeners[KEY_BACK] = self.go_back
        listeners[KEY_PLAYER] = self.go_catalog_bestseller_player
        listeners[KEY_CATALOG] = self.go_catalog
        listeners[KEY_DETAILS] = self.go_catalog_bestseller_tracks

        bestsellers = CatalogBase(self.util, KEY_CATALOG_BESTSELLERS, listeners, self.config[LABELS][KEY_BESTSELLERS])
        self.screens[KEY_CATALOG_BESTSELLERS] = bestsellers

        if self.use_web:
            self.add_screen_observers(bestsellers)
            redraw = self.web_server.redraw_web_ui
            bestsellers.add_loading_listener(redraw)

        self.set_current_screen(KEY_CATALOG_BESTSELLERS)

    def go_catalog_bestseller_tracks(self, state):
        """ Go to the Catalog Album Tracks Screen

        :param state: button state
        """
        setattr(state, KEY_CATALOG_SERVICE, (KEY_CATALOG_TRACK_SERVICE, SERVICE_QOBUZ))

        if self.get_current_screen(KEY_CATALOG_BESTSELLER_TRACKS, state=state): return

        listeners = {}
        listeners[KEY_HOME] = self.go_home
        listeners[KEY_BACK] = self.go_back
        listeners[KEY_PLAYER] = self.go_catalog_bestseller_player
        listeners[KEY_CATALOG] = self.go_catalog
        listeners[KEY_DETAILS] = self.go_catalog_bestseller_player

        custom_nav_button = ("album", self.go_catalog_bestseller_albums)
        release_screen = CatalogAlbumTracks(self.util, KEY_CATALOG_BESTSELLER_TRACKS, listeners, state.name, custom_nav_button)
        self.screens[KEY_CATALOG_BESTSELLER_TRACKS] = release_screen

        if self.use_web:
            self.add_screen_observers(release_screen)
            redraw = self.web_server.redraw_web_ui
            release_screen.add_loading_listener(redraw)

        self.set_current_screen(KEY_CATALOG_BESTSELLER_TRACKS, state=state)

    def go_catalog_bestseller_player(self, state):
        """ Go to the Catalog New Release player screen

        :param state: button state
        """
        if getattr(state, "source", None) == None:
            return

        if self.current_player_screen != KEY_CATALOG_BESTSELLER_PLAYER:
            self.deactivate_current_player(KEY_CATALOG_BESTSELLER_PLAYER)

        try:
            if self.screens[KEY_CATALOG_BESTSELLER_PLAYER]:
                if getattr(state, "name", None) and (state.name == KEY_HOME or state.name == KEY_BACK):
                    self.set_current_screen(KEY_CATALOG_BESTSELLER_PLAYER)
                else:
                    if getattr(state, "source", None) == None:
                        state.source = RESUME
                    self.set_current_screen(name=KEY_CATALOG_BESTSELLER_PLAYER, state=state)
                self.current_player_screen = KEY_CATALOG_BESTSELLER_PLAYER
                return
        except:
            pass

        listeners = self.get_play_screen_listeners()
        listeners[KEY_CATALOG_TRACK] = self.go_catalog_bestseller_tracks
        listeners[KEY_SEEK] = self.player.seek
        listeners[AUDIO_FILES] = self.go_catalog_bestseller_tracks
        listeners[YA_STREAM] = self.go_ya_search_browser
        screen = CatalogPlayerScreen(listeners, self.util, self.volume_control)
        self.screens[KEY_CATALOG_BESTSELLER_PLAYER] = screen

        if self.screens.get(KEY_CATALOG_BESTSELLER_TRACKS, None):
            tracks_screen =  self.screens[KEY_CATALOG_BESTSELLER_TRACKS]
            screen.add_track_change_listener(tracks_screen.handle_track_change)
            tracks_screen.add_album_change_listener(screen.stop)

        self.player.add_player_listener(screen.time_control.set_track_info)
        self.player.add_player_listener(screen.update_arrow_button_labels)
        self.player.add_end_of_track_listener(screen.end_of_track)

        screen.add_play_listener(self.screensaver_dispatcher.change_image)
        screen.add_play_listener(self.screensaver_dispatcher.change_image_folder)

        self.set_current_screen(KEY_CATALOG_BESTSELLER_PLAYER, state=state)
        self.current_player_screen = KEY_CATALOG_BESTSELLER_PLAYER

        if self.use_web:
            update = self.web_server.update_web_ui
            redraw = self.web_server.redraw_web_ui
            start = self.web_server.start_time_control_to_json
            stop = self.web_server.stop_time_control_to_json
            title_to_json = self.web_server.title_to_json
            screen.add_screen_observers(update, redraw, start, stop, title_to_json)
            screen.add_loading_listener(redraw)
            self.web_server.add_player_listener(screen.time_control)
            self.player.add_player_listener(self.web_server.update_player_listeners)

    def go_catalog_genres(self, state):
        """ Go to the Catalog Genres Screen

        :param state: button state
        """
        self.stop_catalog_playback(KEY_CATALOG_GENRES)
        self.config[KEY_CURRENT_CATALOG_MODE] = KEY_CATALOG_GENRES

        if self.get_current_screen(KEY_CATALOG_GENRES): return

        listeners = {}
        listeners[KEY_HOME] = self.go_home
        listeners[KEY_BACK] = self.go_back
        listeners[KEY_PLAYER] = self.go_catalog_genre_player
        listeners[KEY_CATALOG] = self.go_catalog
        listeners[KEY_DETAILS] = self.go_catalog_genre_artists

        genres = CatalogGenres(self.util, KEY_CATALOG_GENRES, listeners, self.config[LABELS][KEY_GENRES])
        self.screens[KEY_CATALOG_GENRES] = genres

        if self.use_web:
            self.add_screen_observers(genres)
            redraw = self.web_server.redraw_web_ui
            genres.add_loading_listener(redraw)

        self.set_current_screen(KEY_CATALOG_GENRES)

    def go_catalog_genre_artists(self, state):
        """ Go to the Catalog Genres Screen

        :param state: button state
        """
        if getattr(state, "source", None) != "artist":
            title = state.name + ". " + self.config[LABELS][KEY_CATALOG_ARTISTS]
            state.title = title

        setattr(state, KEY_CATALOG_SERVICE, (KEY_CATALOG_ARTIST_SERVICE, SERVICE_DEEZER))

        if self.get_current_screen(KEY_CATALOG_GENRE_ARTISTS, state=state): return

        listeners = {}
        listeners[KEY_HOME] = self.go_home
        listeners[KEY_BACK] = self.go_back
        listeners[KEY_PLAYER] = self.go_catalog_genre_player
        listeners[KEY_CATALOG] = self.go_catalog
        listeners[KEY_DETAILS] = self.go_catalog_genre_artist_albums

        custom_nav_button = ("genre", self.go_catalog_genres)
        genres = CatalogGenreArtists(self.util, KEY_CATALOG_GENRE_ARTISTS, listeners, title, custom_nav_button)
        self.screens[KEY_CATALOG_GENRE_ARTISTS] = genres

        if self.use_web:
            self.add_screen_observers(genres)
            redraw = self.web_server.redraw_web_ui
            genres.add_loading_listener(redraw)

        self.set_current_screen(KEY_CATALOG_GENRE_ARTISTS, state=state)

    def go_catalog_genre_artist_albums(self, state):
        """ Go to the Catalog Genres Screen

        :param state: button state
        """
        title = state.name + ". " + self.config[LABELS][KEY_CATALOG_ALBUMS]
        state.title = title

        setattr(state, KEY_CATALOG_SERVICE, (KEY_CATALOG_ALBUM_SERVICE, SERVICE_DEEZER))

        if self.get_current_screen(KEY_CATALOG_GENRE_ARTIST_ALBUMS, state=state): return

        listeners = {}
        listeners[KEY_HOME] = self.go_home
        listeners[KEY_BACK] = self.go_back
        listeners[KEY_PLAYER] = self.go_catalog_genre_player
        listeners[KEY_CATALOG] = self.go_catalog
        listeners[KEY_DETAILS] = self.go_catalog_genre_album_tracks

        custom_nav_button = (ARTIST, self.go_catalog_genre_artists)
        albums = CatalogBase(self.util, KEY_CATALOG_GENRE_ARTIST_ALBUMS, listeners, title, custom_nav_button)
        self.screens[KEY_CATALOG_GENRE_ARTIST_ALBUMS] = albums

        if self.use_web:
            self.add_screen_observers(albums)
            redraw = self.web_server.redraw_web_ui
            albums.add_loading_listener(redraw)

        self.set_current_screen(KEY_CATALOG_GENRE_ARTIST_ALBUMS, state=state)

    def go_catalog_genre_album_tracks(self, state):
        """ Go to the Catalog Album Tracks Screen

        :param state: button state
        """
        setattr(state, KEY_CATALOG_SERVICE, (KEY_CATALOG_TRACK_SERVICE, SERVICE_DEEZER))

        if self.get_current_screen(KEY_CATALOG_GENRE_ALBUM_TRACKS, state=state): return

        listeners = {}
        listeners[KEY_HOME] = self.go_home
        listeners[KEY_BACK] = self.go_back
        listeners[KEY_PLAYER] = self.go_catalog_genre_player
        listeners[KEY_CATALOG] = self.go_catalog
        listeners[KEY_DETAILS] = self.go_catalog_genre_player

        custom_nav_button = ("album", self.go_catalog_genre_artist_albums)
        release_screen = CatalogAlbumTracks(self.util, KEY_CATALOG_GENRE_ALBUM_TRACKS, listeners, state.name, custom_nav_button)
        self.screens[KEY_CATALOG_GENRE_ALBUM_TRACKS] = release_screen

        if self.use_web:
            self.add_screen_observers(release_screen)
            redraw = self.web_server.redraw_web_ui
            release_screen.add_loading_listener(redraw)

        self.set_current_screen(KEY_CATALOG_GENRE_ALBUM_TRACKS, state=state)

    def go_catalog_genre_player(self, state):
        """ Go to the Catalog Genre player screen

        :param state: button state
        """
        if getattr(state, "source", None) == None:
            return

        if self.current_player_screen != KEY_CATALOG_GENRE_PLAYER:
            self.deactivate_current_player(KEY_CATALOG_GENRE_PLAYER)

        try:
            if self.screens[KEY_CATALOG_GENRE_PLAYER]:
                if getattr(state, "name", None) and (state.name == KEY_HOME or state.name == KEY_BACK):
                    self.set_current_screen(KEY_CATALOG_GENRE_PLAYER)
                else:
                    if getattr(state, "source", None) == None:
                        state.source = RESUME
                    self.set_current_screen(name=KEY_CATALOG_GENRE_PLAYER, state=state)
                self.current_player_screen = KEY_CATALOG_GENRE_PLAYER
                return
        except:
            pass

        listeners = self.get_play_screen_listeners()
        listeners[KEY_CATALOG_TRACK] = self.go_catalog_genre_album_tracks
        listeners[KEY_SEEK] = self.player.seek
        listeners[AUDIO_FILES] = self.go_catalog_genre_album_tracks
        listeners[YA_STREAM] = self.go_ya_search_browser
        screen = CatalogPlayerScreen(listeners, self.util, self.volume_control)
        self.screens[KEY_CATALOG_GENRE_PLAYER] = screen

        if self.screens.get(KEY_CATALOG_GENRE_ALBUM_TRACKS, None):
            tracks_screen =  self.screens[KEY_CATALOG_GENRE_ALBUM_TRACKS]
            screen.add_track_change_listener(tracks_screen.handle_track_change)
            tracks_screen.add_album_change_listener(screen.stop)

        self.player.add_player_listener(screen.time_control.set_track_info)
        self.player.add_player_listener(screen.update_arrow_button_labels)
        self.player.add_end_of_track_listener(screen.end_of_track)

        screen.add_play_listener(self.screensaver_dispatcher.change_image)
        screen.add_play_listener(self.screensaver_dispatcher.change_image_folder)

        self.set_current_screen(KEY_CATALOG_GENRE_PLAYER, state=state)
        self.current_player_screen = KEY_CATALOG_GENRE_PLAYER

        if self.use_web:
            update = self.web_server.update_web_ui
            redraw = self.web_server.redraw_web_ui
            start = self.web_server.start_time_control_to_json
            stop = self.web_server.stop_time_control_to_json
            title_to_json = self.web_server.title_to_json
            screen.add_screen_observers(update, redraw, start, stop, title_to_json)
            screen.add_loading_listener(redraw)
            self.web_server.add_player_listener(screen.time_control)
            self.player.add_player_listener(self.web_server.update_player_listeners)

    def go_search_artist_keyboard(self, state=None, max_text_length=64, min_text_length=0):
        """ Go to the Keyboard Screen

        :param state: button state
        :param max_text_length: maximum text length
        """
        s = self.get_current_screen(KEY_CATALOG_SEARCH_ARTIST_KEYBOARD)
        if state:
            search_by = getattr(state, "search_by", None)
        else:
            search_by = None
        if s:
            title = getattr(state, "title", None)
            if title and title != s.screen_title.text:
                s.screen_title.set_text(title)
                s.input_text.set_text("")
                s.keyboard.text = ""
                s.keyboard.search_by = search_by
                s.keyboard.callback = state.callback
            return

        listeners = {}
        listeners[KEY_HOME] = self.go_home
        listeners[KEY_PLAYER] = self.go_catalog_search_artist_player
        listeners[KEY_BACK] = self.go_back
        listeners[KEY_CALLBACK] = state.callback
        title = getattr(state, "title", None)
        visibility = getattr(state, "visibility", True)
        keyboard_screen = KeyboardScreen(title, self.util, listeners, visibility, max_text_length=max_text_length, min_text_length=min_text_length, search_by=search_by)
        self.screens[KEY_CATALOG_SEARCH_ARTIST_KEYBOARD] = keyboard_screen

        if self.use_web:
            self.add_screen_observers(keyboard_screen)

        self.set_current_screen(KEY_CATALOG_SEARCH_ARTIST_KEYBOARD)

    def go_catalog_search_artist(self, state):
        """ Go to the Catalog Search Artist Screen

        :param state: button state
        """
        self.stop_catalog_playback(KEY_CATALOG_SEARCH_ARTISTS)
        self.config[KEY_CURRENT_CATALOG_MODE] = KEY_CATALOG_SEARCH_ARTISTS

        state.visibility = False
        state.callback = self.go_catalog_search_artist_browser
        state.title = self.config[LABELS]["artist"]
        state.search_by = KEY_CATALOG_SEARCH_ARTISTS
        self.go_search_artist_keyboard(state, min_text_length=3)

    def go_catalog_search_artist_browser(self, state):
        """ Go to the Catalog Genres Screen

        :param state: button state
        """
        if getattr(state, KEY_CALLBACK_VAR, None):
            title = self.config[LABELS][KEY_CATALOG_ARTIST] + ": " + getattr(state, KEY_CALLBACK_VAR, "")
            state.title = title

        setattr(state, KEY_CATALOG_SERVICE, (KEY_CATALOG_ARTIST_SERVICE, SERVICE_SPOTIFY))

        if self.get_current_screen(KEY_CATALOG_ARTISTS, state=state): return

        listeners = {}
        listeners[KEY_HOME] = self.go_home
        listeners[KEY_BACK] = self.go_back
        listeners[KEY_PLAYER] = self.go_player
        listeners[KEY_CATALOG] = self.go_catalog
        listeners[KEY_DETAILS] = self.go_catalog_search_artist_albums_browser

        custom_nav_button = ("search-by-name", self.go_catalog_search_artist)
        albums = CatalogBase(self.util, KEY_CATALOG_ARTISTS, listeners, title, custom_nav_button)
        self.screens[KEY_CATALOG_ARTISTS] = albums

        if self.use_web:
            self.add_screen_observers(albums)
            redraw = self.web_server.redraw_web_ui
            albums.add_loading_listener(redraw)

        self.set_current_screen(KEY_CATALOG_ARTISTS, state=state)

    def go_catalog_search_artist_albums_browser(self, state):
        """ Go to the Catalog Search Album Screen

        :param state: button state
        """
        title = state.name + ". " + self.config[LABELS][KEY_CATALOG_ALBUMS]
        state.title = title

        setattr(state, KEY_CATALOG_SERVICE, (KEY_CATALOG_ALBUM_SERVICE, SERVICE_SPOTIFY))

        if self.get_current_screen(KEY_CATALOG_ARTIST_ALBUMS, state=state): return

        listeners = {}
        listeners[KEY_HOME] = self.go_home
        listeners[KEY_BACK] = self.go_back
        listeners[KEY_PLAYER] = self.go_player
        listeners[KEY_CATALOG] = self.go_catalog
        listeners[KEY_DETAILS] = self.go_catalog_search_artist_album_tracks_browser

        custom_nav_button = ("artist", self.go_catalog_search_artist_browser)
        albums = CatalogBase(self.util, KEY_CATALOG_ARTIST_ALBUMS, listeners, title, custom_nav_button)
        self.screens[KEY_CATALOG_ARTIST_ALBUMS] = albums

        if self.use_web:
            self.add_screen_observers(albums)
            redraw = self.web_server.redraw_web_ui
            albums.add_loading_listener(redraw)

        self.set_current_screen(KEY_CATALOG_ARTIST_ALBUMS, state=state)

    def go_catalog_search_artist_album_tracks_browser(self, state):
        """ Go to the Catalog Search Album Screen

        :param state: button state
        """
        setattr(state, KEY_CATALOG_SERVICE, (KEY_CATALOG_TRACK_SERVICE, SERVICE_SPOTIFY))

        if self.get_current_screen(KEY_CATALOG_ARTIST_ALBUM_TRACKS, state=state): return

        listeners = {}
        listeners[KEY_HOME] = self.go_home
        listeners[KEY_BACK] = self.go_back
        listeners[KEY_PLAYER] = self.go_catalog_search_artist_player
        listeners[KEY_CATALOG] = self.go_catalog
        listeners[KEY_DETAILS] = self.go_catalog_search_artist_player

        custom_nav_button = ("album", self.go_catalog_search_artist_albums_browser)
        release_screen = CatalogAlbumTracks(self.util, KEY_CATALOG_ARTIST_ALBUM_TRACKS, listeners, state.name, custom_nav_button)
        self.screens[KEY_CATALOG_ARTIST_ALBUM_TRACKS] = release_screen

        if self.use_web:
            self.add_screen_observers(release_screen)
            redraw = self.web_server.redraw_web_ui
            release_screen.add_loading_listener(redraw)

        self.set_current_screen(KEY_CATALOG_ARTIST_ALBUM_TRACKS, state=state)

    def go_catalog_search_artist_player(self, state):
        """ Go to the Catalog Search Artist Player

        :param state: button state
        """
        if getattr(state, "source", None) == None:
            return

        if self.current_player_screen != KEY_CATALOG_SEARCH_ARTIST_PLAYER:
            self.deactivate_current_player(KEY_CATALOG_SEARCH_ARTIST_PLAYER)

        try:
            if self.screens[KEY_CATALOG_SEARCH_ARTIST_PLAYER]:
                if getattr(state, "name", None) and (state.name == KEY_HOME or state.name == KEY_BACK):
                    self.set_current_screen(KEY_CATALOG_SEARCH_ARTIST_PLAYER)
                else:
                    if getattr(state, "source", None) == None:
                        state.source = RESUME
                    self.set_current_screen(name=KEY_CATALOG_SEARCH_ARTIST_PLAYER, state=state)
                self.current_player_screen = KEY_CATALOG_SEARCH_ARTIST_PLAYER
                return
        except:
            pass

        listeners = self.get_play_screen_listeners()
        listeners[KEY_CATALOG_TRACK] = self.go_catalog_search_artist_album_tracks_browser
        listeners[KEY_SEEK] = self.player.seek
        listeners[AUDIO_FILES] = self.go_catalog_search_artist_album_tracks_browser
        listeners[YA_STREAM] = self.go_ya_search_browser
        screen = CatalogPlayerScreen(listeners, self.util, self.volume_control)
        self.screens[KEY_CATALOG_SEARCH_ARTIST_PLAYER] = screen

        if self.screens.get(KEY_CATALOG_ARTIST_ALBUM_TRACKS, None):
            tracks_screen =  self.screens[KEY_CATALOG_ARTIST_ALBUM_TRACKS]
            screen.add_track_change_listener(tracks_screen.handle_track_change)
            tracks_screen.add_album_change_listener(screen.stop)

        self.player.add_player_listener(screen.time_control.set_track_info)
        self.player.add_player_listener(screen.update_arrow_button_labels)
        self.player.add_end_of_track_listener(screen.end_of_track)

        screen.add_play_listener(self.screensaver_dispatcher.change_image)
        screen.add_play_listener(self.screensaver_dispatcher.change_image_folder)

        self.set_current_screen(KEY_CATALOG_SEARCH_ARTIST_PLAYER, state=state)
        self.current_player_screen = KEY_CATALOG_SEARCH_ARTIST_PLAYER

        if self.use_web:
            update = self.web_server.update_web_ui
            redraw = self.web_server.redraw_web_ui
            start = self.web_server.start_time_control_to_json
            stop = self.web_server.stop_time_control_to_json
            title_to_json = self.web_server.title_to_json
            screen.add_screen_observers(update, redraw, start, stop, title_to_json)
            screen.add_loading_listener(redraw)
            self.web_server.add_player_listener(screen.time_control)
            self.player.add_player_listener(self.web_server.update_player_listeners)

    def go_search_album_keyboard(self, state=None, max_text_length=64, min_text_length=0):
        """ Go to the Keyboard Screen

        :param state: button state
        :param max_text_length: maximum text length
        """
        s = self.get_current_screen(KEY_CATALOG_SEARCH_ALBUM_KEYBOARD)
        if state:
            search_by = getattr(state, "search_by", None)
        else:
            search_by = None
        if s:
            title = getattr(state, "title", None)
            if title and title != s.screen_title.text:
                s.screen_title.set_text(title)
                s.input_text.set_text("")
                s.keyboard.text = ""
                s.keyboard.search_by = search_by
                s.keyboard.callback = state.callback
            return

        listeners = {}
        listeners[KEY_HOME] = self.go_home
        listeners[KEY_PLAYER] = self.go_catalog_search_album_player
        listeners[KEY_BACK] = self.go_back
        listeners[KEY_CALLBACK] = state.callback
        title = getattr(state, "title", None)
        visibility = getattr(state, "visibility", True)
        keyboard_screen = KeyboardScreen(title, self.util, listeners, visibility, max_text_length=max_text_length, min_text_length=min_text_length, search_by=search_by)
        self.screens[KEY_CATALOG_SEARCH_ALBUM_KEYBOARD] = keyboard_screen

        if self.use_web:
            self.add_screen_observers(keyboard_screen)

        self.set_current_screen(KEY_CATALOG_SEARCH_ALBUM_KEYBOARD)

    def go_catalog_search_album(self, state):
        """ Go to the Catalog Search Album Screen

        :param state: button state
        """
        self.stop_catalog_playback(KEY_CATALOG_SEARCH_ALBUMS)
        self.config[KEY_CURRENT_CATALOG_MODE] = KEY_CATALOG_SEARCH_ALBUMS

        state.visibility = False
        state.callback = self.go_catalog_search_album_browser
        state.title = self.config[LABELS]["album"]
        state.search_by = KEY_CATALOG_SEARCH_ALBUMS
        self.go_search_album_keyboard(state, min_text_length=3)

    def go_catalog_search_album_browser(self, state):
        """ Go to the Catalog Search Album Browser Screen

        :param state: button state
        """
        if getattr(state, KEY_CALLBACK_VAR, None):
            title = self.config[LABELS][KEY_CATALOG_ALBUM] + ": " + getattr(state, KEY_CALLBACK_VAR, "")
            state.title = title

        setattr(state, KEY_CATALOG_SERVICE, (KEY_CATALOG_ALBUM_SERVICE, SERVICE_SPOTIFY))

        if self.get_current_screen(KEY_CATALOG_ALBUMS, state=state): return

        listeners = {}
        listeners[KEY_HOME] = self.go_home
        listeners[KEY_BACK] = self.go_back
        listeners[KEY_PLAYER] = self.go_player
        listeners[KEY_CATALOG] = self.go_catalog
        listeners[KEY_DETAILS] = self.go_catalog_search_album_tracks_browser

        custom_nav_button = ("search-by-name", self.go_catalog_search_album)
        albums = CatalogBase(self.util, KEY_CATALOG_ALBUMS, listeners, title, custom_nav_button)
        self.screens[KEY_CATALOG_ALBUMS] = albums

        if self.use_web:
            self.add_screen_observers(albums)
            redraw = self.web_server.redraw_web_ui
            albums.add_loading_listener(redraw)

        self.set_current_screen(KEY_CATALOG_ALBUMS, state=state)

    def go_catalog_search_album_tracks_browser(self, state):
        """ Go to the Catalog Search Album Screen

        :param state: button state
        """
        setattr(state, KEY_CATALOG_SERVICE, (KEY_CATALOG_TRACK_SERVICE, SERVICE_SPOTIFY))

        if self.get_current_screen(KEY_CATALOG_ALBUM_TRACKS, state=state): return

        listeners = {}
        listeners[KEY_HOME] = self.go_home
        listeners[KEY_BACK] = self.go_back
        listeners[KEY_PLAYER] = self.go_catalog_search_album_player
        listeners[KEY_CATALOG] = self.go_catalog
        listeners[KEY_DETAILS] = self.go_catalog_search_album_player

        custom_nav_button = ("album", self.go_catalog_search_album_browser)
        release_screen = CatalogAlbumTracks(self.util, KEY_CATALOG_ALBUM_TRACKS, listeners, state.name, custom_nav_button)
        self.screens[KEY_CATALOG_ALBUM_TRACKS] = release_screen

        if self.use_web:
            self.add_screen_observers(release_screen)
            redraw = self.web_server.redraw_web_ui
            release_screen.add_loading_listener(redraw)

        self.set_current_screen(KEY_CATALOG_ALBUM_TRACKS, state=state)

    def go_catalog_search_album_player(self, state):
        """ Go to the Catalog Search Album Player

        :param state: button state
        """
        if getattr(state, "source", None) == None:
            return

        if self.current_player_screen != KEY_CATALOG_SEARCH_ALBUM_PLAYER:
            self.deactivate_current_player(KEY_CATALOG_SEARCH_ALBUM_PLAYER)

        try:
            if self.screens[KEY_CATALOG_SEARCH_ALBUM_PLAYER]:
                if getattr(state, "name", None) and (state.name == KEY_HOME or state.name == KEY_BACK):
                    self.set_current_screen(KEY_CATALOG_SEARCH_ALBUM_PLAYER)
                else:
                    if getattr(state, "source", None) == None:
                        state.source = RESUME
                    self.set_current_screen(name=KEY_CATALOG_SEARCH_ALBUM_PLAYER, state=state)
                self.current_player_screen = KEY_CATALOG_SEARCH_ALBUM_PLAYER
                return
        except:
            pass

        listeners = self.get_play_screen_listeners()
        listeners[KEY_CATALOG_TRACK] = self.go_catalog_search_album_tracks_browser
        listeners[KEY_SEEK] = self.player.seek
        listeners[AUDIO_FILES] = self.go_catalog_search_album_tracks_browser
        listeners[YA_STREAM] = self.go_ya_search_browser
        screen = CatalogPlayerScreen(listeners, self.util, self.volume_control)
        self.screens[KEY_CATALOG_SEARCH_ALBUM_PLAYER] = screen

        if self.screens.get(KEY_CATALOG_ALBUM_TRACKS, None):
            tracks_screen =  self.screens[KEY_CATALOG_ALBUM_TRACKS]
            screen.add_track_change_listener(tracks_screen.handle_track_change)
            tracks_screen.add_album_change_listener(screen.stop)

        self.player.add_player_listener(screen.time_control.set_track_info)
        self.player.add_player_listener(screen.update_arrow_button_labels)
        self.player.add_end_of_track_listener(screen.end_of_track)

        screen.add_play_listener(self.screensaver_dispatcher.change_image)
        screen.add_play_listener(self.screensaver_dispatcher.change_image_folder)

        self.set_current_screen(KEY_CATALOG_SEARCH_ALBUM_PLAYER, state=state)
        self.current_player_screen = KEY_CATALOG_SEARCH_ALBUM_PLAYER

        if self.use_web:
            update = self.web_server.update_web_ui
            redraw = self.web_server.redraw_web_ui
            start = self.web_server.start_time_control_to_json
            stop = self.web_server.stop_time_control_to_json
            title_to_json = self.web_server.title_to_json
            screen.add_screen_observers(update, redraw, start, stop, title_to_json)
            screen.add_loading_listener(redraw)
            self.web_server.add_player_listener(screen.time_control)
            self.player.add_player_listener(self.web_server.update_player_listeners)

    def go_search_track_keyboard(self, state=None, max_text_length=64, min_text_length=0):
        """ Go to the Keyboard Screen

        :param state: button state
        :param max_text_length: maximum text length
        """
        s = self.get_current_screen(KEY_CATALOG_SEARCH_TRACK_KEYBOARD)
        if state:
            search_by = getattr(state, "search_by", None)
        else:
            search_by = None
        if s:
            title = getattr(state, "title", None)
            if title and title != s.screen_title.text:
                s.screen_title.set_text(title)
                s.input_text.set_text("")
                s.keyboard.text = ""
                s.keyboard.search_by = search_by
                s.keyboard.callback = state.callback
            return

        listeners = {}
        listeners[KEY_HOME] = self.go_home
        listeners[KEY_PLAYER] = self.go_catalog_search_track_player
        listeners[KEY_BACK] = self.go_back
        listeners[KEY_CALLBACK] = state.callback
        title = getattr(state, "title", None)
        visibility = getattr(state, "visibility", True)
        keyboard_screen = KeyboardScreen(title, self.util, listeners, visibility, max_text_length=max_text_length, min_text_length=min_text_length, search_by=search_by)
        self.screens[KEY_CATALOG_SEARCH_TRACK_KEYBOARD] = keyboard_screen

        if self.use_web:
            self.add_screen_observers(keyboard_screen)

        self.set_current_screen(KEY_CATALOG_SEARCH_TRACK_KEYBOARD)

    def go_catalog_search_track(self, state):
        """ Go to the Catalog Serach Track Screen

        :param state: button state
        """
        self.stop_catalog_playback(KEY_CATALOG_SEARCH_TRACKS)
        self.config[KEY_CURRENT_CATALOG_MODE] = KEY_CATALOG_SEARCH_TRACKS

        state.visibility = False
        state.callback = self.go_catalog_search_track_browser
        state.title = self.config[LABELS]["track"]
        state.search_by = KEY_CATALOG_SEARCH_TRACKS
        self.go_search_track_keyboard(state, min_text_length=3)

    def go_catalog_search_track_browser(self, state):
        """ Go to the Catalog Search Track Browser Screen

        :param state: button state
        """
        if getattr(state, KEY_CALLBACK_VAR, None):
            title = self.config[LABELS][KEY_CATALOG_TRACK] + ": " + getattr(state, KEY_CALLBACK_VAR, "")
            state.title = title
            state.name = title
            state.album_id = state.id = getattr(state, KEY_CALLBACK_VAR, "")

        setattr(state, KEY_CATALOG_SERVICE, (KEY_CATALOG_TRACK_SERVICE, SERVICE_SPOTIFY))

        if self.get_current_screen(KEY_CATALOG_SEARCH_TRACK, state=state): return

        listeners = {}
        listeners[KEY_HOME] = self.go_home
        listeners[KEY_BACK] = self.go_back
        listeners[KEY_PLAYER] = self.go_catalog_search_track_player
        listeners[KEY_CATALOG] = self.go_catalog
        listeners[KEY_DETAILS] = self.go_catalog_search_track_player

        custom_nav_button = ("search-by-name", self.go_catalog_search_track)
        tracks = CatalogAlbumTracks(self.util, KEY_CATALOG_SEARCH_TRACK, listeners, state.name, custom_nav_button)
        self.screens[KEY_CATALOG_SEARCH_TRACK] = tracks

        if self.use_web:
            self.add_screen_observers(tracks)
            redraw = self.web_server.redraw_web_ui
            tracks.add_loading_listener(redraw)

        self.set_current_screen(KEY_CATALOG_SEARCH_TRACK, state=state)

    def go_catalog_search_track_player(self, state):
        """ Go to the Catalog Search Track Player

        :param state: button state
        """
        if getattr(state, "source", None) == None:
            return

        if self.current_player_screen != KEY_CATALOG_SEARCH_TRACK_PLAYER:
            self.deactivate_current_player(KEY_CATALOG_SEARCH_TRACK_PLAYER)

        try:
            if self.screens[KEY_CATALOG_SEARCH_TRACK_PLAYER]:
                if getattr(state, "name", None) and (state.name == KEY_HOME or state.name == KEY_BACK):
                    self.set_current_screen(KEY_CATALOG_SEARCH_TRACK_PLAYER)
                else:
                    if getattr(state, "source", None) == None:
                        state.source = RESUME
                    self.set_current_screen(name=KEY_CATALOG_SEARCH_TRACK_PLAYER, state=state)
                self.current_player_screen = KEY_CATALOG_SEARCH_TRACK_PLAYER
                return
        except:
            pass

        listeners = self.get_play_screen_listeners()
        listeners[KEY_CATALOG_TRACK] = self.go_catalog_search_track_browser
        listeners[KEY_SEEK] = self.player.seek
        listeners[AUDIO_FILES] = self.go_catalog_search_track_browser
        listeners[YA_STREAM] = self.go_ya_search_browser
        screen = CatalogPlayerScreen(listeners, self.util, self.volume_control)
        self.screens[KEY_CATALOG_SEARCH_TRACK_PLAYER] = screen

        if self.screens.get(KEY_CATALOG_SEARCH_TRACK, None):
            tracks_screen =  self.screens[KEY_CATALOG_SEARCH_TRACK]
            screen.add_track_change_listener(tracks_screen.handle_track_change)
            tracks_screen.add_album_change_listener(screen.stop)

        self.player.add_player_listener(screen.time_control.set_track_info)
        self.player.add_player_listener(screen.update_arrow_button_labels)
        self.player.add_end_of_track_listener(screen.end_of_track)

        screen.add_play_listener(self.screensaver_dispatcher.change_image)
        screen.add_play_listener(self.screensaver_dispatcher.change_image_folder)

        self.set_current_screen(KEY_CATALOG_SEARCH_TRACK_PLAYER, state=state)
        self.current_player_screen = KEY_CATALOG_SEARCH_TRACK_PLAYER

        if self.use_web:
            update = self.web_server.update_web_ui
            redraw = self.web_server.redraw_web_ui
            start = self.web_server.start_time_control_to_json
            stop = self.web_server.stop_time_control_to_json
            title_to_json = self.web_server.title_to_json
            screen.add_screen_observers(update, redraw, start, stop, title_to_json)
            screen.add_loading_listener(redraw)
            self.web_server.add_player_listener(screen.time_control)
            self.player.add_player_listener(self.web_server.update_player_listeners)

    def go_topic(self, state):
        """ Go to the Collection Topic Screen
        
        :param state: button state
        """   
        if self.get_current_screen(COLLECTION_TOPIC, state=state):
            return
        
        listeners = {}
        listeners[KEY_HOME] = self.go_home
        listeners[KEY_BACK] = self.go_back
        listeners[KEY_PLAYER] = self.go_player
        listeners[COLLECTION] = self.go_collection
        listeners[KEY_ABC] = self.go_latin_abc
        listeners[KEY_KEYBOARD_KEY] = self.go_keyboard

        listeners[TOPIC_DETAIL] = self.go_topic_detail
        listeners[KEY_CALLBACK] = self.go_topic
        listeners[KEY_PLAY_COLLECTION] = self.go_collection_playback
        
        screen = TopicScreen(self.util, listeners)
        self.screens[COLLECTION_TOPIC] = screen
        self.set_current_screen(COLLECTION_TOPIC, state=state)
        
        if self.use_web:
            self.add_screen_observers(screen)

    def go_topic_detail(self, state):
        """ Go to the Collection Album Screen
        
        :param state: button state
        """
        s = self.get_current_screen(TOPIC_DETAIL, state=state)   
        if s:
            return
        
        listeners = {}
        listeners[KEY_HOME] = self.go_home
        listeners[KEY_BACK] = self.go_back
        listeners[KEY_PLAYER] = self.go_player
        listeners[COLLECTION] = self.go_collection
        listeners[COLLECTION_TOPIC] = self.go_topic
        listeners[KEY_PLAY_COLLECTION] = self.go_collection_playback

        collection_screen = TopicDetailScreen(self.util, listeners)

        if self.use_web:
            self.add_screen_observers(collection_screen)

        self.screens[TOPIC_DETAIL] = collection_screen
        self.set_current_screen(TOPIC_DETAIL, state=state)

    def go_latin_abc(self, state=None):
        """ Go to Latin Alphabet Screen

        :param state: button state
        """
        s = self.get_current_screen(KEY_ABC)
        if s: 
            title = getattr(state, "title", None)
            if title and title != s.screen_title.text:
                s.screen_title.set_text(title)
            return

        listeners = {}
        listeners[KEY_HOME] = self.go_home
        listeners[KEY_BACK] = self.go_back
        listeners[COLLECTION] = self.go_collection
        listeners[KEY_PLAYER] = self.go_player
        listeners[KEY_CALLBACK] = state.callback
        
        title = getattr(state, "title", None)
        screen = LatinAbcScreen(title, self.util, listeners)
        self.screens[KEY_ABC] = screen

        if self.use_web:
            self.add_screen_observers(screen)

        self.set_current_screen(KEY_ABC)

    def reconfigure_player(self, new_player_name):
        if hasattr(self.player, "proxy") and self.player.proxy.stop_command:
            self.player.proxy.stop()

        self.player.stop_client()

        if self.config[LINUX_PLATFORM]:
            platform = "linux"
        else:
            platform = "windows"

        key = new_player_name + "." + platform

        if key not in self.config[PLAYERS].keys():
            return

        player_config = self.config[PLAYERS][key]

        self.config[AUDIO][PLAYER_NAME] = new_player_name
        self.config[AUDIO][SERVER_START_COMMAND] = player_config[SERVER_START_COMMAND]
        self.config[AUDIO][CLIENT_NAME] = player_config[CLIENT_NAME]

        try:
            self.config[AUDIO][STREAM_SERVER_PARAMETERS] = player_config[STREAM_SERVER_PARAMETERS]
        except:
            self.config[AUDIO][STREAM_SERVER_PARAMETERS] = None

        try:
            self.config[AUDIO][STREAM_CLIENT_PARAMETERS] = player_config[STREAM_CLIENT_PARAMETERS]
        except:
            self.config[AUDIO][STREAM_CLIENT_PARAMETERS] = None

        try:
            self.config[AUDIO][SERVER_STOP_COMMAND] = player_config[SERVER_STOP_COMMAND]
        except:
            self.config[AUDIO][SERVER_STOP_COMMAND] = None

        self.start_audio()

    def go_equalizer(self, state=None):
        """ Go to the Equalizer Screen
        
        :param state: button state
        """        
        if self.get_current_screen(EQUALIZER): return
        
        listeners = {}
        listeners[KEY_HOME] = self.go_home
        listeners[KEY_PLAYER] = self.go_player
        equalizer_screen = EqualizerScreen(self.util, listeners)
        self.screens[EQUALIZER] = equalizer_screen
        self.set_current_screen(EQUALIZER)
        
        if self.use_web:
            self.add_screen_observers(equalizer_screen)
            
    def go_timer(self, state=None):
        """ Go to the Timer Screen

        :param state: button state
        """
        if self.get_current_screen(TIMER): return

        listeners = {}
        listeners[KEY_HOME] = self.go_home
        listeners[KEY_PLAYER] = self.go_player
        listeners[SLEEP_NOW] = self.sleep
        timer_screen = TimerScreen(self.util, listeners, self.lock, self.start_timer_thread)
        self.screens[TIMER] = timer_screen
        self.set_current_screen(TIMER)

        if self.use_web:
            self.add_screen_observers(timer_screen)

    def go_network(self, state=None):
        """ Go to the Network Screen

        :param state: button state
        """
        if self.get_current_screen(NETWORK, state=state): return

        listeners = {}
        listeners[KEY_HOME] = self.go_home
        listeners[KEY_PLAYER] = self.go_player
        listeners[KEY_CHECK_INTERNET] = self.check_internet_connectivity
        listeners[KEY_SET_MODES] = self.screens[KEY_HOME].home_menu.set_current_modes
        listeners[WIFI] = self.go_wifi
        listeners[BLUETOOTH] = self.go_bluetooth

        network_screen = NetworkScreen(self.util, listeners)
        self.screens[NETWORK] = network_screen

        if self.use_web:
            self.add_screen_observers(network_screen)

        self.set_current_screen(NETWORK)

    def go_wifi(self, state=None):
        """ Go to the Wi-Fi Screen

        :param state: button state
        """
        if self.get_current_screen(WIFI, state=state): return

        listeners = {}
        listeners[KEY_HOME] = self.go_home
        listeners[KEY_PLAYER] = self.go_player
        listeners[KEY_KEYBOARD_KEY] = self.go_keyboard
        listeners[KEY_CALLBACK] = self.go_network
        listeners[WIFI] = self.go_wifi

        wifi_screen = WiFiScreen(self.util, listeners)
        wifi_screen.add_wifi_selection_listener(self.screens[NETWORK].set_current_wifi_network)
        self.screens[WIFI] = wifi_screen

        if self.use_web:
            self.add_screen_observers(wifi_screen)

        self.set_current_screen(WIFI)

    def go_bluetooth(self, state=None):
        """ Go to the Bluetooth Screen

        :param state: button state
        """
        if self.get_current_screen(BLUETOOTH, state=state): return

        listeners = {}
        listeners[KEY_HOME] = self.go_home
        listeners[KEY_PLAYER] = self.go_player
        listeners[KEY_NETWORK] = self.go_network

        bluetooth_screen = BluetoothScreen(self.util, listeners)
        self.screens[BLUETOOTH] = bluetooth_screen

        if self.use_web:
            self.add_screen_observers(bluetooth_screen)

        self.set_current_screen(BLUETOOTH)

    def go_keyboard(self, state=None, max_text_length=64, min_text_length=0):
        """ Go to the Keyboard Screen

        :param state: button state
        :param max_text_length: maximum text length
        """
        s = self.get_current_screen(KEYBOARD)
        if state:
            search_by = getattr(state, "search_by", None)
        else:
            search_by = None
        if s: 
            title = getattr(state, "title", None)
            if title and title != s.screen_title.text:
                s.screen_title.set_text(title)
                s.input_text.set_text("")
                s.keyboard.text = ""
                s.keyboard.search_by = search_by
                s.keyboard.callback = state.callback
            return

        listeners = {}
        listeners[KEY_HOME] = self.go_home
        listeners[KEY_PLAYER] = self.go_player
        listeners[KEY_BACK] = self.go_back
        listeners[KEY_CALLBACK] = state.callback
        title = getattr(state, "title", None)
        visibility = getattr(state, "visibility", True)
        keyboard_screen = KeyboardScreen(title, self.util, listeners, visibility, max_text_length=max_text_length, min_text_length=min_text_length, search_by=search_by)
        self.screens[KEYBOARD] = keyboard_screen

        if self.use_web:
            self.add_screen_observers(keyboard_screen)

        self.set_current_screen(KEYBOARD)

    def get_language_url(self):
        """ Return language URL constant for current language """
        
        language = self.config[CURRENT][LANGUAGE]
        
        if language == ENGLISH_USA:
            return ""
        else:
            return LANGUAGE_PREFIX + language + os.sep
    
    def get_parser(self):
        """ Return site parser for the current site """
        
        name = self.config[AUDIOBOOKS][BROWSER_SITE]
        if name == LOYALBOOKS:            
            return LoyalBooksParser()            
        return None

    def start_saver(self, state):
        """ Start screensaver

        :param state:
        """
        self.screensaver_dispatcher.start_screensaver()

    def go_savers(self, state):
        """ Go to the Screensavers Screen
        
        :param state: button state
        """
        if self.get_current_screen(SCREENSAVER): return
        
        listeners = {KEY_HOME: self.go_home, KEY_PLAYER: self.go_player, KEY_START_SAVER: self.start_saver}
        saver_screen = SaverScreen(self.util, listeners)
        saver_screen.saver_menu.add_listener(self.screensaver_dispatcher.change_saver_type)
        self.screens[SCREENSAVER] = saver_screen
        self.set_current_screen(SCREENSAVER)
        
        if self.use_web:
            self.add_screen_observers(saver_screen)
        
    def go_about(self, state):
        """ Go to the About Screen
        
        :param state: button state
        """
        self.exit_current_screen()
        self.set_current_screen(KEY_ABOUT)
        if self.use_web:
            self.add_screen_observers(self.screens[KEY_ABOUT])
    
    def go_black(self):
        """ Go to the Black Screen for sleeping mode
        
        :param state: button state
        """
        self.exit_current_screen()
        
        try:
            self.screens[KEY_BLACK]    
        except:
            black = BlackScreen(self.util)
            black.add_listener(self.wake_up)
            self.screens[KEY_BLACK] = black
        
        self.set_current_screen(KEY_BLACK)
        if self.use_web:
            self.web_server.redraw_web_ui()
    
    def go_stations(self, state=None):
        """ Go to the Stations Screen
        
        :param state: button state
        """
        self.deactivate_current_player(KEY_STATIONS)
        
        radio_player_screen = None
        self.config[CURRENT_SCREEN] = KEY_STATIONS

        try:
            radio_player_screen = self.screens[KEY_STATIONS]
        except:
            pass

        if radio_player_screen != None:
            radio_player_screen.set_current(state)
            self.get_current_screen(KEY_STATIONS, state)
            self.screensaver_dispatcher.change_image_folder(State())
            return
        
        listeners = self.get_play_screen_listeners()
        listeners[KEY_GENRES] = self.go_genres
        listeners[KEY_RADIO_BROWSER] = self.go_radio_browser
        listeners[KEY_SEARCH_BROWSER] = self.go_radio_search

        radio_player_screen = RadioPlayerScreen(self.util, listeners, self.volume_control)
        radio_player_screen.play()

        self.screens[KEY_STATIONS] = radio_player_screen
        self.set_current_screen(KEY_STATIONS, False, state)

        self.player.add_player_listener(radio_player_screen.screen_title.set_text)
        self.player.add_title_listener(radio_player_screen.set_title_metadata)
        self.player.add_metadata_listener(radio_player_screen.set_station_metadata)
        radio_player_screen.add_change_logo_listener(self.screensaver_dispatcher.change_image)
        self.screensaver_dispatcher.change_image_folder(State())
        if self.config[USAGE][USE_ALBUM_ART]:
            self.player.add_player_listener(radio_player_screen.show_album_art) 

        if radio_player_screen.center_button:
            self.screensaver_dispatcher.change_image(radio_player_screen.center_button.state)

        if self.use_web:
            update = self.web_server.update_web_ui
            redraw = self.web_server.redraw_web_ui
            title_to_json = self.web_server.title_to_json
            radio_player_screen.add_screen_observers(update, redraw, title_to_json)
    
    def set_config_volume(self, volume):
        """ Listener for volume change events
        
        :param volume: new volume value
        """
        self.config[PLAYER_SETTINGS][VOLUME] = str(int(volume.position))

    def go_radio_browser_player(self, state=None):
        """ Go to the Radio Browser Player Screen

        :param state: button state
        """
        radio_browser_player_screen = None
        try:
            radio_browser_player_screen = self.screens[KEY_RADIO_BROWSER_PLAYER]
            self.deactivate_current_player(KEY_RADIO_BROWSER_PLAYER)

            self.config[CURRENT_SCREEN] = KEY_RADIO_BROWSER_PLAYER
            
            if self.current_player_screen == KEY_RADIO_BROWSER_PLAYER:
                if state.source == KEY_SEARCH_BROWSER or state.source == KEY_FAVORITES:
                    go_back = False
                else:
                    state.source = KEY_BACK
                    go_back = True
            else:
                state.source = KEY_HOME
                self.current_player_screen = KEY_RADIO_BROWSER_PLAYER
                go_back = False

            self.set_current_screen(KEY_RADIO_BROWSER_PLAYER, go_back=go_back, state=state)
            self.screensaver_dispatcher.change_image_folder(State())
            return
        except:
            pass

        search_station_id = self.config.get(RADIO_BROWSER_SEARCH_STATION_ID, None)
        favorite_station_id = self.config[RADIO_BROWSER].get(FAVORITE_STATION_ID, None)
        if search_station_id == None and not favorite_station_id and state.source != KEY_SEARCH_BROWSER:
            if state.source == KEY_FAVORITES:
                self.go_favorites_screen(state)
                return
            else:
                self.go_search_by_screen(state)
                return

        listeners = self.get_play_screen_listeners()
        listeners[KEY_SEARCH_BY_SCREEN] = self.go_search_by_screen
        listeners[KEY_SEARCH_BROWSER] = self.go_radio_search
        listeners[KEY_FAVORITES_SCREEN] = self.go_favorites_screen

        radio_browser_player_screen = RadioBrowserPlayerScreen(self.util, listeners, self.volume_control)
        radio_browser_player_screen.play()
        self.current_player_screen = KEY_RADIO_BROWSER_PLAYER
        self.config[CURRENT_SCREEN] = KEY_RADIO_BROWSER_PLAYER

        self.screens[KEY_RADIO_BROWSER_PLAYER] = radio_browser_player_screen
        state.source = INIT
        if getattr(state, "image_path", None) != None:
            del state.image_path
        self.set_current_screen(KEY_RADIO_BROWSER_PLAYER, False, state)

        self.player.add_player_listener(radio_browser_player_screen.screen_title.set_text)
        self.player.add_title_listener(radio_browser_player_screen.set_title_metadata)
        self.player.add_metadata_listener(radio_browser_player_screen.set_station_metadata)
        radio_browser_player_screen.add_change_logo_listener(self.screensaver_dispatcher.change_image)
        self.screensaver_dispatcher.change_image_folder(State())
        if self.config[USAGE][USE_ALBUM_ART]:
            self.player.add_player_listener(radio_browser_player_screen.show_album_art)

        if radio_browser_player_screen.center_button:
            self.screensaver_dispatcher.change_image(radio_browser_player_screen.center_button.state)

        if self.use_web:
            update = self.web_server.update_web_ui
            redraw = self.web_server.redraw_web_ui
            title_to_json = self.web_server.title_to_json
            radio_browser_player_screen.add_screen_observers(update, redraw, title_to_json)

    def go_search_by_screen(self, state):
        """ Go to the 'Search By' screen

        :param state: button state
        """
        try:
            self.screens[KEY_SEARCH_BY_SCREEN]
            self.set_current_screen(KEY_SEARCH_BY_SCREEN)
            return
        except:
            pass

        listeners = {
            KEY_BACK: self.go_back,
            KEY_HOME: self.go_home,
            KEY_SEARCH_BY_COUNTRY: self.go_search_by_country,
            KEY_SEARCH_BY_LANGUAGE: self.go_search_by_language,
            KEY_SEARCH_BY_GENRE: self.go_search_by_genre,
            KEY_SEARCH_BY_NAME: self.go_search_by_name,
            KEY_PLAYER: self.go_player,
            KEY_FAVORITES: self.go_radio_browser_favorites
        }
        search_by_screen = SearchByScreen(self.util, listeners)
        self.screens[KEY_SEARCH_BY_SCREEN] = search_by_screen
        self.set_current_screen(KEY_SEARCH_BY_SCREEN)

        if self.use_web:
            self.add_screen_observers(search_by_screen)

    def go_search_by_country(self, state):
        """ Go to the 'Search By Country' screen

        :param state: button state
        """
        try:
            self.screens[KEY_COUNTRY_SCREEN]
            self.set_current_screen(KEY_COUNTRY_SCREEN)
            return
        except:
            pass

        listeners = {
            KEY_BACK: self.go_back,
            KEY_HOME: self.go_home,
            KEY_SEARCH_BROWSER: self.go_radio_search,
            KEY_SEARCH_BY_SCREEN: self.go_search_by_screen,
            KEY_PLAYER: self.go_player
        }
        browser_screen = BrowserScreen(self.util, listeners, KEY_COUNTRY_SCREEN, self.config[LABELS][SELECT_COUNTRY])
        if self.use_web:
            self.add_screen_observers(browser_screen)

        self.screens[KEY_COUNTRY_SCREEN] = browser_screen
        self.set_current_screen(KEY_COUNTRY_SCREEN)
        browser_screen.set_current()

    def go_search_by_language(self, state):
        """ Go to the 'Search By Language' screen

        :param state: button state
        """
        try:
            self.screens[KEY_LANGUAGE_SCREEN]
            self.set_current_screen(KEY_LANGUAGE_SCREEN)
            return
        except:
            pass

        listeners = {
            KEY_BACK: self.go_back,
            KEY_HOME: self.go_home,
            KEY_SEARCH_BROWSER: self.go_radio_search,
            KEY_SEARCH_BY_SCREEN: self.go_search_by_screen,
            KEY_PLAYER: self.go_player
        }
        browser_screen = BrowserScreen(self.util, listeners, KEY_LANGUAGE_SCREEN, self.config[LABELS][SELECT_LANGUAGE])
        if self.use_web:
            self.add_screen_observers(browser_screen)

        self.screens[KEY_LANGUAGE_SCREEN] = browser_screen
        self.set_current_screen(KEY_LANGUAGE_SCREEN)
        browser_screen.set_current()

    def go_search_by_genre(self, state):
        """ Go to the 'Search By Genre' screen

        :param state: button state
        """
        state.visibility = False
        state.callback = self.go_radio_search
        state.title = self.config[LABELS]["enter.genre"]
        state.search_by = KEY_SEARCH_BY_GENRE
        self.go_keyboard(state, min_text_length=3)

    def go_search_by_name(self, state):
        """ Go to the 'Search By Name' screen

        :param state: button state
        """
        state.visibility = False
        state.callback = self.go_radio_search
        state.title = self.config[LABELS]["enter.station.name"]
        state.search_by = KEY_SEARCH_BY_NAME
        self.go_keyboard(state, min_text_length=3)

    def go_radio_search(self, state):
        """ Go to the Radio Search Screen

        :param state: button state
        """
        try:
            self.screens[KEY_SEARCH_BROWSER]
            self.set_current_screen(KEY_SEARCH_BROWSER, state=state)
            return
        except:
            pass

        listeners = {
            KEY_BACK: self.go_back,
            KEY_HOME: self.go_home,
            KEY_PLAYER: self.go_radio_browser_player,
            KEY_SEARCH_BY_SCREEN: self.go_search_by_screen,
            KEY_SEARCH_BY_COUNTRY: self.go_search_by_country,
            KEY_SEARCH_BY_LANGUAGE: self.go_search_by_language,
            KEY_SEARCH_BY_GENRE: self.go_search_by_genre,
            KEY_SEARCH_BY_NAME: self.go_search_by_name
        }
        radio_search_screen = RadioSearchScreen(self.util, listeners, state)
        if self.use_web:
            self.add_screen_observers(radio_search_screen)

        radio_search_screen.go_player = self.go_radio_browser_player
        self.screens[KEY_SEARCH_BROWSER] = radio_search_screen
        self.set_current_screen(KEY_SEARCH_BROWSER)
        radio_search_screen.load_page(state)

    def go_favorites_screen(self, state):
        """ Go to the Radio Browser Favorites Screen

        :param state: button state
        """
        try:
            self.screens[KEY_FAVORITES_SCREEN]
            self.set_current_screen(KEY_FAVORITES_SCREEN, state=state)
            return
        except:
            pass

        listeners = {
            KEY_BACK: self.go_back,
            KEY_HOME: self.go_home,
            KEY_PLAYER: self.go_radio_browser_player,
            KEY_SEARCH_BY_SCREEN: self.go_search_by_screen,
            KEY_SEARCH_BY_COUNTRY: self.go_search_by_country,
            KEY_SEARCH_BY_LANGUAGE: self.go_search_by_language,
            KEY_SEARCH_BY_GENRE: self.go_search_by_genre,
            KEY_SEARCH_BY_NAME: self.go_search_by_name
        }
        radio_search_screen = FavoritesScreen(self.util, listeners, state)
        radio_search_screen.go_player = self.go_radio_browser_player
        self.screens[KEY_FAVORITES_SCREEN] = radio_search_screen
        self.set_current_screen(KEY_FAVORITES_SCREEN, state=state)

        if self.use_web:
            self.add_screen_observers(radio_search_screen)

    def go_genres(self, state):
        """ Go to the Genre Screen
        
        :param state: button state
        """
        if self.get_current_screen(KEY_GENRES): return
        
        listeners = {
            KEY_GENRE: self.go_stations,
            KEY_HOME: self.go_home,
            KEY_PLAYER: self.go_player,
            KEY_FAVORITES: self.go_favorites
        }
        genre_screen = RadioGroupScreen(self.util, listeners)
        self.screens[KEY_GENRES] = genre_screen
        self.set_current_screen(KEY_GENRES)
        
        if self.use_web:
            self.add_screen_observers(genre_screen)

    def go_radio_browser(self, state):
        """ Go to the Radio Browser Screen
        
        :param state: button state
        """
        try:
            self.screens[KEY_RADIO_BROWSER].set_current(state)
        except:
            pass

        self.config[CURRENT_SCREEN] = KEY_RADIO_BROWSER

        if self.get_current_screen(KEY_RADIO_BROWSER): 
            return
        
        listeners = {KEY_GENRE: self.go_stations, KEY_HOME: self.go_home, KEY_PLAYER: self.go_player}
        radio_browser_screen = RadioBrowserScreen(self.util, listeners)
        radio_browser_screen.go_player = self.go_stations

        radio_player_screen = self.screens[KEY_STATIONS]
        radio_player_screen.center_button.add_release_listener(radio_browser_screen.handle_favorite)

        self.screens[KEY_RADIO_BROWSER] = radio_browser_screen
        self.set_current_screen(KEY_RADIO_BROWSER)
        
        if self.use_web:
            self.add_screen_observers(radio_browser_screen)

    def go_stream_browser(self, state):
        """ Go to the Stream Browser Screen
        
        :param state: button state
        """
        try:
            self.screens[KEY_STREAM_BROWSER].set_current(state)
        except:
            pass

        if self.get_current_screen(KEY_STREAM_BROWSER): 
            return
        
        listeners = {KEY_HOME: self.go_home, KEY_PLAYER: self.go_player, STREAM: self.go_stream}
        stream_browser_screen = StreamBrowserScreen(self.util, listeners)
        self.screens[KEY_STREAM_BROWSER] = stream_browser_screen
        stream_browser_screen.go_player = self.go_stream
        self.set_current_screen(KEY_STREAM_BROWSER)

        if self.use_web:
            self.add_screen_observers(stream_browser_screen)

    def go_archive_items_browser(self, state):
        """ Go to the Archive Items Browser Screen

        :param state: button state
        """
        if self.get_current_screen(KEY_ARCHIVE_ITEMS_BROWSER, state):
            return

        file_browser = self.get_current_screen(KEY_ARCHIVE_FILES_BROWSER, state)

        listeners = {
            KEY_HOME: self.go_home,
            KEY_PLAYER: self.go_player,
            ARCHIVE: self.go_archive,
            KEY_KEYBOARD_KEY: self.go_keyboard,
            KEY_BACK: self.go_back,
            KEY_ARCHIVE_ITEMS: self.go_archive_items_browser,
            KEY_CALLBACK: self.go_archive_items_browser,
            KEY_ARCHIVE_FILES_BROWSER: file_browser.reset_page_counter
        }
        archive_browser_screen = ArchiveItemsBrowserScreen(self.util, listeners)
        self.screens[KEY_ARCHIVE_ITEMS_BROWSER] = archive_browser_screen
        archive_browser_screen.go_player = self.go_archive

        if self.use_web:
            archive_browser_screen.add_loading_listener(self.web_server.redraw_web_ui)

        self.set_current_screen(KEY_ARCHIVE_ITEMS_BROWSER, state=state)

        if self.use_web:
            self.add_screen_observers(archive_browser_screen)

    def go_archive_files_browser(self, state):
        """ Go to the Archive Files Browser Screen

        :param state: button state
        """
        if self.get_current_screen(KEY_ARCHIVE_FILES_BROWSER, state):
            return

        listeners = {
            KEY_HOME: self.go_home,
            KEY_PLAYER: self.go_player,
            ARCHIVE: self.go_archive,
            KEY_KEYBOARD_KEY: self.go_keyboard,
            KEY_BACK: self.go_back,
            KEY_ARCHIVE_ITEMS: self.go_archive_items_browser,
            KEY_CALLBACK: self.go_archive_items_browser
        }
        archive_browser_screen = ArchiveFilesBrowserScreen(self.util, listeners)
        self.screens[KEY_ARCHIVE_FILES_BROWSER] = archive_browser_screen
        archive_browser_screen.go_player = self.go_archive
        self.set_current_screen(KEY_ARCHIVE_FILES_BROWSER)

        if self.use_web:
            self.add_screen_observers(archive_browser_screen)
    
    def play_pause(self, state=None):
        """ Handle Play/Pause
        
        :param state: button state
        """
        self.config[PLAYER_SETTINGS][PAUSE] = not self.config[PLAYER_SETTINGS][PAUSE]
        self.player.play_pause(self.config[PLAYER_SETTINGS][PAUSE])
        
    def set_current_screen(self, name, go_back=False, state=None):
        """ Set current screen defined by its name
        
        :param name: screen name
        """
        with self.lock:
            self.previous_screen_name = self.current_screen
            if self.current_screen:
                ps = self.screens[self.current_screen]
                ps.set_visible(False)
            self.current_screen = name
            cs = self.screens[self.current_screen]
            p = getattr(cs, "player_screen", None)
            if p: 
                cs.enable_player_screen(True)
            
            cs.set_visible(True)

            if go_back:
                cs.go_back()
            else:
                if name == KEY_PLAY_FILE:
                    f = getattr(state, "file_name", None)
                    if f or self.current_player_screen != name:
                        if f != None:
                            self.current_audio_file = f
                        cs.set_current(state=state)
                elif name == KEY_PLAY_COLLECTION:
                    cs.set_current(new_track=True, state=state)
                elif name.endswith(KEY_BOOK_SCREEN):
                    if state:
                        cs.set_current(state)
                elif name == KEY_PLAY_SITE:
                    cs.set_current(state=state)
                elif name == KEY_BOOK_TRACK_SCREEN:
                    state = State()
                    ps = self.screens[KEY_PLAY_SITE]
                    state.playlist = ps.get_playlist()
                    state.current_track_index = ps.current_track_index
                    cs.set_current(state)
                elif name == KEY_PODCAST_PLAYER:
                    f = getattr(state, "file_name", None)
                    if (f and self.current_audio_file != f) or self.current_player_screen != name or state.source == INIT:
                        self.current_audio_file = f
                        cs.set_current_screen(state)
                else:
                    cs.set_current(state)

            cs.clean_draw_update()
            self.event_dispatcher.set_current_screen(cs)
            self.set_volume()

            if p: 
                self.current_player_screen = name
    
    def go_back(self, state):
        """ Go to the previous screen
        
        :param state: button state
        """
        if not self.previous_screen_name:
            return
        
        cs = self.screens[self.current_screen]
        cs.exit_screen()
        state.source = KEY_BACK
        self.set_current_screen(self.previous_screen_name, state=state)
    
    def set_volume(self, volume=None):
        """ Set volume level 
        
        :param volume: volume level 0-100
        """
        cs = self.screens[self.current_screen]
        player_screen = getattr(cs, "player_screen", None)
        if player_screen:            
            if volume == None: 
                config_volume = int(self.config[PLAYER_SETTINGS][VOLUME])
            else:
                config_volume = volume.position
            
            self.volume_control.set_volume(config_volume)
    
    def mute(self, state):
        """ Mute

        :param state: button state
        """
        self.config[PLAYER_SETTINGS][MUTE] = not self.config[PLAYER_SETTINGS][MUTE]
        self.player.mute()

    def volume_up(self, state):
        """ Volume up

        :param state: button state
        """
        step = 10
        current_volume = int(self.config[PLAYER_SETTINGS][VOLUME])
        current_volume += step
        if current_volume > 100:
            current_volume = 100
        self.config[PLAYER_SETTINGS][VOLUME] = current_volume
        self.volume_control.set_volume(current_volume)

    def volume_down(self, state):
        """ Volume down

        :param state: button state
        """
        step = 10
        current_volume = int(self.config[PLAYER_SETTINGS][VOLUME])
        current_volume -= step
        if current_volume < 0:
            current_volume = 0
        self.config[PLAYER_SETTINGS][VOLUME] = current_volume
        self.volume_control.set_volume(current_volume)

    def is_player_screen(self):
        """ Check if the current screen is player screen

        :return: True- current screen is player screen, False - current screen is not player screen
        """
        try:
            return getattr(self.screens[self.current_screen], "player_screen", False)
        except:
            return False

    def deactivate_current_player(self, new_player_screen_name):
        """ Disable current player
        
        :param new_player_screen_name: new player screen name
        """
        for scr in self.screens.items():
            p = getattr(scr[1], "player_screen", None)
            if not p: 
                continue
            scr[1].enable_player_screen(False)
            
        self.exit_current_screen()
        
        if new_player_screen_name == self.current_player_screen:
            return
        
        with self.lock:
            try:
                s = self.screens[self.current_player_screen]
                s.stop_timer()
            except:
                pass
        
    def store_current_track_time(self, mode):
        """ Save current track time in configuration object
        
        :param mode: 
        """
        k = self.current_player_screen

        if k and k in self.screens and getattr(self.screens[k], "time_control", None):
            s = self.screens[k]
            tc = s.time_control
            t = tc.seek_time
            if t == None or t == 'None':
                t = 0
            ps = self.current_player_screen
            if ps == KEY_PLAY_SITE:
                self.config[AUDIOBOOKS][BROWSER_BOOK_TIME] = t
            elif ps == KEY_PLAY_FILE:
                self.config[FILE_PLAYBACK][CURRENT_TRACK_TIME] = t
            elif ps == KEY_PODCAST_PLAYER:
                self.config[PODCASTS][PODCAST_EPISODE_TIME] = t
            elif ps == KEY_PLAY_COLLECTION:
                self.config[COLLECTION_PLAYBACK][COLLECTION_TRACK_TIME] = t
            elif ps == KEY_YA_PLAYLIST_PLAYER:
                self.config[YA_STREAM][YA_PLAYLIST_TIME] = t
            elif ps == KEY_YA_SEARCH_PLAYER:
                self.config[YA_STREAM][YA_SEARCH_TIME] = t
            elif ps == KEY_ARCHIVE_PLAYER:
                self.config[ARCHIVE][FILE_TIME] = t

    def pre_shutdown(self, save=True, reboot=False):
        """ Pre-shutdown operations 
        
        :param save: True - save current player state, False - don't save
        :param reboot: True - reboot command, False - shutdown command
        """

        s = self.config[SCRIPTS][SCRIPT_PLAYER_STOP]
        if s != None and len(s.strip()) != 0:
            self.util.run_script(s)

        if save:
            self.store_current_track_time(self.config[CURRENT][MODE])

            if self.config.get(KEY_YA_STREAM_CURRENT_PLAYER, None) == KEY_YA_SEARCH_PLAYER:
                self.config[YA_STREAM][YA_STREAM_ID] = ""
                self.config[YA_STREAM][YA_STREAM_NAME] = ""
                self.config[YA_STREAM][YA_STREAM_URL] = ""
                self.config[YA_STREAM][YA_THUMBNAIL_PATH] = ""
                self.config[YA_STREAM][YA_SEARCH_TIME] = ""
                self.config[YA_STREAM][YA_PLAYLIST_TIME] = ""

            self.util.config_class.save_current_settings()
            self.util.config_class.save_switch_config()

            if self.util.ya_stream_util.playlist_updated:
                self.util.ya_stream_util.save_playlist()

        self.player.shutdown()
        self.util.samba_util.stop_sharing()

        if self.use_web:
            try:
                self.web_server.shutdown()
            except Exception as e:
                logging.debug(e)

        self.event_dispatcher.run_dispatcher = False
        time.sleep(0.4)
        
        title_screen_name = self.get_title_screen_name()
        self.player.stop_client()

        if title_screen_name:
            try:
                self.screens[title_screen_name].screen_title.shutdown()
            except:
                pass

        self.stop_player_timer_thread(title_screen_name)

        pygame.quit()
        
        if self.config[LINUX_PLATFORM]:
            if self.disk_manager.observer:
                self.disk_manager.observer.stop()
            if not self.config[USAGE][USE_DESKTOP] and not reboot:
                self.disk_manager.poweroff_all_usb_disks()
                self.nas_manager.poweroff_all_nases()

        if self.config[USE_SWITCH]:
            self.config[KEY_SWITCH] = []
            self.util.switch_util.switch_power()

        if self.config[USAGE][USE_VOICE_ASSISTANT] and self.voice_assistant:
            self.voice_assistant.stop()

        if not reboot and self.config[DSI_DISPLAY_BACKLIGHT][USE_DSI_DISPLAY] and self.config[BACKLIGHTER]:
            self.config[BACKLIGHTER].power = False    

    def get_title_screen_name(self):
        """ Get current player screen name

        :return: screen name
        """
        title_screen_name = None

        if self.config[CURRENT][MODE] == RADIO:
            title_screen_name = KEY_STATIONS
        elif self.config[CURRENT][MODE] == AUDIO_FILES:
            title_screen_name = KEY_PLAY_FILE
        elif self.config[CURRENT][MODE] == AUDIOBOOKS:
            title_screen_name = KEY_PLAY_SITE
        elif self.config[CURRENT][MODE] == AIRPLAY:
            self.player.proxy.stop()
        elif self.config[CURRENT][MODE] == SPOTIFY_CONNECT:
            self.player.proxy.stop()
        elif self.config[CURRENT][MODE] == COLLECTION:
            title_screen_name = KEY_PLAY_COLLECTION

        return title_screen_name

    def stop_player_timer_thread(self, title_screen_name):
        """ Stop current player timer thread 
        
        :param title_screen_name: player screen name
        """
        players = [KEY_PLAY_FILE, KEY_PLAY_SITE, KEY_PLAY_COLLECTION]

        if title_screen_name and (title_screen_name in players):
            try:
                self.screens[title_screen_name].time_control.stop_thread()
            except:
                pass

    def shutdown(self, event=None):
        """ System shutdown handler

        :param event: the event
        """
        self.pre_shutdown()

        if self.config[LINUX_PLATFORM]:
            if not self.config[USAGE][USE_DESKTOP]:
                subprocess.call("sudo poweroff", shell=True)
            else:
                os._exit(0)
        else:
            self.shutdown_windows()

    def reboot(self, save=True):
        """ Reboot player 
        
        :param save: True - save current player state before reboot, False - reboot w/o saving
        """

        self.pre_shutdown(save, reboot=True)

        if self.config[LINUX_PLATFORM]:
            try:
                status_command = "sudo systemctl status peppy"
                check_output(status_command.split())
                restart_command = "sudo systemctl restart peppy"
                Popen(restart_command.split(), shell=False)
            except Exception as e:
                logging.debug(e)
                reboot_command = "sudo reboot"
                subprocess.call(reboot_command.split(), shell=False)
        else:
            self.shutdown_windows()

    def shutdown_windows(self):
        """ Shutdown Windows player """

        if self.config[AUDIO][PLAYER_NAME] == MPD_NAME:
            try:
                Popen("taskkill /F /T /PID {pid}".format(pid=self.proxy_process.pid))
            except:
                pass
        os._exit(0)

    def update_mpd_database(self):
        """ Update mpd database """

        if self.config[AUDIO][PLAYER_NAME] == MPD_NAME:
            self.player.update_mpd_database()

def main():
    """ Main method """

    peppy = Peppy()
    peppy.event_dispatcher.dispatch(peppy.player, peppy.shutdown)    
        
if __name__ == "__main__":
    main()
