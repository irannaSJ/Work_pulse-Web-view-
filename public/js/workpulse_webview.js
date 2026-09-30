const params = new URLSearchParams(window.location.search);

const pageName =
    params.get("page_name") || "Employee Directory";

const pageSize = 10;

let currentPage = Math.max(
    parseInt(params.get("page") || "1", 10),
    1
);

let currentSearch = params.get("search") || "";
let retryAction = () => loadPage(currentPage, currentSearch);

const contentContainer =
    document.getElementById("wp-content");

const loadingState =
    document.getElementById("wp-loading");

const errorState =
    document.getElementById("wp-error");

const emptyState =
    document.getElementById("wp-empty");

const retryButton =
    document.getElementById("wp-retry-button");

const errorBackButton =
    document.getElementById("wp-error-back-button");

const pageTitle =
    document.getElementById("wp-page-title");

const pageDescription =
    document.getElementById("wp-page-description");

const errorMessage =
    document.getElementById("wp-error-message");

const shellCard =
    document.getElementById("wp-shell-card");

const searchInput =
    document.getElementById("wp-search-input");

const searchButton =
    document.getElementById("wp-search-button");

const searchClearButton =
    document.getElementById("wp-search-clear");

const dynamicContainer =
    document.createElement("div");

dynamicContainer.id =
    "wp-dynamic-content";

contentContainer.appendChild(
    dynamicContainer
);


function listUrl(page = currentPage, search = currentSearch) {
    const url = new URL(window.location.href);

    url.search = "";
    url.searchParams.set("page_name", pageName);
    url.searchParams.set("page", page);
    url.searchParams.set("page_size", pageSize);

    if (search) {
        url.searchParams.set("search", search);
    }

    return url.href;
}


function detailUrl(section) {
    const url = new URL(listUrl());

    url.searchParams.set("view", "detail");
    url.searchParams.set("section_name", section.section_name);
    url.searchParams.set("record_name", section.record_name);

    return url.href;
}


function updateListUrl(replace = true) {
    const method = replace ? "replaceState" : "pushState";

    window.history[method](
        { wpView: "list" },
        "",
        listUrl()
    );
}


function goBackToList() {
    if (window.history.state?.wpView === "detail") {
        window.history.back();
        return;
    }

    updateListUrl(true);
    loadPage(currentPage, currentSearch, { updateUrl: false });
}


function showState(state) {
    loadingState.hidden = state !== "loading";

    errorState.hidden = state !== "error";

    emptyState.hidden = state !== "empty";

    shellCard.hidden = true
}


async function loadPage(
    page = 1,
    search = currentSearch,
    options = {}
) {

    currentPage = page;
    currentSearch = search.trim();

    retryAction = () => loadPage(
        currentPage,
        currentSearch,
        { updateUrl: false }
    );

    if (options.updateUrl !== false) {
        updateListUrl(true);
    }

    showState("loading");

    dynamicContainer.innerHTML = "";

    try {

        const searchParameter =
            currentSearch
                ? `&search=${encodeURIComponent(currentSearch)}`
                : "";

        const url =
            `/api/method/hrms_customization.api.web_view.webview.get_page` +
            `?page_name=${encodeURIComponent(pageName)}` +
            `&page=${currentPage}` +
            `&page_size=${pageSize}` +
            searchParameter;

        const response = await fetch(url);

        if (!response.ok) {
            throw new Error(
                `HTTP error: ${response.status}`
            );
        }

        const result = await response.json();

        const data = result.message;

        if (!data) {
            throw new Error("Invalid API response");
        }

        renderPage(data);

    } catch (error) {

        console.error(
            "WorkPulse WebView error:",
            error
        );

        if (errorMessage) {
            errorMessage.textContent =
                "Unable to load this page. Please try again.";
        }

        showState("error");
    }
}


