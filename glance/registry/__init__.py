# Copyright 2010-2011 OpenStack Foundation
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""
Registry API
"""

from oslo_config import cfg

from glance.i18n import _


registry_addr_opts = [
    cfg.StrOpt('registry_host', default='0.0.0.0',
               help=_("""
Address the registry server is hosted on.

Possible values:
    * A valid IP or hostname

Related options:
    * None

""")),
    cfg.PortOpt('registry_port', default=9191,
                help=_("""
Port the registry server is listening on.

Possible values:
    * A valid port number

Related options:
    * None

""")),
]

CONF = cfg.CONF
CONF.register_opts(registry_addr_opts)
