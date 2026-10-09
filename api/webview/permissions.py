import frappe


def _get_effective_doctype_permissions(
    doctype,
    user,
):
    """
    Resolve effective DocType-level permissions
    for the given user.
    """

    permission_types = [
        "select",
        "read",
        "write",
        "create",
        "delete",
        "submit",
        "cancel",
        "amend",
        "report",
        "export",
        "import",
        "share",
        "print",
        "email",
    ]

    permissions = {}

    for permission_type in permission_types:

        permissions[permission_type] = bool(
            frappe.has_permission(
                doctype=doctype,
                ptype=permission_type,
                user=user,
            )
        )

    return permissions


def _get_effective_field_permissions(
    meta,
    user,
):
    """
    Resolve field-level permissions from
    Frappe permission levels.

    Returns field names that the current user
    can read and write.
    """

    read_fields = meta.get_permitted_fieldnames(
        user=user,
        permission_type="read",
    )

    write_fields = meta.get_permitted_fieldnames(
        user=user,
        permission_type="write",
    )

    read_permission_levels = sorted(
        meta.get_permlevel_access(
            permission_type="read",
            user=user,
        )
    )

    write_permission_levels = sorted(
        meta.get_permlevel_access(
            permission_type="write",
            user=user,
        )
    )

    return {
        "read": sorted(
            set(read_fields)
        ),
        "write": sorted(
            set(write_fields)
        ),
        "permissionLevels": {
            "read": read_permission_levels,
            "write": write_permission_levels,
        },
    }


@frappe.whitelist()
def get_source_doctype_permissions():
    """
    Return DocType-level and field-level permissions
    for all configured Workpulse source DocTypes.
    """

    user = frappe.session.user

    # Import lazily to avoid circular imports.
    from .metadata import get_source_doctype_metadata

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

        permissions = (
            _get_effective_doctype_permissions(
                doctype=doctype,
                user=user,
            )
        )

        field_permissions = (
            _get_effective_field_permissions(
                meta=meta,
                user=user,
            )
        )

        results.append(
            {
                "doctype": doctype,
                "permissions": permissions,
                "fieldPermissions": field_permissions,
            }
        )

    return {
        "user": user,
        "sourceDoctypes": results,
    }