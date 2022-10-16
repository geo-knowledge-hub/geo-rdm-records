/*
 * This file is part of Geo Secretariat.
 * Copyright (C) 2022 GEO Secretariat.
 *
 * GEO-RDM-Records is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import React from "react";
import ReactDOM from "react-dom";

import { RecordPolicyForm } from "./RecordPolicyForm";

const domContainer = document.getElementById("app");
const formConfig = JSON.parse(domContainer.dataset.formConfig);
const package_ = JSON.parse(domContainer.dataset.package);

if (domContainer) {
  ReactDOM.render(
    <RecordPolicyForm formConfig={formConfig} package={package_} />,
    domContainer
  );
}
