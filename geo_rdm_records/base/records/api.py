# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Base Record API for the GEO RDM Records."""


class GEOBaseRecord:
    """A base class for the records handled in the GEO RDM Records (and its customization)."""

    type = None
    """Type of the entity represented by the Record in the System."""