async function loadDetail(section, options = {}) {

    const detailState = {
        section_name: section.section_name,
        record_name: section.record_name,
    };

    retryAction = () => loadDetail(
        detailState,
        { pushHistory: false }
    );

    if (options.pushHistory !== false) {
        window.history.pushState(
            { wpView: "detail" },
            "",
            detailUrl(detailState)
        );
    }

    showState("loading");
    dynamicContainer.innerHTML = "";

    try {
        const url =
            `/api/method/hrms_customization.api.web_view.webview.get_detail` +
            `?page_name=${encodeURIComponent(pageName)}` +
            `&section_name=${encodeURIComponent(detailState.section_name)}` +
            `&record_name=${encodeURIComponent(detailState.record_name)}`;

        const response = await fetch(url);

        if (!response.ok) {
            throw new Error(`HTTP error: ${response.status}`);
        }

        const result = await response.json();

        if (!result.message) {
            throw new Error("Invalid detail response");
        }

        renderDetail(result.message, detailState);
    } catch (error) {
        console.error("WorkPulse WebView detail error:", error);

        if (errorMessage) {
            errorMessage.textContent =
                "Unable to load this record. Please try again.";
        }

        showState("error");
    }
}


function renderPage(data) {


    loadingState.hidden = true;
    errorState.hidden = true;
    emptyState.hidden = true;
    shellCard.hidden = true;

    const page = data.page;

    if (pageTitle) {
        pageTitle.textContent =
            page.title || page.page_name;
    }

    if (pageDescription) {
        pageDescription.textContent =
            page.description || "";
    }

    dynamicContainer.innerHTML = "";

    if (
        !data.sections ||
        data.sections.length === 0
    ) {
        showState("empty");
        return;
    }

    for (const section of data.sections) {

        if (section.summary) {
            renderSummarySection(section);
            continue;
        }

        if (
            !section.records ||
            section.records.length === 0
        ) {
            continue;
        }

        renderListSection(section);
    }

    if (dynamicContainer.children.length === 0) {
        showState("empty");
        return;
    }

    if (data.sections.some((section) => !section.summary)) {
        renderPagination(data.pagination);
    }
}


function renderSummarySection(section) {
    const sectionContainer = document.createElement("section");
    sectionContainer.className = "wp-dynamic-section wp-summary-section";

    if (section.title || section.description) {
        const heading = document.createElement("h2");
        heading.className = "wp-section-title";
        heading.textContent = section.title || section.section_name;
        sectionContainer.appendChild(heading);

        if (section.description) {
            const description = document.createElement("p");
            description.className = "wp-section-description";
            description.textContent = section.description;
            sectionContainer.appendChild(description);
        }
    }

    const cards = document.createElement("div");
    cards.className = "wp-summary-cards";

    for (const metric of section.summary.metrics || []) {
        const card = document.createElement("article");
        card.className = "wp-summary-card";

        const label = document.createElement("span");
        label.className = "wp-summary-card-label";
        label.textContent = metric.label || metric.key;

        const value = document.createElement("strong");
        value.className = "wp-summary-card-value";
        value.textContent = formatSummaryValue(metric);

        card.appendChild(label);
        card.appendChild(value);
        cards.appendChild(card);
    }

    sectionContainer.appendChild(cards);
    dynamicContainer.appendChild(sectionContainer);
}


function formatSummaryValue(metric) {
    if (metric.value === null || metric.value === undefined) {
        return "—";
    }

    if (metric.type === "AVERAGE" || metric.type === "SUM") {
        const number = Number(metric.value);

        if (!Number.isNaN(number)) {
            return number.toLocaleString(undefined, {
                maximumFractionDigits: 2,
            });
        }
    }

    return String(metric.value);
}


