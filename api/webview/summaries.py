import frappe

from .constants import CONFIG_DOCTYPE
from .fields import _get_enabled_ui_fieldnames


def _get_workpulse_section(
    configuration,
    section_id,
):
    """
    Resolve and validate a Workpulse configuration
    section.

    Returns:
        config_doc,
        section,
        source_doctype
    """

    config_doc = frappe.get_doc(
        CONFIG_DOCTYPE,
        configuration,
    )

    config_doc.check_permission(
        "read"
    )

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

    if not frappe.db.exists(
        "DocType",
        source_doctype,
    ):
        frappe.throw(
            f"Source DocType does not exist: {source_doctype}"
        )

    user = frappe.session.user

    if not frappe.has_permission(
        source_doctype,
        ptype="read",
        user=user,
    ):
        frappe.throw(
            "You do not have read permission for this DocType.",
            frappe.PermissionError,
        )

    return (
        config_doc,
        section,
        source_doctype,
    )


@frappe.whitelist()
def get_source_doctype_ui_count(
    configuration,
    section_id,
):
    """
    Return the permission-aware record count
    for one configured Workpulse section.
    """

    _, _, source_doctype = (
        _get_workpulse_section(
            configuration=configuration,
            section_id=section_id,
        )
    )

    # ---------------------------------------------------------
    # Fetch permission-aware count
    # ---------------------------------------------------------

    count_result = frappe.get_list(
        source_doctype,
        fields=[
            "COUNT(name) AS count"
        ],
        limit_page_length=1,
        ignore_permissions=False,
    )

    total_count = 0

    if count_result:
        total_count = frappe.utils.cint(
            count_result[0].get(
                "count"
            )
            or 0
        )

    return {
        "configuration": configuration,

        "sectionId": section_id,

        "sourceDoctype": source_doctype,

        "count": total_count,
    }


@frappe.whitelist()
def get_source_doctype_ui_sum(
    configuration,
    section_id,
    fieldname,
):
    """
    Return the permission-aware SUM for one
    configured Workpulse section and enabled
    numeric field.
    """

    _, _, source_doctype = (
        _get_workpulse_section(
            configuration=configuration,
            section_id=section_id,
        )
    )

    # ---------------------------------------------------------
    # 1. Validate Workpulse UI field access
    # ---------------------------------------------------------

    user = frappe.session.user

    ui_fields = (
        _get_enabled_ui_fieldnames(
            configuration_id=configuration,
            section_id=section_id,
            source_doctype=source_doctype,
            user=user,
        )
    )

    if fieldname not in ui_fields:
        frappe.throw(
            f"Field '{fieldname}' is not enabled for Workpulse UI."
        )

    # ---------------------------------------------------------
    # 2. Validate field exists
    # ---------------------------------------------------------

    meta = frappe.get_meta(
        source_doctype
    )

    field_map = {
        field.get("fieldname"): field
        for field in meta.fields
        if field.get("fieldname")
    }

    field = field_map.get(
        fieldname
    )

    if not field:
        frappe.throw(
            f"Field '{fieldname}' does not exist in {source_doctype}."
        )

    # ---------------------------------------------------------
    # 3. Validate numeric field type
    # ---------------------------------------------------------

    numeric_field_types = {
        "Int",
        "Float",
        "Currency",
        "Percent",
    }

    field_type = field.get(
        "fieldtype"
    )

    if field_type not in numeric_field_types:
        frappe.throw(
            f"Field '{fieldname}' with type '{field_type}' "
            "cannot be used for SUM."
        )

    # ---------------------------------------------------------
    # 4. Calculate permission-aware SUM
    # ---------------------------------------------------------

    result = frappe.get_list(
        source_doctype,
        fields=[
            f"SUM(`{fieldname}`) AS total"
        ],
        limit_page_length=1,
        ignore_permissions=False,
    )

    total_sum = 0

    if result:
        total_sum = frappe.utils.flt(
            result[0].get(
                "total"
            )
            or 0
        )

    return {
        "configuration": configuration,

        "sectionId": section_id,

        "sourceDoctype": source_doctype,

        "fieldname": fieldname,

        "fieldType": field_type,

        "sum": total_sum,
    }


@frappe.whitelist()
def get_source_doctype_ui_average(
    configuration,
    section_id,
    fieldname,
):
    """
    Return the permission-aware AVERAGE for one
    configured Workpulse section and enabled
    numeric field.
    """

    _, _, source_doctype = (
        _get_workpulse_section(
            configuration=configuration,
            section_id=section_id,
        )
    )

    # ---------------------------------------------------------
    # 1. Validate Workpulse UI field access
    # ---------------------------------------------------------

    user = frappe.session.user

    ui_fields = (
        _get_enabled_ui_fieldnames(
            configuration_id=configuration,
            section_id=section_id,
            source_doctype=source_doctype,
            user=user,
        )
    )

    if fieldname not in ui_fields:
        frappe.throw(
            f"Field '{fieldname}' is not enabled for Workpulse UI."
        )

    # ---------------------------------------------------------
    # 2. Validate field exists
    # ---------------------------------------------------------

    meta = frappe.get_meta(
        source_doctype
    )

    field_map = {
        field.get("fieldname"): field
        for field in meta.fields
        if field.get("fieldname")
    }

    field = field_map.get(
        fieldname
    )

    if not field:
        frappe.throw(
            f"Field '{fieldname}' does not exist in {source_doctype}."
        )

    # ---------------------------------------------------------
    # 3. Validate numeric field type
    # ---------------------------------------------------------

    numeric_field_types = {
        "Int",
        "Float",
        "Currency",
        "Percent",
    }

    field_type = field.get(
        "fieldtype"
    )

    if field_type not in numeric_field_types:
        frappe.throw(
            f"Field '{fieldname}' with type '{field_type}' "
            "cannot be used for AVERAGE."
        )

    # ---------------------------------------------------------
    # 4. Calculate permission-aware average
    # ---------------------------------------------------------

    result = frappe.get_list(
        source_doctype,
        fields=[
            f"AVG(`{fieldname}`) AS average"
        ],
        limit_page_length=1,
        ignore_permissions=False,
    )

    average_value = 0

    if result:
        average_value = frappe.utils.flt(
            result[0].get(
                "average"
            )
            or 0
        )

    return {
        "configuration": configuration,

        "sectionId": section_id,

        "sourceDoctype": source_doctype,

        "fieldname": fieldname,

        "fieldType": field_type,

        "average": average_value,
    }