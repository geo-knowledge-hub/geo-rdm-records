/*
 * This file is part of Geo Secretariat.
 * Copyright (C) 2022 GEO Secretariat.
 *
 * GEO-RDM-Records is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import React, { Component } from "react";

import _get from "lodash/get";

import { Formik } from "formik";
import { RadioField } from "react-invenio-forms";
import { Button, Form, Grid, Icon, Header, Message } from "semantic-ui-react";

import { i18next } from "@translations/geo_rdm_records/i18next";

import { PackagesAPI, packageErrorSerializer } from "../api";

export class RecordPolicyForm extends Component {
  state = {
    error: "",
    isSaved: false,
  };

  getInitialValues = () => {
    return {
      access: {
        record_policy: this.props.package.parent.access.record_policy || "open",
      },
    };
  };

  setGlobalError = (errorMsg) => {
    this.setState({ error: errorMsg });
  };

  setIsSavedState = (newValue) => {
    this.setState({ isSaved: newValue });
  };

  onSubmit = async (values, { setSubmitting, setFieldError }) => {
    setSubmitting(true);

    try {
      const client = new PackagesAPI();
      await client.updateContext(this.props.package.id, values);

      this.setIsSavedState(true);
    } catch (error) {
      if (error === "UNMOUNTED") return;

      const { message, errors } = packageErrorSerializer(error);

      if (message) {
        this.setGlobalError(message);
      }

      if (errors) {
        errors.forEach(({ field, messages }) =>
          setFieldError(field, messages[0])
        );
      }
    }

    setSubmitting(false);
  };

  render() {
    const { isSaved, error } = this.state;
    const { formConfig } = this.props;

    return (
      <Formik initialValues={this.getInitialValues()} onSubmit={this.onSubmit}>
        {({ isSubmitting, handleSubmit, values }) => (
          <Form onSubmit={handleSubmit}>
            <Message hidden={error === ""} negative className="flashed">
              <Grid container>
                <Grid.Column width={15} textAlign="left">
                  <strong>{error}</strong>
                </Grid.Column>
              </Grid>
            </Message>
            <Grid>
              <Grid.Row className="pt-10 pb-0">
                <Grid.Column mobile={16} tablet={12} computer={8}>
                  <Header as="h2" size="tiny">
                    {i18next.t("Record policy visibility")}
                  </Header>
                  {formConfig.access.record_policy.map((item) => (
                    <React.Fragment key={item.value}>
                      <RadioField
                        key={item.value}
                        fieldPath="access.record_policy"
                        label={item.text}
                        labelIcon={item.icon}
                        checked={
                          _get(values, "access.record_policy") === item.value
                        }
                        value={item.value}
                        onChange={({ event, data, formikProps }) => {
                          formikProps.form.setFieldValue(
                            "access.record_policy",
                            item.value
                          );
                          this.setIsSavedState(false);
                        }}
                      />
                      <label className="helptext">{item.helpText}</label>
                    </React.Fragment>
                  ))}
                  <Button
                    compact
                    primary
                    icon
                    labelPosition="left"
                    loading={isSubmitting}
                    toggle
                    active={isSaved}
                    type="submit"
                  >
                    <Icon name="save" />
                    {isSaved ? i18next.t("Saved") : i18next.t("Save")}
                  </Button>
                </Grid.Column>
              </Grid.Row>
            </Grid>
          </Form>
        )}
      </Formik>
    );
  }
}
