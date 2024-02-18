# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2024 GEO Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""GEO Marketplace Resource."""

from flask import abort
from invenio_rdm_records.resources.resources import (
    RDMRecordResource as BaseRecordResource,
)


class GEOMarketplaceItemResource(BaseRecordResource):
    """GEO Marketplace Item resource."""

    #
    # PIDs
    #
    def pids_reserve(self):
        """Reserve a PID."""
        abort(403)

    def pids_discard(self):
        """Discard a previously reserved PID."""
        abort(403)
