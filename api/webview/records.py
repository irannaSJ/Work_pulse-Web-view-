import frappe

from .constants import (
    CONFIG_DOCTYPE,
    FIELD_ACCESS_DOCTYPE,
    NON_DATA_FIELD_TYPES,
)

from .fields import (
    _get_enabled_ui_fieldnames,
)


@frappe.whitelist()
def get_source_doctype_ui_records(
    configuration,
    section_id,
    limit_page_length=20,
    limit_start=0,
    search=None,
):
    """
    Return record data for one configured section.

    Returned fields must satisfy both:

    1. Frappe read permission
    2. Workpulse UI Field Access = enabled
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

    # ---------------------------------------------------------
    # 2. Find requested section
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
    # 4. Validate Frappe DocType permission
    # ---------------------------------------------------------

    # if not frappe.has_permission(
    #     source_doctype,
    #     ptype="read",
    #     user=user,
    # ):
        # frappe.throw(
        #     "You do not have read permission for this DocType.",
        #     frappe.PermissionError,
        # )
        # continue

    # ---------------------------------------------------------
    # 5. Resolve Workpulse-enabled fields
    # ---------------------------------------------------------

    ui_fields = (
        _get_enabled_ui_fieldnames(
            configuration_id=configuration,
            section_id=section_id,
            source_doctype=source_doctype,
            user=user,
        )
    )

    # ---------------------------------------------------------
    # 6. Always retain document identity
    # ---------------------------------------------------------

    query_fields = ["name"]

    for fieldname in ui_fields:

        if fieldname == "name":
            continue

        query_fields.append(
            fieldname
        )

    # ---------------------------------------------------------
    # 7. Validate pagination
    # ---------------------------------------------------------

    limit_page_length = max(
        1,
        min(
            frappe.utils.cint(
                limit_page_length
            ),
            100,
        ),
    )

    limit_start = max(
        0,
        frappe.utils.cint(
            limit_start
        ),
    )

    # ---------------------------------------------------------
    # 8. Validate search
    # ---------------------------------------------------------

    search = frappe.utils.cstr(
        search or ""
    ).strip()

    search = search[:100]

    # ---------------------------------------------------------
    # 9. Build server-side search filters
    # ---------------------------------------------------------

    or_filters = []

    if search:

        meta = frappe.get_meta(
            source_doctype
        )

        searchable_field_types = {
            "Data",
            "Small Text",
            "Long Text",
            "Text",
            "Text Editor",
            "Read Only",
            "Select",
            "Link",
            "Dynamic Link",
            "Phone",
            "Email",
        }

        metadata_fields = {
            field.get("fieldname"): field
            for field in meta.fields
            if field.get("fieldname")
        }

        searchable_fields = [
            "name"
        ]

        for fieldname in ui_fields:

            if fieldname == "name":
                continue

            field = metadata_fields.get(
                fieldname
            )

            if not field:
                continue

            if (
                field.get("fieldtype")
                not in searchable_field_types
            ):
                continue

            searchable_fields.append(
                fieldname
            )

        for fieldname in searchable_fields:

            or_filters.append(
                {
                    fieldname: [
                        "like",
                        f"%{search}%",
                    ]
                }
            )

    # ---------------------------------------------------------
    # 10. Fetch permission-aware records
    # ---------------------------------------------------------

    query_args = {
        "doctype": source_doctype,
        "fields": query_fields,
        "limit_start": limit_start,
        "limit_page_length": (
            limit_page_length + 1
        ),
        "ignore_permissions": False,
    }

    if or_filters:
        query_args[
            "or_filters"
        ] = or_filters

    records = frappe.get_list(
        **query_args
    )

    # ---------------------------------------------------------
    # 11. Resolve pagination state
    # ---------------------------------------------------------

    has_more = (
        len(records)
        > limit_page_length
    )

    records = records[
        :limit_page_length
    ]

    # ---------------------------------------------------------
    # 12. Return response
    # ---------------------------------------------------------

    return {
        "configuration": configuration,

        "sectionId": section_id,

        "sourceDoctype": source_doctype,

        "fields": ui_fields,

        "records": records,

        "pagination": {
            "limit": limit_page_length,
            "start": limit_start,
            "returned": len(records),
            "hasMore": has_more,
        },
    }


@frappe.whitelist()
def get_source_doctype_ui_record(
    configuration,
    section_id,
    record_name,
):
    """
    Return one permission-aware Workpulse
    record together with its frontend-safe
    field metadata.
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

    # ---------------------------------------------------------
    # 2. Find requested section
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
    # 4. Validate DocType permission
    # ---------------------------------------------------------

    if not frappe.has_permission(
        source_doctype,
        ptype="read",
        user=user,
    ):
        frappe.throw(
            "You do not have read permission for this DocType.",
            frappe.PermissionError,
        )

    # ---------------------------------------------------------
    # 5. Resolve enabled + readable fields
    # ---------------------------------------------------------

    ui_fieldnames = (
        _get_enabled_ui_fieldnames(
            configuration_id=configuration,
            section_id=section_id,
            source_doctype=source_doctype,
            user=user,
        )
    )

    # ---------------------------------------------------------
    # 6. Build frontend-safe field metadata
    # ---------------------------------------------------------

    meta = frappe.get_meta(
        source_doctype
    )

    metadata_fields = {
        field.get("fieldname"): field
        for field in meta.fields
        if field.get("fieldname")
    }

    ui_fields = []

    for fieldname in ui_fieldnames:

        field = metadata_fields.get(
            fieldname
        )

        if not field:
            continue

        # -----------------------------------------------------
        # Find Workpulse field order
        # -----------------------------------------------------

        field_order = next(
            (
                record.get("order")
                for record in (
                    frappe.db.get_all(
                        FIELD_ACCESS_DOCTYPE,

                        filters={
                            "configuration": configuration,
                            "section_id": section_id,
                            "source_doctype": source_doctype,
                            "fieldname": fieldname,
                            "enabled": 1,
                        },

                        fields=[
                            "order"
                        ],

                        limit_page_length=1,
                    )
                )
            ),
            0,
        )

        ui_fields.append(
            {
                "fieldname": fieldname,

                "label": (
                    field.get("label")
                    or fieldname
                ),

                "fieldtype": (
                    field.get(
                        "fieldtype"
                    )
                    or "Data"
                ),

                "options": field.get(
                    "options"
                ),

                "idx": field.get(
                    "idx"
                ),

                "order": field_order,
            }
        )

    # ---------------------------------------------------------
    # 7. Query record
    # ---------------------------------------------------------

    query_fields = ["name"]

    for fieldname in ui_fieldnames:

        if fieldname == "name":
            continue

        query_fields.append(
            fieldname
        )

    records = frappe.get_list(
        source_doctype,

        filters={
            "name": record_name
        },

        fields=query_fields,

        limit_page_length=1,

        ignore_permissions=False,
    )

    if not records:
        frappe.throw(
            "Record not found."
        )

    # ---------------------------------------------------------
    # 8. Return frontend-safe response
    # ---------------------------------------------------------

    return {
        "configuration": configuration,

        "sectionId": section_id,

        "sourceDoctype": source_doctype,

        "record": records[0],

        "fields": ui_fields,
    }