function renderListSection(section) {

    const sectionContainer =
        document.createElement("section");

    sectionContainer.className =
        "wp-dynamic-section";


    const title =
        document.createElement("h2");

    title.textContent =
        section.title ||
        section.section_name;

    sectionContainer.appendChild(title);


    if (section.description) {

        const description =
            document.createElement("p");

        description.textContent =
            section.description;

        sectionContainer.appendChild(
            description
        );
    }


    const tableWrapper =
        document.createElement("div");

    tableWrapper.className =
        "wp-table-wrapper";


    const table =
        document.createElement("table");

    table.className =
        "wp-data-table";


    const thead =
        document.createElement("thead");

    const headerRow =
        document.createElement("tr");


    for (const field of section.fields) {

        const th =
            document.createElement("th");

        th.textContent =
            field.label || field.fieldname;

        headerRow.appendChild(th);
    }


    thead.appendChild(headerRow);
    table.appendChild(thead);


    const tbody =
        document.createElement("tbody");


    for (const record of section.records) {

        const row =
            document.createElement("tr");

        row.className = "wp-clickable-row";
        row.tabIndex = 0;

        const openDetail = () => loadDetail({
            section_name: section.section_name,
            record_name: record.name,
        });

        row.addEventListener("click", openDetail);
        row.addEventListener("keydown", (event) => {
            if (event.key === "Enter" || event.key === " ") {
                event.preventDefault();
                openDetail();
            }
        });


        for (const field of section.fields) {

            const cell =
                document.createElement("td");

            const value =
                record[field.fieldname];

            cell.textContent =
                value === null ||
                value === undefined
                    ? ""
                    : String(value);

            row.appendChild(cell);
        }

        tbody.appendChild(row);
    }


    table.appendChild(tbody);

    tableWrapper.appendChild(table);

    sectionContainer.appendChild(
        tableWrapper
    );

    dynamicContainer.appendChild(
        sectionContainer
    );
}


function renderDetail(data, listContext) {

    loadingState.hidden = true;
    errorState.hidden = true;
    emptyState.hidden = true;
    shellCard.hidden = true;

    pageTitle.textContent = data.page.title || data.page.page_name;
    pageDescription.textContent = data.section.description || "";

    const sectionContainer = document.createElement("section");
    sectionContainer.className = "wp-dynamic-section wp-detail-section";

    const backButton = document.createElement("button");
    backButton.type = "button";
    backButton.className = "wp-button wp-detail-back";
    backButton.textContent = "Back to list";
    backButton.addEventListener("click", goBackToList);
    sectionContainer.appendChild(backButton);

    const sectionTitle = document.createElement("h2");
    sectionTitle.className = "wp-section-title";
    sectionTitle.textContent =
        data.section.title || data.section.section_name;
    sectionContainer.appendChild(sectionTitle);

    const recordTitle = document.createElement("h3");
    recordTitle.className = "wp-detail-record-title";
    recordTitle.textContent = data.record.name || listContext.record_name;
    sectionContainer.appendChild(recordTitle);

    const fieldsContainer = document.createElement("dl");
    fieldsContainer.className = "wp-detail-fields";

    for (const field of data.fields || []) {
        const label = document.createElement("dt");
        label.textContent = field.label || field.fieldname;

        const value = document.createElement("dd");
        value.textContent = formatFieldValue(field, data.record[field.fieldname]);

        fieldsContainer.appendChild(label);
        fieldsContainer.appendChild(value);
    }

    sectionContainer.appendChild(fieldsContainer);
    dynamicContainer.appendChild(sectionContainer);
}


function formatFieldValue(field, value) {
    if (value === null || value === undefined || value === "") {
        return "—";
    }

    if (field.fieldtype === "Check") {
        return value === true || value === 1 || value === "1"
            ? "Yes"
            : "No";
    }

    if (field.fieldtype === "Percent") {
        return `${value}%`;
    }

    if (["Int", "Float", "Currency"].includes(field.fieldtype)) {
        const numericValue = Number(value);

        if (!Number.isNaN(numericValue)) {
            return numericValue.toLocaleString(undefined, {
                maximumFractionDigits:
                    field.fieldtype === "Int" ? 0 : 2,
            });
        }
    }

    if (field.fieldtype === "Date") {
        const date = new Date(`${value}T00:00:00`);

        if (!Number.isNaN(date.getTime())) {
            return date.toLocaleDateString();
        }
    }

    if (field.fieldtype === "Datetime") {
        const date = new Date(value.replace(" ", "T"));

        if (!Number.isNaN(date.getTime())) {
            return date.toLocaleString();
        }
    }

    if (field.fieldtype === "Time") {
        return String(value).slice(0, 8);
    }

    if (field.fieldtype === "Rating") {
        const rating = Number(value);

        if (!Number.isNaN(rating)) {
            return `${rating} / 5`;
        }
    }

    return String(value);
}


