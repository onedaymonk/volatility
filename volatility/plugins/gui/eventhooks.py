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

import volatility.utils as utils
import volatility.debug as debug
import volatility.plugins.gui.sessions as sessions

class EventHooks(sessions.Sessions):
    """Print details on windows event hooks"""

    @staticmethod
    def is_valid_profile(profile):
        version = (profile.metadata.get('major', 0), 
                   profile.metadata.get('minor', 0))

        return (profile.metadata.get('os', '') == 'windows' and
                version < (6, 2))

    def render_text(self, outfd, data):

        space = utils.load_as(self._config, astype = 'physical')
        
        if not self.is_valid_profile(space.profile):
            debug.error("This command does not support the selected profile.")

        for session in data:
            shared_info = session.find_shared_info()

            if not shared_info:
                continue

            filters = [lambda x : str(x.bType) == "TYPE_WINEVENTHOOK"]

            for handle in shared_info.handles(filters):

                outfd.write("Handle: {0:#x}, Object: {1:#x}, Session: {2}\n".format(
                    handle.phead.h if handle.phead else 0,
                    handle.phead.v(),
                    session.SessionId))

                outfd.write("Type: {0}, Flags: {1}, Thread: {2}, Process: {3}\n".format(
                    handle.bType,
                    handle.bFlags,
                    handle.Thread.Cid.UniqueThread,
                    handle.Process.UniqueProcessId,
                ))

                event_hook = handle.reference_object()

                outfd.write("eventMin: {0:#x} {1}\neventMax: {2:#x} {3}\n".format(
                    event_hook.eventMin.v(),
                    str(event_hook.eventMin),
                    event_hook.eventMax.v(),
                    str(event_hook.eventMax),
                    ))

                outfd.write("Flags: {0}, offPfn: {1:#x}, idProcess: {2}, idThread: {3}\n".format(
                    event_hook.dwFlags,
                    event_hook.offPfn,
                    event_hook.idProcess,
                    event_hook.idThread,
                    ))

                ## Work out the WindowStation\Desktop path by the handle            
                ## owner (thread or process)

                outfd.write("ihmod: {0}\n".format(event_hook.ihmod))
                outfd.write("\n")


