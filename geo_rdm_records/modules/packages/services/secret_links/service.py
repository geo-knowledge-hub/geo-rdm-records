# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""GEO RDM Records Packages Secrets links Service."""

from invenio_rdm_records.proxies import current_rdm_records_service
from invenio_rdm_records.secret_links.errors import InvalidPermissionLevelError
from invenio_rdm_records.services.secret_links.service import (
    SecretLinkService as BaseSecretLinkService,
)
from invenio_records_resources.services.uow import RecordCommitOp, unit_of_work
from marshmallow.exceptions import ValidationError


class SecretLinkService(BaseSecretLinkService):
    """Secret link service for Packages.

    This Service was adapted from the Invenio RDM Records package to enable
    the package management workflow.
    """

    def _update_resources_link(self, identity, record, uow):
        """Update the secret links of a given record."""
        package_resources = record.relationship.managed

        # When a record is associated with a package, users must
        # manage it using the package. So, we always overwrite all
        # links to avoid any inconsistency between packages and
        # records access.
        for package_resource in package_resources:
            package_resource = package_resource.resolve()
            package_resource.parent.access.links = record.parent.access.links

            # Commit
            uow.register(RecordCommitOp(package_resource.parent))
            uow.register(
                RecordCommitOp(
                    package_resource, indexer=current_rdm_records_service.indexer
                )
            )

            # Index all child records of the parent
            self._index_related_records(
                package_resource, package_resource.parent, uow=uow
            )

    @unit_of_work()
    def create(self, identity, id_, data, links_config=None, uow=None):
        """Create a secret link for a record (resp. its parent)."""
        record, parent = self.get_parent_and_record_or_draft(id_)

        # Permissions
        self.require_permission(identity, "manage", record=record)

        # Validation
        data, __ = self.schema_secret_link.load(
            data, context=dict(identity=identity), raise_errors=True
        )
        expires_at = self._validate_secret_link_expires_at(data.get("expires_at"))
        if "permission" not in data:
            raise ValidationError(
                _("An access permission level is required"),
                field_name="permission",
            )

        # Creation
        try:
            link = parent.access.links.create(
                permission_level=data["permission"],
                expires_at=expires_at,
                extra_data=data.get("extra_data", {}),
            )
        except InvalidPermissionLevelError:
            raise ValidationError(
                _("Invalid access permission level."),
                field_name="permission",
            )

        # Commit
        uow.register(RecordCommitOp(parent))
        if record:
            uow.register(RecordCommitOp(record))

        # Index all child records of the parent
        self._index_related_records(record, parent, uow=uow)

        # Modify and index all records associated with the package
        self._update_resources_link(identity, record, uow)

        return self.link_result_item(
            self,
            identity,
            link,
            links_config=links_config,
        )

    @unit_of_work()
    def update(
        self,
        identity,
        id_,
        link_id,
        data,
        links_config=None,
        uow=None,
    ):
        """Update a secret link for a record (resp. its parent)."""
        record, parent = self.get_parent_and_record_or_draft(id_)

        # Permissions
        self.require_permission(identity, "manage", record=record)

        # Fetching (required for parts of the validation)
        link_ids = [link.link_id for link in parent.access.links]
        if str(link_id) not in link_ids:
            raise LookupError(str(link_id))

        link_idx = link_ids.index(link_id)
        link = parent.access.links[link_idx].resolve()

        # Validation
        data, __ = self.schema_secret_link.load(
            data, context=dict(identity=identity), raise_errors=True
        )
        permission = data.get("permission")
        expires_at = self._validate_secret_link_expires_at(
            data.get("expires_at"),
            is_specified=("expires_at" in data),
            secret_link=link,
        )

        # Update
        # we can't update the link's extra data, as that is encoded
        # in the token and would thus require a new token
        link.expires_at = expires_at or link.expires_at
        link.permission_level = permission or link.permission_level

        # Commit
        uow.register(RecordCommitOp(parent))
        if record:
            uow.register(RecordCommitOp(record))

        # Index all child records of the parent
        self._index_related_records(record, parent, uow=uow)

        # Modify and index all records associated with the package
        self._update_resources_link(identity, record, uow)

        return self.link_result_item(
            self,
            identity,
            link,
            links_config=links_config,
        )

    @unit_of_work()
    def delete(self, identity, id_, link_id, links_config=None, uow=None):
        """Delete a secret link for a record (resp. its parent)."""
        record, parent = self.get_parent_and_record_or_draft(id_)

        # Permissions
        self.require_permission(identity, "manage", record=record)

        # Fetching
        link_ids = [link.link_id for link in parent.access.links]
        if str(link_id) not in link_ids:
            raise LookupError(str(link_id))

        link_idx = link_ids.index(link_id)
        link = parent.access.links[link_idx].resolve()

        # Deletion
        parent.access.links.pop(link_idx)
        link.revoke()

        # Commit
        uow.register(RecordCommitOp(parent))
        if record:
            uow.register(RecordCommitOp(record))

        # Index all child records of the parent
        self._index_related_records(record, parent, uow=uow)

        # Modify and index all records associated with the package
        self._update_resources_link(identity, record, uow)

        return True
