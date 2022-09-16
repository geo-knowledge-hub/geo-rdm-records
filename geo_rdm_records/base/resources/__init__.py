# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Base resources for the GEO RDM Records."""

from .args import GEOSearchRequestArgsSchema
from .config import BaseGEOResourceConfig

__all__ = ("BaseGEOResourceConfig", "GEOSearchRequestArgsSchema")
