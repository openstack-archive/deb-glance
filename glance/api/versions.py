# Copyright 2012 OpenStack Foundation.
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

from oslo_config import cfg
from oslo_log import log as logging
from oslo_serialization import jsonutils
from six.moves import http_client
import webob.dec

from glance.common import wsgi
from glance.i18n import _, _LW


versions_opts = [

    # Note: Since both glance-api and glare-api have the same name for the
    # option public_endpoint, oslo.config generator throws a DuplicateError
    # exception during the conf file generation incase of differing help
    # texts. Hence we have to have identical help texts for glance-api and
    # glare-api's public_endpoint if not for changing the conf opt name.

    cfg.StrOpt('public_endpoint',
               help=_("""
Public url endpoint to use for Glance/Glare versions response.

This is the public url endpoint that will appear in the Glance/Glare
"versions" response. If no value is specified, the endpoint that is
displayed in the version's response is that of the host running the
API service. Change the endpoint to represent the proxy URL if the
API service is running behind a proxy. If the service is running
behind a load balancer, add the load balancer's URL for this value.

Possible values:
    * None
    * Proxy URL
    * Load balancer URL

Related options:
    * None

""")),
]

CONF = cfg.CONF
CONF.register_opts(versions_opts)

LOG = logging.getLogger(__name__)


class Controller(object):

    """A wsgi controller that reports which API versions are supported."""

    def index(self, req, explicit=False):
        """Respond to a request for all OpenStack API versions."""
        def build_version_object(version, path, status):
            url = CONF.public_endpoint or req.host_url
            return {
                'id': 'v%s' % version,
                'status': status,
                'links': [
                    {
                        'rel': 'self',
                        'href': '%s/%s/' % (url, path),
                    },
                ],
            }

        version_objs = []
        if CONF.enable_v2_api:
            version_objs.extend([
                build_version_object(2.3, 'v2', 'CURRENT'),
                build_version_object(2.2, 'v2', 'SUPPORTED'),
                build_version_object(2.1, 'v2', 'SUPPORTED'),
                build_version_object(2.0, 'v2', 'SUPPORTED'),
            ])
        if CONF.enable_v1_api:
            LOG.warn(_LW('The Images (Glance) v1 API is deprecated and will '
                         'be removed on or after the Pike release, following '
                         'the standard OpenStack deprecation policy. '
                         'Currently, the solution is to set '
                         'enable_v1_api=False and enable_v2_api=True in your '
                         'glance-api.conf file. Once those options are '
                         'removed from the code, Images (Glance) v2 API will '
                         'be switched on by default and will be the only '
                         'option to deploy and use.'))
            version_objs.extend([
                build_version_object(1.1, 'v1', 'DEPRECATED'),
                build_version_object(1.0, 'v1', 'DEPRECATED'),
            ])

        status = explicit and http_client.OK or http_client.MULTIPLE_CHOICES
        response = webob.Response(request=req,
                                  status=status,
                                  content_type='application/json')
        response.body = jsonutils.dump_as_bytes(dict(versions=version_objs))
        return response

    @webob.dec.wsgify(RequestClass=wsgi.Request)
    def __call__(self, req):
        return self.index(req)


def create_resource(conf):
    return wsgi.Resource(Controller())
