# Copyright 2011 OpenStack Foundation
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
A filter middleware that inspects the requested URI for a version string
and/or Accept headers and attempts to negotiate an API controller to
return
"""

from oslo_config import cfg
from oslo_log import log as logging

from glance.api.glare import versions as artifacts_versions
from glance.api import versions
from glance.common import wsgi

CONF = cfg.CONF

LOG = logging.getLogger(__name__)


class VersionNegotiationFilter(wsgi.Middleware):

    def __init__(self, app):
        self.versions_app = versions.Controller()
        self.allowed_versions = None
        self.vnd_mime_type = 'application/vnd.openstack.images-'
        super(VersionNegotiationFilter, self).__init__(app)

    def process_request(self, req):
        """Try to find a version first in the accept header, then the URL"""
        args = {'method': req.method, 'path': req.path, 'accept': req.accept}
        LOG.debug("Determining version of request: %(method)s %(path)s "
                  "Accept: %(accept)s", args)

        # If the request is for /versions, just return the versions container
        if req.path_info_peek() == "versions":
            return self.versions_app.index(req, explicit=True)

        accept = str(req.accept)
        if accept.startswith(self.vnd_mime_type):
            LOG.debug("Using media-type versioning")
            token_loc = len(self.vnd_mime_type)
            req_version = accept[token_loc:]
        else:
            LOG.debug("Using url versioning")
            # Remove version in url so it doesn't conflict later
            req_version = self._pop_path_info(req)

        try:
            version = self._match_version_string(req_version)
        except ValueError:
            LOG.debug("Unknown version. Returning version choices.")
            return self.versions_app

        req.environ['api.version'] = version
        req.path_info = ''.join(('/v', str(version), req.path_info))
        LOG.debug("Matched version: v%d", version)
        LOG.debug('new path %s', req.path_info)
        return None

    def _get_allowed_versions(self):
        allowed_versions = {}
        if CONF.enable_v1_api:
            allowed_versions['v1'] = 1
            allowed_versions['v1.0'] = 1
            allowed_versions['v1.1'] = 1
        if CONF.enable_v2_api:
            allowed_versions['v2'] = 2
            allowed_versions['v2.0'] = 2
            allowed_versions['v2.1'] = 2
            allowed_versions['v2.2'] = 2
            allowed_versions['v2.3'] = 2
        return allowed_versions

    def _match_version_string(self, subject):
        """
        Given a string, tries to match a major and/or
        minor version number.

        :param subject: The string to check
        :returns: version found in the subject
        :raises: ValueError if no acceptable version could be found
        """
        if self.allowed_versions is None:
            self.allowed_versions = self._get_allowed_versions()
        if subject in self.allowed_versions:
            return self.allowed_versions[subject]
        else:
            raise ValueError()

    def _pop_path_info(self, req):
        """
        'Pops' off the next segment of PATH_INFO, returns the popped
        segment. Do NOT push it onto SCRIPT_NAME.
        """
        path = req.path_info
        if not path:
            return None
        while path.startswith('/'):
            path = path[1:]
        idx = path.find('/')
        if idx == -1:
            idx = len(path)
        r = path[:idx]
        req.path_info = path[idx:]
        return r


class GlareVersionNegotiationFilter(VersionNegotiationFilter):
    def __init__(self, app):
        super(GlareVersionNegotiationFilter, self).__init__(app)
        self.versions_app = artifacts_versions.Controller()
        self.vnd_mime_type = 'application/vnd.openstack.artifacts-'

    def _get_allowed_versions(self):
        return {
            'v0.1': 0.1
        }
