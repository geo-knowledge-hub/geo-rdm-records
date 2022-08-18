# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Resources test configuration."""

import json

import pytest


@pytest.fixture(scope="function")
def draft_record(running_app, client_with_login, minimal_record, headers):
    """Draft record using the ``Records API`` resources."""
    base_url = "/records"
    client = client_with_login

    # Create a draft
    created_draft = client.post(
        base_url, headers=headers, data=json.dumps(minimal_record)
    )

    return created_draft.json["id"]


@pytest.fixture(scope="function")
def published_record(running_app, client_with_login, minimal_record, headers):
    """Publish record using the ``Records API`` resources."""
    base_url = "/records"
    client = client_with_login

    # Create a draft
    created_draft = client.post(
        base_url, headers=headers, data=json.dumps(minimal_record)
    )

    id_ = created_draft.json["id"]
    response = client.post(f"{base_url}/{id_}/draft/actions/publish", headers=headers)

    return response.json["id"]
