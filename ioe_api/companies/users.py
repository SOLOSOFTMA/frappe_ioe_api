# -*- coding: utf-8 -*-
# Copyright (c) 2019, Dirk Chang and contributors
# For license information, please see license.txt
#
# Api for companies.users
#

from __future__ import unicode_literals
import frappe
from ioe_api.helper import valid_auth_code, get_post_json_data, throw, get_doc_as_dict, update_doc


@frappe.whitelist(allow_guest=True)
def test():
	frappe.response.update({
		"ok": True,
		"data": "test_ok_result",
		"source": "companies.users.test"
	})


@frappe.whitelist(allow_guest=True)
def create():
	try:
		valid_auth_code()
		data = get_post_json_data()

		if 'Company Admin' not in frappe.get_roles():
			throw("only_admin_can_create_employee")

		if not data.get("email"):
			throw("email_missing")
		if not data.get("company"):
			throw("company_id_missing")
		if not data.get("first_name"):
			throw("first_name_missing")
		if not data.get("last_name"):
			throw("last_name_missing")
		if not data.get("mobile_no"):
			throw("mobile_no_missing")
		if not data.get("new_password"):
			throw("new_password_missing")

		data.update({
			"doctype": "User",
			"language": "zh",
			"enabled": 1,
			"send_welcome_email": 0
		})
		doc = frappe.get_doc(data).insert(ignore_permissions=True)

		frappe.response.update({
			"ok": True,
			"data": doc.name
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": str(ex)
		})


@frappe.whitelist(allow_guest=True)
def read(name):
	try:
		valid_auth_code()

		frappe.response.update({
			"ok": True,
			"data": get_doc_as_dict("User", name)
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": str(ex)
		})


@frappe.whitelist(allow_guest=True)
def update(name, first_name, last_name, mobile_no, new_password=None, enabled=1):
	try:
		valid_auth_code()
		if 'Company Admin' not in frappe.get_roles():
			throw("only_admin_can_update_group")
		company = frappe.get_value("Cloud Employee", name, "company")
		if not company:
			throw("user_is_not_an_employee")
		if frappe.get_value("Cloud Company", company, "admin") != frappe.session.user:
			throw("user_is_not_in_your_company")

		user = frappe.get_doc("User", name)
		user.update({
			"send_welcome_email": 0,
			"first_name": first_name,
			"last_name": last_name,
			"mobile_no": mobile_no,
			"enabled": enabled
		})
		if new_password is not None:
			user.update({"new_password": new_password})

		user.save(ignore_permissions=True)

		frappe.response.update({
			"ok": True,
			"message": "company_group_updated"
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": str(ex)
		})
