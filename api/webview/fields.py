import frappe

from .constants import (
    FIELD_ACCESS_DOCTYPE,
    NON_DATA_FIELD_TYPES,
)


def _preprocess_hidden_fields(meta):
    """
    Return DocType fields that are not hidden.
    """

    visible_fields = []

    for field in meta.fields:

        if field.hidden:
            continue

        visible_fields.append(
            field.as_dict()
        )

    return visible_fields


def _is_data_field(field):
    """
    Return True when the field represents
    actual data rather than UI/layout structure.
    """

    return (
        field.get("fieldtype")
        not in NON_DATA_FIELD_TYPES
    )


def _preprocess_sensitive_fields(
    fields,
    field_permissions,
):
    """
    Add frontend-safe permission/sensitivity
    information to data-bearing fields.
    """

    readable_fields = set(
        field_permissions.get(
            "read",
            [],
        )
    )

    processed_fields = []

    for field in fields:

        fieldname = field.get(
            "fieldname"
        )

        if not fieldname:
            continue

        if not _is_data_field(field):
            continue

        raw_permlevel = (
            field.get("permlevel")
            or 0
        )

        try:
            permlevel = int(
                raw_permlevel
            )
        except (
            TypeError,
            ValueError,
        ):
            permlevel = 0

        has_read_access = (
            fieldname
            in readable_fields
        )

        permission_restricted = (
            permlevel > 0
        )

        processed_field = {
            "fieldname": fieldname,

            "label": field.get(
                "label"
            ),

            "fieldtype": field.get(
                "fieldtype"
            ),

            "options": field.get(
                "options"
            ),

            "permlevel": permlevel,

            # Actual frontend exposure
            # information.
            "readAccess": has_read_access,

            # Permission-level restriction.
            "permissionRestricted": (
                permission_restricted
            ),

            # Sensitive means the field
            # has a non-zero permission level.
            "sensitive": (
                permission_restricted
            ),

            # Useful distinction for
            # frontend preprocessing.
            "readRestricted": (
                not has_read_access
            ),

            "dataBearing": True,
        }

        processed_fields.append(
            processed_field
        )

    return processed_fields


def _get_field_access_records(
    configuration_id,
    section_id,
    source_doctype,
):
    """
    Get Workpulse UI field configuration
    for one configuration + section +
    source DocType combination.
    """

    return frappe.db.get_all(
        FIELD_ACCESS_DOCTYPE,

        filters={
            "configuration": configuration_id,
            "section_id": section_id,
            "source_doctype": source_doctype,
        },

        fields=[
            "name",
            "fieldname",
            "field_label",
            "field_type",
            "enabled",
            "order",
        ],

        order_by=(
            "`order` asc, fieldname asc"
        ),
    )


def _preprocess_ui_fields(
    meta,
    field_permissions,
    field_access_records,
):
    """
    Build the final frontend-safe field list.

    A field is exposed only when:

    1. It exists in current DocType metadata.
    2. It is not hidden.
    3. It is not a structural/UI field.
    4. Current user has Frappe read access.
    5. Workpulse Field Access has Enabled = 1.
    """

    readable_fields = set(
        field_permissions.get(
            "read",
            [],
        )
    )

    metadata_fields = {
        field.get("fieldname"): field
        for field in meta.fields
        if field.get("fieldname")
    }

    exposed_fields = []

    stats = {
        "metadataFields": len(
            metadata_fields
        ),
        "configuredFields": len(
            field_access_records
        ),
        "enabledFields": 0,
        "exposedFields": 0,
        "blockedByPermission": 0,
        "hiddenFields": 0,
        "structuralFields": 0,
        "staleFields": 0,
    }

    for access_record in field_access_records:

        fieldname = access_record.get(
            "fieldname"
        )

        if not fieldname:
            continue

        field = metadata_fields.get(
            fieldname
        )

        # Field no longer exists
        # in the DocType.
        if not field:
            stats["staleFields"] += 1
            continue

        # Frappe-hidden field.
        if field.get("hidden"):
            stats["hiddenFields"] += 1
            continue

        # Structural/UI field.
        if (
            field.get("fieldtype")
            in NON_DATA_FIELD_TYPES
        ):
            stats["structuralFields"] += 1
            continue

        # Workpulse UI access disabled.
        if not access_record.get(
            "enabled"
        ):
            continue

        stats["enabledFields"] += 1

        # Current user cannot read
        # the field.
        if fieldname not in readable_fields:
            stats[
                "blockedByPermission"
            ] += 1
            continue

        exposed_fields.append(
            {
                "fieldname": fieldname,

                "label": (
                    field.get("label")
                    or access_record.get(
                        "field_label"
                    )
                    or fieldname
                ),

                "fieldtype": field.get(
                    "fieldtype"
                ),

                "options": field.get(
                    "options"
                ),

                "idx": field.get(
                    "idx"
                ),

                "order": access_record.get(
                    "order"
                ),

                "reqd": field.get(
                    "reqd"
                ),

                "readOnly": field.get(
                    "read_only"
                ),

                "permlevel": field.get(
                    "permlevel"
                ),

                "inListView": field.get(
                    "in_list_view"
                ),

                "inFilter": field.get(
                    "in_filter"
                ),

                "inStandardFilter": field.get(
                    "in_standard_filter"
                ),

                "inGlobalSearch": field.get(
                    "in_global_search"
                ),

                "inPreview": field.get(
                    "in_preview"
                ),

                "default": field.get(
                    "default"
                ),

                "description": field.get(
                    "description"
                ),

                "fetchFrom": field.get(
                    "fetch_from"
                ),

                "fetchIfEmpty": field.get(
                    "fetch_if_empty"
                ),

                "dataBearing": True,

                "readAccess": True,

                "uiAccess": True,
            }
        )

    stats["exposedFields"] = len(
        exposed_fields
    )

    return (
        exposed_fields,
        stats,
    )


