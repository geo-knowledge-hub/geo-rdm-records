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
    RecordDeleteOp,
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

    def _validate_draft_package(self, identity, package_draft):
        """Validate a package draft."""
        # 1. Checking if the package can be published
        self._validate_draft(identity, package_draft)

        # 2. Checking all resources can be published
        # We validate only the ``Managed`` resource once we
        # need to publish them with the package itself.
        package_resources = package_draft.relationship.managed

        for package_resource in package_resources:
            # Checking the resource
            # here, we are using an internal method from the `record service`.
            # This maybe is not a good approach. Is the future, we can return
            # to this implementation and evaluate if this is the best solution.

            # ToDo: Check a way to return errors (e.g., Use a list of errors).
            current_rdm_records_service._validate_draft(
                identity, package_resource.resolve()
            )

    def _publish_package(self, identity, package_draft, uow, expand):
        """Publish a package."""
        # Create the record from the draft
        latest_id = package_draft.versions.latest_id
        record = self.record_cls.publish(package_draft)

        # Run components
        self.run_components(
            "publish", identity, draft=package_draft, record=record, uow=uow
        )

        # Commit and index
        uow.register(RecordCommitOp(record, indexer=self.indexer))
        uow.register(RecordDeleteOp(package_draft, force=False, indexer=self.indexer))

        if latest_id:
            self._reindex_latest(latest_id, uow=uow)

        return self.result_item(
            self,
            identity,
            record,
            links_tpl=self.links_item_tpl,
            expandable_fields=self.expandable_fields,
            expand=expand,
        )

    def _publish_resource(self, identity, resource_draft, uow, expand):
        """Publish a package resource."""
        # ToDo: Should we use another service in this way ? We are in
        #       the same 'architecture level', but, maybe, this can be confusing
        #       to maintain. Also, the service is not injected in a 'direct' way.
        resource_pid = resource_draft.pid.pid_value

        return current_rdm_records_service.publish(
            identity, resource_pid, uow=uow, expand=expand
        )

    #
    # High-level Resources API.
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

    #
    # High-level Packages API.
    #
    @unit_of_work()
    def publish(self, identity, id_, uow=None, expand=False):
        """Publish a draft."""
        # Get the package draft
        draft = self.draft_cls.pid.resolve(id_, registered_only=False)
        self.require_permission(identity, "publish", record=draft)

        # Package publishing workflow

        # 1. Publishing the package and its resources
        self._validate_draft_package(identity, draft)

        # 2. Publishing the package
        published_package = self._publish_package(identity, draft, uow, expand)

        # 3. Publish the resources
        package_resources = draft.relationship.managed

        for package_resource in package_resources:
            self._publish_resource(identity, package_resource.resolve(), uow, expand)

        # 4. Returning the projection of the published record.
        return published_package
