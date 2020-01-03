
from __future__ import unicode_literals
import frappe
import base64
from frappe import _
from hmac import new as hmac
from time import sleep, time
from urllib.parse import quote, unquote
from hashlib import sha1
from frappe import throw
from frappe.sessions import get_expiry_in_seconds


# Copy from frappe.sessions
#
def get_session_data_from_cache(sid):
	data = frappe.cache().hget("session", sid)
	if data:
		data = frappe._dict(data)
		session_data = data.get("data", {})

		# set user for correct timezone
		time_diff = frappe.utils.time_diff_in_seconds(frappe.utils.now(),
		                                              session_data.get("last_updated"))
		expiry = get_expiry_in_seconds(session_data.get("session_expiry"))

		if time_diff > expiry:
			data = None

	return data and data.data


def hash_hmac(ac_key, text):
	return base64.b64encode(hmac(ac_key, text, sha1).digest())


def get_signature(appid, appkey, user, sid, conf, version, version_new):
	contents = "_w_appid=" + appid + "_w_conf_name=" + conf + "_w_tokentype=1_w_secretkey=" + appkey
	b64 = hash_hmac(appkey.encode(), contents.encode()).decode()
	new = '_w_appid=' + appid + '&_w_conf_name=' + conf +  '&_w_tokentype=1&_w_signature=' + quote(b64) + \
	      "&conf_version=" + version + "&conf_version_new=" + version_new + "&userid=" + user + "&sid=" + sid
	return 'https://wwo.wps.cn/office/s/' + str(int(time())) + '?' + new


def valid_weboffice_token(user, sid, token=None):
	if 'Guest' != frappe.session.user:
		return
	token = token or frappe.get_request_header("x-wps-weboffice-token")

	frappe.logger(__name__).debug(_("WPS Auth user {0} sid {1} token {2}").format(user, sid, token))

	if not sid or not token:
		throw("token_information_missing")

	session_data = get_session_data_from_cache(sid)

	if session_data.user != user:
		throw("user_sid_mismatch")

	if session_data.csrf_token != token:
		throw("token_auth_failure")

	# form dict keeping
	form_dict = frappe.local.form_dict
	frappe.set_user(user)
	frappe.local.form_dict = form_dict
