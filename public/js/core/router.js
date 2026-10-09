const HOME_ROUTE = "HOME";
const LIST_ROUTE = "LIST";
const RECORD_ROUTE = "RECORD";
const FORM_ROUTE = "FORM";

let currentRoute = {
    name: HOME_ROUTE
};

const listeners = new Set();

function normalizeRoute(route = {}) {
    return {
        name: route.name ?? HOME_ROUTE,
        configuration: route.configuration ?? null,
        sectionId: route.sectionId ?? null,
        recordName: route.recordName ?? null
    };
}

function parseRoute() {
    const hash =
        window.location.hash.replace(
            /^#/,
            ""
        );

    if (!hash || hash === "home") {
        return {
            name: HOME_ROUTE
        };
    }

    const [
        path,
        queryString = ""
    ] = hash.split("?");

    const params =
        new URLSearchParams(
            queryString
        );

    switch (path.toUpperCase()) {

        case "LIST":

            return normalizeRoute({
                name: LIST_ROUTE,
                configuration:
                    params.get(
                        "configuration"
                    ),
                sectionId:
                    params.get(
                        "section_id"
                    )
            });

        case "RECORD":

            return normalizeRoute({
                name: RECORD_ROUTE,
                configuration:
                    params.get(
                        "configuration"
                    ),
                sectionId:
                    params.get(
                        "section_id"
                    ),
                recordName:
                    params.get(
                        "record_name"
                    )
            });

        case "FORM":

            return normalizeRoute({
                name: FORM_ROUTE,
                configuration:
                    params.get(
                        "configuration"
                    ),
                sectionId:
                    params.get(
                        "section_id"
                    ),
                recordName:
                    params.get(
                        "record_name"
                    )
            });

        default:

            return {
                name: HOME_ROUTE
            };
    }
}

function buildRouteHash(route) {
    const normalized =
        normalizeRoute(route);

    if (
        normalized.name ===
        LIST_ROUTE
    ) {

        const params =
            new URLSearchParams();

        if (normalized.configuration) {
            params.set(
                "configuration",
                normalized.configuration
            );
        }

        if (normalized.sectionId) {
            params.set(
                "section_id",
                normalized.sectionId
            );
        }

        const query =
            params.toString();

        return query
            ? `#list?${query}`
            : "#list";
    }

    if (
        normalized.name ===
        RECORD_ROUTE
    ) {

        const params =
            new URLSearchParams();

        if (normalized.configuration) {
            params.set(
                "configuration",
                normalized.configuration
            );
        }

        if (normalized.sectionId) {
            params.set(
                "section_id",
                normalized.sectionId
            );
        }

        if (normalized.recordName) {
            params.set(
                "record_name",
                normalized.recordName
            );
        }

        const query =
            params.toString();

        return query
            ? `#record?${query}`
            : "#record";
    }

    if (
        normalized.name ===
        FORM_ROUTE
    ) {

        const params =
            new URLSearchParams();

        if (normalized.configuration) {
            params.set(
                "configuration",
                normalized.configuration
            );
        }

        if (normalized.sectionId) {
            params.set(
                "section_id",
                normalized.sectionId
            );
        }

        if (normalized.recordName) {
            params.set(
                "record_name",
                normalized.recordName
            );
        }

        const query =
            params.toString();

        return query
            ? `#form?${query}`
            : "#form";
    }

    return "#home";
}

function notify(route) {
    currentRoute =
        normalizeRoute(route);

    listeners.forEach(
        listener =>
            listener(currentRoute)
    );
}

function handleHashChange() {
    notify(
        parseRoute()
    );
}

export function getCurrentRoute() {
    return {
        ...currentRoute
    };
}

export function navigate(route) {
    const nextRoute =
        normalizeRoute(route);

    const nextHash =
        buildRouteHash(nextRoute);

    if (
        window.location.hash !==
        nextHash
    ) {

        window.location.hash =
            nextHash;

        return;
    }

    notify(nextRoute);
}

export function subscribe(listener) {
    listeners.add(listener);

    listener(
        getCurrentRoute()
    );

    return () => {
        listeners.delete(
            listener
        );
    };
}

export function startRouter() {
    window.addEventListener(
        "hashchange",
        handleHashChange
    );

    handleHashChange();
}