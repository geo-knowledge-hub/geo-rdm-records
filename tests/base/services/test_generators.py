# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Test services generators."""

import pytest
from invenio_access.permissions import system_process
from invenio_records_permissions.generators import SystemProcess

from geo_rdm_records.base.services.generators import IfPackage
from geo_rdm_records.customizations.records.api import GEORecord
from geo_rdm_records.modules.packages.records.api import GEOPackageRecord


#
# Fixtures
#
def _package():
    """Package fixture."""
    return GEOPackageRecord({}, access={})


def _record():
    """Record fixture."""
    return GEORecord({}, access={})


def _then_needs():
    return {system_process}


def _else_needs():
    return set()


#
# Tests
#
@pytest.mark.parametrize(
    "element_fnc,expected_needs_fun",
    [
        (_package, _then_needs),
        (_record, _else_needs),
    ],
)
def test_ifpackage_needs(element_fnc, expected_needs_fun):
    """Test IfPackage generator."""
    generator = IfPackage(
        then_=[
            SystemProcess(),
        ],
        else_=[],
    )

    assert generator.needs(record=element_fnc()) == expected_needs_fun()
    assert generator.excludes(record=element_fnc()) == set()
