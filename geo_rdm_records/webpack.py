# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""JS/CSS bundles for GEO RDM Records."""

from invenio_assets.webpack import WebpackThemeBundle

theme = WebpackThemeBundle(
    __name__,
    "assets",
    default="semantic-ui",
    themes={
        "semantic-ui": dict(
            entry={
                "geo-rdm-records-dashboard-versions": "./js/geo_rdm_records/packages/search/versions.js",
                "geo-rdm-records-dashboard-resources": "./js/geo_rdm_records/packages/search/resources.js",
                "geo-rdm-records-dashboard-privileges": "./js/geo_rdm_records/packages/settings/privileges.js",
                "geo-rdm-records-dashboard-members": "./js/geo_rdm_records/packages/members/index.js",
            },
            dependencies={
                "semantic-ui-css": "^2.4.1",
                "semantic-ui-react": "^2.1.1",
                "@ckeditor/ckeditor5-build-classic": "^16.0.0",
                "@ckeditor/ckeditor5-react": "^2.1.0",
                "axios": "^0.19.0",
                "lodash": "^4.17.15",
                "luxon": "^1.21.1",
                "path": "^0.12.7",
                "prop-types": "^15.7.2",
                "react": "^16.12.0",
                "react-dom": "^16.11.0",
                "yup": "^0.27.0",
                "react-overridable": "^0.0.3",
                "@semantic-ui-react/css-patch": "^1.0.0",
                "redux": "^4.0.5",
                "redux-devtools-extension": "^2.13.8",
                "redux-thunk": "^2.3.0",
                "react-redux": "^7.2.0",
                "i18next": "^20.3.0",
                "i18next-browser-languagedetector": "^6.1.0",
                "react-i18next": "^11.11.0",
            },
            aliases={
                "@js/geo_rdm_records": "js/geo_rdm_records",
                "@translations/geo_rdm_records": "translations/geo_rdm_records",
            },
        )
    },
)
