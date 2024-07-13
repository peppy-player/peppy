# Copyright 2022-2024 Peppy Player peppy.player@gmail.com
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

import time

from ui.state import State
from ui.player.fileplayer import FilePlayerScreen
from util.config import *
from util.fileutil import FILE_AUDIO
from util.keys import *

class YaPlaylistPlayerScreen(FilePlayerScreen):
    """ YA Stream Player Screen """
    
    def __init__(self, listeners, util, get_current_playlist, volume_control):
        """ Initializer
        
        :param listeners: screen listeners
        :param util: utility object
        :param get_current_playlist: current playlist getter
        :param volume_control: volume control
        """
        self.ya_stream_util = util.ya_stream_util
        FilePlayerScreen.__init__(self, listeners, util, get_current_playlist, volume_control)
        self.center_button.state.name = ""
        self.screen_title.active = True

    def set_current(self, state=None):
        """ Set current stream
        
        :param state: button state
        """
        self.config[KEY_YA_STREAM_CURRENT_PLAYER] = KEY_YA_PLAYLIST_PLAYER
        loading = False

        source = getattr(state, "source", None)
        if source == KEY_YA_STREAM_PLAYLIST_BROWSER or source == ARROW_BUTTON or source == INIT:
            self.time_control.reset()
            self.set_loading()
            loading = True
            self.ya_stream_util.get_playlist_stream_properties(state, self.bounding_box)
        elif source == RESUME:
            state = self.ya_stream_util.get_stream_by_id(self.config[YA_STREAM][YA_STREAM_ID])
        elif source == KEY_HOME or source == GO_PLAYER or source == KEY_BACK:
            return

        if not hasattr(state, "url"):
            if loading:
                self.reset_loading()
            self.clean_draw_update()
            return

        self.config[YA_STREAM][YA_STREAM_ID] = state.id
        self.config[YA_STREAM][YA_STREAM_NAME] = state.l_name
        self.config[YA_STREAM][YA_STREAM_URL] = state.url
        self.config[YA_STREAM][YA_THUMBNAIL_PATH] = state.image_path
        if hasattr(state, "time"):
            self.config[YA_STREAM][YA_PLAYLIST_TIME] = state.time
        if not hasattr(state, "index"):
            state.index = self.ya_stream_util.get_index_by_id(state.id)

        if state != None:
            self.center_button.state.name = state.l_name
            self.center_button.state.url = state.url

        self.screen_title.set_text(state.l_name)

        if getattr(state, "image_path", None) != None and getattr(state, "full_screen_image", None) == None:
            img = self.ya_stream_util.get_thumbnail(state.image_path, 1.0, 1.0, self.bounding_box)
            if img:
                state.full_screen_image = img[1]

        self.set_center_button((state.image_path, state.full_screen_image))
        self.center_button.clean()
        self.center_button.draw()
        
        config_volume_level = int(self.config[PLAYER_SETTINGS][VOLUME])
         
        if state:
            state.volume = config_volume_level
        
        self.set_audio_file(state)

        if source == KEY_YA_STREAM_PLAYLIST_BROWSER or source == ARROW_BUTTON or source == INIT:
            self.clean_draw_update()

        if loading:
            self.reset_loading()

        if self.volume.get_position() != config_volume_level:
            self.volume.set_position(config_volume_level)
            self.volume.update_position()

        self.update_component = True
        
    def is_valid_mode(self):
        """ Check that current mode is valid mode
        
        :return: True - SA Stream mode is valid
        """
        return True

    def set_current_track_index(self, state):
        """ Set current track index

        :param state: state object representing current track
        """
        if not self.is_valid_mode(): return

        self.current_track_index = 0

        if self.playlist_size == 1:
            return

        if not self.audio_files:
            self.audio_files = self.get_audio_files()
            if not self.audio_files: return

        self.current_track_index = self.get_current_track_index(state)
        self.update_component = True

    def get_current_track_index(self, state=None):
        """ Return current track index.
        
        :param state: button state
        
        :return: current track index
        """
        state_id = self.get_id(state["file_name"])
        for i, f in enumerate(self.audio_files):
            link = getattr(f, "url", None)
            if link:
                import urllib.parse
                link = urllib.parse.unquote(link)
                link_id = self.get_id(link)

                if state_id == link_id:
                    return i
        return 0

    def get_id(self, link):
        """ Get stream ID from the link

        :param link: stream link

        :return: stream ID
        """
        token = "&id="
        start = link.find(token)

        if start != -1:
            stop = link.find("&", start + len(token))
        else:
            return None

        id = link[start + len(token): stop]
        return id

    def set_audio_file(self, s=None):
        """ Set new stream
        
        "param s" button state
        """
        state = State()
        state.folder = PODCASTS_FOLDER        
        state.url = s.url
            
        self.config[PLAYER_SETTINGS][PAUSE] = False
        state.mute = self.config[PLAYER_SETTINGS][MUTE]
        state.pause = self.config[PLAYER_SETTINGS][PAUSE]
        state.file_type = FILE_AUDIO
        state.dont_notify = True
        state.source = FILE_AUDIO 
        state.playback_mode = FILE_AUDIO
        state.index = s.index

        if hasattr(s, "file_name"):      
            state.file_name = s.file_name
        source = None
        if s:
            source = getattr(s, "source", None)

        tt = self.config[YA_STREAM][YA_PLAYLIST_TIME]
                    
        if (isinstance(tt, str) and len(tt) != 0) or (isinstance(tt, float) or (source and source == RESUME)) or isinstance(tt, int):
            state.track_time = tt
        
        self.time_control.slider.set_position(0)
            
        if self.center_button and self.center_button.components[1] and self.center_button.components[1].content:
            state.icon_base = self.center_button.components[1].content
        
        if s:
            if self.config[VOLUME_CONTROL][VOLUME_CONTROL_TYPE] == VOLUME_CONTROL_TYPE_PLAYER:
                state.volume = s.volume
            else:
                state.volume = None
            
        if getattr(s, "full_screen_image", None) != None:
             state.full_screen_image = s.full_screen_image

        self.notify_play_listeners(state)

    def change_track(self, track_index):
        """ Change track
        
        :param track_index: track index
        """        
        s = self.audio_files[track_index]
        self.stop_player()
        self.stop_timer()
        self.ya_stream_util.get_playlist_stream_properties(s, self.bounding_box)
        time.sleep(0.3)
        s.source = ARROW_BUTTON
        self.set_current(s)

    def start_timer(self):
        """ Start time control timer """
        
        self.time_control.start_timer()

    def get_audio_files(self):
        """ Return the list of audio files in current folder
        
        :return: list of audio files
        """
        return self.ya_stream_util.get_ya_stream_playlist()