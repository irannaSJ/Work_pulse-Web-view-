import frappe


DISPLAYABLE_LIST_FIELD_TYPES = {
    "Data",
    "Small Text",
    "Long Text",
    "Text Editor",
    "Int",
    "Float",
    "Currency",
    "Percent",
    "Check",
    "Date",
    "Datetime",
    "Time",
    "Select",
    "Link",
    "Dynamic Link",
    "Rating",
}

DISPLAYABLE_DETAIL_FIELD_TYPES = DISPLAYABLE_LIST_FIELD_TYPES

SEARCHABLE_FIELD_TYPES = {
    "Data",
    "Small Text",
    "Long Text",
    "Text Editor",
    "Link",
    "Dynamic Link",
    "Select",
}

SUMMARY_FIELD_TYPES = {
    "Int",
    "Float",
    "Currency",
    "Percent",
}

SUMMARY_TYPES = {"COUNT", "SUM", "AVERAGE"}


def _field_metadata(field):
    return {
        "fieldname": field.fieldname,
        "label": field.label or field.fieldname,
        "fieldtype": field.fieldtype,
        "options": field.options,
        "hidden": bool(field.hidden),
        "read_only": bool(field.read_only),
        "reqd": bool(field.reqd),
        "in_list_view": bool(field.in_list_view),
        "default": field.default,
        "depends_on": field.depends_on,
    }


def _get_permitted_fields(meta):
    permitted_fieldnames = set(
        meta.get_permitted_fieldnames(permission_type="read")
    )

    return [
        field
        for field in meta.fields
        if field.fieldname in permitted_fieldnames
        and not field.hidden
        and field.fieldtype in DISPLAYABLE_DETAIL_FIELD_TYPES
    ]


def get_list_fields(meta):
    fields = []

    # Always keep the document identifier.
    fields.append({
        "fieldname": "name",
        "label": "ID",
        "fieldtype": "Data",
        "options": None,
    })

    for field in _get_permitted_fields(meta):
        if field.fieldname == "name" or not field.in_list_view:
            continue

        fields.append(_field_metadata(field))

    return fields

def get_detail_fields(meta):
    fields = []

    fields.append({
        "fieldname": "name",
        "label": "ID",
        "fieldtype": "Data",
        "options": None,
    })

    for field in _get_permitted_fields(meta):
        if field.fieldname == "name":
            continue

        fields.append(_field_metadata(field))

    return fields


def _get_summary_field(meta, fieldname):
    permitted_fieldnames = set(
        meta.get_permitted_fieldnames(permission_type="read")
    )

    field = next(
        (
            field
            for field in meta.fields
            if field.fieldname == fieldname
        ),
        None,
    )

    if not field or field.fieldname not in permitted_fieldnames:
        frappe.throw("Summary field is not readable")

    if field.hidden:
        frappe.throw("Summary field is hidden")

    if field.fieldtype not in SUMMARY_FIELD_TYPES:
        frappe.throw(
            f"{field.fieldtype} fields do not support summaries"
        )

    return field


def _get_summary(doctype, meta, aggregate_type="COUNT", fieldname=None):
    aggregate_type = (aggregate_type or "COUNT").upper()

    if aggregate_type not in SUMMARY_TYPES:
        frappe.throw("Unsupported summary type")

    if aggregate_type == "COUNT":
        rows = frappe.get_list(
            doctype,
            fields=["count(name) as value"],
            limit_page_length=1,
        )
        value = rows[0].get("value", 0) if rows else 0
        return {
            "key": "count",
            "label": "Total",
            "value": value or 0,
            "type": aggregate_type,
        }

    if not fieldname:
        frappe.throw("A summary field is required")

    field = _get_summary_field(meta, fieldname)
    function = "sum" if aggregate_type == "SUM" else "avg"
    rows = frappe.get_list(
        doctype,
        fields=[f"{function}(`{field.fieldname}`) as value"],
        limit_page_length=1,
    )
    value = rows[0].get("value") if rows else None

    return {
        "key": f"{aggregate_type.lower()}_{field.fieldname}",
        "label": field.label or field.fieldname,
        "value": value or 0,
        "type": aggregate_type,
    }


def _get_summary_section(
    section,
    aggregate_type="COUNT",
    fieldname=None,
):
    if section.section_type not in {"SUMMARY", "CARD"}:
        return None

    if not section.source_doctype:
        frappe.throw("Summary section requires a source DocType")

    if not frappe.db.exists("DocType", section.source_doctype):
        frappe.throw("Configured source DocType does not exist")

    if not frappe.has_permission(
        section.source_doctype,
        ptype="read"
    ):
        frappe.throw(
            "You do not have permission "
            "to read this summary"
        )

    meta = frappe.get_meta(section.source_doctype)
    metric = _get_summary(
        section.source_doctype,
        meta,
        aggregate_type,
        fieldname,
    )

    if section.title:
        metric["label"] = section.title

    return {
        "doctype": section.source_doctype,
        "metrics": [metric],
    }


@frappe.whitelist()
def get_summary(
    page_name: str,
    section_name: str,
    aggregate_type: str = "COUNT",
    fieldname: str = None,
):
    page_name_value = frappe.db.get_value(
        "WorkPulse Web Page",
        {"page_name": page_name},
        "name"
    )

    if not page_name_value:
        frappe.throw(
            f"WorkPulse Web Page with page_name "
            f"'{page_name}' not found"
        )

    web_page = frappe.get_doc(
        "WorkPulse Web Page",
        page_name_value
    )

    if not web_page.enabled:
        frappe.throw("Web Page is disabled")

    section = next(
        (
            row
            for row in web_page.sections
            if row.enabled
            and row.section_name == section_name
        ),
        None,
    )

    if not section:
        frappe.throw(
            f"Section '{section_name}' "
            f"not found on page '{page_name}'"
        )

    if section.section_type not in {"SUMMARY", "CARD"}:
        frappe.throw("Section is not configured for summaries")

    summary = _get_summary_section(
        section,
        aggregate_type,
        fieldname,
    )

    return {
        "page": {
            "name": web_page.name,
            "page_name": web_page.page_name,
            "title": web_page.title,
            "route_key": web_page.route_key,
            "description": web_page.description,
        },
        "section": {
            "section_name": section.section_name,
            "section_type": section.section_type,
            "title": section.title,
            "doctype": section.source_doctype,
            "description": section.description,
        },
        "summary": summary,
    }


