export function formatFieldValue(field, value) {

    if (
        value === null ||
        value === undefined ||
        value === ""
    ) {
        return "—";
    }

    const fieldType =
        field.fieldtype || "Data";


    switch (fieldType) {

        case "Check":
            return (
                value === true ||
                value === 1 ||
                value === "1"
            )
                ? "✓"
                : "—";


        case "Int":
            return formatInteger(value);


        case "Float":
            return formatDecimal(value);


        case "Currency":
            return formatCurrency(value);


        case "Percent":
            return formatPercent(value);


        case "Date":
            return formatDate(value);


        case "Datetime":
            return formatDatetime(value);


        case "Time":
            return formatTime(value);


        case "Rating":
            return formatRating(value);


        case "Text Editor":
            return stripHtml(value);


        case "Data":
        case "Small Text":
        case "Long Text":
        case "Read Only":
        case "Select":
        case "Link":
        case "Dynamic Link":
        default:
            return String(value);
    }
}


function formatInteger(value) {

    const number =
        Number(value);

    if (Number.isNaN(number)) {
        return String(value);
    }

    return new Intl.NumberFormat().format(
        number
    );
}


function formatDecimal(value) {

    const number =
        Number(value);

    if (Number.isNaN(number)) {
        return String(value);
    }

    return new Intl.NumberFormat(
        undefined,
        {
            minimumFractionDigits: 0,
            maximumFractionDigits: 4
        }
    ).format(number);
}


function formatCurrency(value) {

    const number =
        Number(value);

    if (Number.isNaN(number)) {
        return String(value);
    }

    return new Intl.NumberFormat(
        undefined,
        {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        }
    ).format(number);
}


function formatPercent(value) {

    const number =
        Number(value);

    if (Number.isNaN(number)) {
        return String(value);
    }

    return `${number}%`;
}


function formatDate(value) {

    const date =
        new Date(`${value}T00:00:00`);

    if (Number.isNaN(date.getTime())) {
        return String(value);
    }

    return new Intl.DateTimeFormat(
        undefined,
        {
            day: "2-digit",
            month: "short",
            year: "numeric"
        }
    ).format(date);
}


function formatDatetime(value) {

    const normalizedValue =
        String(value).replace(" ", "T");

    const date =
        new Date(normalizedValue);

    if (Number.isNaN(date.getTime())) {
        return String(value);
    }

    return new Intl.DateTimeFormat(
        undefined,
        {
            day: "2-digit",
            month: "short",
            year: "numeric",
            hour: "numeric",
            minute: "2-digit"
        }
    ).format(date);
}


function formatTime(value) {

    const parts =
        String(value).split(":");

    if (parts.length < 2) {
        return String(value);
    }

    const hours =
        Number(parts[0]);

    const minutes =
        Number(parts[1]);

    if (
        Number.isNaN(hours) ||
        Number.isNaN(minutes)
    ) {
        return String(value);
    }

    const date =
        new Date();

    date.setHours(
        hours,
        minutes,
        0,
        0
    );

    return new Intl.DateTimeFormat(
        undefined,
        {
            hour: "numeric",
            minute: "2-digit"
        }
    ).format(date);
}


function formatRating(value) {

    const rating =
        Number(value);

    if (Number.isNaN(rating)) {
        return String(value);
    }

    const safeRating =
        Math.max(
            0,
            Math.min(
                5,
                Math.round(rating)
            )
        );

    return (
        "★".repeat(safeRating) +
        "☆".repeat(5 - safeRating)
    );
}


function stripHtml(value) {

    const parser =
        new DOMParser();

    const document =
        parser.parseFromString(
            String(value),
            "text/html"
        );

    return document.body.textContent || "";
}


export function renderField(
    field,
    value = null
) {

    const fieldWrapper =
        document.createElement("article");

    fieldWrapper.className =
        "dynamic-field";

    fieldWrapper.setAttribute(
        "aria-label",
        field.label ||
        field.fieldname ||
        "Field"
    );


    const fieldHeader =
        document.createElement("div");

    fieldHeader.className =
        "dynamic-field-header";


    const fieldLabel =
        document.createElement("span");

    fieldLabel.className =
        "dynamic-field-label";

    fieldLabel.textContent =
        field.label ||
        field.fieldname ||
        "Untitled Field";


    const fieldType =
        document.createElement("span");

    fieldType.className =
        "dynamic-field-type";

    fieldType.textContent =
        field.fieldtype ||
        "Unknown";


    fieldHeader.appendChild(
        fieldLabel
    );

    fieldHeader.appendChild(
        fieldType
    );


    const fieldValue =
        document.createElement("div");

    fieldValue.className =
        "dynamic-field-value";

    fieldValue.textContent =
        formatFieldValue(
            field,
            value
        );


    fieldWrapper.appendChild(
        fieldHeader
    );

    fieldWrapper.appendChild(
        fieldValue
    );


    fieldWrapper.dataset.fieldname =
        field.fieldname || "";

    fieldWrapper.dataset.fieldtype =
        field.fieldtype || "";


    return fieldWrapper;
}




export function renderFields(
    fields = [],
    record = {}
) {

    const fragment =
        document.createDocumentFragment();


    for (const field of fields) {

        const value =
            record[field.fieldname];


        const renderedField =
            renderField(
                field,
                value
            );


        fragment.appendChild(
            renderedField
        );
    }


    return fragment;
}



export function renderListScreenContent({
    title = "List",
    sourceDoctype = "",
    fields = [],
    records = []
} = {}) {
    return `
        <section class="dynamic-screen">

            <div class="dynamic-screen-header">

                <div class="dynamic-screen-header-main">

                    <span class="dynamic-screen-eyebrow">
                        ${escapeHtml(sourceDoctype)}
                    </span>

                    <h1 class="dynamic-screen-title">
                        ${escapeHtml(title)}
                    </h1>

                    <p class="dynamic-screen-description">
                        Browse configured records.
                    </p>

                </div>

            </div>

            <div class="dynamic-screen-content">

                ${renderListTable({
                    fields,
                    records
                })}

            </div>

        </section>
    `;
}