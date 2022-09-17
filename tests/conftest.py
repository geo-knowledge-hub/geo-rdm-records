# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""Pytest configuration.

See https://pytest-invenio.readthedocs.io/ for documentation on which test
fixtures are available.
"""

from collections import namedtuple
from copy import deepcopy

import pytest
from fake_datacite_client import FakeDataCiteClient
from flask import g
from flask_principal import Identity, Need, UserNeed
from flask_security import login_user, logout_user
from flask_security.utils import hash_password
from invenio_access.models import ActionRoles
from invenio_access.permissions import superuser_access, system_identity
from invenio_accounts.models import Role
from invenio_accounts.testutils import login_user_via_session
from invenio_admin.permissions import action_admin_access
from invenio_app.factory import create_api as _create_api
from invenio_communities.communities.records.api import Community
from invenio_rdm_records.services.pids import providers
from invenio_records_resources.proxies import current_service_registry
from invenio_vocabularies.contrib.affiliations.api import Affiliation
from invenio_vocabularies.contrib.awards.api import Award
from invenio_vocabularies.contrib.funders.api import Funder
from invenio_vocabularies.contrib.subjects.api import Subject
from invenio_vocabularies.proxies import current_service as vocabulary_service
from invenio_vocabularies.records.api import Vocabulary

from geo_rdm_records import config
from geo_rdm_records.customizations.records.api import GEODraft, GEORecord
from geo_rdm_records.modules.packages.records.api import (
    GEOPackageDraft,
    GEOPackageRecord,
)


#
# Application
#
def _(x):
    """Identity function for string extraction."""
    return x


@pytest.fixture(scope="module")
def celery_config():
    """Override pytest-invenio fixture."""
    return {}


@pytest.fixture(scope="module")
def app_config(app_config):
    """Override pytest-invenio app_config fixture.

    For test purposes we need to enforce the configuration variables set in
    config.py. Because invenio-rdm-records is not a flavour extension, it does
    not enforce them via a config entrypoint or ext.py; only flavour
    extensions are allowed to forcefully set configuration.

    This means there is a clash between configuration set by
    invenio-records-rest and this module for instance. We want this module's
    config.py to apply in tests.
    """
    supported_configurations = [
        "FILES_REST_PERMISSION_FACTORY",
        "PIDSTORE_RECID_FIELD",
        "RECORDS_PERMISSIONS_RECORD_POLICY",
        "RECORDS_REST_ENDPOINTS",
    ]

    for config_key in supported_configurations:
        app_config[config_key] = getattr(config, config_key, None)

    app_config[
        "RECORDS_REFRESOLVER_CLS"
    ] = "invenio_records.resolver.InvenioRefResolver"
    app_config[
        "RECORDS_REFRESOLVER_STORE"
    ] = "invenio_jsonschemas.proxies.current_refresolver_store"

    # OAI Server
    app_config["OAISERVER_ID_PREFIX"] = "oai:inveniosoftware.org:recid/"
    app_config["OAISERVER_RECORD_INDEX"] = "rdmrecords-records"
    app_config["OAISERVER_METADATA_FORMATS"] = {
        "oai_dc": {
            "serializer": "invenio_rdm_records.oai:dublincore_etree",
            "schema": "http://www.openarchives.org/OAI/2.0/oai_dc.xsd",
            "namespace": "http://www.openarchives.org/OAI/2.0/oai_dc/",
        },
        "datacite": {
            "serializer": "invenio_rdm_records.oai:datacite_etree",
            "schema": "http://schema.datacite.orgmeta/nonexistant/nonexistant.xsd",  # noqa
            "namespace": "http://datacite.org/schema/nonexistant",
        },
        "oai_datacite": {
            "serializer": "invenio_rdm_records.oai:oai_datacite_etree",
            "schema": "http://schema.datacite.org/oai/oai-1.1/oai.xsd",
            "namespace": "http://schema.datacite.org/oai/oai-1.1/",
        },
    }
    app_config["INDEXER_DEFAULT_INDEX"] = "rdmrecords-records-record-v5.0.0"
    # Variable not used. We set it to silent warnings
    app_config["JSONSCHEMAS_HOST"] = "not-used"

    # Enable DOI minting...
    app_config["DATACITE_ENABLED"] = True
    app_config["DATACITE_USERNAME"] = "INVALID"
    app_config["DATACITE_PASSWORD"] = "INVALID"
    app_config["DATACITE_PREFIX"] = "10.1234"
    app_config["DATACITE_DATACENTER_SYMBOL"] = "TEST"
    # ...but fake it

    app_config["RDM_PERSISTENT_IDENTIFIER_PROVIDERS"] = [
        # DataCite DOI provider with fake client
        providers.DataCitePIDProvider(
            "datacite",
            client=FakeDataCiteClient("datacite", config_prefix="DATACITE"),
            label=_("DOI"),
        ),
        # DOI provider for externally managed DOIs
        providers.ExternalPIDProvider(
            "external",
            "doi",
            validators=[providers.BlockedPrefixes(config_names=["DATACITE_PREFIX"])],
            label=_("DOI"),
        ),
        # OAI identifier
        providers.OAIPIDProvider(
            "oai",
            label=_("OAI ID"),
        ),
    ]

    # GEO RDM Records Configurations
    app_config[
        "RDM_RECORD_RESOURCE"
    ] = "geo_rdm_records.customizations.resources.resource.GEORDMRecordResource"

    app_config[
        "RDM_RECORD_RESOURCE_CFG"
    ] = "geo_rdm_records.customizations.resources.config.GEORecordResourceConfig"

    app_config[
        "RDM_RECORD_SERVICE"
    ] = "geo_rdm_records.customizations.services.service.GEORDMRecordService"

    app_config[
        "RDM_RECORD_SERVICE_CFG"
    ] = "geo_rdm_records.customizations.services.config.GEORecordServiceConfig"

    app_config[
        "RDM_FILE_SERVICE_CFG"
    ] = "geo_rdm_records.customizations.services.config.GEOFileRecordServiceConfig"

    app_config[
        "RDM_FILE_DRAFT_SERVICE_CFG"
    ] = "geo_rdm_records.customizations.services.config.GEOFileDraftServiceConfig"

    app_config[
        "RDM_REVIEW_SERVICE"
    ] = "geo_rdm_records.customizations.services.review.service.ReviewService"

    #
    # Actions
    #
    app_config[
        "RDM_COMMUNITY_ACTION_SUBMIT"
    ] = "geo_rdm_records.base.requests.SubmitAction"

    app_config[
        "RDM_COMMUNITY_ACTION_ACCEPT"
    ] = "geo_rdm_records.base.requests.AcceptAction"

    app_config[
        "RDM_COMMUNITY_ACTION_DECLINE"
    ] = "geo_rdm_records.base.requests.DeclineAction"

    app_config[
        "RDM_COMMUNITY_ACTION_CANCEL"
    ] = "geo_rdm_records.base.requests.CancelAction"

    app_config[
        "RDM_COMMUNITY_ACTION_EXPIRE"
    ] = "geo_rdm_records.base.requests.ExpireAction"

    return app_config


@pytest.fixture
def running_app(
    app,
    superuser_identity,
    location,
    cache,
    resource_type_v,
    subject_v,
    languages_v,
    affiliations_v,
    title_type_v,
    description_type_v,
    date_type_v,
    contributors_role_v,
    relation_type_v,
    licenses_v,
    funders_v,
    awards_v,
    target_users_v,
    programme_activities_v,
    engagement_priorities_v,
):
    """This fixture provides an app with the typically needed db data loaded.

    All of these fixtures are often needed together, so collecting them
    under a semantic umbrella makes sense.
    """
    return RunningApp(
        app,
        superuser_identity,
        location,
        cache,
        resource_type_v,
        subject_v,
        languages_v,
        affiliations_v,
        title_type_v,
        description_type_v,
        date_type_v,
        contributors_role_v,
        relation_type_v,
        licenses_v,
        funders_v,
        awards_v,
        target_users_v,
        programme_activities_v,
        engagement_priorities_v,
    )


@pytest.fixture(scope="module")
def create_app(instance_path):
    """Application factory fixture."""
    return _create_api


#
# Elasticsearch configurations and fixtures
#
def _es_create_indexes(current_search, current_search_client):
    """Create all registered Elasticsearch indexes."""
    to_create = [
        GEODraft.index._name,
        GEORecord.index._name,
        GEOPackageRecord.index._name,
        GEOPackageDraft.index._name,
        Community.index._name,
    ]
    # list to trigger iter
    list(current_search.create(ignore_existing=True, index_list=to_create))
    current_search_client.indices.refresh()


def _es_delete_indexes(current_search):
    """Delete all registered Elasticsearch indexes."""
    to_delete = [
        GEODraft.index._name,
        GEORecord.index._name,
        GEOPackageRecord.index._name,
        GEOPackageDraft.index._name,
        Community.index._name,
    ]
    list(current_search.delete(index_list=to_delete))


# overwrite pytest_invenio.fixture to only delete record indices
# keeping vocabularies.
@pytest.fixture(scope="function")
def es_clear(es):
    """Clear Elasticsearch indices after test finishes (function scope).

    This fixture rollback any changes performed to the indexes during a test,
    in order to leave Elasticsearch in a clean state for the next test.
    """
    from invenio_search import current_search, current_search_client

    yield es
    _es_delete_indexes(current_search)
    _es_create_indexes(current_search, current_search_client)


@pytest.fixture()
def refresh_index():
    """Refresh elasticsearch indices."""

    def _wrapper():
        GEOPackageDraft.index.refresh()
        GEODraft.index.refresh()
        GEORecord.index.refresh()

    return _wrapper


#
# Requests
#
@pytest.fixture(scope="session")
def headers():
    """Default headers for making requests."""
    return {
        "content-type": "application/json",
        "accept": "application/json",
    }


#
# Records (resources) and Packages
#
@pytest.fixture(scope="function")
def minimal_record():
    """Minimal record data as dict coming from the external world."""
    return {
        "pids": {},
        "access": {
            "record": "public",
            "files": "public",
        },
        "files": {
            "enabled": False,  # Most tests don't care about files
        },
        "metadata": {
            "target_audiences": [{"id": "tu-geo-eoanalyst"}],
            "engagement_priorities": [
                {
                    "id": "convention-on-biological-diversity",
                }
            ],
            "geo_work_programme_activity": {
                "id": "geo-activities-geobon",
            },
            "publication_date": "2020-06-01",
            "resource_type": {"id": "image-photo"},
            "creators": [
                {
                    "person_or_org": {
                        "family_name": "Brown",
                        "given_name": "Troy",
                        "type": "personal",
                    }
                },
                {
                    "person_or_org": {
                        "name": "Troy Inc.",
                        "type": "organizational",
                    },
                },
            ],
            "title": "A Romans story",
        },
    }


@pytest.fixture()
def minimal_community():
    """Data for a minimal community."""
    return {
        "slug": "blr",
        "access": {
            "visibility": "public",
        },
        "metadata": {
            "title": "Biodiversity Literature Repository",
            "type": {"id": "topic"},
        },
    }


@pytest.fixture(scope="module")
def minimal_package():
    """Minimal package metadata."""
    return {
        "pids": {},
        "access": {
            "record": "public",
            "files": "public",
        },
        "files": {
            "enabled": False,  # Most tests don't care about files
        },
        "metadata": {
            "publication_date": "2020-06-01",
            "resource_type": {"id": "image-photo"},
            "creators": [
                {
                    "person_or_org": {
                        "family_name": "Brown",
                        "given_name": "Troy",
                        "type": "personal",
                    }
                },
                {
                    "person_or_org": {
                        "name": "Troy Inc.",
                        "type": "organizational",
                    },
                },
            ],
            "title": "A Romans story",
        },
    }


#
# Communities
#
@pytest.fixture()
def community_record(running_app, db):
    """Basic community fixture."""
    _c = Community.create({})
    _c.commit()
    db.session.commit()

    return _c


#
# Users and identities
#
class UserFixture_:
    """A user fixture for easy test user creation."""

    def __init__(self, email=None, password=None, active=True):
        """Constructor."""
        self._email = email
        self._active = active
        self._password = password
        self._identity = None
        self._user = None
        self._client = None

    #
    # Creation
    #
    def create(self, app, db):
        """Create the user."""
        with db.session.begin_nested():
            datastore = app.extensions["security"].datastore
            user = datastore.create_user(
                email=self.email,
                password=hash_password(self.password),
                active=self._active,
            )
        db.session.commit()
        self._user = user
        return self

    #
    # Properties
    #
    @property
    def user(self):
        """Get the user."""
        return self._user

    @property
    def id(self):
        """Get the user id as a string."""
        return str(self._user.id)

    @property
    def email(self):
        """Get the user."""
        return self._email

    @property
    def password(self):
        """Get the user."""
        return self._password

    #
    # App context helpers
    #
    @property
    def identity(self):
        """Create identity for the user."""
        if self._identity is None:
            # Simulate a full login
            assert login_user(self.user)
            self._identity = deepcopy(g.identity)
            # Clean up - we just want the identity object.
            logout_user()
        return self._identity

    @identity.deleter
    def identity(self):
        """Delete the user."""
        self._identity = None

    def app_login(self):
        """Create identity for the user."""
        assert login_user(self.user)

    def app_logout(self):
        """Create identity for the user."""
        assert logout_user()

    @identity.deleter
    def identity(self):
        """Delete the user."""
        self._identity = None

    #
    # Test client helpers
    #
    def login(self, client, logout_first=False):
        """Login the given client."""
        return self._login(client, "/", logout_first)

    def api_login(self, client, logout_first=False):
        """Login the given client."""
        return self._login(client, "/api/", logout_first)

    def logout(self, client):
        """Logout the given client."""
        return self._logout(client, "/")

    def api_logout(self, client):
        """Logout the given client."""
        return self._logout(client, "/api/")

    def _login(self, client, base_path, logout):
        """Login the given client."""
        if logout:
            self._logout(client, base_path)
        res = client.post(
            f"{base_path}login",
            data=dict(email=self.email, password=self.password),
            environ_base={"REMOTE_ADDR": "127.0.0.1"},
            follow_redirects=True,
        )
        assert res.status_code == 200
        return client

    def _logout(self, client, base_path):
        """Logout the client."""
        res = client.get(f"{base_path}logout")
        assert res.status_code < 400
        return client


@pytest.fixture(scope="function")
def identity_simple(users):
    """Simple identity fixture."""
    user = users[0]
    i = Identity(user.id)
    i.provides.add(UserNeed(user.id))
    i.provides.add(Need(method="system_role", value="any_user"))
    i.provides.add(Need(method="system_role", value="authenticated_user"))
    return i


RunningApp = namedtuple(
    "RunningApp",
    [
        "app",
        "superuser_identity",
        "location",
        "cache",
        "resource_type_v",
        "subject_v",
        "languages_v",
        "affiliations_v",
        "title_type_v",
        "description_type_v",
        "date_type_v",
        "contributors_role_v",
        "relation_type_v",
        "licenses_v",
        "funders_v",
        "awards_v",
        "target_users_v",
        "programme_activities_v",
        "engagement_priorities_v",
    ],
)


@pytest.fixture(scope="session")
def UserFixture():
    """Class to create user fixtures from."""
    return UserFixture_


@pytest.fixture(scope="function")
def superuser_role_need(db):
    """Store 1 role with 'superuser-access' ActionNeed.

    WHY: This is needed because expansion of ActionNeed is
         done on the basis of a User/Role being associated with that Need.
         If no User/Role is associated with that Need (in the DB), the
         permission is expanded to an empty list.
    """
    role = Role(name="superuser-access")
    db.session.add(role)

    action_role = ActionRoles.create(action=superuser_access, role=role)
    db.session.add(action_role)

    db.session.commit()

    return action_role.need


@pytest.fixture(scope="function")
def superuser_identity(admin, superuser_role_need):
    """Superuser identity fixture."""
    identity = admin.identity
    identity.provides.add(superuser_role_need)
    return identity


@pytest.fixture(scope="function")
def admin_role_need(db):
    """Store 1 role with 'superuser-access' ActionNeed.

    WHY: This is needed because expansion of ActionNeed is
         done on the basis of a User/Role being associated with that Need.
         If no User/Role is associated with that Need (in the DB), the
         permission is expanded to an empty list.
    """
    role = Role(name="admin-access")
    db.session.add(role)

    action_role = ActionRoles.create(action=action_admin_access, role=role)
    db.session.add(action_role)

    db.session.commit()

    return action_role.need


@pytest.fixture()
def admin(UserFixture, app, db, admin_role_need):
    """Admin user for requests."""
    u = UserFixture(
        email="admin@inveniosoftware.org",
        password="admin",
    )
    u.create(app, db)

    datastore = app.extensions["security"].datastore
    _, role = datastore._prepare_role_modify_args(u.user, "admin-access")

    datastore.add_role_to_user(u.user, role)
    db.session.commit()
    return u


@pytest.fixture()
def users(app, db):
    """Create example user."""
    with db.session.begin_nested():
        datastore = app.extensions["security"].datastore
        user1 = datastore.create_user(
            email="info@inveniosoftware.org",
            password=hash_password("password"),
            active=True,
        )
        user2 = datastore.create_user(
            email="ser-testalot@inveniosoftware.org",
            password=hash_password("beetlesmasher"),
            active=True,
        )

    db.session.commit()
    return [user1, user2]


@pytest.fixture()
def client_with_login(client, users):
    """Log in a user to the client."""
    user = users[0]
    login_user(user)
    login_user_via_session(client, email=user.email)
    return client


#
# Vocabularies
#
@pytest.fixture(scope="module")
def resource_type_type(app):
    """Resource type vocabulary type."""
    return vocabulary_service.create_type(system_identity, "resourcetypes", "rsrct")


@pytest.fixture(scope="module")
def resource_type_v(app, resource_type_type):
    """Resource type vocabulary record."""
    vocabulary_service.create(
        system_identity,
        {
            "id": "dataset",
            "icon": "table",
            "props": {
                "csl": "dataset",
                "datacite_general": "Dataset",
                "datacite_type": "",
                "openaire_resourceType": "21",
                "openaire_type": "dataset",
                "eurepo": "info:eu-repo/semantics/other",
                "schema.org": "https://schema.org/Dataset",
                "subtype": "",
                "type": "dataset",
            },
            "title": {"en": "Dataset"},
            "tags": ["depositable", "linkable"],
            "type": "resourcetypes",
        },
    )

    vocabulary_service.create(
        system_identity,
        {  # create base resource type
            "id": "image",
            "props": {
                "csl": "figure",
                "datacite_general": "Image",
                "datacite_type": "",
                "openaire_resourceType": "25",
                "openaire_type": "dataset",
                "eurepo": "info:eu-repo/semantic/other",
                "schema.org": "https://schema.org/ImageObject",
                "subtype": "",
                "type": "image",
            },
            "icon": "chart bar outline",
            "title": {"en": "Image"},
            "tags": ["depositable", "linkable"],
            "type": "resourcetypes",
        },
    )

    vocab = vocabulary_service.create(
        system_identity,
        {
            "id": "image-photo",
            "props": {
                "csl": "graphic",
                "datacite_general": "Image",
                "datacite_type": "Photo",
                "openaire_resourceType": "25",
                "openaire_type": "dataset",
                "eurepo": "info:eu-repo/semantic/other",
                "schema.org": "https://schema.org/Photograph",
                "subtype": "image-photo",
                "type": "image",
            },
            "icon": "chart bar outline",
            "title": {"en": "Photo"},
            "tags": ["depositable", "linkable"],
            "type": "resourcetypes",
        },
    )

    Vocabulary.index.refresh()

    return vocab


@pytest.fixture(scope="module")
def subject_v(app):
    """Subject vocabulary record."""
    subjects_service = current_service_registry.get("subjects")
    vocab = subjects_service.create(
        system_identity,
        {
            "id": "http://id.nlm.nih.gov/mesh/A-D000007",
            "scheme": "MeSH",
            "subject": "Abdominal Injuries",
        },
    )

    Subject.index.refresh()

    return vocab


@pytest.fixture(scope="module")
def languages_type(app):
    """Lanuage vocabulary type."""
    return vocabulary_service.create_type(system_identity, "languages", "lng")


@pytest.fixture(scope="module")
def languages_v(app, languages_type):
    """Language vocabulary record."""
    vocabulary_service.create(
        system_identity,
        {
            "id": "dan",
            "title": {
                "en": "Danish",
                "da": "Dansk",
            },
            "props": {"alpha_2": "da"},
            "tags": ["individual", "living"],
            "type": "languages",
        },
    )

    vocab = vocabulary_service.create(
        system_identity,
        {
            "id": "eng",
            "title": {
                "en": "English",
                "da": "Engelsk",
            },
            "tags": ["individual", "living"],
            "type": "languages",
        },
    )

    Vocabulary.index.refresh()

    return vocab


@pytest.fixture(scope="module")
def affiliations_v(app):
    """Affiliation vocabulary record."""
    affiliations_service = current_service_registry.get("affiliations")
    aff = affiliations_service.create(
        system_identity,
        {
            "id": "cern",
            "name": "CERN",
            "acronym": "CERN",
            "identifiers": [
                {
                    "scheme": "ror",
                    "identifier": "01ggx4157",
                },
                {
                    "scheme": "isni",
                    "identifier": "000000012156142X",
                },
            ],
        },
    )

    Affiliation.index.refresh()

    return aff


@pytest.fixture(scope="module")
def title_type(app):
    """Title vocabulary type."""
    return vocabulary_service.create_type(system_identity, "titletypes", "ttyp")


@pytest.fixture(scope="module")
def title_type_v(app, title_type):
    """Title Type vocabulary record."""
    vocabulary_service.create(
        system_identity,
        {
            "id": "subtitle",
            "props": {"datacite": "Subtitle"},
            "title": {"en": "Subtitle"},
            "type": "titletypes",
        },
    )

    vocab = vocabulary_service.create(
        system_identity,
        {
            "id": "alternative-title",
            "props": {"datacite": "AlternativeTitle"},
            "title": {"en": "Alternative title"},
            "type": "titletypes",
        },
    )

    Vocabulary.index.refresh()

    return vocab


@pytest.fixture(scope="module")
def description_type(app):
    """Description vocabulary type."""
    return vocabulary_service.create_type(system_identity, "descriptiontypes", "dty")


@pytest.fixture(scope="module")
def description_type_v(app, description_type):
    """Description Type vocabulary record."""
    vocab = vocabulary_service.create(
        system_identity,
        {
            "id": "methods",
            "title": {"en": "Methods"},
            "props": {"datacite": "Methods"},
            "type": "descriptiontypes",
        },
    )

    Vocabulary.index.refresh()

    return vocab


@pytest.fixture(scope="module")
def date_type(app):
    """Date vocabulary type."""
    return vocabulary_service.create_type(system_identity, "datetypes", "dat")


@pytest.fixture(scope="module")
def date_type_v(app, date_type):
    """Subject vocabulary record."""
    vocab = vocabulary_service.create(
        system_identity,
        {
            "id": "other",
            "title": {"en": "Other"},
            "props": {"datacite": "Other"},
            "type": "datetypes",
        },
    )

    Vocabulary.index.refresh()

    return vocab


@pytest.fixture(scope="module")
def contributors_role_type(app):
    """Contributor role vocabulary type."""
    return vocabulary_service.create_type(system_identity, "contributorsroles", "cor")


@pytest.fixture(scope="module")
def contributors_role_v(app, contributors_role_type):
    """Contributor role vocabulary record."""
    vocab = vocabulary_service.create(
        system_identity,
        {
            "id": "other",
            "props": {"datacite": "Other"},
            "title": {"en": "Other"},
            "type": "contributorsroles",
        },
    )

    Vocabulary.index.refresh()

    return vocab


@pytest.fixture(scope="module")
def relation_type(app):
    """Relation type vocabulary type."""
    return vocabulary_service.create_type(system_identity, "relationtypes", "rlt")


@pytest.fixture(scope="module")
def relation_type_v(app, relation_type):
    """Relation type vocabulary record."""
    vocab = vocabulary_service.create(
        system_identity,
        {
            "id": "iscitedby",
            "props": {"datacite": "IsCitedBy"},
            "title": {"en": "Is cited by"},
            "type": "relationtypes",
        },
    )

    Vocabulary.index.refresh()

    return vocab


@pytest.fixture(scope="module")
def licenses(app):
    """Licenses vocabulary type."""
    return vocabulary_service.create_type(system_identity, "licenses", "lic")


@pytest.fixture(scope="module")
def licenses_v(app, licenses):
    """Licenses vocabulary record."""
    vocab = vocabulary_service.create(
        system_identity,
        {
            "id": "cc-by-4.0",
            "props": {
                "url": "https://creativecommons.org/licenses/by/4.0/legalcode",
                "scheme": "spdx",
                "osi_approved": "",
            },
            "title": {"en": "Creative Commons Attribution 4.0 International"},
            "tags": ["recommended", "all"],
            "description": {
                "en": "The Creative Commons Attribution license allows"
                " re-distribution and re-use of a licensed work on"
                " the condition that the creator is appropriately credited."
            },
            "type": "licenses",
        },
    )

    Vocabulary.index.refresh()

    return vocab


@pytest.fixture(scope="module")
def funders_v(app):
    """Funder vocabulary record."""
    funders_service = current_service_registry.get("funders")
    funder = funders_service.create(
        system_identity,
        {
            "id": "00k4n6c32",
            "identifiers": [
                {
                    "identifier": "000000012156142X",
                    "scheme": "isni",
                },
                {
                    "identifier": "00k4n6c32",
                    "scheme": "ror",
                },
            ],
            "name": "European Commission",
            "title": {
                "en": "European Commission",
                "fr": "Commission européenne",
            },
            "country": "BE",
        },
    )

    Funder.index.refresh()

    return funder


@pytest.fixture(scope="module")
def awards_v(app, funders_v):
    """Funder vocabulary record."""
    awards_service = current_service_registry.get("awards")
    award = awards_service.create(
        system_identity,
        {
            "id": "755021",
            "identifiers": [
                {
                    "identifier": "https://cordis.europa.eu/project/id/755021",
                    "scheme": "url",
                }
            ],
            "number": "755021",
            "title": {
                "en": (
                    "Personalised Treatment For Cystic Fibrosis Patients With "
                    "Ultra-rare CFTR Mutations (and beyond)"
                ),
            },
            "funder": {"id": "00k4n6c32"},
            "acronym": "HIT-CF",
        },
    )

    Award.index.refresh()

    return award


@pytest.fixture(scope="module")
def target_users(app):
    """Licenses vocabulary type."""
    return vocabulary_service.create_type(
        system_identity, "targetaudiencestypes", "tarau"
    )


@pytest.fixture(scope="module")
def target_users_v(app, target_users):
    """Target Users vocabulary record."""
    vocab = vocabulary_service.create(
        system_identity,
        {
            "id": "tu-geo-eoanalyst",
            "props": {
                "description_long": "A person who makes Earth Observation Analysis",
                "description_short": "A person who makes Earth Observation Analysis",
                "icon": "",
                "subtype": "",
                "type": "target-audience",
            },
            "title": {"en": "Earth Observation Analyst"},
            "type": "targetaudiencestypes",
        },
    )

    Vocabulary.index.refresh()

    return vocab


@pytest.fixture(scope="module")
def programme_activities(app):
    """Programme Activities vocabulary type."""
    return vocabulary_service.create_type(system_identity, "geowptypes", "geowp")


@pytest.fixture(scope="module")
def programme_activities_v(app, programme_activities):
    """Programme Activities vocabulary record."""
    vocab = vocabulary_service.create(
        system_identity,
        {
            "id": "geo-activities-geobon",
            "props": {
                "acronym": "GEO BON",
                "description_long": "",
                "description_short": "",
                "icon": "",
                "subtype": "",
                "type": "geo-work-programme-activities",
                "uri": "www.earthobservations.org/documents/gwp20_22/GEO-BON.pdf",
            },
            "title": {"en": "GEO Biodiversity Observation Network (GEO BON)"},
            "type": "geowptypes",
        },
    )

    Vocabulary.index.refresh()

    return vocab


@pytest.fixture(scope="module")
def engagement_priorities(app):
    """Engagement Priorities vocabulary type."""
    return vocabulary_service.create_type(
        system_identity, "engagementprioritiestypes", "enpri"
    )


@pytest.fixture(scope="module")
def engagement_priorities_v(app, engagement_priorities):
    """Engagement Priorities vocabulary record."""
    vocab = vocabulary_service.create(
        system_identity,
        {
            "id": "convention-on-biological-diversity",
            "props": {
                "type": "convention-on-biological-diversity",
                "subtype": "",
                "icon": "images/labels/engagement-priorities/conventions/convention-on-biological-diversity.png",
                "uri": "https://www.cbd.int/",
                "description": "",
                "is_subtype": "false",
                "has_subtype": "false",
                "engagement_type": "convention",
            },
            "title": {"en": "Convention on Biological Diversity"},
            "type": "engagementprioritiestypes",
        },
    )

    Vocabulary.index.refresh()

    return vocab
