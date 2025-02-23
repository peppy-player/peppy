/* Copyright 2024 Peppy Player peppy.player@gmail.com
 
This file is part of Peppy Player.
 
Peppy Player is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
 
Peppy Player is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
 
You should have received a copy of the GNU General Public License
along with Peppy Player. If not, see <http://www.gnu.org/licenses/>.
*/

import React from "react";
import Box from '@mui/material/Box';

export default class Image extends React.Component {
  render() {

    return (
        <Box style={{ width: '100px', height: '100px' }}>
              <img style={{ width: '100%', borderRadius: '4px', boxShadow: '4px 4px 8px rgba(0, 0, 0, 0.3)' }}
                src="images/abba.jpg"
                alt='cover'
              />
            </Box>
    );
  }
}
