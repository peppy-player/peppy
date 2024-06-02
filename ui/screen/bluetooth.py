# Copyright 2020-2023 Peppy Player peppy.player@gmail.com
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

import math
import logging

from ui.layout.borderlayout import BorderLayout
from ui.factory import Factory
from ui.screen.menuscreen import MenuScreen
from ui.menu.menu import ALIGN_LEFT
from util.config import LABELS
from ui.menu.multipagemenu import MultiPageMenu
from util.bluetoothutil import MENU_ROWS_BLUETOOTH, MENU_COLUMNS_BLUETOOTH, PAGE_SIZE_BLUETOOTH
from ui.navigator.bluetooth import BluetoothNavigator
from util.keys import KEY_HOME, KEY_NETWORK, KEY_REFRESH, KEY_PLAYER, KEY_PAGE_DOWN, KEY_PAGE_UP, KEY_NETWORK

# 480x320
PERCENT_TOP_HEIGHT = 14.0625
PERCENT_BOTTOM_HEIGHT = 14.0625

class BluetoothScreen(MenuScreen):
    """ Bluetooth Screen """

    def __init__(self, util, listeners):
        """ Initializer

        :param util: utility object
        :param listeners: listeners
        """
        self.util = util
        self.config = util.config
        self.listeners = listeners
        self.factory = Factory(util)
        self.go_home = listeners[KEY_HOME]
        self.go_network = listeners[KEY_NETWORK]
        self.go_player = listeners[KEY_PLAYER]

        self.wifi_selection_listeners = []

        self.bluetooth_util = self.util.get_bluetooth_util()
        self.bounding_box = util.screen_rect
        layout = BorderLayout(self.bounding_box)
        layout.set_percent_constraints(PERCENT_TOP_HEIGHT, PERCENT_BOTTOM_HEIGHT, 0, 0)

        d = [MENU_ROWS_BLUETOOTH, MENU_COLUMNS_BLUETOOTH]
        MenuScreen.__init__(self, util, listeners, d, self.turn_page, page_in_title=False, show_loading=False)
        self.title = self.config[LABELS]["select.bluetooth.device"]
        self.set_title(1)

        listeners[KEY_HOME] = self.before_home
        listeners[KEY_NETWORK] = self.before_network
        listeners[KEY_PLAYER] = self.before_player
        listeners[KEY_REFRESH] = self.set_current

        self.navigator = BluetoothNavigator(self.util, self.layout.BOTTOM, listeners, PAGE_SIZE_BLUETOOTH + 1)
        self.add_navigator(self.navigator)
        self.network_button = self.navigator.get_button_by_name(KEY_NETWORK)
        self.left_button = self.navigator.get_button_by_name(KEY_PAGE_DOWN)
        self.right_button = self.navigator.get_button_by_name(KEY_PAGE_UP)

        m = self.factory.create_wifi_menu_button
        font_height = 32
        font_size = int(((self.menu_layout.h / MENU_ROWS_BLUETOOTH) / 100) * font_height)
        self.bluetooth_menu = MultiPageMenu(util, self.next_page, self.previous_page, self.set_title, self.reset_title,
                                       self.go_to_page, m, MENU_ROWS_BLUETOOTH, MENU_COLUMNS_BLUETOOTH, None,
                                       (0, 0, 0), self.menu_layout, align=ALIGN_LEFT, font_size=font_size)
        self.set_menu(self.bluetooth_menu)

        self.devices = None
        self.networks = None
        self.sort_direction = False
        self.current_device = None

    def set_current(self, state):
        """ Set current state

        :param state: button state
        """
        self.set_loading(self.title)
        self.bluetooth_util.start_scan()
        self.devices = self.bluetooth_util.get_available_devices()

        if not self.devices:
            self.reset_loading()
            self.left_button.change_label("0")
            self.right_button.change_label("0")
            if not self.navigator.is_selected():
                self.network_button.set_selected(True)
                self.link_borders()
            self.clean_draw_update()
            return

        d = self.bluetooth_util.get_connected_device()
        if d:
            self.current_device = d
        else:
            self.current_device = None

        self.total_pages = math.ceil(len(self.devices) / PAGE_SIZE_BLUETOOTH)
        self.reset_loading()

        self.current_page = self.bluetooth_util.get_page_num(self.current_device, self.devices)
        if not self.current_page:
            self.current_page = 1

        self.turn_page()

    def select_network(self, state=None):
        """ Select network from menu

        :param state: button state
        """
        if hasattr(state, "mac_address") and self.bluetooth_util.is_device_connected(state.mac_address):
            self.before_network(state)
            return

        state.source = "bluetooth"
        self.notify_wifi_selection_listeners(state.name)
        self.before_network(state)

    def turn_page(self):
        """ Turn page """

        p = self.bluetooth_util.get_page(self.current_page, self.devices)
        try:
            self.bluetooth_menu.set_items(p, 0, self.select_network, False)
        except Exception as e:
            logging.debug(e)

        if len(self.devices) != 0 and self.navigator and self.total_pages > 1:
            self.left_button.change_label(str(self.current_page - 1))
            self.right_button.change_label(str(self.total_pages - self.current_page))

        self.set_title(self.current_page)
        self.bluetooth_menu.clean_draw_update()

        if hasattr(self, "update_observer"):
            self.bluetooth_menu.add_menu_observers(self.update_observer, self.redraw_observer)

        self.bluetooth_menu.unselect()
        for b in self.bluetooth_menu.buttons.values():
            if self.current_device and self.current_device["name"] == b.state.name:
                self.bluetooth_menu.select_by_index(b.state.index)
                break
        
        if self.bluetooth_menu.get_selected_item() != None:
            self.navigator.unselect()
        else:
            if not self.navigator.is_selected():
                self.network_button.set_selected(True)

        self.link_borders()

    def before_home(self, state):
        """ Stop bluetooth scanning and go to home screen

        :param state: button state
        """
        self.bluetooth_util.stop_scan()
        self.go_home(state)

    def before_network(self, state):
        """ Stop bluetooth scanning and go to network screen

        :param state: button state
        """
        self.bluetooth_util.stop_scan()
        self.go_network(state)

    def before_player(self, state):
        """ Stop bluetooth scanning and go to player screen

        :param state: button state
        """
        self.bluetooth_util.stop_scan()
        self.go_player(state)

    def add_bluetooth_selection_listener(self, listener):
        """ Add listener

        :param listener: event listener
        """
        if listener not in self.wifi_selection_listeners:
            self.wifi_selection_listeners.append(listener)

    def notify_wifi_selection_listeners(self, selected_wifi):
        """ Notify all listeners

        :param selected_wifi:
        """
        for listener in self.wifi_selection_listeners:
            listener(selected_wifi)

    def add_screen_observers(self, update_observer, redraw_observer):
        """ Add screen observers

        :param update_observer: observer for updating the screen
        :param redraw_observer: observer to redraw the whole screen
        """
        MenuScreen.add_screen_observers(self, update_observer, redraw_observer)
        self.update_observer = update_observer
        self.redraw_observer = redraw_observer
        self.add_loading_listener(redraw_observer)
        self.navigator.add_observers(update_observer, redraw_observer)

    def handle_event(self, event):
        """ Handle screen event

        :param event: the event to handle
        """
        self.handle_event_common(event)
