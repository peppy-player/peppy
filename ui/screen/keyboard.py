# Copyright 2019-2024 Peppy Player peppy.player@gmail.com
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

from ui.layout.borderlayout import BorderLayout
from ui.screen.menuscreen import MenuScreen
from ui.navigator.keyboard import KeyboardNavigator
from util.keys import KEY_CALLBACK, H_ALIGN_LEFT, KEY_DELETE, KEY_VIEW
from util.config import COLORS, COLOR_BRIGHT, COLOR_CONTRAST
from ui.keyboard.keyboard import Keyboard

# 480x320
PERCENT_TOP_HEIGHT = 14.0625
PERCENT_BOTTOM_HEIGHT = 14.0625

class KeyboardScreen(MenuScreen):
    """ Keyboard Screen """

    def __init__(self, title, util, listeners, show_visibility=True, max_text_length=64, min_text_length=0, search_by=None):
        """ Initializer

        :param util: utility object
        :param listeners: listeners
        :param max_text_length: maximum text length
        """
        self.util = util
        self.listeners = listeners
        layout = BorderLayout(util.screen_rect)
        layout.set_percent_constraints(PERCENT_TOP_HEIGHT, PERCENT_BOTTOM_HEIGHT, 0, 0)

        MenuScreen.__init__(self, util, listeners)
        self.screen_title.set_text(title)

        k_layout = BorderLayout(self.layout.CENTER)
        k_layout.set_percent_constraints(20, 0, 0, 0)

        font_size = int((k_layout.TOP.h * 50) / 100)
        fgr = util.config[COLORS][COLOR_BRIGHT]
        bgr = (0, 0, 0)
        bb = k_layout.TOP
        s_x = int(font_size/2)
        s_y = int(font_size/5)
        self.input_text = self.factory.create_output_text("kbd.text", bb, bgr, fgr, font_size, H_ALIGN_LEFT,
                                                          shift_x=s_x, shift_y=s_y, show_cursor=True, cursor_color=util.config[COLORS][COLOR_CONTRAST])
        self.input_text.obfuscate_flag = show_visibility
        self.add_component(self.input_text)
        self.other_components.append(self.input_text)

        keyboard_layout = k_layout.CENTER
        self.keyboard = Keyboard(util, keyboard_layout, listeners[KEY_CALLBACK], self, max_text_length=max_text_length, min_text_length=min_text_length, search_by=search_by)
        self.set_menu(self.keyboard)
        self.keyboard.add_text_listener(self.input_text.set_text)

        listeners[KEY_DELETE] = self.keyboard.delete
        listeners[KEY_VIEW] = self.input_text.obfuscate
        self.navigator = KeyboardNavigator(self.util, self.layout.BOTTOM, listeners, show_visibility)
        self.add_navigator(self.navigator)

        self.link_borders()
        self.input_text.add_cursor_listener(self.keyboard.set_cursor)

    def add_screen_observers(self, update_observer, redraw_observer):
        """ Add screen observers

        :param update_observer: observer for updating the screen
        :param redraw_observer: observer to redraw the whole screen
        """
        MenuScreen.add_screen_observers(self, update_observer, redraw_observer)
        self.update_observer = update_observer
        self.redraw_observer = redraw_observer
        self.keyboard.add_menu_observers(update_observer, redraw_observer)
        self.navigator.add_observers(update_observer, redraw_observer)
