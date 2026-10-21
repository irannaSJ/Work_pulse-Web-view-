import frappe

from .constants import CONFIG_DOCTYPE
from .configuration import get_workpulse_configuration
from .permissions import _get_effective_field_permissions
from .fields import (
    _get_field_access_records,
    _preprocess_ui_fields,
    _build_form_layout,
)


def _clean_field_definition(
    field,
    section_type,
    writable_fields,
):
    """
    Build the final frontend field definition.

    LIST fields receive display metadata.

    FORM fields additionally receive
    writeAccess and editable information.
    """

    fieldname = field.get(
        "fieldname"
    )

    read_only = bool(
        field.get("readOnly")
    )

    write_access = (
        fieldname in writable_fields
    )

    result = {
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

        "enabled": True,

        "order": field.get(
            "order"
        ),

        "idx": field.get(
            "idx"
        ),

        "reqd": bool(
            field.get("reqd")
        ),

        "readOnly": read_only,

        "default": field.get(
            "default"
        ),

        "description": field.get(
            "description"
        ),

        "fetchFrom": field.get(
            "fetchFrom"
        ),

        "fetchIfEmpty": bool(
            field.get("fetchIfEmpty")
        ),

        "readAccess": bool(
            field.get("readAccess")
        ),
    }

    # ---------------------------------------------------------
    # LIST-specific fields
    # ---------------------------------------------------------

    if section_type == "LIST":

        result["inListView"] = bool(
            field.get("inListView")
        )

        result["inFilter"] = bool(
            field.get("inFilter")
        )

        result["inStandardFilter"] = bool(
            field.get(
                "inStandardFilter"
            )
        )

    # ---------------------------------------------------------
    # FORM-specific fields
    # ---------------------------------------------------------

    if section_type == "FORM":

        result["writeAccess"] = (
            write_access
        )

        result["editable"] = (
            write_access
            and not read_only
        )

    return result


def _clean_form_layout(
    meta,
    ui_fields,
):
    """
    Build a clean FORM layout.

    Empty sections, tabs, and trailing column
    breaks are removed.
    """

    raw_layout = _build_form_layout(
        meta=meta,
        ui_fields=ui_fields,
    )

    if not raw_layout:
        return []

    cleaned_layout = []

    structural_boundaries = {
        "SECTION",
        "TAB",
    }

    total_items = len(
        raw_layout
    )

    for index, item in enumerate(
        raw_layout
    ):

        item_type = item.get(
            "type"
        )

        # -----------------------------------------------------
        # FIELD
        # -----------------------------------------------------

        if item_type == "FIELD":

            cleaned_layout.append(
                item
            )

            continue

        # -----------------------------------------------------
        # SECTION / TAB
        # -----------------------------------------------------

        if item_type in structural_boundaries:

            has_field_after = False

            for next_index in range(
                index + 1,
                total_items,
            ):

                next_item = (
                    raw_layout[
                        next_index
                    ]
                )

                next_type = (
                    next_item.get(
                        "type"
                    )
                )

                if (
                    next_type
                    in structural_boundaries
                ):
                    break

                if next_type == "FIELD":
                    has_field_after = True
                    break

            if has_field_after:
                cleaned_layout.append(
                    item
                )

            continue

        # -----------------------------------------------------
        # COLUMN BREAK
        # -----------------------------------------------------

        if item_type == "COLUMN":

            has_field_before = False
            has_field_after = False

            # Look backward until the last
            # section/tab boundary.
            for previous_index in range(
                index - 1,
                -1,
                -1,
            ):

                previous_item = (
                    raw_layout[
                        previous_index
                    ]
                )

                previous_type = (
                    previous_item.get(
                        "type"
                    )
                )

                if (
                    previous_type
                    in structural_boundaries
                ):
                    break

                if previous_type == "FIELD":
                    has_field_before = True
                    break

            # Look forward until the next
            # section/tab boundary.
            for next_index in range(
                index + 1,
                total_items,
            ):

                next_item = (
                    raw_layout[
                        next_index
                    ]
                )

                next_type = (
                    next_item.get(
                        "type"
                    )
                )

                if (
                    next_type
                    in structural_boundaries
                ):
                    break

                if next_type == "FIELD":
                    has_field_after = True
                    break

            if (
                has_field_before
                and has_field_after
            ):
                cleaned_layout.append(
                    item
                )

    return cleaned_layout


