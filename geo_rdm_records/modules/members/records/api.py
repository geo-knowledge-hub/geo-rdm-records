# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""GEO RDM Records Members API data layer."""

from invenio_accounts.models import Role
from invenio_db import db
from invenio_records.dumpers import ElasticsearchDumper
from invenio_records.dumpers.indexedat import IndexedAtDumperExt
from invenio_records.dumpers.relations import RelationDumperExt
from invenio_records.systemfields import ModelField, ModelRelation, RelationsField
from invenio_records_resources.records.api import Record
from invenio_records_resources.records.systemfields import IndexField
from invenio_requests.records.api import Request
from invenio_users_resources.records.api import GroupAggregate, UserAggregate
from sqlalchemy import or_

from ..errors import InvalidMemberError
from .models import ArchivedInvitationModel, MemberModel

relations_dumper = ElasticsearchDumper(
    extensions=[
        RelationDumperExt("relations"),
        IndexedAtDumperExt(),
    ]
)
"""Relations dumper for members and archived invitations."""


class MemberMixin:
    """Fields defined on both member/invitation models.

    Note:
        Implemented based on ``MemberMixin`` from the Invenio Communities.
    """

    package_id = ModelField("package_id")
    """The data-layer UUID of the Package."""

    user_id = ModelField("user_id")
    """The data-layer id of the user (or None)."""

    group_id = ModelField("group_id")
    """The data-layer id of the user (or None)."""

    request_id = ModelField("request_id")
    """The data-layer id of the user (or None)."""

    role = ModelField("role")
    """The role of the entity."""

    visible = ModelField("visible")
    """Visibility of the membership."""

    active = ModelField("active")
    """Determine if it's an active membership.

    This is used for e.g. invitations where a memberships is created but not
    yet activated.
    """

    relations = RelationsField(
        user=ModelRelation(
            UserAggregate,
            "user_id",
            "user",
            attrs=[
                "email",
                "username",
                "profile",
                "preferences",
                "active",
                "confirmed",
            ],
        ),
        group=ModelRelation(
            GroupAggregate,
            "group_id",
            "group",
            attrs=["id", "name"],
        ),
        request=ModelRelation(
            Request,
            "request_id",
            "request",
            attrs=["status", "expires_at", "is_open"],
        ),
    )

    @classmethod
    def get_memberships(cls, identity):
        """Get Package memberships for a given identity."""
        # TODO: extract group/role ids from identity
        query = cls.model_cls.query_memberships(user_id=identity.id, group_ids=[])
        return [(str(comm_id), role) for comm_id, role in query]

    @classmethod
    def get_member_by_request(cls, request_id):
        """Get a membership by request id."""
        assert request_id is not None
        obj = cls.model_cls.query.filter(cls.model_cls.request_id == request_id).one()
        return cls(obj.data, model=obj)

    @classmethod
    def get_members(cls, package_id, members=None):
        """Get package members."""
        # Collect users and groups we are interested in
        user_ids = []
        group_names = []
        for m in members or []:
            if m["type"] == "group":
                group_names.append(m["id"])
            elif m["type"] == "user":
                user_ids.append(m["id"])
            else:
                raise InvalidMemberError(m)

        # Query
        q = cls.model_cls.query.filter(cls.model_cls.package_id == package_id)

        # Apply user and group query if applicable
        user_q = cls.model_cls.user_id.in_(user_ids)
        groups_q = cls.model_cls.group_id.in_(
            db.session.query(Role.id).filter(Role.name.in_(group_names))
        )
        if user_ids and group_names:
            q = q.filter(or_(user_q, groups_q))
        elif user_ids:
            q = q.filter(user_q)
        elif group_names:
            q = q.filter(groups_q)

        return [cls(obj.data, model=obj) for obj in q.all()]

    @classmethod
    def has_members(cls, package_id, role=None):
        """Check the number of members inside a package."""
        return cls.model_cls.count_members(package_id, role=role)


class Member(Record, MemberMixin):
    """A member/invitation record.

    Note:
        Implemented based on ``Member`` from the Invenio Communities.

    Note:
        (From Invenio Communities) We are using a record without using the actual
        JSON document and schema validation normally used in a record. The reason
        for using a record is to facilitate the indexing which we need to have an
        effective search over the list of members.
    """

    model_cls = MemberModel

    # Needs to be here instead of on MemberMixin to overwrite Record.dumper
    dumper = relations_dumper

    # Systemfields

    metadata = None

    index = IndexField(
        "packagemembers-members-member-v1.0.0",
        search_alias="packagemembers-members",
    )
    """The ES index used."""


class ArchivedInvitation(Record, MemberMixin):
    """An archived invitation record.

    Note:
        Implemented based on ``ArchivedInvitation`` from the Invenio Communities.

    Note:
        (From Invenio Communities) We are using a record without using the actual
        JSON document and schema validation normally used in a record. The reason
        for using a record is to facilitate the indexing which we need to have an
        effective search over the list of members.
    """

    model_cls = ArchivedInvitationModel

    # Needs to be here instead of on MemberMixin to overwrite Record.dumper
    dumper = relations_dumper

    # Systemfields

    metadata = None

    index = IndexField(
        "packagemembers-archivedinvitations-archivedinvitation-v1.0.0",
        search_alias="packagemembers",
    )
    """The ES index used."""

    @classmethod
    def create_from_member(cls, member):
        """Create an archived invitation record from a member."""
        with db.session.begin_nested():
            record = cls({}, model=cls.model_cls.from_member_model(member.model))
            db.session.add(record.model)
        return record
