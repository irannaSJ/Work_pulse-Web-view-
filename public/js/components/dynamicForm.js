function createElement(tagName, className = "") {
    const element = document.createElement(tagName);

    if (className) {
        element.className = className;
    }

    return element;
}

function createFieldContainer(field) {
    const container = createElement(
        "div",
        "dynamic-form-field"
    );

    container.dataset.fieldname = field.fieldname || "";

    return container;
}

function createFieldLabel(field) {
    const label = createElement(
        "label",
        "dynamic-form-field-label"
    );

    label.textContent =
        field.label ||
        field.fieldname ||
        "";

    if (isFieldRequired(field)) {
        const requiredIndicator =
            createElement(
                "span",
                "dynamic-form-required"
            );

        requiredIndicator.textContent = " *";

        label.appendChild(
            requiredIndicator
        );
    }

    return label;
}

function createTextInput(field, value) {
    const input = createElement(
        "input",
        "dynamic-form-input"
    );

    input.type = "text";

    input.name = field.fieldname || "";
    input.value = value ?? "";

    return input;
}

function createNumberInput(field, value) {
    const input = createElement(
        "input",
        "dynamic-form-input"
    );

    input.type = "number";

    input.name = field.fieldname || "";

    if (value !== null && value !== undefined) {
        input.value = value;
    }

    return input;
}

function createTextarea(field, value) {
    const textarea = createElement(
        "textarea",
        "dynamic-form-textarea"
    );

    textarea.name = field.fieldname || "";
    textarea.value = value ?? "";

    return textarea;
}

function createCheckbox(field, value) {
    const input = createElement(
        "input",
        "dynamic-form-checkbox"
    );

    input.type = "checkbox";

    input.name = field.fieldname || "";

    input.checked = (
        value === true ||
        value === 1 ||
        value === "1"
    );

    return input;
}

function createDateInput(field, value) {
    const input = createElement(
        "input",
        "dynamic-form-input"
    );

    input.type = "date";

    input.name = field.fieldname || "";
    input.value = value ?? "";

    return input;
}

function createDatetimeInput(field, value) {
    const input = createElement(
        "input",
        "dynamic-form-input"
    );

    input.type = "datetime-local";

    input.name = field.fieldname || "";

    if (value) {
        input.value = String(value)
            .replace(" ", "T")
            .slice(0, 16);
    }

    return input;
}

function createTimeInput(field, value) {
    const input = createElement(
        "input",
        "dynamic-form-input"
    );

    input.type = "time";

    input.name = field.fieldname || "";
    input.value = value ?? "";

    return input;
}

function createSelectInput(field, value) {
    const select = createElement(
        "select",
        "dynamic-form-select"
    );

    select.name = field.fieldname || "";

    const options = String(
        field.options || ""
    )
        .split("\n")
        .map(option => option.trim())
        .filter(Boolean);

    for (const optionValue of options) {
        const option = createElement(
            "option"
        );

        option.value = optionValue;
        option.textContent = optionValue;

        if (String(value ?? "") === optionValue) {
            option.selected = true;
        }

        select.appendChild(option);
    }

    return select;
}

function createReadOnlyField(field, value) {
    const output = createElement(
        "div",
        "dynamic-form-readonly"
    );

    output.textContent = value ?? "—";

    return output;
}

function createRatingInput(field, value) {
    const input = createElement(
        "input",
        "dynamic-form-input"
    );

    input.type = "number";
    input.min = "0";
    input.max = "5";
    input.step = "1";

    input.name = field.fieldname || "";

    if (value !== null && value !== undefined) {
        input.value = value;
    }

    return input;
}

function createFieldControl(field, value) {
    const fieldType = field.fieldtype || "Data";

    switch (fieldType) {
        case "Data":
            return createTextInput(field, value);

        case "Small Text":
        case "Long Text":
        case "Text Editor":
            return createTextarea(field, value);

        case "Read Only":
            return createReadOnlyField(field, value);

        case "Int":
        case "Float":
        case "Currency":
        case "Percent":
            return createNumberInput(field, value);

        case "Check":
            return createCheckbox(field, value);

        case "Date":
            return createDateInput(field, value);

        case "Datetime":
            return createDatetimeInput(field, value);

        case "Time":
            return createTimeInput(field, value);

        case "Select":
            return createSelectInput(field, value);

        case "Link":
        case "Dynamic Link":
            return createTextInput(field, value);

        case "Rating":
            return createRatingInput(field, value);

        default:
            return createTextInput(field, value);
    }
}

function isFieldRequired(field) {
    return (
        field.reqd === 1 ||
        field.reqd === true
    );
}

function isFieldReadOnly(field) {
    return (
        field.readOnly === 1 ||
        field.readOnly === true ||
        field.editable === false
    );
}