@frappe.whitelist()
def get_workpulse_ui_definition(
    configuration,
):
    """
    Return the complete frontend UI definition
    for one Workpulse configuration.

    This is the main UI-definition endpoint for
    the React frontend.
    """

    user = frappe.session.user

    # ---------------------------------------------------------
    # 1. Validate configuration
    # ---------------------------------------------------------

    config_doc = frappe.get_doc(
        CONFIG_DOCTYPE,
        configuration,
    )

    config_doc.check_permission(
        "read"
    )

    if not config_doc.get(
        "enabled"
    ):
        frappe.throw(
            "This Workpulse configuration is disabled."
        )

    # ---------------------------------------------------------
    # 2. Resolve configuration
    # ---------------------------------------------------------

    configuration_data = (
        get_workpulse_configuration()
    )

    configurations = (
        configuration_data.get(
            CONFIG_DOCTYPE,
            []
        )
    )

    selected_configuration = next(
        (
            item
            for item in configurations
            if item.get("ID")
            == configuration
        ),
        None,
    )

    if not selected_configuration:
        frappe.throw(
            "Workpulse configuration not found."
        )

    # ---------------------------------------------------------
    # 3. Build base response
    # ---------------------------------------------------------

    result = {
        "configuration": {
            "id": selected_configuration.get(
                "ID"
            ),

            "title": selected_configuration.get(
                "Title"
            ),

            "logo": selected_configuration.get(
                "Logo"
            ),

            "enabled": True,
        },

        "sections": [],
    }

    # ---------------------------------------------------------
    # 4. Process sections
    # ---------------------------------------------------------

    sections = (
        selected_configuration.get(
            "Sections",
            []
        )
    )

    for section in sections:

        if not section.get(
            "Enabled"
        ):
            continue

        section_id = section.get(
            "ID"
        )

        section_type = section.get(
            "Select Type"
        )

        source_doctype = section.get(
            "Source Doctype"
        )

        section_order = section.get(
            "Order"
        )

        if not section_id:
            continue

        if not source_doctype:
            continue

        source_doctype = (
            source_doctype.strip()
        )

        # -----------------------------------------------------
        # Validate DocType
        # -----------------------------------------------------

        if not frappe.db.exists(
            "DocType",
            source_doctype,
        ):
            frappe.throw(
                f"Source DocType does not exist: {source_doctype}"
            )

        # -----------------------------------------------------
        # Validate read permission
        # -----------------------------------------------------

        if not frappe.has_permission(
            source_doctype,
            ptype="read",
            user=user,
        ):
            # frappe.throw(
            #     f"You do not have read permission for {source_doctype}.",
            #     frappe.PermissionError,
            # )
            continue

        # -----------------------------------------------------
        # Get metadata
        # -----------------------------------------------------

        meta = frappe.get_meta(
            source_doctype
        )

        # -----------------------------------------------------
        # Resolve field permissions
        # -----------------------------------------------------

        field_permissions = (
            _get_effective_field_permissions(
                meta=meta,
                user=user,
            )
        )

        writable_fields = set(
            field_permissions.get(
                "write",
                []
            )
        )

        # -----------------------------------------------------
        # Resolve Manage UI fields
        # -----------------------------------------------------

        field_access_records = (
            _get_field_access_records(
                configuration_id=configuration,
                section_id=section_id,
                source_doctype=source_doctype,
            )
        )

        ui_fields, _field_stats = (
            _preprocess_ui_fields(
                meta=meta,
                field_permissions=field_permissions,
                field_access_records=field_access_records,
            )
        )

        # -----------------------------------------------------
        # Build final field definitions
        # -----------------------------------------------------

        final_fields = []

        for field in ui_fields:

            final_fields.append(
                _clean_field_definition(
                    field=field,
                    section_type=section_type,
                    writable_fields=writable_fields,
                )
            )

        # -----------------------------------------------------
        # Build FORM layout
        # -----------------------------------------------------

        layout = []

        if section_type == "FORM":

            layout = _clean_form_layout(
                meta=meta,
                ui_fields=ui_fields,
            )

        # -----------------------------------------------------
        # Build final section
        # -----------------------------------------------------

        section_definition = {
            "id": section_id,

            "sourceDoctype": (
                source_doctype
            ),

            "type": section_type,

            "enabled": True,

            "order": section_order,

            "fields": final_fields,
        }

        if section_type == "FORM":

            section_definition[
                "layout"
            ] = layout

        result[
            "sections"
        ].append(
            section_definition
        )

    # ---------------------------------------------------------
    # 5. Sort sections
    # ---------------------------------------------------------

    result[
        "sections"
    ].sort(
        key=lambda section: (
            section.get("order")
            if section.get("order")
            is not None
            else 0
        )
    )

    return result