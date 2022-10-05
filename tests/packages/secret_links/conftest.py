# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Pytest configuration for the package secret links service."""

import pytest
from invenio_app.factory import create_api


@pytest.fixture(scope="module")
def create_app(instance_path):
    """Application factory fixture."""
    return create_api
