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

import pygame

from ui.component import Component
from ui.state import State
from ui.container import Container
from ui.layout.gridlayout import GridLayout
from ui.factory import Factory
from ui.button.button import Button
from operator import attrgetter
from util.config import BACKGROUND, MENU_BGR_COLOR
from util.keys import USER_EVENT_TYPE, SUB_TYPE_KEYBOARD, kbd_keys, kbd_num_keys, \
    KEY_LEFT, KEY_RIGHT, KEY_UP, KEY_DOWN, KEY_SELECT, SELECT_EVENT_TYPE
    
ALIGN_LEFT = "left"
ALIGN_CENTER = "center"
ALIGN_RIGHT = "right"

class Menu(Container):
    """ Base class for all menu components. Extends Container class. """
        
    def __init__(self, util, bgr=None, bb=None, rows=3, cols=3, create_item_method=None, menu_button_layout=None, font_size=None,
        align=ALIGN_CENTER, button_padding_x=None, bgr_component=None, horizontal_layout=True, column_weights=None):
        """ Initializer
        
        :param util: utility object
        :param bgr: menu background
        :param bb: bounding box
        :param rows: number of rows in menu
        :param cols: number of columns in menu
        :param create_item_method: factory method for menu item creation
        :param menu_button_layout: menu buttons layout
        :param font_size: font size
        :param align: label alignment
        :param button_padding_x: padding X
        :param bgr_component: menu background component
        :param horizontal_layout: True - horizontal layout, False - vertical layout
        :param column_weights: list with column weights
        """        
        Container.__init__(self, util, bb, bgr)
        self.content = None
        self.bb = bb
        self.rows = rows
        self.cols = cols
        self.util = util
        self.menu_button_layout = menu_button_layout
        self.start_listeners = []
        self.move_listeners = []
        self.menu_loaded_listeners = []
        self.font_size = font_size
        self.button_padding_x = button_padding_x
        self.horizontal_layout = horizontal_layout
        self.column_weights = column_weights
               
        self.buttons = {}
        self.factory = Factory(util)
        self.create_item_method = create_item_method
        self.selected_index = None
        self.align = align

        self.update_observer = None
        self.redraw_observer = None
        self.press = False
        self.release = False
        self.in_motion = False

        if bgr_component:
            self.add_component(bgr_component)

    def set_parent_screen(self, scr):
        """ Add parent screen

        :param scr: parent screen
        """
        self.parent_screen = scr
        for b in self.buttons.values():
            b.parent_screen = scr

    def set_items(self, it, page_index, listener, scale=True, order=None, fill=False, append_right=None, lazy_load_images=False):
        """ Set menu items
        
        :param it: menu items
        :param page_index: menu page number
        :param listener: event listener
        :param scale: True - scale menu items, False - don't scale menu items
        :param order: map defining the order of menu items
        :param fill: True - fill gaps with empty spacers, False - don't fill
        :param append_right: None - don't append to existing buttons, True - append to the right side, False - to the left
        :param lazy_load_images: True - load images after menu creation, False - don't lazy load
        """
        if not it:
            return

        self.layout = self.get_layout(it)
        self.layout.current_constraints = 0

        if append_right == None:
            self.components = []
            self.buttons = dict()

        if fill:
            self.spacers = (self.rows * self.cols) - len(it)
        
        if not order:
            sorted_items = sorted(it.values(), key=attrgetter('index'))
        else:
            sorted_items = self.sort_items(it.items(), order)         
        
        for index, item in enumerate(sorted_items):
            i = getattr(item, "index", None)
            if i == None:
                item.index = index
            constr = self.layout.get_next_constraints()

            if append_right == True:
                constr.x += self.bounding_box.w - 1
            elif append_right == False:
                constr.x -= self.bounding_box.w - 1

            if getattr(item, "long_press", False):
                item.long_press = False
            
            if self.menu_button_layout:            
                button = self.create_item_method(item, constr, self.item_selected, scale, menu_button_layout=self.menu_button_layout)
            else:
                if self.font_size:
                    button = self.create_item_method(item, constr, self.item_selected, scale, self.font_size)
                else:
                    button = self.create_item_method(item, constr, self.item_selected, scale)
            
            if listener:
                button.add_release_listener(listener)
            comp_name = ""
            if item.name:
                comp_name = item.name
                try:
                    if self.buttons[comp_name]:
                        comp_name += str(index)
                except:
                    pass
            button.add_press_listener(self.press_button_listener)
            self.add_component(button)
            self.buttons[comp_name] = button

        if fill and self.spacers > 0:
            for s in range(self.spacers):
                content = self.layout.get_next_constraints()
                b = self.util.config[BACKGROUND][MENU_BGR_COLOR]
                c = Component(self.util, content, bb=content, bgr=b)
                c.name = "spacer." + str(s)
                state = State()
                state.bounding_box = None
                state.l_name = ""
                c.state = state

                if append_right == None:
                    c.components = []

                if append_right == True:
                    c.content.x += self.bounding_box.w - 1
                elif append_right == False:
                    c.content.x -= self.bounding_box.w - 1

                self.add_component(c)
        
        self.align_content(self.align, lazy_load_images)
        self.add_button_observers()
        self.notify_menu_loaded_listeners()
        self.column_width = self.bb.w / self.cols

    def get_layout(self, items):
        """ Create menu layout for provided items
        
        :param items: menu items
        
        :return: menu layout
        """
        if not items:
            return

        layout = GridLayout(self.bb, self.horizontal_layout, getattr(self, "column_weights", None))
        n = len(items)
        
        if self.rows == 1 and self.cols == None:
            layout.set_pixel_constraints(1, n, 1, 1)
        elif self.rows and self.cols:
            layout.set_pixel_constraints(self.rows, self.cols, 1, 1)
        else:
            if n == 1:
                self.rows = 1
                self.cols = 1
            elif n == 2:
                self.rows = 1
                self.cols = 2
            elif n == 3 or n == 4:
                self.rows = 2
                self.cols = 2
            elif n == 5 or n == 6:
                self.rows = 2
                self.cols = 3
            elif n == 7 or n == 9:
                self.rows = 3
                self.cols = 3
            elif n == 8:
                self.rows = 2
                self.cols = 4
            elif n == 10 or n == 11 or n == 12:
                self.rows = 3
                self.cols = 4
            else:
                self.rows = 3
                self.cols = 5
            layout.set_pixel_constraints(self.rows, self.cols, 1, 1)
        return layout 
            
    def align_content(self, align, lazy_load_images=False):
        """ Align menu button content
        
        :param align: alignment type
        :param lazy_load_images: True - load images after menu creation, False - don't lazy load
        """
        if not self.components:
            return
        
        b = self.components[0]

        if lazy_load_images or (b.components[1] and b.components[1].content):
            button_has_image = True
        else:
            button_has_image = False

        fixed_height = getattr(b.state, "fixed_height", None)
        if fixed_height:
            font_size = fixed_height
        else:
            if button_has_image:
                if b.components[2]:
                    vert_gap = 4 #percent
                    label_area_percent = getattr(b.state, "label_area_percent", None)
                    if not label_area_percent:
                        label_area_percent = getattr(b.state, "label_text_height", None)
                    font_size = int(b.bounding_box.h - (b.bounding_box.h * (100 - label_area_percent + vert_gap))/100)
                else:
                    font_size = 0
            else:
                font_size = int((b.bounding_box.h * b.state.label_text_height)/100.0)
        
        longest_string = ""
        icon_max_width = 0
        
        for b in self.components:
            if hasattr(b, "state") and len(b.state.l_name) > len(longest_string):
                longest_string = b.state.l_name
            if hasattr(b, "components") and len(b.components) > 0 and b.components[1] and b.components[1].content:
                if isinstance(b.components[1].content, tuple):
                    content = b.components[1].content[1]
                else:
                    content = b.components[1].content

                if content:
                    w = content.get_size()[0]
                    icon_max_width = max(w, icon_max_width)
            
        font = self.util.get_font(font_size)
        label_size = font.size(longest_string)

        if label_size[0] >= b.bounding_box.w:
            final_size = (b.bounding_box.w, label_size[1])
        else:
            final_size = label_size

        if self.button_padding_x:
            padding_x = int((b.bounding_box.w * self.button_padding_x) /100)
        else:
            padding_x = getattr(b.state, "padding", 0)
            padding_x = int((b.bounding_box.w / 100) * padding_x)

        for button in self.components:
            if not isinstance(button, Button) or len(button.components) == 0:
                continue

            comps = button.components
            d = (button.bounding_box.w - final_size[0]) / 2

            if lazy_load_images or (button.components[1] and button.components[1].content):
                button_has_image = True
            else:
                button_has_image = False

            if button_has_image:
                continue

            if align == ALIGN_LEFT:
                x = button.bounding_box.x
                if comps[2]:
                    if button_has_image:
                        comps[2].content_x = x + icon_max_width
                    else:
                        comps[2].content_x = x + d
                        if len(comps) == 4 and padding_x > d or d < 3:
                            comps[2].content_x += padding_x
                if len(comps) == 4:
                    if button_has_image:
                        comps[3].content_x = x + icon_max_width
                    else:
                        comps[3].content_x = x + d
                        if padding_x > d:
                            comps[3].content_x += padding_x
                if button_has_image:
                    comps[1].content_x = int(button.bounding_box.x + padding_x + (icon_max_width - comps[1].content[1].get_size()[0]) / 2)
            elif align == ALIGN_RIGHT:
                x = button.bounding_box.x + button.bounding_box.w - padding_x

                if comps[2]:
                    comps[2].content_x = x - comps[2].content.get_size()[0] - icon_max_width - padding_x

                if len(comps) == 4:
                    comps[3].content_x = x - comps[3].content.get_size()[0] - icon_max_width - padding_x

                if button_has_image:
                    comps[1].content_x = x - comps[1].content[1].get_size()[0]
            else:
                if button_has_image:
                    if comps[2]:
                        comps[2].content_x = int(button.bounding_box.x + (button.bounding_box.w - comps[2].content.get_size()[0]) / 2)
                else:
                    comps[2].content_x = int(button.bounding_box.x + (button.bounding_box.w - comps[2].content.get_size()[0]) / 2)

    def sort_items(self, d, order):
        """ Sort items according to the specified order
        
        :param d: items to sort
        :param order: order of menu items
        """
        sorted_items = [None] * len(d)
        for t in d:
            k = t[0]
            index = int(order[k.lower()]) - 1
            t[1].index = index          
            sorted_items[index] = t[1]
        return sorted_items 

    def press_button_listener(self, state):
        """ Press button handler

        :param state: button state
        """
        s_comp = self.get_comparator(state)
        for button in self.buttons.values():
            b_comp = getattr(button.state, "comparator_item", None)

            redraw = False
            if b_comp != None and s_comp != None and b_comp != s_comp and button.selected:
                redraw = True

            if redraw and self.visible:
                button.clean_draw_update()
                if self.update_observer:
                    self.update_observer(button.state)

    def item_selected(self, state=None):
        """ Handle menu item selection
        
        :param state: button state
        """
        s_comp = self.get_comparator(state)
        button_exist = False
        for button in self.buttons.values():
            b_comp = getattr(button.state, "comparator_item", None)
            if b_comp != None and s_comp != None and b_comp == s_comp:
                button_exist = True
                break
        
        if not button_exist:
            return

        for button in self.buttons.values():
            b_comp = getattr(button.state, "comparator_item", None)

            redraw = False
            if b_comp != None and s_comp != None and b_comp == s_comp:
                if not button.selected:
                    button.set_selected(True)
                    redraw = True
                self.selected_index = button.state.index
            else:
                button.set_selected(False)
                redraw = True              

            if redraw and self.visible:
                button.clean_draw_update()
                if self.update_observer:
                    self.update_observer(button.state)

    def get_comparator(self, state):
        """ Return comparator object from state
        
        :param state: state object containing comparator item
        """
        return getattr(state, "comparator_item", None)
    
    def add_listener(self, listener):
        """ Add menu event listener
        
        :param listener: event listener
        """
        if listener not in self.start_listeners:
            self.start_listeners.append(listener)
            
    def notify_listeners(self, state):
        """ Notify all menu listeners
        
        :param state: button state
        """
        for listener in self.start_listeners:
            listener(state)
            
    def add_move_listener(self, listener):
        """ Add arrow button event listener
        
        :param listener: event listener
        """
        if listener not in self.move_listeners:
            self.move_listeners.append(listener)
            
    def notify_move_listeners(self):
        """ Notify arrow button event listeners """
        
        for listener in self.move_listeners:
            listener(None)
    
    def add_menu_loaded_listener(self, listener):
        """ Add menu loaded event listener
        
        :param listener: event listener
        """
        if listener not in self.menu_loaded_listeners:
            self.menu_loaded_listeners.append(listener)
            
    def notify_menu_loaded_listeners(self):
        """ Notify all menu loaded listeners
        
        :param state: button state
        """
        for listener in self.menu_loaded_listeners:
            listener(self)
            
    def unselect(self):
        """ Unselect currently selected button
        
        :return: index of the button which was selected
        """
        for button in self.buttons.values():
            if button.selected:
                button.set_selected(False)
                if self.visible:
                    button.clean_draw_update()
                return button.state.index
        self.selected_index = -1
    
    def get_selected_index(self):
        """ Return the index of the button which was selected
        
        :return: index of the selected button
        """
        item = self.get_selected_item()
        if item != None:
            return item.state.index
        else:
            return None

    def get_selected_item(self):
        """ Return the selected item

        :return: selected item
        """
        for button in self.buttons.values():
            if button.selected:
                return button
        return None    

    def select_by_index(self, index):
        """ Select button by specified index
        
        :param index: button index
        """
        selected = False
        for button in self.buttons.values():
            if button.state.index == index:
                button.set_selected(True)
                if self.visible:
                    button.clean_draw_update()
                self.selected_index = index
                self.notify_move_listeners()
                selected = True
                break
        return selected

    def select_action(self):
        """ Notify listeners of the selected button """
        
        for button in self.buttons.values():
            if button.state.index == self.selected_index:
                button.notify_release_listeners(button.state)
                break
            
    def is_enabled(self, i):
        """ Check if the button is enabled. 
        Disabled buttons have enabled flag set to False. 
        Enabled buttons don't have this flag  
        
        :param index: button index
        :return: True - button enabled, False - button disabled
        """
        for button in self.buttons.values():
            enabled = getattr(button.state, "enabled", None)
            if button.state.index == i and enabled == None:
                return True
        return False
    
    def make_dict(self, page):
        """ Create dictionary from the list
        
        :param page: the input list
        
        :return: dictionary where key - index, value - object
        """
        if not page:
            return

        return {i : item for i, item in enumerate(page)}

    def handle_number_key(self, event):
        """ Handle keyboard number key

        :param event: keyboard event
        """
        cp = getattr(self, "current_page", None)
        if cp:
            prefix = (cp - 1) * (self.rows * self.cols)
        else:
            prefix = 0

        if kbd_num_keys[event.keyboard_key] == 0:
            i = prefix + 9
        else:
            i = (kbd_num_keys[event.keyboard_key] - 1) + prefix

        if self.is_enabled(i):
            self.unselect()
            self.select_by_index(i)
            self.select_action()

    def handle_event(self, event):
        """ Menu event handler
        
        :param event: menu event
        """
        if not self.visible: return
        
        if event.type == USER_EVENT_TYPE and event.sub_type == SUB_TYPE_KEYBOARD and event.action == pygame.KEYUP:
            key_events = [kbd_keys[KEY_LEFT], kbd_keys[KEY_RIGHT], kbd_keys[KEY_UP], kbd_keys[KEY_DOWN]]
            i = None

            if event.keyboard_key in kbd_num_keys.keys():
                self.handle_number_key(event)
                return

            if event.keyboard_key in key_events:
                i = self.get_selected_index()
                if i == None:
                    return

                if self.horizontal_layout:
                    row = int(i / self.cols)
                else:
                    row = int(i % self.rows)

                first_index = self.components[0].state.index

                non_spacer_components = []
                for c in self.components[0 : self.cols * self.rows]:
                    if hasattr(c.state, "name") and not c.state.name.startswith("spacer.") or hasattr(c, "name") and not c.name.startswith("spacer."):
                        non_spacer_components.append(c)

                last_index = self.components[len(non_spacer_components) - 1].state.index

            if event.keyboard_key == kbd_keys[KEY_SELECT]:
                self.select_action()
                return
             
            if event.keyboard_key == kbd_keys[KEY_LEFT]:
                if i == first_index:
                    if self.exit_menu(self.exit_top_y, event, self.exit_left_x):
                        return
                else:
                    i -= 1
            elif event.keyboard_key == kbd_keys[KEY_RIGHT]:
                if i == last_index:
                    if self.exit_menu(self.exit_top_y, event, self.exit_right_x):
                        return
                else:
                    i += 1
            elif event.keyboard_key == kbd_keys[KEY_UP]:
                cp = getattr(self, "current_page", None)
                if self.horizontal_layout:
                    if row == 0 or (cp and ((cp - 1) * self.rows) == row):
                        if self.exit_menu(self.exit_top_y, event):
                            return
                        i = i + (self.rows - 1) * self.cols
                    else:
                        i = i - self.cols
                else:
                    if row == 0:
                        if self.exit_menu(self.exit_top_y, event):
                            return
                        i = i + self.rows - 1
                    else:
                        i = i - 1
            elif event.keyboard_key == kbd_keys[KEY_DOWN]:
                selected_item = self.get_selected_item()
                if selected_item != None:
                    x = selected_item.bounding_box.x + selected_item.bounding_box.w / 2
                    h = selected_item.bounding_box.h
                    y = selected_item.bounding_box.y + h + (h / 2)
                    button_below = self.get_clicked_menu_button(x, y)
                    if button_below == None:
                        if self.exit_menu(self.exit_bottom_y, event):
                            return    

                if self.horizontal_layout:
                    if row == self.rows - 1:
                        if self.exit_menu(self.exit_bottom_y, event):
                            return
                        i = int(i % self.cols)
                    else:
                        i = i + self.cols
                else:
                    if row == self.rows - 1:
                        if self.exit_menu(self.exit_bottom_y, event):
                            return
                        i = i - self.rows + 1
                    else:
                        i = i + 1

            if i == None:
                return

            if self.is_enabled(i):
                self.unselect()
                self.select_by_index(i)
            else:
                if not self.is_enabled(i + 1) and self.exit_menu(self.exit_top_y, event, self.exit_right_x):
                    return
        elif event.type == SELECT_EVENT_TYPE:
            if event.source == self:
                return
            self.handle_select_action(event.x, event.y)
        elif event.type == pygame.MOUSEMOTION and event.buttons[0] == 1:
            self.handle_motion_action(event)
        else:
            Container.handle_event(self, event) 

    def start_motion(self, event):
        """ Scrollable subclasses should implement this function

        :param event: motion event
        """
        pass

    def stop_motion(self):
        """ Scrollable subclasses should implement this function """

        pass

    def handle_motion_action(self, event):
        """ Scrollable subclasses should implement this function """

        pass

    def exit_menu(self, exit_border, event, exit_x=None):
        """ Exit menu

        :param exit_border: exit border
        :Param event: exit event
        """
        item = self.get_selected_item()
        if exit_border == None or item == None or event.action != pygame.KEYUP:
            return False
        
        if not exit_x:
            x = int(item.bounding_box.x + (item.bounding_box.w / 2))
        else:
            x = exit_x

        y = exit_border
        self.unselect()
        self.util.post_exit_event(x, y, self)
        self.selected_index = -1
        if self.redraw_observer:
            self.redraw_observer()
        return True

    def handle_select_action(self, x, y):
        """ Handle select action

        :param x: x coordinate
        :param y: y coordinate
        """
        clicked_button = self.get_clicked_menu_button(x, y)
        if clicked_button != None:
            self.select_by_index(clicked_button.state.index)

    def get_clicked_menu_button(self, x, y):
        if self.buttons:
            for button in self.buttons.values():
                if button.bounding_box.collidepoint((x, y)):
                    return button
        return None

    def add_button_observers(self):
        for b in self.buttons.values():
            Container.add_button_observers(self, b, self.update_observer, self.redraw_observer, self.press, self.release)

    def add_menu_observers(self, update_observer, redraw_observer=None, press=True, release=True):
        """ Add menu observer
        
        :param update_observer: observer for updating menu
        :param redraw_observer: observer to redraw the whole screen
        :param press: True - add observer as press listener (default)
        :param release: True - add observer as release listener (default)
        """
        self.update_observer = update_observer
        self.redraw_observer = redraw_observer
        self.press = press
        self.release = release
        self.add_button_observers()

        if redraw_observer:
            self.add_move_listener(redraw_observer)
            self.add_listener(redraw_observer)
            