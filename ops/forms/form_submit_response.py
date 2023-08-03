from fastapi.responses import HTMLResponse


def get_form_submit_response(text):

    html_content = f'''
        <head>
            <title>Response Received</title>
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.3.1/dist/css/bootstrap.min.css" integrity="sha384-ggOyR0iXCbMQv3Xipma34MD+dH/1fQ784/j6cY/iJTQUOhcWr7x9JvoRxT2MZw1T" crossorigin="anonymous">
        </head>
        <div class="alert alert-info" role="alert">
            {text}
        </div>
    '''

    return HTMLResponse(content=html_content, status_code=200)
