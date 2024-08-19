// This file is part of InvenioRDM
// Copyright (C) 2023 CERN.
//
// Invenio App RDM is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

/**
 * Add here all the overridden components of your app.
 */

import { i18next } from "@translations/invenio_app_rdm/i18next";
import React from "react";
import { CreatibutorsField } from "@js/invenio_rdm_records";
import PropTypes from "prop-types";

const AuthorsField = ({ config }) => {
  const vocabularies = {
    metadata: {
      ...config.vocabularies,
      creators: {
        ...config.vocabularies.creators,
        type: [
          { text: "Person", value: "personal" },
          { text: "Organization", value: "organizational" },
        ],
      },
      contributors: {
        ...config.vocabularies.contributors,
        type: [
          { text: "Person", value: "personal" },
          { text: "Organization", value: "organizational" },
        ],
      },
      identifiers: {
        ...config.vocabularies.identifiers,
      },
    },
  };

  return (
    <CreatibutorsField
      addButtonLabel={i18next.t("Add author")}
      label={i18next.t("Authors")}
      labelIcon="user"
      fieldPath="metadata.creators"
      roleOptions={vocabularies.metadata.creators.role}
      schema="creators"
      autocompleteNames={config.autocomplete_names}
      required
      modal={{
        addLabel: i18next.t("Add author"),
        editLabel: i18next.t("Edit author"),
      }}
    />
  );
};

AuthorsField.propTypes = {
  config: PropTypes.shape({
    vocabularies: PropTypes.object.isRequired,
    autocomplete_names: PropTypes.bool.isRequired,
  }).isRequired,
};

export default AuthorsField;

export const overriddenComponents = {
"InvenioAppRdm.Deposit.CreatorsField.container": AuthorsField,
};