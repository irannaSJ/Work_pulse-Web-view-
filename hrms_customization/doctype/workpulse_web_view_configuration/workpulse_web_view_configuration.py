import frappe
from frappe.model.document import Document


FIELD_ACCESS_DOCTYPE = "Workpulse Web View Field Access"


class Workpulsewebviewconfiguration(Document):

    def on_update(self):
        self.sync_field_access()

    def sync_field_access(self):
        """
        Synchronize Workpulse Web View Field Access records
        with the Source Doctype metadata configured in Sections.
        """

        existing_records = frappe.get_all(
            FIELD_ACCESS_DOCTYPE,
            filters={
                "configuration": self.name
            },
            fields=[
                "name",
                "section_id",
                "source_doctype",
                "fieldname",
                "enabled",
                "order"
            ]
        )

        NON_DATA_FIELD_TYPES = {
            "Tab Break",
            "Section Break",
            "Column Break",
            "Button",
            "HTML",
            "Heading",
        }

        existing_map = {
            (
                record.section_id,
                record.source_doctype,
                record.fieldname
            ): record
            for record in existing_records
        }

        current_keys = set()

        for section in self.get("sections") or []:

            source_doctype = section.get("source_doctype")

            if not source_doctype:
                continue

            section_id = (
                section.get("id")
                or section.name
            )

            if not frappe.db.exists(
                "DocType",
                source_doctype
            ):
                frappe.throw(
                    f"Source DocType does not exist: {source_doctype}"
                )

            if not frappe.has_permission(
                source_doctype,
                ptype="read",
                user=frappe.session.user
            ):
                frappe.throw(
                    f"You do not have read permission for Source DocType: {source_doctype}"
                )

            meta = frappe.get_meta(source_doctype)

            for field in meta.fields:

                fieldname = field.get("fieldname")

                field_type = field.get("fieldtype")

                if field_type in NON_DATA_FIELD_TYPES:
                    continue

                if not fieldname:
                    continue

                # Frappe-hidden fields should not be exposed
                # as WorkPulse UI fields.
                if field.get("hidden"):
                    continue

                key = (
                    section_id,
                    source_doctype,
                    fieldname
                )

                current_keys.add(key)

                existing_record = existing_map.get(key)

                field_label = (
                    field.get("label")
                    or fieldname
                )

                field_type = (
                    field.get("fieldtype")
                    or ""
                )

                field_order = (
                    field.get("idx")
                    or 0
                )

                if existing_record:

                    # Keep administrator's existing Enabled
                    # and Order choices.
                    frappe.db.set_value(
                        FIELD_ACCESS_DOCTYPE,
                        existing_record.name,
                        {
                            "field_label": field_label,
                            "field_type": field_type
                        }
                    )

                else:

                    frappe.get_doc({
                        "doctype": FIELD_ACCESS_DOCTYPE,

                        "configuration": self.name,

                        "section_id": section_id,

                        "source_doctype": source_doctype,

                        "fieldname": fieldname,

                        "field_label": field_label,

                        "field_type": field_type,

                        # New fields are NOT exposed automatically.
                        "enabled": 0,

                        # Start with the same order as the
                        # original Frappe DocType field order.
                        "order": field_order
                    }).insert()

        self.disable_stale_field_access(
            current_keys=current_keys,
            existing_records=existing_records
        )

    def disable_stale_field_access(
        self,
        current_keys,
        existing_records
    ):
        """
        Disable Field Access records that no longer belong
        to the current configuration metadata.

        Records are disabled instead of immediately deleted,
        preserving configuration history.
        """

        for record in existing_records:

            key = (
                record.section_id,
                record.source_doctype,
                record.fieldname
            )

            if key not in current_keys:

                if record.enabled:
                    frappe.db.set_value(
                        FIELD_ACCESS_DOCTYPE,
                        record.name,
                        "enabled",
                        0
                    )





    @frappe.whitelist()
    def get_field_access_fields(self, section_id):
        """
        Return the Field Access records belonging to one configured section.
        """

        self.check_permission("read")

        if not frappe.has_permission(
            "Workpulse Web View Field Access",
            ptype="read",
            user=frappe.session.user
        ):
            frappe.throw(
                "You do not have permission to read Workpulse Web View Field Access."
            )

        section = next(
            (
                row
                for row in (self.get("sections") or [])
                if row.name == section_id
            ),
            None
        )

        if not section:
            frappe.throw("Section not found in this configuration.")

        if not section.source_doctype:
            frappe.throw("This section does not have a Source Doctype.")

        fields = frappe.get_all(
            "Workpulse Web View Field Access",
            filters={
                "configuration": self.name,
                "section_id": section.name,
                "source_doctype": section.source_doctype
            },
            fields=[
                "name",
                "fieldname",
                "field_label",
                "field_type",
                "enabled",
                "order"
            ],
            order_by="`order` asc, fieldname asc"
        )

        return {
            "section_id": section.name,
            "source_doctype": section.source_doctype,
            "fields": fields
        }


    @frappe.whitelist()
    def update_field_access(self, section_id, fields):
        """
        Update UI exposure for fields belonging to one configured section.
        """

        self.check_permission("write")

        if not frappe.has_permission(
            "Workpulse Web View Field Access",
            ptype="write",
            user=frappe.session.user
        ):
            frappe.throw(
                "You do not have permission to modify Workpulse Web View Field Access."
            )

        section = next(
            (
                row
                for row in (self.get("sections") or [])
                if row.name == section_id
            ),
            None
        )

        if not section:
            frappe.throw("Section not found in this configuration.")

        if not section.source_doctype:
            frappe.throw("This section does not have a Source Doctype.")

        if isinstance(fields, str):
            fields = frappe.parse_json(fields)

        if not isinstance(fields, list):
            frappe.throw("Invalid field access data.")

        existing_records = frappe.get_all(
            "Workpulse Web View Field Access",
            filters={
                "configuration": self.name,
                "section_id": section.name,
                "source_doctype": section.source_doctype
            },
            fields=["name"]
        )

        allowed_names = {
            record.name
            for record in existing_records
        }

        updated_count = 0

        for item in fields:

            if not isinstance(item, dict):
                continue

            record_name = item.get("name")

            if record_name not in allowed_names:
                frappe.throw(
                    f"Invalid Field Access record: {record_name}"
                )

            enabled = 1 if item.get("enabled") else 0

            frappe.db.set_value(
                "Workpulse Web View Field Access",
                record_name,
                "enabled",
                enabled
            )

            updated_count += 1

        return {
            "updated": updated_count
        }