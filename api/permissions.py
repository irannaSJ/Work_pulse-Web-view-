import frappe
def get_logged_in_employee():
    employee = frappe.db.get_value(
        "Employee",
        {"user_id":frappe.session.user},
        "name"
    )

    if not employee:
        frappe.throw("No employee is linked to the current user")
    return employee