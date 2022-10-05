# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.


"""Test sharing of restricted records via secret links."""

from io import BytesIO

import pytest
from flask_principal import AnonymousIdentity, Identity, UserNeed
from invenio_access.permissions import any_user, authenticated_user
from invenio_db import db
from invenio_rdm_records.secret_links.permissions import LinkNeed
from invenio_records_resources.services.errors import PermissionDeniedError
from marshmallow.exceptions import ValidationError

from geo_rdm_records.modules.packages import GEOPackageRecord


@pytest.fixture()
def service(running_app, es_clear):
    """Get the current GEO RDM Records service."""
    return running_app.app.extensions["geo-rdm-records"].service


@pytest.fixture()
def resources_service(running_app, es_clear):
    """Get the current Invenio RDM Records service."""
    return running_app.app.extensions["invenio-rdm-records"].records_service


@pytest.fixture()
def restricted_record(service, resources_service, minimal_record, identity_simple):
    """Restricted record fixture."""

    def _record_factory(data, service_obj):
        # Create
        draft = service_obj.create(identity_simple, data)

        # Add a file
        service_obj.draft_files.init_files(
            identity_simple, draft.id, data=[{"key": "test.pdf"}]
        )
        service_obj.draft_files.set_file_content(
            identity_simple, draft.id, "test.pdf", BytesIO(b"test file")
        )
        service_obj.draft_files.commit_file(identity_simple, draft.id, "test.pdf")

        return draft

    # Create package
    data = minimal_record.copy()
    data["files"]["enabled"] = True
    data["access"]["record"] = "restricted"
    data["access"]["files"] = "restricted"

    package = _record_factory(data, service)

    # Create resource
    data = minimal_record.copy()
    data["files"]["enabled"] = True

    resource = _record_factory(data, resources_service)

    resources = dict(
        resources=[
            {"id": resource.id, "type": "managed"},
        ]
    )

    service.resource_add(identity_simple, package.id, resources)

    # Publish
    record = service.publish(identity_simple, package.id)

    # Put in edit mode so that draft exists
    service.edit(identity_simple, package.id)
    resources_service.edit(identity_simple, resource.id)

    return record


def test_invalid_level(service, restricted_record, identity_simple):
    """Test invalid permission level."""
    record = restricted_record
    with pytest.raises(ValidationError):
        service.secret_links.create(
            identity_simple, record.id, {"permission": "invalid"}
        )


