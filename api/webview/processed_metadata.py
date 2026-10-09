import frappe

from .fields import (
    _get_field_access_records,
    _preprocess_hidden_fields,
    _preprocess_sensitive_fields,
    _preprocess_ui_fields,
)

from .metadata import (
    get_source_doctype_metadata,
)

from .permissions import (
    get_source_doctype_permissions,
)


@frappe.whitelist()
def get_source_doctype_hidden_processed_metadata():
    """
    Return source DocType metadata after applying
    hidden-field preprocessing.
    """

    source_metadata = (
        get_source_doctype_metadata()
    )

    results = []

    for source in source_metadata.get(
        "Source Doctypes",
        [],
    ):

        doctype = source.get(
            "Source Doctype"
        )

        if not doctype:
            continue

        meta = frappe.get_meta(
            doctype
        )

        original_fields = (
            meta.fields
        )

        visible_fields = (
            _preprocess_hidden_fields(
                meta
            )
        )

        results.append(
            {
                "doctype": doctype,

                "fieldStats": {
                    "total": len(
                        original_fields
                    ),

                    "visible": len(
                        visible_fields
                    ),

                    "hidden": (
                        len(
                            original_fields
                        )
                        - len(
                            visible_fields
                        )
                    ),
                },

                "fields": visible_fields,
            }
        )

    return {
        "sourceDoctypes": results
    }


@frappe.whitelist()
def get_source_doctype_sensitive_processed_metadata():
    """
    Return source DocType metadata after applying
    hidden-field and sensitive-field preprocessing.
    """

    source_metadata = (
        get_source_doctype_metadata()
    )

    permission_data = (
        get_source_doctype_permissions()
    )

    permission_map = {
        item["doctype"]: item
        for item in permission_data.get(
            "sourceDoctypes",
            [],
        )
    }

    results = []

    for source in source_metadata.get(
        "Source Doctypes",
        [],
    ):

        doctype = source.get(
            "Source Doctype"
        )

        if not doctype:
            continue

        meta = frappe.get_meta(
            doctype
        )

        current_permission = (
            permission_map.get(
                doctype,
                {},
            )
        )

        field_permissions = (
            current_permission.get(
                "fieldPermissions",
                {},
            )
        )

        visible_fields = (
            _preprocess_hidden_fields(
                meta
            )
        )

        processed_fields = (
            _preprocess_sensitive_fields(
                visible_fields,
                field_permissions,
            )
        )

        sensitive_fields = [
            field
            for field in processed_fields
            if field["sensitive"]
        ]

        unreadable_fields = [
            field
            for field in processed_fields
            if not field["readAccess"]
        ]

        results.append(
            {
                "doctype": doctype,

                "fieldStats": {
                    "total": len(
                        processed_fields
                    ),

                    "sensitive": len(
                        sensitive_fields
                    ),

                    "unreadable": len(
                        unreadable_fields
                    ),
                },

                "sensitiveFields": (
                    sensitive_fields
                ),

                "unreadableFields": (
                    unreadable_fields
                ),
            }
        )

    return {
        "sourceDoctypes": results
    }


@frappe.whitelist()
def get_source_doctype_ui_processed_metadata():
    """
    Return frontend-safe metadata based on:

    - Workpulse configuration
    - Source DocType metadata
    - Frappe read permissions
    - Workpulse Web View Field Access
    """

    source_metadata = (
        get_source_doctype_metadata()
    )

    permission_data = (
        get_source_doctype_permissions()
    )

    permission_map = {
        item["doctype"]: item
        for item in permission_data.get(
            "sourceDoctypes",
            [],
        )
    }

    results = []

    for source in source_metadata.get(
        "Source Doctypes",
        [],
    ):

        doctype = source.get(
            "Source Doctype"
        )

        if not doctype:
            continue

        meta = frappe.get_meta(
            doctype
        )

        current_permissions = (
            permission_map.get(
                doctype,
                {},
            )
        )

        field_permissions = (
            current_permissions.get(
                "fieldPermissions",
                {},
            )
        )

        usages = []

        for usage in source.get(
            "Used By",
            [],
        ):

            configuration_id = (
                usage.get(
                    "Configuration ID"
                )
            )

            section_id = (
                usage.get(
                    "Section ID"
                )
            )

            if (
                not configuration_id
                or not section_id
            ):
                continue

            field_access_records = (
                _get_field_access_records(
                    configuration_id=(
                        configuration_id
                    ),
                    section_id=section_id,
                    source_doctype=doctype,
                )
            )

            fields, field_stats = (
                _preprocess_ui_fields(
                    meta=meta,
                    field_permissions=(
                        field_permissions
                    ),
                    field_access_records=(
                        field_access_records
                    ),
                )
            )

            usages.append(
                {
                    "configurationId": (
                        configuration_id
                    ),

                    "sectionId": (
                        section_id
                    ),

                    "type": usage.get(
                        "Select Type"
                    ),

                    "order": usage.get(
                        "Order"
                    ),

                    "fieldStats": (
                        field_stats
                    ),

                    "fields": fields,
                }
            )

        results.append(
            {
                "doctype": doctype,
                "usages": usages,
            }
        )

    return {
        "sourceDoctypes": results
    }