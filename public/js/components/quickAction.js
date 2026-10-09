function escapeHtml(value) {
    return String(value ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}

function getDefaultIcon() {
    return "+";
}

export function renderQuickAction({
    id = "",
    label = "Quick Action",
    description = "",
    icon = getDefaultIcon(),
    disabled = false,

    actionType = "",
    configuration = "",
    sectionId = "",
    recordName = ""
} = {}) {
    return `
        <button
            type="button"
            class="quick-action"
            data-quick-action="${escapeHtml(id)}"
            data-action-type="${escapeHtml(actionType)}"
            data-configuration="${escapeHtml(configuration)}"
            data-section-id="${escapeHtml(sectionId)}"
            data-record-name="${escapeHtml(recordName)}"
            ${disabled ? "disabled" : ""}
            aria-label="${escapeHtml(label)}"
        >
            <span
                class="quick-action-icon"
                aria-hidden="true"
            >
                ${escapeHtml(icon)}
            </span>

            <span class="quick-action-content">

                <span class="quick-action-label">
                    ${escapeHtml(label)}
                </span>

                ${
                    description
                        ? `
                            <span class="quick-action-description">
                                ${escapeHtml(description)}
                            </span>
                        `
                        : ""
                }

            </span>

            <span
                class="quick-action-arrow"
                aria-hidden="true"
            >
                →
            </span>
        </button>
    `;
}

export function renderQuickActions(actions = []) {
    return actions
        .map(action => renderQuickAction(action))
        .join("");
}