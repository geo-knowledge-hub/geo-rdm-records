# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""GEO Knowledge Hub records module"""

import os

from setuptools import find_packages, setup

readme = open("README.rst").read()
history = open("CHANGES.rst").read()

invenio_version = "~=3.5.0a4"
invenio_search_version = ">=1.4.2,<1.5.0"
invenio_db_version = ">=1.0.11,<1.1.0"

tests_require = [
    "pytest-invenio~=1.4.2",
]

setup_requires = [
    "Babel>=2.8,<3",
]

extras_require = {
    # Invenio-Search
    "elasticsearch6": [f"invenio-search[elasticsearch6]{invenio_search_version}"],
    # Invenio-DB
    "mysql": [f"invenio-db[mysql,versioning]{invenio_db_version}"],
    "postgresql": [f"invenio-db[postgresql,versioning]{invenio_db_version}"],
    "sqlite": [f"invenio-db[versioning]{invenio_db_version}"],
    # Extras
    "docs": [
        "Sphinx==4.2.0",
    ],
    "tests": tests_require,
}

extras_require["all"] = []
for name, reqs in extras_require.items():
    if name[0] == ":" or name in (
        "elasticsearch6",
        "elasticsearch7",
        "mysql",
        "postgresql",
        "sqlite",
    ):
        continue
    extras_require["all"].extend(reqs)

install_requires = [
    "invenio-rdm-records>=0.34.5,<0.35.0",
    f"invenio[base,auth,metadata,files]{invenio_version}",
]

packages = find_packages()


# Get the version string. Cannot be done with import!
g = {}
with open(os.path.join("geo_rdm_records", "version.py"), "rt") as fp:
    exec(fp.read(), g)
    version = g["__version__"]

setup(
    name="geo-rdm-records",
    version=version,
    description=__doc__,
    long_description=readme + "\n\n" + history,
    keywords="invenio TODO",
    license="MIT",
    author="Geo Secretariat",
    author_email="geokhub@geosec.org",
    url="https://github.com/geo-knowledge-hub/geo-rdm-records",
    packages=packages,
    zip_safe=False,
    include_package_data=True,
    platforms="any",
    entry_points={
        "invenio_base.apps": [
            "geo_rdm_records = geo_rdm_records:GEORDMRecords",
        ],
        "invenio_base.api_apps": [
            "geo_rdm_records = geo_rdm_records:GEORDMRecords",
        ],
        "invenio_i18n.translations": [
            "messages = geo_rdm_records",
        ],
        "invenio_search.mappings": ["geordmrecords = geo_rdm_records.records.mappings"],
        "invenio_jsonschemas.schemas": [
            "geo_rdm_records = geo_rdm_records.records.jsonschemas"
        ]
        # TODO: Edit these entry points to fit your needs.
        # 'invenio_access.actions': [],
        # 'invenio_admin.actions': [],
        # 'invenio_assets.bundles': [],
        # 'invenio_base.api_apps': [],
        # 'invenio_base.api_blueprints': [],
        # 'invenio_base.blueprints': [],
        # 'invenio_celery.tasks': [],
        # 'invenio_db.models': [],
        # 'invenio_pidstore.minters': [],
        # 'invenio_records.jsonresolver': [],
    },
    extras_require=extras_require,
    install_requires=install_requires,
    setup_requires=setup_requires,
    tests_require=tests_require,
    classifiers=[
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Development Status :: 1 - Planning",
    ],
)
