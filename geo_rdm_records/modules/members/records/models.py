# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""GEO RDM Records Member Model."""

import uuid

from invenio_accounts.models import Role, User
from invenio_db import db
from invenio_records.models import RecordMetadataBase
from invenio_requests.records.models import RequestMetadata
from sqlalchemy import CheckConstraint, Index
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy_utils.types import UUIDType

from ...packages.records.models import GEOPackageParentMetadata


class BaseMemberModel(RecordMetadataBase):
    """
    Base model for members, invitations and archived invitations.

    Note:
        This class was implemented using the ``BaseMemberModel`` from the Invenio Communities.

    Note:
        (From Invenio Communities) We restrict deletion of users/groups if they are
        present in the member table, to ensure that we have at least one owner.
        I.e. users must first be removed from memberships before they can be deleted,
        ensuring that another owner is set of a community if they are the sole owner.
    """

    id = db.Column(UUIDType, primary_key=True, default=uuid.uuid4)
    """Member ID inside the package."""

    @declared_attr
    def package_id(cls):
        """Foreign key to the related package."""
        return db.Column(
            UUIDType,
            db.ForeignKey(GEOPackageParentMetadata.id, ondelete="CASCADE"),
            nullable=False,
        )

    role = db.Column(db.String(50), nullable=False)
    """Member role."""

    visible = db.Column(db.Boolean(), nullable=False)
    """Member visibility"""

    @declared_attr
    def user_id(cls):
        """Foreign key to the related user."""
        return db.Column(
            db.Integer(),
            db.ForeignKey(User.id, ondelete="RESTRICT"),
            nullable=True,
        )

    @declared_attr
    def group_id(cls):
        """Foreign key to the related group."""
        return db.Column(
            db.Integer(),
            db.ForeignKey(Role.id, ondelete="RESTRICT"),
            nullable=True,
        )

    @declared_attr
    def request_id(cls):
        """Foreign key to the related request.

        A request can only be associated with one membership/invitation.
        """
        return db.Column(
            UUIDType,
            db.ForeignKey(RequestMetadata.id, ondelete="SET NULL"),
            nullable=True,
            unique=True,
        )

    active = db.Column(db.Boolean(), index=True, nullable=False)
    """Flag to set if a user is activated."""

    @classmethod
    def query_memberships(cls, user_id=None, group_ids=None, active=True):
        """Query for (package,role)-pairs."""
        q = db.session.query(cls.package_id, cls.role).filter(cls.active == active)

        if user_id:
            q = q.filter(cls.user_id == user_id)
        if group_ids:
            q = q.filter(cls.group_id.in_(group_ids))

        return q.distinct()

    @classmethod
    def count_members(cls, community_id, role=None, active=True):
        """Count number of members."""
        q = cls.query.filter(cls.package_id == community_id, cls.active == active)
        if role is not None:
            q = q.filter(cls.role == role)
        return q.count()


class MemberModel(db.Model, BaseMemberModel):
    """Member and invitation model.

    Note:
        This class was implemented using the ``MemberModel`` from the Invenio Communities.

    Note:
        (From Invenio Communities)
        We store members and invitations on the same table for two reasons:

        1. Reduced table size: The table is queried on login for all memberships
           of a user, and thus a smaller size is preferable.

        2. Mixing members and invitations ensures we can easily check integrity
           constraints. E.g. it's not possible to invite an existing member, and
           a person can only be invited once (database insertion will fail).
    """

    __tablename__ = "geo_package_members"
    __table_args__ = (
        Index("ix_package_user", "package_id", "user_id", unique=True),
        Index("ix_package_group", "package_id", "group_id", unique=True),
        # Make sure user or group is set but not both.
        CheckConstraint(
            "(user_id IS NULL AND group_id IS NOT NULL) OR "
            "(user_id IS NOT NULL AND group_id IS NULL)",
            name="user_or_group",
        ),
    )


class ArchivedInvitationModel(db.Model, BaseMemberModel):
    """Archived invitations model.

    Note:
        This class was implemented using the ``ArchivedInvitationModel`` from the Invenio Communities.

    Note:
        (From Invenio Communities)
        The archived invitations model stores invitations that was rejected or
        cancelled, to support the use case of seeing if invitations was rejected
        or cancelled, and seeing past invitations.
    """

    __tablename__ = "geo_package_archivedinvitations"

    # From Invenio Communities:
    #   We're not adding a check constraint since the row has already been
    #   inserted in the member model where it was checked.

    @classmethod
    def from_member_model(cls, member_model):
        """Create an archived invitation model from a member model."""
        # Note, we keep the "active" model field, because it makes it easier to
        # handle with the search index, when we search over a combined
        # search alias for members/invitations and archived invitations.
        assert member_model.active is False
        return cls(
            id=member_model.id,
            package_id=member_model.package_id,
            user_id=member_model.user_id,
            group_id=member_model.group_id,
            request_id=member_model.request_id,
            role=member_model.role,
            visible=member_model.visible,
            active=member_model.active,
            created=member_model.created,
            updated=member_model.updated,
            version_id=member_model.version_id,
        )
