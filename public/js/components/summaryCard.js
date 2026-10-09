function escapeHtml(value) {
    return String(value ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}

function getDefaultIcon() {
    return "◫";
}

export function renderSummaryCard({
    label = "Summary",
    value = "—",
    description = "",
    icon = getDefaultIcon()
} = {}) {
    return `
        <article
            class="summary-card"
            role="group"
            aria-label="${escapeHtml(label)}"
        >
            <div class="summary-card-header">

                <div
                    class="summary-card-icon"
                    aria-hidden="true"
                >
                    ${escapeHtml(icon)}
                </div>

            </div>

            <div class="summary-card-content">

                <div class="summary-card-value">
                    ${escapeHtml(value)}
                </div>

                <div class="summary-card-label">
                    ${escapeHtml(label)}
                </div>

                ${
                    description
                        ? `
                            <p class="summary-card-description">
                                ${escapeHtml(description)}
                            </p>
                        `
                        : ""
                }

            </div>
        </article>
    `;
}

export function renderSummaryCards(cards = []) {
    return cards
        .map(card => renderSummaryCard(card))
        .join("");
}