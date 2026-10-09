import frappe

from .constants import CONFIG_DOCTYPE
from .permissions import _get_effective_field_permissions
from .fields import (
    _get_field_access_records,
    _preprocess_ui_fields,
    _build_form_layout,
)


@frappe.whitelist()
def get_source_doctype_ui_form_metadata(
    configuration,
    section_id,
    record_name=None,
):
    """
    Return frontend-safe FORM metadata for one
    configured Workpulse section.

    If record_name is provided:

        mode = edit
        record values are returned.

    If record_name is not provided:

        mode = create
        default values are returned where available.
    """

    user = frappe.session.user

    # ---------------------------------------------------------
    # 1. Validate Workpulse configuration
    # ---------------------------------------------------------

    config_doc = frappe.get_doc(
        CONFIG_DOCTYPE,
        configuration,
    )

    config_doc.check_permission(
        "read"
    )

    # ---------------------------------------------------------
    # 2. Resolve requested section
    # ---------------------------------------------------------

    section = next(
        (
            row
            for row in (
                config_doc.get(
                    "sections"
                )
                or []
            )
            if row.name == section_id
        ),
        None,
    )

    if not section:
        frappe.throw(
            "Section not found in this configuration."
        )

    if not section.get("enabled"):
        frappe.throw(
            "This section is disabled."
        )

    source_doctype = section.get(
        "source_doctype"
    )

    if not source_doctype:
        frappe.throw(
            "This section has no Source Doctype."
        )

    # ---------------------------------------------------------
    # 3. Validate Source DocType
    # ---------------------------------------------------------

    if not frappe.db.exists(
        "DocType",
        source_doctype,
    ):
        frappe.throw(
            f"Source DocType does not exist: {source_doctype}"
        )

    # ---------------------------------------------------------
    # 4. Resolve DocType permissions
    # ---------------------------------------------------------

    can_read = frappe.has_permission(
        source_doctype,
        ptype="read",
        user=user,
    )

    can_create = frappe.has_permission(
        source_doctype,
        ptype="create",
        user=user,
    )

    can_write = frappe.has_permission(
        source_doctype,
        ptype="write",
        user=user,
    )

    if not can_read:
        frappe.throw(
            "You do not have read permission for this DocType.",
            frappe.PermissionError,
        )

    # ---------------------------------------------------------
    # 5. Determine FORM mode
    # ---------------------------------------------------------

    mode = (
        "edit"
        if record_name
        else "create"
    )

    if (
        mode == "create"
        and not can_create
    ):
        frappe.throw(
            "You do not have create permission for this DocType.",
            frappe.PermissionError,
        )

    if (
        mode == "edit"
        and not can_write
    ):
        frappe.throw(
            "You do not have write permission for this DocType.",
            frappe.PermissionError,
        )

    # ---------------------------------------------------------
    # 6. Resolve DocType metadata
    # ---------------------------------------------------------

    meta = frappe.get_meta(
        source_doctype
    )

    field_permissions = (
        _get_effective_field_permissions(
            meta=meta,
            user=user,
        )
    )

    field_access_records = (
        _get_field_access_records(
            configuration_id=configuration,
            section_id=section_id,
            source_doctype=source_doctype,
        )
    )

    # ---------------------------------------------------------
    # 7. Build frontend-safe fields
    # ---------------------------------------------------------

    ui_fields, field_stats = (
        _preprocess_ui_fields(
            meta=meta,
            field_permissions=field_permissions,
            field_access_records=field_access_records,
        )
    )

    form_layout = _build_form_layout(
        meta=meta,
        ui_fields=ui_fields,
    )

    # ---------------------------------------------------------
    # 8. Add frontend editability information
    # ---------------------------------------------------------

    writable_fields = set(
        field_permissions.get(
            "write",
            [],
        )
    )

    for field in ui_fields:

        fieldname = field.get(
            "fieldname"
        )

        write_access = (
            fieldname
            in writable_fields
        )

        read_only = bool(
            field.get("readOnly")
        )

        field["writeAccess"] = (
            write_access
        )

        field["editable"] = (
            write_access
            and not read_only
        )

    # ---------------------------------------------------------
    # 9. Prepare initial record values
    # ---------------------------------------------------------

    record = {}

    if mode == "create":

        for field in ui_fields:

            fieldname = field.get(
                "fieldname"
            )

            record[fieldname] = (
                field.get("default")
            )

    else:

        document = frappe.get_doc(
            source_doctype,
            record_name,
        )

        document.check_permission(
            "read"
        )

        document.check_permission(
            "write"
        )

        for field in ui_fields:

            fieldname = field.get(
                "fieldname"
            )

            record[fieldname] = (
                document.get(
                    fieldname
                )
            )

    # ---------------------------------------------------------
    # 10. Return FORM metadata
    # ---------------------------------------------------------

    return {
        "configuration": configuration,

        "sectionId": section_id,

        "sourceDoctype": source_doctype,

        "mode": mode,

        "recordName": record_name,

        "permissions": {
            "read": can_read,
            "create": can_create,
            "write": can_write,
        },

        "fieldStats": field_stats,

        "fields": ui_fields,

        "layout": form_layout,

        "record": record,
    }