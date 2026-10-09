function escapeHtml(value) {
    return String(value ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}

function getDisplayValue(value) {
    if (
        value === null ||
        value === undefined ||
        value === ""
    ) {
        return "—";
    }

    return String(value);
}

function getListColumns(fields = []) {
    const configuredColumns = fields
        .filter(
            field =>
                field?.fieldname &&
                field?.label
        );

    /*
     * Every Frappe document has a `name`.
     * It is already returned by the backend record API
     * even when no UI fields are configured.
     *
     * Therefore the generic LIST can still identify
     * records without inventing DocType-specific fields.
     */
    if (configuredColumns.length === 0) {
        return [
            {
                fieldname: "name",
                label: "Name"
            }
        ];
    }

    return configuredColumns;
}

export function renderListTable({
    fields = [],
    records = []
} = {}) {

    const columns =
        getListColumns(fields);

    if (records.length === 0) {
        return `
            <div class="list-table-empty">
                No records found.
            </div>
        `;
    }

    return `
        <div class="list-table-wrapper">

            <table class="list-table">

                <thead>

                    <tr>

                        ${columns
                            .map(
                                field => `
                                    <th scope="col">
                                        ${escapeHtml(
                                            field.label
                                        )}
                                    </th>
                                `
                            )
                            .join("")}

                    </tr>

                </thead>

                <tbody>

                    ${records
                        .map(
                            record => `
                                <tr
                                    class="list-table-row"
                                    data-record-name="${escapeHtml(
                                        record.name
                                    )}"
                                >

                                    ${columns
                                        .map(
                                            field => `
                                                <td
                                                    data-label="${escapeHtml(
                                                        field.label
                                                    )}"
                                                >
                                                    ${escapeHtml(
                                                        getDisplayValue(
                                                            record[
                                                                field.fieldname
                                                            ]
                                                        )
                                                    )}
                                                </td>
                                            `
                                        )
                                        .join("")}

                                </tr>
                            `
                        )
                        .join("")}

                </tbody>

            </table>

        </div>
    `;
}




export function renderListPagination({
    start = 0,
    limit = 20,
    hasMore = false
} = {}) {

    const currentPage =
        Math.floor(start / limit) + 1;

    const hasPrevious =
        start > 0;

    return `
        <div class="list-pagination">

            <button
                type="button"
                class="list-pagination-button"
                data-list-page="previous"
                ${hasPrevious ? "" : "disabled"}
            >
                ← Previous
            </button>


            <span class="list-pagination-page">
                Page ${currentPage}
            </span>


            <button
                type="button"
                class="list-pagination-button"
                data-list-page="next"
                ${hasMore ? "" : "disabled"}
            >
                Next →
            </button>

        </div>
    `;
}