# -*- coding: utf-8 -*-
#
# Copyright (C) 2022-2024 GEO Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.


import pytest
from invenio_access.permissions import any_user, authenticated_user, system_process
from invenio_records.api import Record
from invenio_records.models import RecordMetadata
from invenio_records_permissions.generators import (
    AnyUser,
    AuthenticatedUser,
    SystemProcess,
)

from geo_rdm_records.modules.security.generators import IfIsEqual


def _public_record():
    """Public record."""
    return Record(dict(status="public"))


def _private_record():
    """Private record."""
    return Record(dict(status="private"))


def _then_needs():
    return {authenticated_user, system_process}


def _else_needs():
    return {any_user, system_process}


#
# Tests
#
@pytest.mark.parametrize(
    "field,expected_field_value,record_fun,expected_needs_fun",
    [
        ("status", "public", _public_record, _then_needs),
        ("status", "public", _private_record, _else_needs),
        ("status", "private", _private_record, _then_needs),
        ("model_cls", RecordMetadata, _public_record, _then_needs),
        ("model_cls", RecordMetadata, _private_record, _then_needs),
    ],
)
def test_ifisequal_needs(field, expected_field_value, record_fun, expected_needs_fun):
    """Test the IfIsEqual generator."""
    generator = IfIsEqual(
        field=field,
        equal_to=expected_field_value,
        then_=[AuthenticatedUser(), SystemProcess()],
        else_=[AnyUser(), SystemProcess()],
    )

    assert generator.needs(record=record_fun()) == expected_needs_fun()
    assert generator.excludes(record=record_fun()) == set()
