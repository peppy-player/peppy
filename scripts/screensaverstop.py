# Copyright 2021 PeppyMeter peppy.player@gmail.com
# 
# This file is part of PeppyMeter.
# 
# PeppyMeter is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# PeppyMeter is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with PeppyMeter. If not, see <http://www.gnu.org/licenses/>.

import logging

class Screensaverstop(object):
    """ Example of the Screensaver Stop script """
        
    def __init__(self):
        """ Initializer """
        
        self.type = "sync"
        logging.debug("Screensaver Stop script initializer called")
            
    def start(self):
        """ Screensaver Stop script logic goes here """
        
        logging.debug("Running synchronous Screensaver Stop script")
