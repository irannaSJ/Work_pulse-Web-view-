frappe.ui.form.on("Workpulse web view configuration", {
    refresh(frm) {
        if (frm.is_new()) {
            return;
        }

        frm.add_custom_button(
            __("Manage UI Fields"),
            () => {
                open_field_access_dialog(frm);
            }
        );
    }
});


function open_field_access_dialog(frm) {

    const sections = (frm.doc.sections || [])
        .filter(row => row.source_doctype);

    if (!sections.length) {
        frappe.msgprint({
            title: __("No Sections"),
            message: __("Add a section with a Source Doctype first."),
            indicator: "orange"
        });

        return;
    }

    const sectionLookup = {};

    const sectionOptions = sections.map(section => {

        const option = `${section.name} — ${section.source_doctype}`;

        sectionLookup[option] = section;

        return option;
    });

    const dialog = new frappe.ui.Dialog({
        title: __("Manage UI Fields"),

        size: "extra-large",

        fields: [
            {
                label: __("Section"),
                fieldname: "section",
                fieldtype: "Select",
                options: sectionOptions.join("\n"),
                reqd: 1
            },

            {
                label: __("Source Doctype"),
                fieldname: "source_doctype",
                fieldtype: "Data",
                read_only: 1
            },

            {
                fieldname: "fields_html",
                fieldtype: "HTML"
            }
        ],

        primary_action_label: __("Save UI Access"),

        primary_action: async () => {

            const selectedOption = dialog.get_value("section");

            const section = sectionLookup[selectedOption];

            if (!section) {
                frappe.msgprint(
                    __("Please select a section.")
                );

                return;
            }

            const wrapper =
                dialog.fields_dict.fields_html.$wrapper;

            const checkboxes =
                wrapper[0].querySelectorAll(
                    ".wvfa-enabled"
                );

            const fields = Array.from(checkboxes).map(
                checkbox => ({
                    name: checkbox.dataset.name,
                    enabled: checkbox.checked ? 1 : 0
                })
            );

            try {

                const response = await frm.call(
                    "update_field_access",
                    {
                        section_id: section.name,
                        fields: JSON.stringify(fields)
                    }
                );

                const updated =
                    response.message?.updated || 0;

                frappe.show_alert({
                    message: __(
                        `${updated} field access records updated.`
                    ),
                    indicator: "green"
                });

                dialog.hide();

            } catch (error) {

                console.error(
                    "Failed to update Field Access:",
                    error
                );
            }
        }
    });


    function escapeHtml(value) {

        return String(value ?? "")
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }


    async function loadFields() {

        const selectedOption =
            dialog.get_value("section");

        const section =
            sectionLookup[selectedOption];

        if (!section) {
            return;
        }

        dialog.set_value(
            "source_doctype",
            section.source_doctype
        );

        const wrapper =
            dialog.fields_dict.fields_html.$wrapper;

        wrapper.html(`
            <div style="padding: 20px; text-align: center;">
                ${__("Loading fields...")}
            </div>
        `);

        try {

            const response = await frm.call(
                "get_field_access_fields",
                {
                    section_id: section.name
                }
            );

            const result =
                response.message || {};

            const fields =
                result.fields || [];

            if (!fields.length) {

                wrapper.html(`
                    <div style="
                        padding: 30px;
                        text-align: center;
                        color: var(--text-muted);
                    ">
                        ${__("No UI fields available for this section.")}
                    </div>
                `);

                return;
            }

            const rows = fields.map(field => {

                const checked =
                    Number(field.enabled) === 1
                        ? "checked"
                        : "";

                return `
                    <tr>
                        <td>
                            <input
                                type="checkbox"
                                class="wvfa-enabled"
                                data-name="${escapeHtml(field.name)}"
                                ${checked}
                            >
                        </td>

                        <td>
                            <strong>
                                ${escapeHtml(field.field_label)}
                            </strong>

                            <div style="
                                font-size: 11px;
                                color: var(--text-muted);
                            ">
                                ${escapeHtml(field.fieldname)}
                            </div>
                        </td>

                        <td>
                            ${escapeHtml(field.field_type)}
                        </td>

                        <td>
                            ${escapeHtml(field.order)}
                        </td>
                    </tr>
                `;
            }).join("");

            wrapper.html(`
                <div style="
                    max-height: 500px;
                    overflow-y: auto;
                    margin-top: 15px;
                ">

                    <table class="table table-bordered">
                        <thead>
                            <tr>
                                <th style="width: 60px;">
                                    ${__("UI")}
                                </th>

                                <th>
                                    ${__("Field")}
                                </th>

                                <th>
                                    ${__("Type")}
                                </th>

                                <th style="width: 80px;">
                                    ${__("Order")}
                                </th>
                            </tr>
                        </thead>

                        <tbody>
                            ${rows}
                        </tbody>
                    </table>

                </div>
            `);

        } catch (error) {

            console.error(
                "Failed to load Field Access:",
                error
            );

            wrapper.html(`
                <div style="
                    padding: 20px;
                    color: var(--text-danger);
                ">
                    ${__("Unable to load UI fields.")}
                </div>
            `);
        }
    }


    dialog.show();

    dialog.set_value(
        "section",
        sectionOptions[0]
    );

    dialog.fields_dict.section.$input.on(
        "change",
        loadFields
    );

    loadFields();
}