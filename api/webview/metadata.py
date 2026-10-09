import frappe

from frappe import _

from .configuration import get_workpulse_configuration
from .constants import CONFIG_DOCTYPE


def get_source_doctype_metadata():
    """
    Return metadata for all enabled Workpulse
    source DocTypes.
    """

    # ---------------------------------------------------------
    # 1. Get Workpulse configuration
    # ---------------------------------------------------------

    configuration = (
        get_workpulse_configuration()
    )

    configurations = configuration.get(
        CONFIG_DOCTYPE,
        [],
    )

    source_doctypes = {}

    # ---------------------------------------------------------
    # 2. Resolve enabled Source DocTypes
    # ---------------------------------------------------------

    for config in configurations:

        if not config.get("Enabled"):
            continue

        for section in config.get(
            "Sections",
            [],
        ):

            if not section.get("Enabled"):
                continue

            source_doctype = section.get(
                "Source Doctype"
            )

            if not source_doctype:
                continue

            source_doctype = (
                source_doctype.strip()
            )

            if (
                source_doctype
                not in source_doctypes
            ):
                source_doctypes[
                    source_doctype
                ] = {
                    "Source Doctype": (
                        source_doctype
                    ),
                    "Used By": [],
                }

            source_doctypes[
                source_doctype
            ]["Used By"].append(
                {
                    "Configuration ID": (
                        config.get("ID")
                    ),
                    "Section ID": (
                        section.get("ID")
                    ),
                    "Select Type": (
                        section.get(
                            "Select Type"
                        )
                    ),
                    "Order": (
                        section.get(
                            "Order"
                        )
                    ),
                }
            )

    # ---------------------------------------------------------
    # 3. Resolve Frappe metadata
    # ---------------------------------------------------------

    metadata_result = []

    for (
        source_doctype,
        source_info,
    ) in source_doctypes.items():

        # -----------------------------------------------------
        # Verify DocType exists
        # -----------------------------------------------------

        if not frappe.db.exists(
            "DocType",
            source_doctype,
        ):
            frappe.throw(
                _(
                    "Source DocType '{0}' does not exist."
                ).format(
                    source_doctype
                )
            )

        # -----------------------------------------------------
        # Check current user's read permission
        # -----------------------------------------------------

        if not frappe.has_permission(
            source_doctype,
            "read",
        ):
            frappe.throw(
                _(
                    "You do not have permission to read {0}."
                ).format(
                    source_doctype
                ),
                frappe.PermissionError,
            )

        # -----------------------------------------------------
        # Get DocType metadata
        # -----------------------------------------------------

        meta = frappe.get_meta(
            source_doctype
        )

        metadata_result.append(
            {
                "Source Doctype": (
                    source_doctype
                ),
                "Used By": (
                    source_info[
                        "Used By"
                    ]
                ),
                "Metadata": (
                    meta.as_dict()
                ),
            }
        )

    # ---------------------------------------------------------
    # 4. Return result
    # ---------------------------------------------------------

    return {
        "Source Doctypes": metadata_result
    }