function applyFieldState(field, control) {
    const required = isFieldRequired(field);
    const readOnly = isFieldReadOnly(field);

    if (required) {
        control.setAttribute(
            "aria-required",
            "true"
        );

        if (
            control instanceof HTMLInputElement ||
            control instanceof HTMLTextAreaElement ||
            control instanceof HTMLSelectElement
        ) {
            control.required = true;
        }
    }

    if (readOnly) {
        control.classList.add(
            "dynamic-form-control-readonly"
        );

        control.setAttribute(
            "aria-readonly",
            "true"
        );

        if (
            control instanceof HTMLInputElement &&
            control.type === "checkbox"
        ) {
            control.disabled = true;
        } else if (
            control instanceof HTMLSelectElement
        ) {
            control.disabled = true;
        } else if (
            control instanceof HTMLInputElement ||
            control instanceof HTMLTextAreaElement
        ) {
            control.readOnly = true;
        }
    }
}


function isBlankValue(value) {
    return (
        value === null ||
        value === undefined ||
        String(value).trim() === ""
    );
}

function getControlValue(control) {
    if (
        control instanceof HTMLInputElement &&
        control.type === "checkbox"
    ) {
        return control.checked;
    }

    return control.value;
}

function validateFieldValue(field, value) {
    const errors = [];

    const required =
        field.reqd === 1 ||
        field.reqd === true;

    if (required) {
        if (
            field.fieldtype === "Check"
        ) {
            if (value !== true) {
                errors.push(
                    `${field.label || field.fieldname} is required.`
                );
            }
        } else if (isBlankValue(value)) {
            errors.push(
                `${field.label || field.fieldname} is required.`
            );
        }
    }

    if (
        !isBlankValue(value) &&
        [
            "Int",
            "Float",
            "Currency",
            "Percent"
        ].includes(field.fieldtype)
    ) {
        const numericValue = Number(value);

        if (!Number.isFinite(numericValue)) {
            errors.push(
                `${field.label || field.fieldname} must be a valid number.`
            );
        }
    }

    if (
        !isBlankValue(value) &&
        field.fieldtype === "Data" &&
        field.options === "Email"
    ) {
        const emailPattern =
            /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

        if (
            !emailPattern.test(
                String(value).trim()
            )
        ) {
            errors.push(
                `${field.label || field.fieldname} must be a valid email address.`
            );
        }
    }

    if (
        !isBlankValue(value) &&
        field.fieldtype === "Rating"
    ) {
        const rating = Number(value);

        if (
            !Number.isFinite(rating) ||
            rating < 0 ||
            rating > 5
        ) {
            errors.push(
                `${field.label || field.fieldname} must be between 0 and 5.`
            );
        }
    }

    return errors;
}

function clearFieldError(container) {
    const existingError =
        container.querySelector(
            ".dynamic-form-field-error"
        );

    if (existingError) {
        existingError.remove();
    }

    container.classList.remove(
        "dynamic-form-field-invalid"
    );
}

function showFieldError(
    container,
    message
) {
    clearFieldError(container);

    container.classList.add(
        "dynamic-form-field-invalid"
    );

    const error =
        createElement(
            "div",
            "dynamic-form-field-error"
        );

    error.textContent = message;

    container.appendChild(error);
}



export function validateDynamicForm(
    formContainer,
    fields = []
) {
    const errors = {};

    for (const field of fields) {
        const control =
            formContainer.querySelector(
                `[name="${field.fieldname}"]`
            );

        if (!control) {
            continue;
        }

        const value =
            getControlValue(control);

        const fieldErrors =
            validateFieldValue(
                field,
                value
            );

        const fieldContainer =
            control.closest(
                ".dynamic-form-field"
            );

        if (
            fieldErrors.length > 0
        ) {
            errors[field.fieldname] =
                fieldErrors;

            if (fieldContainer) {
                showFieldError(
                    fieldContainer,
                    fieldErrors[0]
                );
            }
        } else if (fieldContainer) {
            clearFieldError(
                fieldContainer
            );
        }
    }

    return {
        valid:
            Object.keys(errors).length === 0,
        errors
    };
}




export function renderFormField(
    field,
    value = null,
    onChange = null
) {
    const container = createFieldContainer(
        field
    );

    if (isFieldReadOnly(field)) {
        container.classList.add(
            "dynamic-form-field-readonly"
        );
    }

    const label = createFieldLabel(
        field
    );

    const control = createFieldControl(
        field,
        value
    );

    applyFieldState(
        field,
        control
    );

    container.appendChild(label);
    container.appendChild(control);

    if (
        typeof onChange === "function" &&
        !isFieldReadOnly(field)
    ) {
        control.addEventListener(
            "change",
            event => {
                const newValue =
                    control instanceof HTMLInputElement &&
                    control.type === "checkbox"
                        ? control.checked
                        : event.target.value;

                onChange(
                    field.fieldname,
                    newValue
                );
            }
        );

        control.addEventListener(
            "input",
            event => {
                if (
                    control instanceof HTMLInputElement &&
                    control.type === "checkbox"
                ) {
                    return;
                }

                onChange(
                    field.fieldname,
                    event.target.value
                );
            }
        );
    }

    return container;
}



