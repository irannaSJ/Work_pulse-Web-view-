import {
    loadConfiguration,
    loadUiMetadata,
    loadUiRecords,
    loadUiRecord,
    loadUiFormMetadata
} from "./core/metadata.js";

import {
    renderLoadingState,
    renderEmptyState,
    renderErrorState,
    clearState
} from "./core/state.js";

import {
    navigate,
    subscribe,
    startRouter
} from "./core/router.js";

import {
    renderSummaryCards
} from "./components/summaryCard.js";

import {
    renderQuickActions
} from "./components/quickAction.js";

import {
    renderDynamicForm
} from "./components/dynamicForm.js";

import {
    renderListTable,
    renderListPagination
} from "./components/listTable.js";

import {
    renderFields
} from "./core/renderer.js";


const app =
    document.getElementById("app");

let currentConfiguration = null;
let currentMetadata = null;


function getPayload(response) {
    return (
        response?.message ??
        response?.data ??
        response
    );
}


function getConfigurationTitle(
    configuration
) {
    const payload =
        getPayload(configuration);

    if (Array.isArray(payload)) {
        return (
            payload[0]?.Title ??
            payload[0]?.title ??
            "WorkPulse"
        );
    }

    if (payload?.configuration) {
        return (
            payload.configuration.Title ??
            payload.configuration.title ??
            "WorkPulse"
        );
    }

    if (payload?.configurations?.length) {
        return (
            payload.configurations[0]?.Title ??
            payload.configurations[0]?.title ??
            "WorkPulse"
        );
    }

    return (
        payload?.Title ??
        payload?.title ??
        "WorkPulse"
    );
}


function getConfiguredSections(
    metadata
) {
    const sourceDoctypes =
        metadata?.sourceDoctypes ?? [];

    return sourceDoctypes
        .flatMap(
            source =>
                (source.usages ?? [])
                    .map(
                        usage => ({
                            doctype:
                                source.doctype,

                            configurationId:
                                usage.configurationId,

                            sectionId:
                                usage.sectionId,

                            type:
                                usage.type,

                            order:
                                usage.order ?? 0,

                            fields:
                                usage.fields ?? []
                        })
                    )
        )
        .sort(
            (a, b) =>
                a.order - b.order
        );
}


function getSectionDescription(
    section
) {
    switch (section.type) {

        case "LIST":
            return `View ${section.doctype} records`;

        case "SUMMARY":
            return `View ${section.doctype} summary`;

        case "QUICK_ACTIONS":
            return `${section.doctype} quick actions`;

        case "CONTENT":
            return `${section.doctype} content`;

        default:
            return `Open ${section.doctype} section`;
    }
}


function getSectionIcon(
    type
) {
    switch (type) {

        case "LIST":
            return "☷";

        case "SUMMARY":
            return "◫";

        case "QUICK_ACTIONS":
            return "✦";

        case "CONTENT":
            return "▤";

        default:
            return "□";
    }
}


