# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Create geo-rdm-records tables."""

import sqlalchemy as sa
import sqlalchemy_utils
from alembic import op
from sqlalchemy.dialects import mysql, postgresql

# revision identifiers, used by Alembic.
revision = "357f00b65029"
down_revision = "15a1212e33c4"
branch_labels = ()
depends_on = ("a3f5a8635cbb", "a29271fd78f8")


def upgrade():
    """Upgrade database."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "geo_package_parents_metadata",
        sa.Column(
            "created",
            sa.DateTime().with_variant(mysql.DATETIME(fsp=6), "mysql"),
            nullable=False,
        ),
        sa.Column(
            "updated",
            sa.DateTime().with_variant(mysql.DATETIME(fsp=6), "mysql"),
            nullable=False,
        ),
        sa.Column("id", sqlalchemy_utils.types.uuid.UUIDType(), nullable=False),
        sa.Column(
            "json",
            sa.JSON()
            .with_variant(sqlalchemy_utils.types.json.JSONType(), "mysql")
            .with_variant(
                postgresql.JSONB(none_as_null=True, astext_type=sa.Text()), "postgresql"
            )
            .with_variant(sqlalchemy_utils.types.json.JSONType(), "sqlite"),
            nullable=True,
        ),
        sa.Column("version_id", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_geo_package_parents_metadata")),
    )
    op.create_table(
        "geo_package_records_metadata_version",
        sa.Column(
            "created",
            sa.DateTime().with_variant(mysql.DATETIME(fsp=6), "mysql"),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column(
            "updated",
            sa.DateTime().with_variant(mysql.DATETIME(fsp=6), "mysql"),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column(
            "id",
            sqlalchemy_utils.types.uuid.UUIDType(),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column(
            "json",
            sa.JSON()
            .with_variant(sqlalchemy_utils.types.json.JSONType(), "mysql")
            .with_variant(
                postgresql.JSONB(none_as_null=True, astext_type=sa.Text()), "postgresql"
            )
            .with_variant(sqlalchemy_utils.types.json.JSONType(), "sqlite"),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column("version_id", sa.Integer(), autoincrement=False, nullable=True),
        sa.Column("index", sa.Integer(), autoincrement=False, nullable=True),
        sa.Column(
            "bucket_id",
            sqlalchemy_utils.types.uuid.UUIDType(),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column(
            "parent_id",
            sqlalchemy_utils.types.uuid.UUIDType(),
            autoincrement=False,
            nullable=True,
        ),
        sa.Column(
            "transaction_id", sa.BigInteger(), autoincrement=False, nullable=False
        ),
        sa.Column("end_transaction_id", sa.BigInteger(), nullable=True),
        sa.Column("operation_type", sa.SmallInteger(), nullable=False),
        sa.PrimaryKeyConstraint(
            "id", "transaction_id", name=op.f("pk_geo_package_records_metadata_version")
        ),
    )
    op.create_index(
        op.f("ix_geo_package_records_metadata_version_end_transaction_id"),
        "geo_package_records_metadata_version",
        ["end_transaction_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_geo_package_records_metadata_version_operation_type"),
        "geo_package_records_metadata_version",
        ["operation_type"],
        unique=False,
    )
    op.create_index(
        op.f("ix_geo_package_records_metadata_version_transaction_id"),
        "geo_package_records_metadata_version",
        ["transaction_id"],
        unique=False,
    )
    op.create_table(
        "geo_package_archivedinvitations",
        sa.Column(
            "created",
            sa.DateTime().with_variant(mysql.DATETIME(fsp=6), "mysql"),
            nullable=False,
        ),
        sa.Column(
            "updated",
            sa.DateTime().with_variant(mysql.DATETIME(fsp=6), "mysql"),
            nullable=False,
        ),
        sa.Column(
            "json",
            sa.JSON()
            .with_variant(sqlalchemy_utils.types.json.JSONType(), "mysql")
            .with_variant(
                postgresql.JSONB(none_as_null=True, astext_type=sa.Text()), "postgresql"
            )
            .with_variant(sqlalchemy_utils.types.json.JSONType(), "sqlite"),
            nullable=True,
        ),
        sa.Column("version_id", sa.Integer(), nullable=False),
        sa.Column("id", sqlalchemy_utils.types.uuid.UUIDType(), nullable=False),
        sa.Column("role", sa.String(length=50), nullable=False),
        sa.Column("visible", sa.Boolean(), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.Column("package_id", sqlalchemy_utils.types.uuid.UUIDType(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("group_id", sa.Integer(), nullable=True),
        sa.Column("request_id", sqlalchemy_utils.types.uuid.UUIDType(), nullable=True),
        sa.ForeignKeyConstraint(
            ["group_id"],
            ["accounts_role.id"],
            name=op.f("fk_geo_package_archivedinvitations_group_id_accounts_role"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["package_id"],
            ["geo_package_parents_metadata.id"],
            name=op.f(
                "fk_geo_package_archivedinvitations_package_id_geo_package_parents_metadata"
            ),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["request_id"],
            ["request_metadata.id"],
            name=op.f("fk_geo_package_archivedinvitations_request_id_request_metadata"),
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["accounts_user.id"],
            name=op.f("fk_geo_package_archivedinvitations_user_id_accounts_user"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_geo_package_archivedinvitations")),
        sa.UniqueConstraint(
            "request_id", name=op.f("uq_geo_package_archivedinvitations_request_id")
        ),
    )
    op.create_index(
        op.f("ix_geo_package_archivedinvitations_active"),
        "geo_package_archivedinvitations",
        ["active"],
        unique=False,
    )
    op.create_table(
        "geo_package_members",
        sa.Column(
            "created",
            sa.DateTime().with_variant(mysql.DATETIME(fsp=6), "mysql"),
            nullable=False,
        ),
        sa.Column(
            "updated",
            sa.DateTime().with_variant(mysql.DATETIME(fsp=6), "mysql"),
            nullable=False,
        ),
        sa.Column(
            "json",
            sa.JSON()
            .with_variant(sqlalchemy_utils.types.json.JSONType(), "mysql")
            .with_variant(
                postgresql.JSONB(none_as_null=True, astext_type=sa.Text()), "postgresql"
            )
            .with_variant(sqlalchemy_utils.types.json.JSONType(), "sqlite"),
            nullable=True,
        ),
        sa.Column("version_id", sa.Integer(), nullable=False),
        sa.Column("id", sqlalchemy_utils.types.uuid.UUIDType(), nullable=False),
        sa.Column("role", sa.String(length=50), nullable=False),
        sa.Column("visible", sa.Boolean(), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.Column("package_id", sqlalchemy_utils.types.uuid.UUIDType(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("group_id", sa.Integer(), nullable=True),
        sa.Column("request_id", sqlalchemy_utils.types.uuid.UUIDType(), nullable=True),
        sa.CheckConstraint(
            "(user_id IS NULL AND group_id IS NOT NULL) OR (user_id IS NOT NULL AND group_id IS NULL)",
            name=op.f("ck_geo_package_members_user_or_group"),
        ),
        sa.ForeignKeyConstraint(
            ["group_id"],
            ["accounts_role.id"],
            name=op.f("fk_geo_package_members_group_id_accounts_role"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["package_id"],
            ["geo_package_parents_metadata.id"],
            name=op.f("fk_geo_package_members_package_id_geo_package_parents_metadata"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["request_id"],
            ["request_metadata.id"],
            name=op.f("fk_geo_package_members_request_id_request_metadata"),
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["accounts_user.id"],
            name=op.f("fk_geo_package_members_user_id_accounts_user"),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_geo_package_members")),
        sa.UniqueConstraint(
            "request_id", name=op.f("uq_geo_package_members_request_id")
        ),
    )
    op.create_index(
        op.f("ix_geo_package_members_active"),
        "geo_package_members",
        ["active"],
        unique=False,
    )
    op.create_index(
        "ix_package_group",
        "geo_package_members",
        ["package_id", "group_id"],
        unique=True,
    )
    op.create_index(
        "ix_package_user", "geo_package_members", ["package_id", "user_id"], unique=True
    )
    op.create_table(
        "geo_package_drafts_metadata",
        sa.Column(
            "created",
            sa.DateTime().with_variant(mysql.DATETIME(fsp=6), "mysql"),
            nullable=False,
        ),
        sa.Column(
            "updated",
            sa.DateTime().with_variant(mysql.DATETIME(fsp=6), "mysql"),
            nullable=False,
        ),
        sa.Column("id", sqlalchemy_utils.types.uuid.UUIDType(), nullable=False),
        sa.Column(
            "json",
            sa.JSON()
            .with_variant(sqlalchemy_utils.types.json.JSONType(), "mysql")
            .with_variant(
                postgresql.JSONB(none_as_null=True, astext_type=sa.Text()), "postgresql"
            )
            .with_variant(sqlalchemy_utils.types.json.JSONType(), "sqlite"),
            nullable=True,
        ),
        sa.Column("version_id", sa.Integer(), nullable=False),
        sa.Column("index", sa.Integer(), nullable=True),
        sa.Column("fork_version_id", sa.Integer(), nullable=True),
        sa.Column(
            "expires_at",
            sa.DateTime().with_variant(mysql.DATETIME(fsp=6), "mysql"),
            nullable=True,
        ),
        sa.Column("bucket_id", sqlalchemy_utils.types.uuid.UUIDType(), nullable=True),
        sa.Column("parent_id", sqlalchemy_utils.types.uuid.UUIDType(), nullable=True),
        sa.ForeignKeyConstraint(
            ["bucket_id"],
            ["files_bucket.id"],
            name=op.f("fk_geo_package_drafts_metadata_bucket_id_files_bucket"),
        ),
        sa.ForeignKeyConstraint(
            ["parent_id"],
            ["geo_package_parents_metadata.id"],
            name=op.f(
                "fk_geo_package_drafts_metadata_parent_id_geo_package_parents_metadata"
            ),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_geo_package_drafts_metadata")),
    )
    op.create_table(
        "geo_package_records_metadata",
        sa.Column(
            "created",
            sa.DateTime().with_variant(mysql.DATETIME(fsp=6), "mysql"),
            nullable=False,
        ),
        sa.Column(
            "updated",
            sa.DateTime().with_variant(mysql.DATETIME(fsp=6), "mysql"),
            nullable=False,
        ),
        sa.Column("id", sqlalchemy_utils.types.uuid.UUIDType(), nullable=False),
        sa.Column(
            "json",
            sa.JSON()
            .with_variant(sqlalchemy_utils.types.json.JSONType(), "mysql")
            .with_variant(
                postgresql.JSONB(none_as_null=True, astext_type=sa.Text()), "postgresql"
            )
            .with_variant(sqlalchemy_utils.types.json.JSONType(), "sqlite"),
            nullable=True,
        ),
        sa.Column("version_id", sa.Integer(), nullable=False),
        sa.Column("index", sa.Integer(), nullable=True),
        sa.Column("bucket_id", sqlalchemy_utils.types.uuid.UUIDType(), nullable=True),
        sa.Column("parent_id", sqlalchemy_utils.types.uuid.UUIDType(), nullable=True),
        sa.ForeignKeyConstraint(
            ["bucket_id"],
            ["files_bucket.id"],
            name=op.f("fk_geo_package_records_metadata_bucket_id_files_bucket"),
        ),
        sa.ForeignKeyConstraint(
            ["parent_id"],
            ["geo_package_parents_metadata.id"],
            name=op.f(
                "fk_geo_package_records_metadata_parent_id_geo_package_parents_metadata"
            ),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_geo_package_records_metadata")),
    )
    op.create_table(
        "geo_package_drafts_files",
        sa.Column(
            "created",
            sa.DateTime().with_variant(mysql.DATETIME(fsp=6), "mysql"),
            nullable=False,
        ),
        sa.Column(
            "updated",
            sa.DateTime().with_variant(mysql.DATETIME(fsp=6), "mysql"),
            nullable=False,
        ),
        sa.Column("id", sqlalchemy_utils.types.uuid.UUIDType(), nullable=False),
        sa.Column(
            "json",
            sa.JSON()
            .with_variant(sqlalchemy_utils.types.json.JSONType(), "mysql")
            .with_variant(
                postgresql.JSONB(none_as_null=True, astext_type=sa.Text()), "postgresql"
            )
            .with_variant(sqlalchemy_utils.types.json.JSONType(), "sqlite"),
            nullable=True,
        ),
        sa.Column("version_id", sa.Integer(), nullable=False),
        sa.Column(
            "key",
            sa.Text().with_variant(mysql.VARCHAR(length=255), "mysql"),
            nullable=False,
        ),
        sa.Column("record_id", sqlalchemy_utils.types.uuid.UUIDType(), nullable=False),
        sa.Column(
            "object_version_id", sqlalchemy_utils.types.uuid.UUIDType(), nullable=True
        ),
        sa.ForeignKeyConstraint(
            ["object_version_id"],
            ["files_object.version_id"],
            name=op.f("fk_geo_package_drafts_files_object_version_id_files_object"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["record_id"],
            ["geo_package_drafts_metadata.id"],
            name=op.f(
                "fk_geo_package_drafts_files_record_id_geo_package_drafts_metadata"
            ),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_geo_package_drafts_files")),
    )
    op.create_index(
        "uidx_geo_package_drafts_files_id_key",
        "geo_package_drafts_files",
        ["id", "key"],
        unique=True,
    )
    op.create_table(
        "geo_package_parents_community",
        sa.Column(
            "community_id", sqlalchemy_utils.types.uuid.UUIDType(), nullable=False
        ),
        sa.Column("record_id", sqlalchemy_utils.types.uuid.UUIDType(), nullable=False),
        sa.Column("request_id", sqlalchemy_utils.types.uuid.UUIDType(), nullable=True),
        sa.ForeignKeyConstraint(
            ["community_id"],
            ["communities_metadata.id"],
            name=op.f(
                "fk_geo_package_parents_community_community_id_communities_metadata"
            ),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["record_id"],
            ["geo_package_parents_metadata.id"],
            name=op.f(
                "fk_geo_package_parents_community_record_id_geo_package_parents_metadata"
            ),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["request_id"],
            ["request_metadata.id"],
            name=op.f("fk_geo_package_parents_community_request_id_request_metadata"),
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint(
            "community_id", "record_id", name=op.f("pk_geo_package_parents_community")
        ),
    )
    op.create_table(
        "geo_package_records_files",
        sa.Column(
            "created",
            sa.DateTime().with_variant(mysql.DATETIME(fsp=6), "mysql"),
            nullable=False,
        ),
        sa.Column(
            "updated",
            sa.DateTime().with_variant(mysql.DATETIME(fsp=6), "mysql"),
            nullable=False,
        ),
        sa.Column("id", sqlalchemy_utils.types.uuid.UUIDType(), nullable=False),
        sa.Column(
            "json",
            sa.JSON()
            .with_variant(sqlalchemy_utils.types.json.JSONType(), "mysql")
            .with_variant(
                postgresql.JSONB(none_as_null=True, astext_type=sa.Text()), "postgresql"
            )
            .with_variant(sqlalchemy_utils.types.json.JSONType(), "sqlite"),
            nullable=True,
        ),
        sa.Column("version_id", sa.Integer(), nullable=False),
        sa.Column(
            "key",
            sa.Text().with_variant(mysql.VARCHAR(length=255), "mysql"),
            nullable=False,
        ),
        sa.Column("record_id", sqlalchemy_utils.types.uuid.UUIDType(), nullable=False),
        sa.Column(
            "object_version_id", sqlalchemy_utils.types.uuid.UUIDType(), nullable=True
        ),
        sa.ForeignKeyConstraint(
            ["object_version_id"],
            ["files_object.version_id"],
            name=op.f("fk_geo_package_records_files_object_version_id_files_object"),
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["record_id"],
            ["geo_package_records_metadata.id"],
            name=op.f(
                "fk_geo_package_records_files_record_id_geo_package_records_metadata"
            ),
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_geo_package_records_files")),
    )
    op.create_index(
        "uidx_geo_package_records_files_id_key",
        "geo_package_records_files",
        ["id", "key"],
        unique=True,
    )
    op.create_table(
        "geo_package_versions_state",
        sa.Column("latest_index", sa.Integer(), nullable=True),
        sa.Column("parent_id", sqlalchemy_utils.types.uuid.UUIDType(), nullable=False),
        sa.Column("latest_id", sqlalchemy_utils.types.uuid.UUIDType(), nullable=True),
        sa.Column(
            "next_draft_id", sqlalchemy_utils.types.uuid.UUIDType(), nullable=True
        ),
        sa.ForeignKeyConstraint(
            ["latest_id"],
            ["geo_package_records_metadata.id"],
            name=op.f(
                "fk_geo_package_versions_state_latest_id_geo_package_records_metadata"
            ),
        ),
        sa.ForeignKeyConstraint(
            ["next_draft_id"],
            ["geo_package_drafts_metadata.id"],
            name=op.f(
                "fk_geo_package_versions_state_next_draft_id_geo_package_drafts_metadata"
            ),
        ),
        sa.ForeignKeyConstraint(
            ["parent_id"],
            ["geo_package_parents_metadata.id"],
            name=op.f(
                "fk_geo_package_versions_state_parent_id_geo_package_parents_metadata"
            ),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint(
            "parent_id", name=op.f("pk_geo_package_versions_state")
        ),
    )
    op.drop_index("ix_uq_partial_files_object_is_head", table_name="files_object")
    # ### end Alembic commands ###


def downgrade():
    """Downgrade database."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index(
        "ix_uq_partial_files_object_is_head",
        "files_object",
        ["bucket_id", "key"],
        unique=False,
    )
    op.drop_table("geo_package_versions_state")
    op.drop_index(
        "uidx_geo_package_records_files_id_key", table_name="geo_package_records_files"
    )
    op.drop_table("geo_package_records_files")
    op.drop_table("geo_package_parents_community")
    op.drop_index(
        "uidx_geo_package_drafts_files_id_key", table_name="geo_package_drafts_files"
    )
    op.drop_table("geo_package_drafts_files")
    op.drop_table("geo_package_records_metadata")
    op.drop_table("geo_package_drafts_metadata")
    op.drop_index("ix_package_user", table_name="geo_package_members")
    op.drop_index("ix_package_group", table_name="geo_package_members")
    op.drop_index(
        op.f("ix_geo_package_members_active"), table_name="geo_package_members"
    )
    op.drop_table("geo_package_members")
    op.drop_index(
        op.f("ix_geo_package_archivedinvitations_active"),
        table_name="geo_package_archivedinvitations",
    )
    op.drop_table("geo_package_archivedinvitations")
    op.drop_index(
        op.f("ix_geo_package_records_metadata_version_transaction_id"),
        table_name="geo_package_records_metadata_version",
    )
    op.drop_index(
        op.f("ix_geo_package_records_metadata_version_operation_type"),
        table_name="geo_package_records_metadata_version",
    )
    op.drop_index(
        op.f("ix_geo_package_records_metadata_version_end_transaction_id"),
        table_name="geo_package_records_metadata_version",
    )
    op.drop_table("geo_package_records_metadata_version")
    op.drop_table("geo_package_parents_metadata")
    # ### end Alembic commands ###
