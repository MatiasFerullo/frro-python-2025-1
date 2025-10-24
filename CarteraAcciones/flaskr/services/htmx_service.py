from flask import json, make_response

def htmx_redirect(url):
    resp = make_response("")
    resp.headers["HX-Redirect"] = url
    return resp

def htmx_show_error_trigger(error_msg):
    resp = make_response("", 400)
    resp.headers['HX-Trigger'] = json.dumps({"showError": error_msg})
    return resp