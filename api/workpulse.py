import frappe

from hrms_customization.api.workpulse_targeting import (
    get_targeted_configuration
)

@frappe.whitelist()
def get_workpulse_configuration():

    config= get_targeted_configuration() 

    # if not configs:
    #     return {
    #         "success":False,
    #         "message":"No enabled workpulse configuration found"
    #     }
    if not config:
        return {
            "success":False,
            "message":"No enabled workpulse configuration found"
        }

    # config = frappe.get_doc("WorkPulse App Configuration",configs[0].name)

    navigation_items = []
    for item in config.navigation_items:
        navigation_items.append({
            "navigation_key":item.navigation_key,
            "label":item.label,
            "icon":item.icon,
            "location":item.location,
            "enabled":bool(item.enabled),
            "order":item.order,
            "feature_key":item.feature_key,
            "permission_required":bool(item.permission_required)
        })
    navigation_items.sort(key=lambda item:item["order"] or 0)

    quick_actions = []

    for item in config.quick_actions:
        quick_actions.append({
            "action_key": item.action_key,
            "label": item.label,
            "icon": item.icon,
            "enabled": bool(item.enabled),
            "order": item.order,
            "feature_key": item.feature_key,
            "permission_required": bool(item.permission_required)
        })
    quick_actions.sort(key =lambda item:item["order"] or 0)

    home_sections = []
    for item in config.home_sections:
        home_sections.append({
            "section_key":item.section_key,
            "title":item.title,
            "section_type":item.section_type,
            "enabled":bool(item.enabled),
            "order":item.order,
            "feature_key":item.feature_key,
            "permission_required":bool(item.permission_required),
            "configuration":item.configuration
        })
    home_sections.sort(key=lambda item:item["order"] or 0)

    features = []
    for item in config.feature:
        features.append({
            "feature_key":item.feature_key,
            "display_name":item.display_name,
            "enabled":bool(item.enabled),
            "order":item.order,
            "configuration":item.configuration,
            "permission_required":bool(item.permission_required)
        })
    features.sort(key = lambda item:item["order"] or 0)

    return {
        "success":True,
        "data":{
            "configuration_name":config.name,
            "version":config.version,
            "theme":{
                "theme_mode":config.theme_mode,
                "primary_color":config.primary_color,
                "secondary_color":config.secondary_color,
                "accent_color":config.accent_color,
                "background_color":config.background_color,
                "surface_color":config.surface_color,
                "primary_text_color":config.primary_text_color,
                "secondary_text_color":config.secondary_text_color,
                "dark_background_color":config.dark_background_color,
                "dark_surface_color":config.dark_surface_color,
                "dark_primary_text_color":config.dark_primary_text_color,
                "dark_secondary_text_color":config.dark_secondary_text_color,
                "corner_radius":config.corner_radius
            },
            "navigation":navigation_items,
            "quick_actions":quick_actions,
            "home":{
                "sections":home_sections
            },
            "features":features

        }
    }