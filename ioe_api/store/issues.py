# -*- coding: utf-8 -*-
# Copyright (c) 2019, Dirk Chang and contributors
# For license information, please see license.txt
#
# Api for store.issues
#

from __future__ import unicode_literals
import frappe
from ioe_api.helper import valid_auth_code, throw


@frappe.whitelist(allow_guest=True)
def test():
	frappe.response.update({
		"ok": True,
		"data": "test_ok_result",
		"source": "store.issues.test"
	})


@frappe.whitelist(allow_guest=True)
def list():
	try:
		valid_auth_code()
		if not True:
			throw("has_no_permission")

		frappe.response.update({
			"ok": True,
		})
	except Exception as ex:
		frappe.response.update({
			"ok": False,
			"error": str(ex)
		})