def test_permission_levels(
    service, resources_service, restricted_record, identity_simple, client
):
    """Test invalid permission level."""

    def _assert_permission_levels(
        view_link, preview_link, edit_link, record_service, record_id
    ):
        """Assert the permission for the package and its resource."""
        # == Anonymous user
        anon = AnonymousIdentity()
        anon.provides.add(any_user)

        # Deny anonymous to read restricted record and draft
        pytest.raises(PermissionDeniedError, record_service.read, anon, record_id)
        pytest.raises(
            PermissionDeniedError, record_service.files.list_files, anon, record_id
        )
        pytest.raises(PermissionDeniedError, record_service.read_draft, anon, record_id)
        with pytest.raises(PermissionDeniedError):
            record_service.draft_files.list_files(anon, record_id)

        # === Anonymous user with view link ===
        anon.provides.add(LinkNeed(view_link.id))

        # Allow anonymous with view link to read record
        record_service.read(anon, record_id)
        record_service.files.list_files(anon, record_id)

        # Deny anonymous with view link to read draft
        pytest.raises(PermissionDeniedError, record_service.read_draft, anon, record_id)
        with pytest.raises(PermissionDeniedError):
            record_service.draft_files.list_files(anon, record_id)

        # === Anonymous user with preview link ===
        anon.provides.remove(LinkNeed(view_link.id))
        anon.provides.add(LinkNeed(preview_link.id))

        # Allow anonymous with preview link to read record and draft
        record_service.read(anon, record_id)
        record_service.files.list_files(anon, record_id)
        record_service.read_draft(anon, record_id)
        record_service.draft_files.list_files(anon, record_id)
        record_service.draft_files.get_file_content(anon, record_id, "test.pdf")
        record_service.draft_files.read_file_metadata(anon, record_id, "test.pdf")

        # Deny anonymous with preview link to update/delete/edit/publish draft
        pytest.raises(
            PermissionDeniedError, record_service.update_draft, anon, record_id, {}
        )
        pytest.raises(PermissionDeniedError, record_service.edit, anon, record_id)
        pytest.raises(
            PermissionDeniedError, record_service.delete_draft, anon, record_id
        )
        pytest.raises(
            PermissionDeniedError, record_service.new_version, anon, record_id
        )
        pytest.raises(PermissionDeniedError, record_service.publish, anon, record_id)

        with pytest.raises(PermissionDeniedError):
            record_service.draft_files.init_files(anon, record_id, {})
        with pytest.raises(PermissionDeniedError):
            record_service.draft_files.update_file_metadata(
                anon, record_id, "test.pdf", {}
            )
        with pytest.raises(PermissionDeniedError):
            record_service.draft_files.commit_file(anon, record_id, "test.pdf")
        with pytest.raises(PermissionDeniedError):
            record_service.draft_files.delete_file(anon, record_id, "test.pdf")
        with pytest.raises(PermissionDeniedError):
            record_service.draft_files.delete_all_files(anon, record_id)
        with pytest.raises(PermissionDeniedError):
            record_service.draft_files.set_file_content(
                anon, record_id, "test.pdf", None
            )

        # === Authenticated user with edit link ===
        i = Identity(100)
        i.provides.add(UserNeed(100))
        i.provides.add(authenticated_user)
        i.provides.add(LinkNeed(edit_link.id))

        # Allow user with edit link to read record and draft
        record_service.read(i, record_id)
        record_service.files.list_files(i, record_id)
        record_service.read_draft(i, record_id)
        record_service.draft_files.list_files(i, record_id)
        record_service.draft_files.get_file_content(i, record_id, "test.pdf")
        record_service.draft_files.read_file_metadata(i, record_id, "test.pdf")

        # Deny user with edit link to share the links
        with pytest.raises(PermissionDeniedError):
            record_service.secret_links.create(i, record_id, {})
        with pytest.raises(PermissionDeniedError):
            record_service.secret_links.read_all(i, record_id)
        with pytest.raises(PermissionDeniedError):
            record_service.secret_links.read(i, record_id, edit_link.id)
        with pytest.raises(PermissionDeniedError):
            record_service.secret_links.update(i, record_id, edit_link.id, {})
        with pytest.raises(PermissionDeniedError):
            record_service.secret_links.delete(i, record_id, edit_link.id)

        # Allow user with edit link to update, delete, edit, publish
        draft = record_service.read_draft(i, record_id)
        data = draft.data
        data["metadata"]["title"] = "allow it"
        record_service.update_draft(i, record_id, data)
        record_service.delete_draft(i, record_id)
        test = record_service.edit(i, record_id)
        record_service.publish(i, record_id)
        new_draft = record_service.new_version(i, record_id)
        new_id = new_draft.id
        record_service.import_files(i, new_id)
        record_service.draft_files.delete_file(i, new_id, "test.pdf")

    # Organizing the package/resource ids
    id_ = restricted_record.id
    related_resource_id_ = restricted_record["relationship"]["managed_resources"][0][
        "id"
    ]

    # 1. Sharing the package (and its resource) via secret link
    view_link = service.secret_links.create(
        identity_simple, id_, {"permission": "view"}
    )
    preview_link = service.secret_links.create(
        identity_simple, id_, {"permission": "preview"}
    )
    edit_link = service.secret_links.create(
        identity_simple, id_, {"permission": "edit"}
    )

    # 2. Testing the sharing system for the packages
    _assert_permission_levels(view_link, preview_link, edit_link, service, id_)

    # 3. Testing the sharing system for the resources (enabled via package).
    _assert_permission_levels(
        view_link, preview_link, edit_link, resources_service, related_resource_id_
    )


def test_read_restricted_record_with_secret_link(
    service, minimal_record, identity_simple, client
):
    """Test access to a restricted record via a shared link."""
    record_data = minimal_record.copy()
    record_data["access"]["files"] = "restricted"
    record_data["access"]["record"] = "restricted"

    draft = service.create(identity=identity_simple, data=record_data)
    record = service.publish(id_=draft.id, identity=identity_simple)
    recid = record.id

    link = record._record.parent.access.links.create(
        permission_level="view",
    )

    # FIXME without this, commit() won't work (b/c of jsonschema)
    record._record.pop("status", None)
    record._record.commit()
    record._record.parent.commit()
    db.session.commit()

    # the record shouldn't be accessible without login and/or token
    response = client.get(f"/packages/{recid}")
    assert response.status_code == 403

    # but it should be accessible with the token
    response = client.get(
        f"/packages/{recid}",
        query_string={"token": link.token},
    )
    assert response.status_code == 200

    # the record shouldn't be showing up in search results, however
    GEOPackageRecord.index.refresh()
    res = client.get("/packages", query_string={"q": f"id:{recid}"})
    assert res.status_code == 200
    assert res.json["hits"]["total"] == 0
