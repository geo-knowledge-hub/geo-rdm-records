# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""GEO RDM Records Packages API Services."""

import enum

from invenio_rdm_records.proxies import current_rdm_records_service
from invenio_rdm_records.services.services import (
    RDMRecordService as BaseRDMRecordService,
)
from invenio_records_resources.services import ServiceSchemaWrapper
from invenio_records_resources.services.uow import (
    RecordCommitOp,
    RecordIndexOp,
    unit_of_work,
)
from sqlalchemy.orm.exc import NoResultFound

from ..errors import InvalidPackageResourceError
from ..records.api import PackageRelationship
from .schemas.resources import ResourcesSchema


#
# Enum
#
class PackageServiceAction(enum.Enum):
    """Package relationship types."""

    CREATE = "package_add_resource"
    """Create action."""

    UPDATE = "package_update_resource"
    """Update action."""

    DELETE = "package_delete_resource"
    """Delete action."""


#
# Service class
#
class GEOPackageRecordService(BaseRDMRecordService):
    """GEO Package record service."""

    #
    # Properties
    #
    @property
    def resource_cls(self):
        """Resource record class."""
        return self.config.resource_cls

    @property
    def resource_draft_cls(self):
        """Resource draft class."""
        return self.config.resource_draft_cls

    @property
    def resource_schema(self):
        """Schema for resource definition."""
        return ServiceSchemaWrapper(self, schema=ResourcesSchema)

    #
    # Internal methods
    #
    def _handle_resources(self, identity, id_, data, revision_id, action, uow, expand):
        """Handle Package resources."""
        # defining auxiliary function
        def uow_storage_record(record):
            uow.register(RecordCommitOp(record.parent))
            uow.register(
                RecordIndexOp(record, indexer=current_rdm_records_service.indexer)
            )

        # reproducibility/consistency requirement: users can only add/remove
        # resources from draft packages.
        draft = self.draft_cls.pid.resolve(id_, registered_only=False)

        # concurrency control (not used to create a record)
        self.check_revision_id(draft, revision_id)

        # permissions
        self.require_permission(identity, "update_draft", record=draft)

        # Load data with service schema
        data, errors = self.resource_schema.load(data, context={"identity": identity})

        resources = data["resources"]

        for resource in resources:
            resource_obj = None
            resource_id = resource["id"]
            relationship_type = resource["type"]

            # defining the rule to load a resource based on
            # the relationship type:
            #   - ``related``: Can't be loaded as a draft;
            #   - ``managed``: Must be loaded as a draft.
            allow_draft = not (relationship_type == PackageRelationship.RELATED.value)

            # for both ``Published`` and ``Draft`` records it is assumed
            # that the permission verification is done in a specialized
            # constrained component. This is done because this verification
            # is combined with other properties of the record.
            try:
                resource_obj = self.resource_cls.pid.resolve(
                    resource_id, registered_only=False
                )

            except NoResultFound as e:
                if not allow_draft:
                    raise InvalidPackageResourceError(resource) from e

                resource_obj = self.resource_draft_cls.pid.resolve(
                    resource_id, registered_only=False
                )

            # running the components to link the package and resources
            self.run_components(
                action,
                identity,
                record=draft,
                resource=resource_obj,
                relationship_type=relationship_type,
            )

            # Commit and index (only in bidirectional connections) where
            # modifications are made in the resource.
            if relationship_type == PackageRelationship.MANAGED.value:

                # in both `create/update` and `delete` actions is
                # assumed that the package/resource integration only
                # uses the ``parent``.
                if action in (
                    PackageServiceAction.CREATE.value,
                    PackageServiceAction.UPDATE.value,
                ):

                    for r in draft.relationship.managed:
                        # verification to avoid unnecessary operations
                        if r.record_id == resource_obj.pid.pid_value:
                            record_resource = r.resolve()  # cached
                            uow_storage_record(record_resource)

                elif action == PackageServiceAction.DELETE.value:

                    uow_storage_record(resource_obj)

        # Commit and index
        uow.register(RecordCommitOp(draft, self.indexer))

        return self.result_item(
            self,
            identity,
            draft,
            links_tpl=self.links_item_tpl,
            errors=errors,
            expandable_fields=self.expandable_fields,
            expand=expand,
        )

    #
    # Resources handling
    #
    @unit_of_work()
    def resource_add(
        self, identity, id_, data, revision_id=None, uow=None, expand=False
    ):
        """Bulk add resources in a package."""
        action = PackageServiceAction.CREATE.value
        return self._handle_resources(
            identity, id_, data, revision_id, action, uow, expand
        )

    @unit_of_work()
    def resource_delete(
        self, identity, id_, data, revision_id=None, uow=None, expand=False
    ):
        """Bulk delete resources from a package."""
        action = PackageServiceAction.DELETE.value
        return self._handle_resources(
            identity, id_, data, revision_id, action, uow, expand
        )

    @unit_of_work()
    def resource_update(
        self, identity, id_, data, revision_id=None, uow=None, expand=False
    ):
        """Bulk update resources from a package."""
        action = PackageServiceAction.UPDATE.value
        return self._handle_resources(
            identity, id_, data, revision_id, action, uow, expand
        )
