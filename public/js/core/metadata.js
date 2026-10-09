const CONFIGURATION_API =
    "/api/method/hrms_customization.api.metadata.get_workpulse_configuration";

const UI_METADATA_API =
    "/api/method/hrms_customization.api.metadata.get_source_doctype_ui_processed_metadata";

    const UI_FORM_METADATA_API =
    "/api/method/hrms_customization.api.metadata.get_source_doctype_ui_form_metadata";

export async function loadConfiguration() {

    const response =
        await fetch(
            CONFIGURATION_API,
            {
                method: "GET",
                headers: {
                    "Accept": "application/json"
                }
            }
        );

    if (!response.ok) {

        throw new Error(
            `configuration request failed: ${response.status}`
        );
    }

    const result =
        await response.json();

    if (!result.message) {

        throw new Error(
            "Frappe returned an empty configuration response."
        );
    }

    return result.message;
}


export async function loadUiMetadata() {

    const response =
        await fetch(
            UI_METADATA_API,
            {
                method: "GET",
                headers: {
                    "Accept": "application/json"
                }
            }
        );

    if (!response.ok) {

        throw new Error(
            `metadata request failed: ${response.status}`
        );
    }

    const result =
        await response.json();

    if (!result.message) {

        throw new Error(
            "Frappe returned an empty metadata response."
        );
    }

    return result.message;
}



export async function loadUiRecords(
    configuration,
    sectionId,
    limitPageLength = 20,
    limitStart = 0
) {
    const params = new URLSearchParams({
        configuration,
        section_id: sectionId,
        limit_page_length: String(limitPageLength),
        limit_start: String(limitStart)
    });

    const response = await fetch(
        `/api/method/hrms_customization.api.metadata.get_source_doctype_ui_records?${params.toString()}`,
        {
            method: "GET",
            credentials: "same-origin"
        }
    );

    if (!response.ok) {
        throw new Error(
            `Failed to load UI records: ${response.status}`
        );
    }

    const data = await response.json();

    return data?.message ?? data;
}



export async function loadUiRecord(
    configuration,
    sectionId,
    recordName
) {
    const params = new URLSearchParams({
        configuration,
        section_id: sectionId,
        record_name: recordName
    });

    const response = await fetch(
        `/api/method/hrms_customization.api.metadata.get_source_doctype_ui_record?${params.toString()}`,
        {
            method: "GET",
            credentials: "include"
        }
    );

    if (!response.ok) {
        throw new Error(
            `Record API failed with status ${response.status}`
        );
    }

    const payload = await response.json();

    if (payload?.exc) {
        throw new Error(
            "Unable to load record."
        );
    }

    return payload?.message ?? payload;
}


export async function loadUiFormMetadata(
    configuration,
    sectionId,
    recordName = null
) {
    const params = new URLSearchParams({
        configuration,
        section_id: sectionId
    });

    if (recordName) {
        params.set(
            "record_name",
            recordName
        );
    }

    const response = await fetch(
        `${UI_FORM_METADATA_API}?${params.toString()}`,
        {
            method: "GET",
            credentials: "same-origin",
            headers: {
                "Accept": "application/json"
            }
        }
    );

    if (!response.ok) {
        throw new Error(
            `FORM metadata API failed with status ${response.status}`
        );
    }

    const payload =
        await response.json();

    if (payload?.exc) {
        throw new Error(
            "Unable to load FORM metadata."
        );
    }

    const data =
        payload?.message ?? payload;

    if (!data) {
        throw new Error(
            "Frappe returned an empty FORM metadata response."
        );
    }

    return data;
}