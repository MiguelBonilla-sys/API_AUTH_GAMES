"""
Endpoint alternativo para Scalar con configuración correcta.
"""

from fastapi.responses import HTMLResponse

def get_scalar_html(app_name: str, openapi_url: str) -> str:
    """
    Generar HTML correcto para Scalar.
    """
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{app_name} - Scalar Documentation</title>
        <meta charset="utf-8"/>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link rel="stylesheet" type="text/css" href="https://cdn.jsdelivr.net/npm/@scalar/api-reference@1.2.0/dist/browser/standalone.css" />
    </head>
    <body>
        <script 
            id="api-reference" 
            type="application/json"
            data-configuration='{{
                "theme": "purple",
                "layout": "modern",
                "showSidebar": true,
                "hideDownloadButton": false,
                "hideTryItPanel": false,
                "hideSchemaPattern": false,
                "hideSearch": false,
                "hideInfo": false,
                "hideServers": false,
                "hideModels": false,
                "hideAuthentication": false,
                "hideRequestSample": false,
                "hideResponseSample": false
            }}'
        ></script>
        <script src="https://cdn.jsdelivr.net/npm/@scalar/api-reference@1.2.0/dist/browser/standalone.js"></script>
    </body>
    </html>
    """
