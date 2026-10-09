import frappe

from frappe import _

from .constants import CONFIG_DOCTYPE


def _normalize_label(value):
    """
    Normalize a field label so it can be compared
    consistently with logical labels.
    """

    if not value:
        return ""

    return (
        value
        .strip()
        .lower()
        .replace("_", " ")
        .replace("-", " ")
    )


def _get_field(
    document,
    field_map,
    label_key,
    default=None,
):
    """
    Read a value from a document using a normalized label.
    """

    fieldname = field_map.get(
        _normalize_label(label_key)
    )

    if not fieldname:
        return default

    value = document.get(fieldname)

    if value is None:
        return default

    return value


@frappe.whitelist()
def get_workpulse_configuration():
    """
    Return the configured Workpulse web view configurations
    and their sections.
    """

    # ---------------------------------------------------------
    # 1. Check permission
    # ---------------------------------------------------------

    if not frappe.has_permission(
        CONFIG_DOCTYPE,
        "read",
    ):
        frappe.throw(
            _(
                "you do not have pemission to read{0}."
            ).format(CONFIG_DOCTYPE),
            frappe.PermissionError,
        )

    # ---------------------------------------------------------
    # 2. Resolve configuration metadata
    # ---------------------------------------------------------

    config_meta = frappe.get_meta(
        CONFIG_DOCTYPE
    )

    # Find the first Table field.
    section_table_field = next(
        (
            field
            for field in config_meta.fields
            if field.fieldtype == "Table"
        ),
        None,
    )

    if not section_table_field:
        frappe.throw(
            _(
                "no table field was found in {0}"
            ).format(CONFIG_DOCTYPE)
        )

    # The Table field points to the child DocType.
    section_doctype = section_table_field.options

    section_meta = frappe.get_meta(
        section_doctype
    )

    # ---------------------------------------------------------
    # 3. Build field maps
    # ---------------------------------------------------------

    parent_fields = {
        _normalize_label(field.label): field.fieldname
        for field in config_meta.fields
        if field.label
    }

    section_fields = {
        _normalize_label(field.label): field.fieldname
        for field in section_meta.fields
        if field.label
    }

    # ---------------------------------------------------------
    # 4. Get configurations
    # ---------------------------------------------------------

    parent_names = frappe.get_list(
        CONFIG_DOCTYPE,
        fields=["name"],
        order_by="creation asc",
    )

    result = []

    # ---------------------------------------------------------
    # 5. Process every configuration
    # ---------------------------------------------------------

    for row in parent_names:

        doc = frappe.get_doc(
            CONFIG_DOCTYPE,
            row.name,
        )

        doc.check_permission("read")

        parent_data = {
            "ID": _get_field(
                doc,
                parent_fields,
                "id",
                default=doc.name,
            ),

            "Title": _get_field(
                doc,
                parent_fields,
                "title",
            ),

            "Logo": _get_field(
                doc,
                parent_fields,
                "logo",
            ),

            "Enabled": _get_field(
                doc,
                parent_fields,
                "enabled",
                default=0,
            ),

            "Sections": [],
        }

        # -----------------------------------------------------
        # 6. Process child sections
        # -----------------------------------------------------

        sections = doc.get(
            section_table_field.fieldname
        ) or []

        for section in sections:

            parent_data["Sections"].append(
                {
                    "ID": _get_field(
                        section,
                        section_fields,
                        "id",
                        default=section.name,
                    ),

                    "Enabled": _get_field(
                        section,
                        section_fields,
                        "enabled",
                        default=0,
                    ),

                    "Order": _get_field(
                        section,
                        section_fields,
                        "order",
                        default=section.idx,
                    ),

                    "Select Type": _get_field(
                        section,
                        section_fields,
                        "select type",
                    ),

                    "Source Doctype": _get_field(
                        section,
                        section_fields,
                        "source doctype",
                    ),
                }
            )

        result.append(
            parent_data
        )

    # ---------------------------------------------------------
    # 7. Return result
    # ---------------------------------------------------------

    return {
        CONFIG_DOCTYPE: result
    }