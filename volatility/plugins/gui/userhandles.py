# Volatility
# Copyright (C) 2007-2013 Volatility Foundation 
# Copyright (C) 2010,2011,2012 Michael Hale Ligh <michael.ligh@mnin.org>
#
# This file is part of Volatility.
#
# Volatility is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License Version 2 as
# published by the Free Software Foundation.  You may not use, modify or
# distribute this program under any other version of the GNU General
# Public License.
#
# Volatility is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Volatility.  If not, see <http://www.gnu.org/licenses/>.
#

import volatility.plugins.gui.sessions as sessions
import volatility.debug as debug
import volatility.utils as utils

class UserHandles(sessions.Sessions):
    """Dump the USER handle tables"""

    def __init__(self, config, *args, **kwargs):

        sessions.Sessions.__init__(self, config, *args, **kwargs)

        config.add_option('PID', short_option = 'p',
                help = 'Pid filter', action = 'store',
                type = 'int')

        config.add_option('TYPE', short_option = 't',
                help = 'Handle type', action = 'store',
                type = 'string')

        config.add_option('FREE', short_option = 'F',
                help = 'Include free handles', action = 'store_true',
                default = False)

    @staticmethod
    def is_valid_profile(profile):
        version = (profile.metadata.get('major', 0), 
                   profile.metadata.get('minor', 0))

        return (profile.metadata.get('os', '') == 'windows' and
                version < (6, 2))

    def render_text(self, outfd, data):

        space = utils.load_as(self._config, astype = 'physical')
        if not is_valid_profile(space.profile):
            debug.error("This command does not support the selected profile.")

        for session in data:
            shared_info = session.find_shared_info()

            if not shared_info:
                debug.debug("Cannot find win32k!gSharedInfo")
                continue

            outfd.write("*" * 50 + "\n")
            outfd.write("SharedInfo: {0:#x}, SessionId: {1} Shared delta: {2}\n".format(
                shared_info.obj_offset, session.SessionId,
                shared_info.ulSharedDelta,
            ))
            outfd.write("aheList: {0:#x}, Table size: {1:#x}, Entry size: {2:#x}\n".format(
                shared_info.aheList.v(),
                shared_info.psi.cbHandleTable,
                shared_info.HeEntrySize if hasattr(shared_info, 'HeEntrySize') else shared_info.obj_vm.profile.get_obj_size("_HANDLEENTRY"),
            ))
            outfd.write("\n")

            filters = []

            # Should we display freed handles
            if not self._config.FREE:
                filters.append(lambda x : not x.Free)

            # Should we filter by process ID
            if self._config.PID:
                filters.append(lambda x : x.Process.UniqueProcessId == self._config.PID)

            # Should we filter by object type
            if self._config.TYPE:
                filters.append(lambda x : str(x.bType) == self._config.TYPE)

            self.table_header(outfd,
                         [("Object(V)", "[addrpad]"),
                          ("Handle", "[addr]"),
                          ("bType", "20"),
                          ("Flags", "^8"),
                          ("Thread", "^8"),
                          ("Process", ""),
                         ])

            for handle in shared_info.handles(filters):

                self.table_row(outfd,
                               handle.phead.v(),
                               handle.phead.h if handle.phead else 0,
                               handle.bType,
                               handle.bFlags,
                               handle.Thread.Cid.UniqueThread,
                               handle.Process.UniqueProcessId)
