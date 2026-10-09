export function renderLoadingState(
    container,
    message = "Loading..."
) {

    container.innerHTML = "";


    const state =
        document.createElement("section");

    state.className =
        "app-state app-state-loading";


    const spinner =
        document.createElement("div");

    spinner.className =
        "app-state-spinner";


    const text =
        document.createElement("p");

    text.className =
        "app-state-message";

    text.textContent =
        message;


    state.appendChild(
        spinner
    );

    state.appendChild(
        text
    );

    state.setAttribute(
        "role",
        "status"
    );

    state.setAttribute(
        "aria-live",
        "polite"
    );


    container.appendChild(
        state
    );
}


export function renderEmptyState(
    container,
    title = "Nothing here",
    message = "There is no data to display."
) {

    container.innerHTML = "";


    const state =
        document.createElement("section");

    state.className =
        "app-state app-state-empty";


    const heading =
        document.createElement("h2");

    heading.className =
        "app-state-title";

    heading.textContent =
        title;


    const text =
        document.createElement("p");

    text.className =
        "app-state-message";

    text.textContent =
        message;


    state.appendChild(
        heading
    );

    state.appendChild(
        text
    );

    state.setAttribute(
        "role",
        "status"
    );


    container.appendChild(
        state
    );
}


export function renderErrorState(
    container,
    message = "Something went wrong.",
    onRetry = null
) {

    container.innerHTML = "";


    const state =
        document.createElement("section");

    state.className =
        "app-state app-state-error";


    const heading =
        document.createElement("h2");

    heading.className =
        "app-state-title";

    heading.textContent =
        "Unable to load";


    const text =
        document.createElement("p");

    text.className =
        "app-state-message";

    text.textContent =
        message;


    state.appendChild(
        heading
    );

    state.appendChild(
        text
    );

    state.setAttribute(
        "role",
        "alert"
    );

    state.setAttribute(
        "aria-live",
        "assertive"
    );


    if (typeof onRetry === "function") {

        const retryButton =
            document.createElement("button");

        retryButton.type =
            "button";

        retryButton.className =
            "app-state-retry";

        retryButton.textContent =
            "Retry";


        retryButton.addEventListener(
            "click",
            onRetry
        );


        state.appendChild(
            retryButton
        );
    }


    container.appendChild(
        state
    );
}


export function clearState(
    container
) {

    container.innerHTML = "";
}