function escapeHtml(value) {
    return String(value ?? "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}


function getSectionByRoute(
    route
) {
    const sections =
        getConfiguredSections(
            currentMetadata
        );

    return sections.find(
        section =>
            section.configurationId ===
                route.configuration &&
            section.sectionId ===
                route.sectionId
    );
}


function renderHomeScreen() {

    const title =
        getConfigurationTitle(
            currentConfiguration
        );

    const sections =
        getConfiguredSections(
            currentMetadata
        );

    const quickActions = [
        {
            id: "NEW_EMPLOYEE",
            label: "New Employee",
            description: "Create a new employee",
            icon: "+",
            actionType: "CREATE",
            configuration: "WWVC-01",
            sectionId: "77f9fntmak"
        }
    ];

    clearState(app);

    app.innerHTML = `
        <main class="dashboard-screen">

            <div class="dashboard-shell">

                <header class="dashboard-topbar">

                    <div class="dashboard-brand">

                        <div class="dashboard-brand-mark">
                            W
                        </div>

                        <div class="dashboard-brand-text">

                            <span class="dashboard-brand-name">
                                ${escapeHtml(title)}
                            </span>

                            <span class="dashboard-brand-caption">
                                Workspace
                            </span>

                        </div>

                    </div>

                    <div class="dashboard-page-label">
                        Dashboard
                    </div>

                </header>


                <section class="dashboard-hero">

                    <div>

                        <span class="dashboard-eyebrow">
                            Welcome back
                        </span>

                        <h1>
                            ${escapeHtml(title)}
                        </h1>

                        <p>
                            Everything you need,
                            organized in one place.
                        </p>

                    </div>

                </section>


                <section class="dashboard-content">


                    <section class="dashboard-summary-area">

                        <div class="dashboard-section-heading">

                            <div>

                                <h2>
                                    Overview
                                </h2>

                                <p>
                                    Key information at a glance.
                                </p>

                            </div>

                        </div>

                        <div class="dashboard-summary-grid">
                            ${renderSummaryCards([])}
                        </div>

                    </section>


                    <section class="dashboard-actions-area">

                        <div class="dashboard-section-heading">

                            <div>

                                <h2>
                                    Quick Actions
                                </h2>

                                <p>
                                    Common actions for your workspace.
                                </p>

                            </div>

                        </div>

                        <div class="dashboard-actions-grid">
                            ${renderQuickActions(quickActions)}
                        </div>

                    </section>


                    <section class="dashboard-workspace-area">

                        <div class="dashboard-section-heading">

                            <div>

                                <h2>
                                    Your workspace
                                </h2>

                                <p>
                                    Access your configured sections.
                                </p>

                            </div>

                        </div>


                        <div class="dashboard-section-grid">

                            ${
                                sections.length > 0

                                    ? sections
                                        .map(
                                            section => {

                                                const isList =
                                                    section.type ===
                                                    "LIST";

                                                return `
                                                    <button
                                                        type="button"
                                                        class="
                                                            dashboard-section-card
                                                            ${
                                                                isList
                                                                    ? "dashboard-section-card-clickable"
                                                                    : ""
                                                            }
                                                        "
                                                        ${
                                                            isList
                                                                ? `
                                                                    data-route="LIST"
                                                                    data-configuration="${escapeHtml(
                                                                        section.configurationId
                                                                    )}"
                                                                    data-section-id="${escapeHtml(
                                                                        section.sectionId
                                                                    )}"
                                                                `
                                                                : ""
                                                        }
                                                    >

                                                        <div class="dashboard-card-icon">
                                                            ${getSectionIcon(
                                                                section.type
                                                            )}
                                                        </div>


                                                        <div class="dashboard-card-content">

                                                            <div class="dashboard-card-header">

                                                                <span class="dashboard-card-type">
                                                                    ${escapeHtml(
                                                                        section.type
                                                                    )}
                                                                </span>

                                                            </div>


                                                            <h3>
                                                                ${escapeHtml(
                                                                    section.doctype
                                                                )}
                                                            </h3>


                                                            <p>
                                                                ${escapeHtml(
                                                                    getSectionDescription(
                                                                        section
                                                                    )
                                                                )}
                                                            </p>


                                                            <div class="dashboard-card-action">

                                                                <span>
                                                                    ${
                                                                        isList
                                                                            ? "Open list"
                                                                            : "Open section"
                                                                    }
                                                                </span>

                                                                <span class="dashboard-card-arrow">
                                                                    →
                                                                </span>

                                                            </div>

                                                        </div>

                                                    </button>
                                                `;
                                            }
                                        )
                                        .join("")

                                    : `
                                        <article class="dashboard-empty-card">

                                            <div class="dashboard-empty-icon">
                                                +
                                            </div>

                                            <h3>
                                                No sections configured
                                            </h3>

                                            <p>
                                                Add an enabled section to the
                                                WorkPulse web view configuration.
                                            </p>

                                        </article>
                                    `
                            }

                        </div>

                    </section>

                </section>

            </div>

        </main>
    `;


    const workspace =
        app.querySelector(
            ".dashboard-section-grid"
        );

    if (workspace) {
        workspace.addEventListener(
            "click",
            event => {

                const button =
                    event.target.closest(
                        '[data-route="LIST"]'
                    );

                if (!button) {
                    return;
                }

                const configuration =
                    button.dataset.configuration;

                const sectionId =
                    button.dataset.sectionId;

                if (!configuration || !sectionId) {
                    console.error(
                        "LIST route data is missing:",
                        {
                            configuration,
                            sectionId
                        }
                    );

                    return;
                }

                navigate({
                    name: "LIST",
                    configuration,
                    sectionId
                });
            }
        );
    }



    const quickActionsContainer =
        app.querySelector(
            ".dashboard-actions-grid"
        );

    if (quickActionsContainer) {

        quickActionsContainer.addEventListener(
            "click",
            event => {

                const button =
                    event.target.closest(
                        "[data-quick-action]"
                    );

                if (!button) {
                    return;
                }

                const actionType =
                    button.dataset.actionType;

                const configuration =
                    button.dataset.configuration;

                const sectionId =
                    button.dataset.sectionId;

                const recordName =
                    button.dataset.recordName || null;

                if (
                    !actionType ||
                    !configuration ||
                    !sectionId
                ) {
                    console.error(
                        "Quick Action route data is missing:",
                        {
                            actionType,
                            configuration,
                            sectionId,
                            recordName
                        }
                    );

                    return;
                }

                if (actionType === "CREATE") {

                    navigate({
                        name: "FORM",
                        configuration,
                        sectionId,
                        recordName
                    });

                    return;
                }

                console.error(
                    "Unsupported Quick Action type:",
                    actionType
                );
            }
        );
    }

}


async function renderListScreen(
    route,
    limit = 20,
    start = 0
) {

    renderLoadingState(app);
    const section =
        getSectionByRoute(
            route
        );


    if (!section) {

        renderErrorState(
            app,
            "The configured list section could not be found.",
            () =>
                navigate({
                    name: "HOME"
                })
        );

        return;
    }


    try {

        renderLoadingState(
            app,
            `Loading ${section.doctype}...`
        );


        const data =
            await loadUiRecords(
                route.configuration,
                route.sectionId,
                limit,
                start
            );

        clearState(app);

        const records = 
            data?.records ?? [];

        const hasRecords =
            records.length > 0;


        app.innerHTML = `
            <main class="dynamic-screen-page">

                <div class="dashboard-shell">


                    <header class="dashboard-topbar">

                        <div class="dashboard-brand">

                            <button
                                type="button"
                                class="screen-back-button"
                                data-back-home
                                aria-label="Back to dashboard"
                            >
                                ←
                            </button>


                            <div class="dashboard-brand-mark">
                                W
                            </div>


                            <div class="dashboard-brand-text">

                                <span class="dashboard-brand-name">
                                    WorkPulse
                                </span>

                                <span class="dashboard-brand-caption">
                                    ${escapeHtml(
                                        section.doctype
                                    )}
                                </span>

                            </div>

                        </div>


                        <div class="dashboard-page-label">
                            List
                        </div>

                    </header>


                    <section class="dynamic-screen-header">

                        <span class="dashboard-eyebrow">
                            ${escapeHtml(
                                section.doctype
                            )}
                        </span>


                        <h1>
                            ${escapeHtml(
                                section.doctype
                            )}
                        </h1>


                        <p>
                            Browse configured records.
                        </p>

                    </section>


                    <section class="dynamic-screen-content">

                        <div class="dashboard-section-heading">

                            <div>

                                <h2>
                                    ${escapeHtml(
                                        section.doctype
                                    )}
                                </h2>

                                <p>
                                    ${
                                        data?.pagination?.returned ??
                                        0
                                    }
                                    record(s) loaded.
                                </p>

                            </div>

                        </div>


                        <div
                            class="list-content-state"
                            data-list-content-state
                        ></div>

                    </section>

                </div>

            </main>
        `;



        const listContentState =
            app.querySelector(
                "[data-list-content-state]"
            );

        if (listContentState) {

            if (hasRecords) {

                listContentState.innerHTML =
                    renderListTable({
                        fields:
                            section.fields,

                        records:
                            records
                    });

                listContentState.insertAdjacentHTML(
                    "beforeend",
                    renderListPagination({
                        start:
                            data?.pagination?.start ?? 0,

                        limit:
                            data?.pagination?.limit ?? limit,

                        hasMore:
                            data?.pagination?.hasMore ?? false
                    })
                );

            } else {

                renderEmptyState(
                    listContentState,
                    "No records found",
                    `There are no ${section.doctype} records to display.`
                );

            }
        }



        const backButton =
            app.querySelector(
                "[data-back-home]"
            );

        
        const listContent =
            app.querySelector(
                ".dynamic-screen-content"
            );

        if (listContent) {

            listContent.addEventListener(
                "click",
                event => {

                    const row =
                        event.target.closest(
                            "[data-record-name]"
                        );

                    if (!row) {
                        return;
                    }

                    const recordName =
                        row.dataset.recordName;

                    if (!recordName) {
                        return;
                    }

                    navigate({
                        name: "RECORD",
                        configuration:
                            route.configuration,
                        sectionId:
                            route.sectionId,
                        recordName:
                            recordName
                    });

                }
            );
        }

        




        if (backButton) {

            backButton.addEventListener(
                "click",
                () => {

                    navigate({
                        name: "HOME"
                    });

                }
            );

        }

        const pagination =
            app.querySelector(
                ".list-pagination"
            );

        if (pagination) {

            pagination.addEventListener(
                "click",
                event => {

                    const button =
                        event.target.closest(
                            "[data-list-page]"
                        );

                    if (!button || button.disabled) {
                        return;
                    }

                    const action =
                        button.dataset.listPage;

                    const currentStart =
                        data?.pagination?.start ?? start;

                    const currentLimit =
                        data?.pagination?.limit ?? limit;

                    if (action === "previous") {

                        const previousStart =
                            Math.max(
                                0,
                                currentStart - currentLimit
                            );

                        renderListScreen(
                            route,
                            currentLimit,
                            previousStart
                        );

                        return;
                    }

                    if (
                        action === "next" &&
                        data?.pagination?.hasMore
                    ) {

                        renderListScreen(
                            route,
                            currentLimit,
                            currentStart + currentLimit
                        );
                    }
                }
            );
        }






    } catch (error) {

        console.error(
            "LIST screen failed:",
            error
        );

        renderErrorState(
            app,
            `Unable to load ${section.doctype}.`,
            () =>
                renderListScreen(
                    route
                )
        );
    }
}




async function renderRecordScreen(route) {

    renderLoadingState(
        app,
        "Loading record..."
    );

    try {

        const data =
            await loadUiRecord(
                route.configuration,
                route.sectionId,
                route.recordName
            );

        const record =
            data?.record ?? {};

        const fields =
            data?.fields ?? [];

        const sourceDoctype =
            data?.sourceDoctype ??
            "Record";

        app.innerHTML = `
            <main class="dynamic-screen-page">

                <div class="dashboard-shell">

                    <header class="dashboard-topbar">

                        <div class="dashboard-brand">

                            <button
                                type="button"
                                class="screen-back-button"
                                data-record-back
                                aria-label="Back to list"
                            >
                                ←
                            </button>

                            <div class="dashboard-brand-mark">
                                W
                            </div>

                            <div class="dashboard-brand-text">

                                <span class="dashboard-brand-name">
                                    WorkPulse
                                </span>

                                <span class="dashboard-brand-caption">
                                    ${escapeHtml(
                                        sourceDoctype
                                    )}
                                </span>

                            </div>

                        </div>

                        <div class="dashboard-page-label">
                            Record
                        </div>

                    </header>

                    <section class="dynamic-screen-header">

                        <span class="dashboard-eyebrow">
                            ${escapeHtml(
                                sourceDoctype
                            )}
                        </span>

                        <h1>
                            ${escapeHtml(
                                record?.name ??
                                route.recordName
                            )}
                        </h1>

                        <p>
                            Record details
                        </p>

                    </section>

                    <section class="dynamic-screen-content">

                        <div class="dashboard-section-heading">

                            <div>

                                <h2>
                                    ${escapeHtml(
                                        sourceDoctype
                                    )}
                                </h2>

                                <p>
                                    ${
                                        fields.length
                                    }
                                    field(s).
                                </p>

                            </div>

                        </div>

                        <div
                            class="record-detail-grid"
                            data-record-details
                        ></div>

                    </section>

                </div>

            </main>
        `;

        const detailContainer =
            app.querySelector(
                "[data-record-details]"
            );

        if (detailContainer) {

            detailContainer.appendChild(
                renderFields(
                    fields,
                    record
                )
            );

        }

        const backButton =
            app.querySelector(
                "[data-record-back]"
            );

        if (backButton) {

            backButton.addEventListener(
                "click",
                () => {

                    navigate({
                        name: "LIST",
                        configuration:
                            route.configuration,
                        sectionId:
                            route.sectionId
                    });

                }
            );
        }

    } catch (error) {

        console.error(
            "RECORD screen failed:",
            error
        );

        renderErrorState(
            app,
            "Unable to load record.",
            () =>
                renderRecordScreen(
                    route
                )
        );
    }
}




async function renderFormScreen(route) {

    renderLoadingState(
        app,
        "Loading form..."
    );

    try {

        const data =
            await loadUiFormMetadata(
                route.configuration,
                route.sectionId,
                route.recordName
            );

        const fields =
            data?.fields ?? [];

        const record =
            data?.record ?? {};

        const layout =
            data?.layout ?? [];

        const sourceDoctype =
            data?.sourceDoctype ??
            "Form";

        clearState(app);

        app.innerHTML = `
            <main class="dynamic-screen-page">

                <div class="dashboard-shell">

                    <header class="dashboard-topbar">

                        <div class="dashboard-brand">

                            <button
                                type="button"
                                class="screen-back-button"
                                data-form-back
                                aria-label="Back"
                            >
                                ←
                            </button>

                            <div class="dashboard-brand-mark">
                                W
                            </div>

                            <div class="dashboard-brand-text">

                                <span class="dashboard-brand-name">
                                    WorkPulse
                                </span>

                                <span class="dashboard-brand-caption">
                                    ${escapeHtml(sourceDoctype)}
                                </span>

                            </div>

                        </div>

                        <div class="dashboard-page-label">
                            Form
                        </div>

                    </header>

                    <section class="dynamic-screen-header">

                        <span class="dashboard-eyebrow">
                            ${escapeHtml(sourceDoctype)}
                        </span>

                        <h1>
                            ${
                                data?.mode === "edit"
                                    ? "Edit"
                                    : "Create"
                            }
                            ${escapeHtml(sourceDoctype)}
                        </h1>

                        <p>
                            ${
                                data?.mode === "edit"
                                    ? "Update the configured record."
                                    : "Enter the required information."
                            }
                        </p>

                    </section>

                    <section class="dynamic-screen-content">

                        <div
                            class="dynamic-form-screen-container"
                            data-form-container
                        ></div>

                    </section>

                </div>

            </main>
        `;

        const formContainer =
            app.querySelector(
                "[data-form-container]"
            );

        if (formContainer) {

            formContainer.appendChild(
                renderDynamicForm(
                    fields,
                    record,
                    (fieldname, value) => {

                        console.log(
                            "FORM field changed:",
                            fieldname,
                            value
                        );

                    },
                    layout
                )
            );

        }

        const backButton =
            app.querySelector(
                "[data-form-back]"
            );

        if (backButton) {

            backButton.addEventListener(
                "click",
                () => {

                    navigate({
                        name: "HOME"
                    });

                }
            );

        }

    } catch (error) {

        console.error(
            "FORM screen failed:",
            error
        );

        renderErrorState(
            app,
            "Unable to load form.",
            () =>
                renderFormScreen(route)
        );

    }
}







function renderRoute(route) {

    switch (route.name) {

        case "LIST":

            renderListScreen(
                route
            );

            break;


        case "RECORD":

            renderRecordScreen(
                route
            );

            break;


        case "FORM":

            renderFormScreen(
                route
            );

            break;


        case "HOME":

            renderHomeScreen();

            break;


        default:

            renderHomeScreen();

            break;
    }
}


async function initializeApp() {

    try {

        renderLoadingState(
            app,
            "Loading WorkPulse..."
        );


        const [
            configuration,
            metadataResponse
        ] = await Promise.all([
            loadConfiguration(),
            loadUiMetadata()
        ]);


        currentConfiguration =
            configuration;

        currentMetadata =
            getPayload(
                metadataResponse
            );


        subscribe(
            renderRoute
        );


        startRouter();

    } catch (error) {

        console.error(
            "WorkPulse initialization failed:",
            error
        );

        renderErrorState(
            app,
            "Unable to load WorkPulse.",
            initializeApp
        );
    }
}


initializeApp();