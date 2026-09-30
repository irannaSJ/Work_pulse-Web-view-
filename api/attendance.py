import frappe
from frappe.utils import get_datetime, now_datetime

from hrms_customization.api.permissions import get_logged_in_employee





def create_employee_checkin(
    employee,
    log_type,
    punch_time = None,
    device_id = None,
    latitude = None,
    longitude = None,
):
    doc = frappe.new_doc("Employee Checkin")
    doc.employee = employee
    doc.time = get_datetime(punch_time) if punch_time else now_datetime()
    doc.log_type = log_type
    doc.device_id = device_id
    doc.latitude = latitude
    doc.longitude = longitude

    doc.insert(ignore_permissions = True)
    return doc


@frappe.whitelist(methods=["POST"])
def punch_in(
    punch_time=None,
    device_id=None,
    latitude=None,
    longitude=None,
):

    employee = get_logged_in_employee()

    doc = create_employee_checkin(
        employee = employee,
        log_type = "IN",
        punch_time = punch_time,
        device_id = device_id,
        latitude = latitude,
        longitude = longitude
    )

    return {
        "success": True,
        "checkin":{
            "name":doc.name,
            "employee":doc.employee,
            "time":str(doc.time),
            "log_type":doc.log_type
        },
    }



@frappe.whitelist(methods = ["POST"])
def punch_out(
    punch_time = None,
    device_id = None,
    latitude = None,
    longitude = None
):
    employee = get_logged_in_employee

    doc = create_employee_checkin(
        employee = employee,
        log_type = "OUT",
        punch_time = punch_time,
        device_id = device_id,
        latitude = latitude,
        longitude = longitude,
    )
    return {
        "success":True,
        "checkin":{
            "name":doc.name,
            "employee":doc.employee,
            "time":str(doc.time),
            "log_type":doc.log_type
        }
    }