function renderPagination(pagination) {

    if (!pagination) {
        return;
    }


    const paginationContainer =
        document.createElement("div");

    paginationContainer.className =
        "wp-pagination";


    const previousButton =
        document.createElement("button");

    previousButton.type = "button";

    previousButton.textContent =
        "Previous";

    previousButton.disabled =
        !pagination.has_previous;


    previousButton.addEventListener(
        "click",
        () => {

            if (
                pagination.has_previous &&
                currentPage > 1
            ) {
                loadPage(
                    currentPage - 1,
                    currentSearch
                );
            }
        }
    );


    const pageIndicator =
        document.createElement("span");

    pageIndicator.textContent =
        `Page ${pagination.page}`;


    const nextButton =
        document.createElement("button");

    nextButton.type = "button";

    nextButton.textContent =
        "Next";

    nextButton.disabled =
        !pagination.has_next;


    nextButton.addEventListener(
        "click",
        () => {

            if (pagination.has_next) {
                loadPage(
                    currentPage + 1,
                    currentSearch
                );
            }
        }
    );


    paginationContainer.appendChild(
        previousButton
    );

    paginationContainer.appendChild(
        pageIndicator
    );

    paginationContainer.appendChild(
        nextButton
    );


    dynamicContainer.appendChild(
        paginationContainer
    );
}


retryButton?.addEventListener(
    "click",
    () => {
        retryAction();
    }
);


errorBackButton?.addEventListener(
    "click",
    goBackToList
);


window.addEventListener(
    "popstate",
    () => {
        const state = new URLSearchParams(window.location.search);
        const view = state.get("view");
        const sectionName = state.get("section_name");
        const recordName = state.get("record_name");

        currentPage = Math.max(
            parseInt(state.get("page") || "1", 10),
            1
        );
        currentSearch = state.get("search") || "";

        if (view === "detail" && sectionName && recordName) {
            loadDetail(
                {
                    section_name: sectionName,
                    record_name: recordName,
                },
                { pushHistory: false }
            );
            return;
        }

        loadPage(
            currentPage,
            currentSearch,
            { updateUrl: false }
        );
    }
);


if (
    params.get("view") === "detail" &&
    params.get("section_name") &&
    params.get("record_name")
) {
    loadDetail(
        {
            section_name: params.get("section_name"),
            record_name: params.get("record_name"),
        },
        { pushHistory: false }
    );
} else {
    loadPage(
        currentPage,
        currentSearch,
        { updateUrl: false }
    );
}

searchButton?.addEventListener(
    "click",
    () => {
        const searchValue = searchInput?.value.trim() || "";
        loadPage(1, searchValue)
    }
)

searchInput?.addEventListener(
    "keydown",
    (event) => {

        if (event.key === "Enter") {

            event.preventDefault();

            const searchValue =
                searchInput.value.trim();

            loadPage(
                1,
                searchValue
            );
        }
    }
);

searchInput?.addEventListener(
    "input",
    () => {

        if (!searchClearButton) {
            return;
        }

        searchClearButton.hidden =
            searchInput.value.trim() === "";
    }
);

searchClearButton?.addEventListener(
    "click",
    () => {

        searchInput.value = "";

        searchClearButton.hidden = true;

        loadPage(
            1,
            ""
        );
    }
);