@frappe.whitelist()
def get_page(
    page_name: str,
    page: int = 1,
    page_size: int = 10,
    search : str = ""
):

    # Resolve the Web Page document.
    page_name_value = frappe.db.get_value(
        "WorkPulse Web Page",
        {
            "page_name": page_name
        },
        "name"
    )

    if not page_name_value:
        frappe.throw(
            f"WorkPulse Web Page with page_name "
            f"'{page_name}' not found"
        )

    web_page = frappe.get_doc(
        "WorkPulse Web Page",
        page_name_value
    )

    if not web_page.enabled:
        frappe.throw("Web Page is disabled")

    # Normalize pagination parameters.
    page_number = max(int(page), 1)

    page_size = max(int(page_size), 1)
    page_size = min(page_size, 50)

    limit_start = (page_number - 1) * page_size

    search_value = (search or "").strip()[:100]

    sections = []

    has_next = False

    for section in sorted(
        web_page.sections,
        key=lambda row: row.order or 0
    ):

        if not section.enabled:
            continue

        if not section.source_doctype:
            continue

        if not frappe.db.exists("DocType", section.source_doctype):
            continue

        if not frappe.has_permission(
            section.source_doctype,
            ptype="read"
        ):
            continue

        summary = _get_summary_section(section)

        if summary:
            sections.append({
                "section_name": section.section_name,
                "section_type": section.section_type,
                "title": section.title,
                "order": section.order,
                "doctype": section.source_doctype,
                "description": section.description,
                "summary": summary,
            })
            continue

        meta = frappe.get_meta(
            section.source_doctype
        )

        fields = get_list_fields(meta)
        fieldnames = [field["fieldname"] for field in fields]

        query_kwargs = {
            "fields": fieldnames,
            "limit_start": limit_start,
            "limit_page_length": page_size + 1,
            "order_by": "modified desc",
        }

        if search_value:
            or_filters = []

            for field in fields:
                if (
                    field["fieldname"] == "name"
                    or field["fieldtype"] in SEARCHABLE_FIELD_TYPES
                ):
                    or_filters.append(
                        [
                            field["fieldname"],
                            "like",
                            f"%{search_value}%"
                        ]
                    )

            if or_filters:
                query_kwargs["or_filters"] = or_filters

        records = frappe.get_list(
            section.source_doctype,
            **query_kwargs
        )

        section_has_next = (
            len(records) > page_size
        )

        if section_has_next:
            records = records[:page_size]

        has_next = has_next or section_has_next

        sections.append({
            "section_name": section.section_name,
            "section_type": section.section_type,
            "title": section.title,
            "order": section.order,
            "doctype": section.source_doctype,
            "description": section.description,
            "fields": fields,
            "records": records,
        })

    has_previous = page_number > 1

    return {
        "page": {
            "name": web_page.name,
            "page_name": web_page.page_name,
            "title": web_page.title,
            "route_key": web_page.route_key,
            "description": web_page.description,
        },
        "sections": sections,
        "pagination": {
            "page": page_number,
            "page_size": page_size,
            "has_previous": has_previous,
            "has_next": has_next,
            "search":search_value
        }
    }

    

@frappe.whitelist()
def get_detail(
    page_name: str,
    section_name: str,
    record_name: str
):
    page_name_value = frappe.db.get_value(
        "WorkPulse Web Page",
        {"page_name": page_name},
        "name"
    )

    if not page_name_value:
        frappe.throw(
            f"WorkPulse Web Page with page_name "
            f"'{page_name}' not found"
        )

    web_page = frappe.get_doc(
        "WorkPulse Web Page",
        page_name_value
    )

    if not web_page.enabled:
        frappe.throw("Web Page is disabled")

    section = None

    for row in web_page.sections:

        if (
            row.enabled
            and row.section_name == section_name
            and row.source_doctype
        ):
            section = row
            break

    if not section:
        frappe.throw(
            f"Section '{section_name}' "
            f"not found on page '{page_name}'"
        )

    if not frappe.db.exists("DocType", section.source_doctype):
        frappe.throw("Configured source DocType does not exist")

    if not frappe.has_permission(
        section.source_doctype,
        ptype="read"
    ):
        frappe.throw(
            "You do not have permission "
            "to read this document"
        )

    meta = frappe.get_meta(
        section.source_doctype
    )

    fields = get_detail_fields(meta)

    records = frappe.get_list(
        section.source_doctype,
        filters={"name": record_name},
        fields=[field["fieldname"] for field in fields],
        limit_page_length=1,
    )

    if not records:
        frappe.throw(
            f"{section.source_doctype} '{record_name}' "
            "not found or not accessible"
        )

    record = records[0]

    return {
        "page": {
            "name": web_page.name,
            "page_name": web_page.page_name,
            "title": web_page.title,
            "route_key": web_page.route_key,
            "description": web_page.description,
        },
        "section": {
            "section_name": section.section_name,
            "section_type": section.section_type,
            "title": section.title,
            "doctype": section.source_doctype,
            "description": section.description,
        },
        "fields": fields,
        "record": record,
    }