@frappe.whitelist()
def get_linked_field_values(
    configuration,
    section_id,
    link_fieldname,
    record_name,
    link_doctype=None,
):
    """
    Fetch permitted values from a selected linked record
    for form fields configured with fetch_from.
    """

    user = frappe.session.user

    # 1. Validate the WorkPulse configuration.
    config_doc = frappe.get_doc(
        CONFIG_DOCTYPE,
        configuration,
    )
    config_doc.check_permission("read")

    # 2. Resolve the configured section.
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

    if not source_doctype or not frappe.db.exists(
        "DocType",
        source_doctype,
    ):
        frappe.throw("Invalid source DocType.")

    # 3. Verify the Link field is enabled for this section.
    enabled_fields = set(
        _get_enabled_ui_fieldnames(
            configuration_id=configuration,
            section_id=section_id,
            source_doctype=source_doctype,
            user=user,
        )
    )

    if link_fieldname not in enabled_fields:
        frappe.throw("This Link field is not enabled.")

    source_meta = frappe.get_meta(source_doctype)
    link_field = source_meta.get_field(link_fieldname)

    if not link_field or link_field.fieldtype not in (
        "Link",
        "Dynamic Link",
    ):
        frappe.throw("Invalid Link field.")

    # 4. Resolve the linked DocType.
    if link_field.fieldtype == "Link":
        target_doctype = link_field.options

    else:
        # A Dynamic Link obtains its target DocType
        # from another field in the current form.
        doctype_fieldname = link_field.options

        doctype_field = source_meta.get_field(
            doctype_fieldname
        )

        if (
            not doctype_field
            or doctype_fieldname not in enabled_fields
        ):
            frappe.throw(
                "The Dynamic Link reference field is not enabled."
            )

        target_doctype = frappe.utils.cstr(
            link_doctype or ""
        ).strip()

        if not target_doctype:
            frappe.throw(
                "Select a DocType before selecting this record."
            )

    if not target_doctype or not frappe.db.exists(
        "DocType",
        target_doctype,
    ):
        frappe.throw("The linked DocType does not exist.")

    if not frappe.has_permission(
        target_doctype,
        ptype="read",
        user=user,
    ):
        frappe.throw(
            "You do not have read permission for the linked DocType.",
            frappe.PermissionError,
        )

    if not record_name:
        return {
            "sourceDoctype": target_doctype,
            "recordName": None,
            "values": {},
        }

    # 5. Discover fetch_from mappings from source metadata.
    target_meta = frappe.get_meta(target_doctype)

    permitted_target_fields = set(
        target_meta.get_permitted_fieldnames(
            user=user,
            permission_type="read",
        )
    )

    fetch_map = {}

    prefix = f"{link_fieldname}."

    for form_field in source_meta.fields:
        form_fieldname = form_field.get("fieldname")

        if form_fieldname not in enabled_fields:
            continue

        fetch_from = frappe.utils.cstr(
            form_field.get("fetch_from") or ""
        ).strip()

        if not fetch_from.startswith(prefix):
            continue

        target_fieldname = fetch_from[len(prefix):].strip()

        if not target_fieldname or "." in target_fieldname:
            continue

        target_field = target_meta.get_field(
            target_fieldname
        )

        if not target_field:
            continue

        if target_field.get("hidden"):
            continue

        if target_fieldname not in permitted_target_fields:
            continue

        fetch_map[form_fieldname] = target_fieldname

    # No matching fields means there is nothing to fetch.
    if not fetch_map:
        return {
            "sourceDoctype": target_doctype,
            "recordName": record_name,
            "values": {},
        }

    # 6. Retrieve the selected record using permission-aware
    #    access. Never bypass Frappe permissions.
    target_fieldnames = list(
        dict.fromkeys(fetch_map.values())
    )

    records = frappe.get_list(
        target_doctype,
        filters={"name": record_name},
        fields=["name", *target_fieldnames],
        limit_page_length=1,
        ignore_permissions=False,
    )

    if not records:
        frappe.throw(
            "Linked record not found or not permitted."
        )

    linked_record = records[0]

    # 7. Return only the mapped values needed by the form.
    values = {
        form_fieldname: linked_record.get(target_fieldname)
        for form_fieldname, target_fieldname
        in fetch_map.items()
    }

    return {
        "sourceDoctype": target_doctype,
        "recordName": linked_record.name,
        "values": values,
    }
