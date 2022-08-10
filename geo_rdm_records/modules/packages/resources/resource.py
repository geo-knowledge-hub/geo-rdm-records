# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Bibliographic Record Resource for the Packages API."""

from invenio_rdm_records.resources.resources import (
    RDMParentRecordLinksResource as BaseParentRecordLinksResource,
)
from invenio_rdm_records.resources.resources import (
    RDMRecordResource as BaseRecordResource,
)


class GEOPackageRecordResource(BaseRecordResource):
    """Record resource."""


class GEOPackageParentRecordLinksResource(BaseParentRecordLinksResource):
    """Secret links resource."""
