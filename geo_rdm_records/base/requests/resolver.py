# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""GEO RDM Records Requests Resolver."""

from invenio_pidstore.errors import PIDUnregistered
from invenio_records_resources.references.resolvers.records import (
    RecordProxy,
    RecordResolver,
)


class BaseRecordProxy(RecordProxy):
    """Base proxy for resolve."""

    record_cls = None
    """Record class."""

    draft_cls = None
    """Draft class."""

    def _resolve(self):
        """Resolve the Record from the proxy's reference dict."""
        pid_value = self._parse_ref_dict_id()

        try:
            return self.record_cls.pid.resolve(pid_value, registered_only=False)
        except PIDUnregistered:
            return self.draft_cls.pid.resolve(pid_value)


class BaseRecordResolver(RecordResolver):
    """Base record entity resolver."""

    type_id = "record"
    """Type id."""

    record_cls = None
    """Record class."""

    proxy_cls = None
    """Proxy class."""

    service_id = None
    """Service id."""

    type_key = "record"
    """Type Key."""

    def __init__(
        self,
        type_id=None,
        record_cls=None,
        proxy_cls=None,
        service_id=None,
        type_key=None,
    ):
        """Initialize the resolver."""
        # Base configurations
        self.type_id = type_id or self.type_id
        self.type_key = type_key or self.type_key

        # Service layer
        self.service_id = service_id or self.service_id

        # Data layer handler
        self.proxy_cls = proxy_cls or self.proxy_cls
        self.record_cls = record_cls or self.record_cls

        super().__init__(
            self.record_cls,
            self.service_id,
            type_key=self.type_key,
            proxy_cls=self.proxy_cls,
        )
