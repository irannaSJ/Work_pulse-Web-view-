import frappe

def get_targeted_configuration():
    user = frappe.session.user
    employee = frappe.db.get_value(
        "Employee",
        {"user_id":user},
        ["name","company","department"],
        as_dict= True
    )

    employee_name = employee.name if employee else None
    company = employee.company if employee else None
    department = employee.department if employee else None

    if employee_name:
        configs = frappe.get_all(
            "WorkPulse App Configuration",
            filters = {
                "enabled":1,
                "configuration_scope":"Employee",
                "employee":employee_name
            },
            fields = ["name", "version", "modified"],
            order_by = "modified desc",
            limit_page_length =1
        )
        if configs:
            return frappe.get_doc(
                "WorkPulse App Configuration",
                configs[0].name
            )

    if department:
        configs = frappe.get_all(
            "WorkPulse App Configuration",
            filters = {
                "enabled":1,
                "configuration_scope":"Department",
                "department":department
            },
            fields= ["name","version","modified"],
            order_by = "modified desc",
            limit_page_length = 1
        )
        if configs:
            return frappe.get_doc(
                "WorkPulse App Configuration",
                configs[0].name
            )

    if company:
        configs = frappe.get_all(
            "WorkPulse App Configuration",
            filters = {
                "enabled":1,
                "configuration_scope":"Company",
                "Company":company
            },
            fields = ["name","version","modified"],
            order_by = "modified desc",
            limit_page_length = 1
        )
        if configs:
            return frappe.get_doc(
                "WorkPulse App Configuration",
                configs[0].name
            )
    
    roles = frappe.get_roles(user)

    if roles:
        configs = frappe.get_all(
            "WorkPulse App Configuration",
            filters=[
                ["enabled", "=", 1],
                ["configuration_scope", "=", "Role"],
                ["role", "in", roles]
            ],
            fields = ["name","version","modified"],
            order_by = "modified desc",
            limit_page_length = 1
        )

        if configs:
            return frappe.get_doc(
                "WorkPulse App Configuration",
                configs[0].name
            )

    configs = frappe.get_all(
            "WorkPulse App Configuration",
            filters = {
                "enabled":1,
                "configuration_scope" :"Global",
                "default_configuration":1
            },
            fields = ["name","version","modified"],
            order_by = "modified desc",
            limit_page_length = 1
        )   

    if configs:
            return frappe.get_doc(
                "WorkPulse App Configuration",
                configs[0].name
            )

    configs = frappe.get_all(
            "WorkPulse App Configuration",
            filters = {
                "enabled":1,
                "configuration_scope" :"Global"
                
            },
            fields = ["name","version","modified"],
            order_by = "modified desc",
            limit_page_length = 1
        )   

    if configs:
            return frappe.get_doc(
                "WorkPulse App Configuration",
                configs[0].name
            )

    return None
        
    