def _build_form_layout(
    meta,
    ui_fields,
):
    """
    Build FORM layout from the existing
    exposed fields.

    This preserves structural information:

    - Tab Break
    - Section Break
    - Column Break
    """

    exposed_fieldnames = {
        field.get("fieldname")
        for field in ui_fields
        if field.get("fieldname")
    }

    layout = []

    for field in meta.fields:

        fieldname = field.get(
            "fieldname"
        )

        fieldtype = field.get(
            "fieldtype"
        )

        if not fieldname:
            continue

        if field.get("hidden"):
            continue

        # -----------------------------------------------------
        # Data field
        # -----------------------------------------------------

        if (
            fieldtype
            not in NON_DATA_FIELD_TYPES
        ):

            if (
                fieldname
                not in exposed_fieldnames
            ):
                continue

            layout.append(
                {
                    "type": "FIELD",
                    "fieldname": fieldname,
                }
            )

            continue

        # -----------------------------------------------------
        # Section Break
        # -----------------------------------------------------

        if fieldtype == "Section Break":

            layout.append(
                {
                    "type": "SECTION",
                    "fieldname": fieldname,
                    "label": (
                        field.get("label")
                        or ""
                    ),
                }
            )

            continue

        # -----------------------------------------------------
        # Column Break
        # -----------------------------------------------------

        if fieldtype == "Column Break":

            layout.append(
                {
                    "type": "COLUMN",
                    "fieldname": fieldname,
                }
            )

            continue

        # -----------------------------------------------------
        # Tab Break
        # -----------------------------------------------------

        if fieldtype == "Tab Break":

            layout.append(
                {
                    "type": "TAB",
                    "fieldname": fieldname,
                    "label": (
                        field.get("label")
                        or ""
                    ),
                }
            )

    return layout


def _get_enabled_ui_fieldnames(
    configuration_id,
    section_id,
    source_doctype,
    user=None,
):
    """
    Return fields that are explicitly enabled for
    Workpulse UI and readable by the current user.
    """

    user = (
        user
        or frappe.session.user
    )

    # ---------------------------------------------------------
    # 1. Get DocType metadata
    # ---------------------------------------------------------

    meta = frappe.get_meta(
        source_doctype
    )

    # ---------------------------------------------------------
    # 2. Resolve Frappe readable fields
    # ---------------------------------------------------------

    readable_fields = set(
        meta.get_permitted_fieldnames(
            user=user,
            permission_type="read",
        )
    )

    # ---------------------------------------------------------
    # 3. Get enabled Workpulse fields
    # ---------------------------------------------------------

    enabled_access_records = (
        frappe.db.get_all(
            FIELD_ACCESS_DOCTYPE,

            filters={
                "configuration": configuration_id,
                "section_id": section_id,
                "source_doctype": source_doctype,
                "enabled": 1,
            },

            fields=[
                "fieldname",
                "order",
            ],

            order_by=(
                "`order` asc, fieldname asc"
            ),
        )
    )

    # ---------------------------------------------------------
    # 4. Build metadata map
    # ---------------------------------------------------------

    metadata_fields = {
        field.get("fieldname"): field
        for field in meta.fields
        if field.get("fieldname")
    }

    allowed_fields = []

    # ---------------------------------------------------------
    # 5. Filter fields
    # ---------------------------------------------------------

    for access_record in (
        enabled_access_records
    ):

        fieldname = access_record.get(
            "fieldname"
        )

        if not fieldname:
            continue

        field = metadata_fields.get(
            fieldname
        )

        # Field does not exist anymore.
        if not field:
            continue

        # Frappe-hidden field.
        if field.get("hidden"):
            continue

        # Structural/UI field.
        if (
            field.get("fieldtype")
            in NON_DATA_FIELD_TYPES
        ):
            continue

        # Current user cannot read it.
        if fieldname not in readable_fields:
            continue

        allowed_fields.append(
            fieldname
        )

    return allowed_fields