"""
WorkPulse metadata API compatibility facade.

The actual implementation is now organized inside:

    api/webview/

This file keeps the existing API import paths working.
"""

# -------------------------------------------------------------
# Configuration
# -------------------------------------------------------------

from .webview.configuration import (
    get_workpulse_configuration,
)


from .webview.ui_definition import (
    get_workpulse_ui_definition
)

# -------------------------------------------------------------
# Source DocType metadata
# -------------------------------------------------------------

from .webview.metadata import (
    get_source_doctype_metadata,
)


# -------------------------------------------------------------
# Permissions
# -------------------------------------------------------------

from .webview.permissions import (
    get_source_doctype_permissions,
)


# -------------------------------------------------------------
# Processed metadata
# -------------------------------------------------------------

from .webview.processed_metadata import (
    get_source_doctype_hidden_processed_metadata,
    get_source_doctype_sensitive_processed_metadata,
    get_source_doctype_ui_processed_metadata,
)


# -------------------------------------------------------------
# Form metadata
# -------------------------------------------------------------

from .webview.forms import (
    get_source_doctype_ui_form_metadata,
)


# -------------------------------------------------------------
# Record APIs
# -------------------------------------------------------------

from .webview.records import (
    get_source_doctype_ui_records,
    get_source_doctype_ui_record,
    get_linked_field_values
)


# -------------------------------------------------------------
# Summary APIs
# -------------------------------------------------------------

from .webview.summaries import (
    get_source_doctype_ui_count,
    get_source_doctype_ui_sum,
    get_source_doctype_ui_average,
)


# -------------------------------------------------------------
# Internal compatibility exports
# -------------------------------------------------------------
#
# These are kept available so code that previously imported
# internal helpers from api.metadata does not immediately break.
#
# New code should import helpers from their actual module.
#

from .webview.permissions import (
    _get_effective_doctype_permissions,
    _get_effective_field_permissions,
)

from .webview.fields import (
    _preprocess_hidden_fields,
    _is_data_field,
    _preprocess_sensitive_fields,
    _get_field_access_records,
    _preprocess_ui_fields,
    _build_form_layout,
    _get_enabled_ui_fieldnames,
)


from .webview.submissions import save_source_doctype_ui_record


__all__ = [
    # Configuration
    "get_workpulse_configuration",
    "get_workpulse_ui_definition",

    # Metadata
    "get_source_doctype_metadata",

    # Permissions
    "get_source_doctype_permissions",

    # Processed metadata
    "get_source_doctype_hidden_processed_metadata",
    "get_source_doctype_sensitive_processed_metadata",
    "get_source_doctype_ui_processed_metadata",

    # Forms
    "get_source_doctype_ui_form_metadata",

    # Records
    "get_source_doctype_ui_records",
    "get_source_doctype_ui_record",
    "get_linked_field_values",

    # Summaries
    "get_source_doctype_ui_count",
    "get_source_doctype_ui_sum",
    "get_source_doctype_ui_average",


    #submission
    "save_source_doctype_ui_record"
]