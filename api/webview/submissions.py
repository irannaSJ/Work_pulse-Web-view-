import frappe

from .constants import (
    CONFIG_DOCTYPE,
    NON_DATA_FIELD_TYPES,
)
from .fields import _get_enabled_ui_fieldnames
from .records import get_linked_field_values


def _is_empty(value):
    return value is None or value == ""


@frappe.whitelist(methods=["POST"])
def save_source_doctype_ui_record(
    configuration,
    section_id,
    values,
    record_name=None,
):
    """
    Create or update a record through the configured WorkPulse UI.

    Security:
    - Requires an authenticated user.
    - Checks configuration and DocType permissions.
    - Accepts only WorkPulse-enabled, writable fields.
    - Calculates configured fetch_from values server-side.
    - Uses normal Frappe insert/save validation.
    """

    user = frappe.session.user

    if user == "Guest":
        frappe.throw(
            "Please log in before saving a record.",
            frappe.PermissionError,
        )

    # ---------------------------------------------------------
    # 1. Parse submitted values
    # ---------------------------------------------------------
    if isinstance(values, str):
        values = frappe.parse_json(values)

    if not isinstance(values, dict):
        frappe.throw("Form values must be a JSON object.")

    # ---------------------------------------------------------
    # 2. Validate WorkPulse configuration
    # ---------------------------------------------------------
    config_doc = frappe.get_doc(
        CONFIG_DOCTYPE,
        configuration,
    )
    config_doc.check_permission("read")

    section = next(
        (
            row
            for row in (config_doc.get("sections") or [])
            if row.name == section_id
        ),
        None,
    )

    if not section:
        frappe.throw("Section not found in this configuration.")

    if not section.get("enabled"):
        frappe.throw("This section is disabled.")

    source_doctype = section.get("source_doctype")

    if (
        not source_doctype
        or not frappe.db.exists("DocType", source_doctype)
    ):
        frappe.throw("Invalid source DocType.")

    # ---------------------------------------------------------
    # 3. Load the existing record or prepare a new one
    # ---------------------------------------------------------
    is_update = bool(record_name)

    if is_update:
        doc = frappe.get_doc(
            source_doctype,
            record_name,
        )
        doc.check_permission("write")
    else:
        if not frappe.has_permission(
            source_doctype,
            ptype="create",
            user=user,
        ):
            frappe.throw(
                "You do not have permission to create this record.",
                frappe.PermissionError,
            )

        doc = frappe.new_doc(source_doctype)

    # ---------------------------------------------------------
    # 4. Resolve enabled fields and write permissions
    # ---------------------------------------------------------
    enabled_fields = set(
        _get_enabled_ui_fieldnames(
            configuration_id=configuration,
            section_id=section_id,
            source_doctype=source_doctype,
            user=user,
        )
    )

    meta = frappe.get_meta(source_doctype)

    metadata_fields = {
        field.get("fieldname"): field
        for field in meta.fields
        if field.get("fieldname")
    }

    writable_fields = set(
        meta.get_permitted_fieldnames(
            user=user,
            permission_type="write",
        )
    )

    # ---------------------------------------------------------
    # 5. Apply allowed submitted values
    # ---------------------------------------------------------
    for fieldname, value in values.items():
        if fieldname not in enabled_fields:
            continue

        field = metadata_fields.get(fieldname)

        if not field:
            continue

        # Never accept client-supplied values for fetch_from
        # fields. Those values are calculated on the server.
        if field.get("fetch_from"):
            continue

        if field.get("hidden"):
            continue

        if field.get("fieldtype") in NON_DATA_FIELD_TYPES:
            continue

        if field.get("read_only"):
            continue

        if fieldname not in writable_fields:
            continue

        doc.set(fieldname, value)

    # ---------------------------------------------------------
    # 6. Calculate configured fetch_from values server-side
    # ---------------------------------------------------------
    for link_field in meta.fields:
        link_fieldname = link_field.get("fieldname")
        link_fieldtype = link_field.get("fieldtype")

        if link_fieldtype not in ("Link", "Dynamic Link"):
            continue

        if link_fieldname not in enabled_fields:
            continue

        # Recalculate fields for Link values included in this
        # submission, such as an Employee selected in the form.
        if link_fieldname not in values:
            continue

        linked_record_name = doc.get(link_fieldname)

        if not linked_record_name:
            continue

        prefix = f"{link_fieldname}."

        fetch_fields = [
            field
            for field in meta.fields
            if (
                field.get("fieldname") in enabled_fields
                and str(field.get("fetch_from") or "").startswith(
                    prefix
                )
            )
        ]

        if not fetch_fields:
            continue

        link_doctype = None

        if link_fieldtype == "Dynamic Link":
            reference_fieldname = link_field.get("options")

            if reference_fieldname:
                link_doctype = doc.get(reference_fieldname)

        linked_values = get_linked_field_values(
            configuration=configuration,
            section_id=section_id,
            link_fieldname=link_fieldname,
            record_name=linked_record_name,
            link_doctype=link_doctype,
        )

        for fieldname, fetched_value in (
            linked_values.get("values") or {}
        ).items():
            field = metadata_fields.get(fieldname)

            if not field:
                continue

            if (
                field.get("fetch_if_empty")
                and not _is_empty(doc.get(fieldname))
            ):
                continue

            doc.set(fieldname, fetched_value)

    # ---------------------------------------------------------
    # 7. Save using normal Frappe validation
    # ---------------------------------------------------------
    if is_update:
        doc.save()
        operation = "updated"
    else:
        doc.insert()
        operation = "created"

    return {
        "success": True,
        "operation": operation,
        "doctype": source_doctype,
        "name": doc.name,
        "message": (
            "Record updated successfully."
            if is_update
            else "Record created successfully."
        ),
    }