# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Base Record Types registry for the GEO RDM Records."""


class GEORecordTypes:
    """GEO RDM Records types definition."""

    resource = "resource"
    """Resource type. This type of record can be linked with a `Package ."""

    package = "package"
    """Package type. This type record can be associated with multiple `Resources`"""
