import re
import requests
import PyExecJS
import xml.etree.ElementTree as ET
from typing import Dict, Any, Optional
from ..models import RequestModel, Environment

VAR_PATTERN = re.compile(r"\{\{\s*(.*?)\s*\}\}")


def substitute_vars(text: str, variables: Dict[str, str]) -> str:
    if not text:
        return text
    def repl(match):
        key = match.group(1)
        return variables.get(key, match.group(0))
    return VAR_PATTERN.sub(repl, text)


def run_js(script: str, context: Dict[str, Any]) -> Dict[str, Any]:
    if not script.strip():
        return context
    # Provide a tiny PM-like API
    env_store = context.get('env', {})
    request_ctx = context.get('request', {})
    response_ctx = context.get('response', {})

    js_prelude = f"""
    var pm = {{
      environment: {{
        get: function(k) {{ return env[k] || ''; }},
        set: function(k, v) {{ env[k] = String(v); }}
      }},
      request: {request_ctx},
      response: {response_ctx}
    }};
    """
    try:
        ctx = PyExecJS.compile(js_prelude + "\n" + script + "\n; env;")
        result = ctx.eval("env")
        return {**context, 'env': result or env_store}
    except Exception:
        return {**context, 'env': env_store}


def send_http_request(req: RequestModel, env: Optional[Environment]):
    variables = {}
    if env:
        for v in env.variables:
            variables[v.key] = v.value

    # Pre-request substitutions
    url = substitute_vars(req.url, variables)
    headers = {k: substitute_vars(str(v), variables) for k, v in (req.headers or {}).items()}
    body = substitute_vars(req.body or '', variables)

    # Run pre-request script
    ctx = {'env': variables, 'request': {'url': url, 'method': req.method, 'headers': headers, 'body': body}}
    ctx = run_js(req.pre_script or '', ctx)
    variables = ctx['env']
    url = ctx['request']['url'] if 'request' in ctx else url

    data = None
    json_payload = None
    
    if req.payload_type == 'xml':
        # For XML, send as raw data with proper encoding
        data = body.encode('utf-8') if body else None
        # Ensure XML content type if not already set
        if 'content-type' not in [k.lower() for k in headers.keys()]:
            headers['Content-Type'] = 'application/xml'
    elif req.payload_type == 'form':
        # For form data, parse as form fields
        if body.strip():
            try:
                # Parse form data from body (key=value&key2=value2 format)
                form_data = {}
                for pair in body.split('&'):
                    if '=' in pair:
                        key, value = pair.split('=', 1)
                        form_data[key] = value
                data = form_data
            except Exception:
                data = body
        # Ensure form content type if not already set
        if 'content-type' not in [k.lower() for k in headers.keys()]:
            headers['Content-Type'] = 'application/x-www-form-urlencoded'
    elif req.payload_type == 'text':
        # For plain text
        data = body.encode('utf-8') if body else None
        if 'content-type' not in [k.lower() for k in headers.keys()]:
            headers['Content-Type'] = 'text/plain'
    else:
        # Default JSON handling
        if body.strip():
            try:
                json_payload = requests.utils.json.loads(body)
            except Exception:
                # If JSON parsing fails, send as raw data
                data = body
        # Ensure JSON content type if not already set and we have JSON payload
        if json_payload and 'content-type' not in [k.lower() for k in headers.keys()]:
            headers['Content-Type'] = 'application/json'

    try:
        resp = requests.request(req.method, url, headers=headers, json=json_payload, data=data, timeout=20)
        content_type = resp.headers.get('content-type', '')
        try:
            parsed = resp.json()
        except Exception:
            parsed = resp.text

        # Post-request script context
        post_ctx = {
            'env': variables,
            'request': {'url': url, 'method': req.method},
            'response': {
                'status': resp.status_code,
                'headers': dict(resp.headers),
                'json': parsed if not isinstance(parsed, str) else None,
                'text': parsed if isinstance(parsed, str) else None
            }
        }
        post_ctx = run_js(req.post_script or '', post_ctx)
        variables = post_ctx['env']

        return {
            'ok': True,
            'status': resp.status_code,
            'headers': dict(resp.headers),
            'data': parsed,
            'env': variables
        }
    except Exception as e:
        return {'ok': False, 'error': str(e)}
