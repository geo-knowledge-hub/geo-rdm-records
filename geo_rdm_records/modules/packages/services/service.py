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
from marshmallow import ValidationError
from sqlalchemy.orm.exc import NoResultFound

from ..errors import InvalidPackageError, InvalidPackageResourceError
from ..records.api import PackageRelationship
from .schemas.resources import RecordsParentSchema, RecordsSchema, ResourcesSchema


#
# Enum
#
class PackageServiceAction(enum.Enum):
    """Package relationship types."""

    #
    # Package
    #
    ADD = "package_add_resource"
    """Create action."""

    DELETE = "package_delete_resource"
    """Delete action."""

    #
    # Package Context
    #
    ASSOCIATE = "context_associate_resource"
    """Associate action."""

    DISSOCIATE = "context_dissociate_resource"
    """Dissociate action."""


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

    @property
    def records_schema(self):
        """Schema for records definition (Package context)."""
        return ServiceSchemaWrapper(self, schema=RecordsSchema)

    @property
    def records_access_schema(self):
        """Schema for records access (parent) definition (Package context)."""
        return ServiceSchemaWrapper(self, schema=RecordsParentSchema)

    #
    # Internal methods
    #
    def _uow_commit_resource(self, record, uow):
        """Register both Commit and Index Operations for a Resource Record."""
        uow.register(RecordCommitOp(record))
        uow.register(RecordCommitOp(record.parent))

        uow.register(RecordIndexOp(record, indexer=current_rdm_records_service.indexer))

    def _read_package(self, identity, id_, allow_draft=False):
        """Read a package (Draft or Record)."""
        try:
            record = self.record_cls.pid.resolve(id_, registered_only=False)
        except NoResultFound as e:
            if not allow_draft:
                raise InvalidPackageError(id_) from e

            record = self.draft_cls.pid.resolve(id_, registered_only=False)

        # basic required permission
        self.require_permission(identity, "read", record=record)

        return record

    def _read_record(self, identity, id_, allow_draft=False):
        """Read a bibliographic record (Draft or Record)."""
        try:
            record = self.resource_cls.pid.resolve(id_, registered_only=False)
        except NoResultFound as e:
            if not allow_draft:
                raise InvalidPackageResourceError(id_) from e

            record = self.resource_draft_cls.pid.resolve(id_, registered_only=False)

        # Checking if user is able to read
        # Note: Is this the best way to do this validation ?
        current_rdm_records_service.require_permission(identity, "read", record=record)

        return record

    def _handle_records(
        self, identity, id_, data, action, uow, revision_id=None, expand=False
    ):
        """Handle records to associate/dissociate them with the package context."""
        package = self._read_package(identity, id_, allow_draft=True)

        # concurrency control (not used to create a record)
        self.check_revision_id(package, revision_id)

        # permissions
        self.require_permission(identity, action, record=package)

        # load data with service schema
        data, _ = self.records_schema.load(data, context={"identity": identity})

        # associating records with the selected package
        errors = []

        records = data["records"]
        records_processed = []

        for record_id in records:
            record_id = record_id["id"]

            record = self._read_record(identity, record_id, allow_draft=True)

            # only record without association with a package context
            # can be added to a context.
            if (
                action == PackageServiceAction.ASSOCIATE
                and record.parent.relationship.managed_by
            ):
                errors.append(
                    dict(
                        record=record.pid.pid_value,
                        message="Record already associated with a package",
                    )
                )

            else:
                # running the components to link the package and resources
                self.run_components(
                    action,
                    identity,
                    package=package,
                    record=record,
                )

                self._uow_commit_resource(record, uow)

                records_processed.append(record)

        if records_processed:  # avoiding extra operations
            uow.register(RecordCommitOp(package, self.indexer))

        return dict(errors=errors)

    def _handle_resources(
        self, identity, id_, data, action, uow, revision_id=None, expand=False
    ):
        """Handle Package resources."""
        # reproducibility/consistency requirement: users can only add/remove
        # resources from draft packages.
        package_draft = self.draft_cls.pid.resolve(id_, registered_only=False)

        # concurrency control (not used to create a record)
        self.check_revision_id(package_draft, revision_id)

        # permissions
        self.require_permission(identity, "update_draft", record=package_draft)

        # load data with service schema
        data, _ = self.resource_schema.load(data, context={"identity": identity})

        errors = []
        resources = data["resources"]
        resources_processed = []

        for resource in resources:
            resource_obj = None
            resource_id = resource["id"]

            resource_errors = []

            # loading the resource metadata.
            # for both ``Published`` and ``Draft`` records it is assumed
            # that the permission verification is done in a specialized
            # constrained component. This is done because this verification
            # is combined with other properties of the record.
            resource_obj = self._read_record(identity, resource_id, allow_draft=True)

            # defining the relation type of the component with the package:
            #   - ``related``: It can't be loaded as a draft (it is out of package context);
            #   - ``managed``: It can be loaded as a draft (it is in the package context).
            relationship_type = "related"

            if resource_obj.parent.relationship.managed_by:

                if resource_obj.parent.relationship.managed_by == package_draft.parent:
                    relationship_type = "managed"

            allow_draft = not (relationship_type == PackageRelationship.RELATED.value)

            # checking if the loaded resource is draft and if draft is allowed
            if not allow_draft:
                if resource_obj.is_draft:

                    errors.append(
                        dict(
                            record=resource_obj.pid.pid_value,
                            message="This record is a draft and can't be linked to "
                            "the package as a resource.",
                        )
                    )

                    continue

            # running the components to link the resources with the package
            self.run_components(
                action,
                identity,
                errors=resource_errors,
                package=package_draft,
                resource=resource_obj,
                relationship_type=relationship_type,
            )

            if not resource_errors:
                # commit and index the modified resource
                self._uow_commit_resource(resource_obj, uow)

                resources_processed.append(resource_obj)
            else:
                # ToDo: Create a way to return multiple error messages.
                errors.append(resource_errors[0])

        # commit and index the package
        if resources_processed:  # avoiding extra operations
            uow.register(RecordCommitOp(package_draft, self.indexer))

        return dict(errors=errors)

    def _validate_draft_package(self, identity, package_draft, raise_error=False):
        """Validate a package draft."""
        errors = []

        # 1. Checking if the package can be published
        self._validate_draft(identity, package_draft)

        # 2. Checking all resources can be published
        # We validate only the ``Managed`` resource once we
        # need to publish them with the package itself.
        package_resources = package_draft.relationship.resources

        for package_resource in package_resources:
            # Checking the resource
            # here, we are using an internal method from the `record service`.
            # This maybe is not a good approach. Is the future, we can return
            # to this implementation and evaluate if this is the best solution.
            package_resource_obj = package_resource.resolve()

            if package_resource_obj.is_draft:
                try:
                    current_rdm_records_service._validate_draft(
                        identity, package_resource_obj
                    )

                except ValidationError as e:

                    if raise_error:
                        raise e

                    errors.append(
                        dict(
                            record=package_resource_obj.pid.pid_value,
                            message="The record can't be published",
                        )
                    )
        return errors

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

    def _publish_resource(self, identity, package, resource_draft, uow, expand):
        """Publish a package resource."""
        if resource_draft.is_draft:
            # Avoiding errors with ``Related`` and ``Managed`` resources.
            if resource_draft.parent.relationship.managed_by == package.parent:
                resource_pid = resource_draft.pid.pid_value

                return current_rdm_records_service.publish(
                    identity, resource_pid, uow=uow, expand=expand
                )

    #
    # High-level Packages API.
    #
    @unit_of_work()
    def resource_add(
        self, identity, id_, data, revision_id=None, uow=None, expand=False
    ):
        """Bulk add resources in a package."""
        action = PackageServiceAction.ADD.value
        return self._handle_resources(
            identity, id_, data, action, uow, revision_id, expand
        )

    @unit_of_work()
    def resource_delete(
        self, identity, id_, data, revision_id=None, uow=None, expand=False
    ):
        """Bulk delete resources from a package."""
        action = PackageServiceAction.DELETE.value
        return self._handle_resources(
            identity, id_, data, action, uow, revision_id, expand
        )

    @unit_of_work()
    def publish(self, identity, id_, uow=None, expand=False):
        """Publish a draft."""
        # get the package draft
        draft = self.draft_cls.pid.resolve(id_, registered_only=False)
        self.require_permission(identity, "publish", record=draft)

        # package publishing workflow
        # 1. validating the package and its resources
        self._validate_draft_package(identity, draft, raise_error=True)

        # 2. publishing the package
        published_package = self._publish_package(identity, draft, uow, expand)

        # 3. publish the resources
        package_resources = draft.relationship.resources

        for package_resource in package_resources:
            self._publish_resource(
                identity, draft, package_resource.resolve(), uow, expand
            )

        # 4. returning the projection of the published record.
        return published_package

    @unit_of_work()
    def import_resources(self, identity, id_, uow=None):
        """Import files from previous record version."""
        # Read draft
        draft = self.draft_cls.pid.resolve(id_, registered_only=False)
        self.require_permission(identity, "update_draft", record=draft)

        # Retrieve latest record
        record = self.record_cls.get_record(draft.versions.latest_id)
        self.require_permission(identity, "read", record=record)

        # Run components
        self.run_components(
            "import_resources", identity, draft=draft, record=record, uow=uow
        )

        # Registering the new package in the resources
        resources = draft.relationship.resources
        resources = dict(
            resources=[dict(id=resource.record_id) for resource in resources]
        )

        self._handle_resources(
            identity,
            draft.pid.pid_value,
            resources,
            action=PackageServiceAction.ADD.value,
            uow=uow,
        )

        # Commit and index
        uow.register(RecordCommitOp(draft, indexer=self.indexer))

        return self.result_item(
            self,
            identity,
            draft,
            links_tpl=self.links_item_tpl,
            expandable_fields=self.expandable_fields,
        )

    @unit_of_work()
    def context_associate(
        self, identity, id_, data, revision_id=None, uow=None, expand=False
    ):
        """Bulk operation to associate resources to a package."""
        action = PackageServiceAction.ASSOCIATE.value
        return self._handle_records(
            identity, id_, data, action, uow, revision_id, expand
        )

    @unit_of_work()
    def context_dissociate(
        self, identity, id_, data, revision_id=None, uow=None, expand=False
    ):
        """Bulk operation to dissociate resources from the package."""
        action = PackageServiceAction.DISSOCIATE.value
        return self._handle_records(
            identity, id_, data, action, uow, revision_id, expand
        )

    @unit_of_work()
    def context_update(
        self, identity, id_, data, revision_id=None, uow=None, expand=False
    ):
        """Update the context of a package."""
        package = self._read_package(identity, id_, allow_draft=True)

        # Concurrency control (not used to create a record)
        self.check_revision_id(package, revision_id)

        # Permissions
        self.require_permission(identity, "context_update_access", record=package)

        # Load data with service schema
        data, errors = self.records_access_schema.load(
            data, context={"identity": identity}
        )

        self.run_components(
            "context_update_access", identity, record=package, data=data
        )

        uow.register(RecordCommitOp(package.parent))
        uow.register(RecordCommitOp(package, self.indexer))

        # ToDo: Improve this return and enable users to
        #       visualize the content updated.
        return True

    def validate_package(self, identity, id_):
        """Validate if package is ready to be published."""
        package_draft = self.draft_cls.pid.resolve(id_, registered_only=False)

        # 1. Permissions
        self.require_permission(identity, "read", record=package_draft)

        # 2. Checking if the package can be published
        errors = self._validate_draft_package(
            identity, package_draft, raise_error=False
        )

        # ToDo: Check if we can create a pattern for this kind
        #       of return in the API.
        return dict(errors=errors)