function resolveFieldValue(field, record = {}) {
    const fieldname = field.fieldname;

    const hasRecordValue =
        Object.prototype.hasOwnProperty.call(
            record,
            fieldname
        );

    const recordValue =
        hasRecordValue
            ? record[fieldname]
            : undefined;

    // A real record value always wins.
    // This also preserves 0, false, and "".
    if (
        recordValue !== null &&
        recordValue !== undefined
    ) {
        return recordValue;
    }

    // Fall back to the metadata default.
    if (
        field.default !== null &&
        field.default !== undefined
    ) {
        return field.default;
    }

    return recordValue ?? null;
}




function createFormSection(label) {
    const section = createElement(
        "section",
        "dynamic-form-section"
    );

    if (label) {
        const title = createElement(
            "h3",
            "dynamic-form-section-title"
        );

        title.textContent = label;

        section.appendChild(title);
    }

    const columns = createElement(
        "div",
        "dynamic-form-columns"
    );

    section.appendChild(columns);

    return section;
}

function createFormColumn() {
    return createElement(
        "div",
        "dynamic-form-column"
    );
}



export function renderDynamicForm(
    fields = [],
    record = {},
    onChange = null,
    layout = null
) {
    const fieldMap = new Map(
        fields.map(field => [
            field.fieldname,
            field
        ])
    );

    /*
     * Backward compatibility:
     *
     * If no layout metadata is provided,
     * render the existing flat form.
     */
    if (!Array.isArray(layout) || layout.length === 0) {
        const fragment =
            document.createDocumentFragment();

        for (const field of fields) {
            const value =
                resolveFieldValue(
                    field,
                    record
                );

            fragment.appendChild(
                renderFormField(
                    field,
                    value,
                    onChange
                )
            );
        }

        return fragment;
    }

    const form =
        createElement(
            "div",
            "dynamic-form-layout"
        );

    let currentSection = null;
    let currentColumns = null;
    let currentColumn = null;

    function ensureSection() {
        if (currentSection) {
            return;
        }

        currentSection =
            createFormSection("");

        currentColumns =
            currentSection.querySelector(
                ".dynamic-form-columns"
            );

        currentColumn =
            createFormColumn();

        currentColumns.appendChild(
            currentColumn
        );

        form.appendChild(
            currentSection
        );
    }

    function ensureColumn() {
        ensureSection();

        if (!currentColumn) {
            currentColumn =
                createFormColumn();

            currentColumns.appendChild(
                currentColumn
            );
        }
    }

    for (const item of layout) {

        // -----------------------------------------------------
        // Section
        // -----------------------------------------------------

        if (item.type === "SECTION") {

            currentSection =
                createFormSection(
                    item.label
                );

            currentColumns =
                currentSection.querySelector(
                    ".dynamic-form-columns"
                );

            currentColumn =
                createFormColumn();

            currentColumns.appendChild(
                currentColumn
            );

            form.appendChild(
                currentSection
            );

            continue;
        }

        // -----------------------------------------------------
        // Column
        // -----------------------------------------------------

        if (item.type === "COLUMN") {

            ensureSection();

            currentColumn =
                createFormColumn();

            currentColumns.appendChild(
                currentColumn
            );

            continue;
        }

        // -----------------------------------------------------
        // Tab
        // -----------------------------------------------------

        if (item.type === "TAB") {

            currentSection =
                createFormSection(
                    item.label
                );

            currentSection.classList.add(
                "dynamic-form-tab"
            );

            currentColumns =
                currentSection.querySelector(
                    ".dynamic-form-columns"
                );

            currentColumn =
                createFormColumn();

            currentColumns.appendChild(
                currentColumn
            );

            form.appendChild(
                currentSection
            );

            continue;
        }

        // -----------------------------------------------------
        // Field
        // -----------------------------------------------------

        if (item.type === "FIELD") {

            const field =
                fieldMap.get(
                    item.fieldname
                );

            if (!field) {
                continue;
            }

            ensureColumn();

            const value =
                resolveFieldValue(
                    field,
                    record
                );

            currentColumn.appendChild(
                renderFormField(
                    field,
                    value,
                    onChange
                )
            );
        }
    }

    return form;
}