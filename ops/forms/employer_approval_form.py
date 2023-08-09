from fastapi.responses import HTMLResponse

from ops.utils.ops_employer_login import get_ops_employer_login_info
from ops.utils.urls import get_ops_microservice_url
from services.html_blocks_service import HTMLBlocksService


def get_employer_approval_form(employer_id):
    # get cognito details
    ops_employer_login_info = get_ops_employer_login_info(employer_id)
    html_blocks = HTMLBlocksService.compile_html_blocks(
        [
            ("Employer Information Received",
             ops_employer_login_info),
        ]
    )
    ops_employer_login_info_html_content = '\n'.join(html_blocks)

    ops_microservice_url = get_ops_microservice_url()

    html_content = f'''
        <head>
            <title>Employer Approval Form</title>
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.3.1/dist/css/bootstrap.min.css" integrity="sha384-ggOyR0iXCbMQv3Xipma34MD+dH/1fQ784/j6cY/iJTQUOhcWr7x9JvoRxT2MZw1T" crossorigin="anonymous">
        </head>
        <div class="col-md-6 offset-md-3 mt-5">
            <h1>Employer Approval Form</h1>
            <br>
            {ops_employer_login_info_html_content}
            <form accept-charset="UTF-8" action="{ops_microservice_url}/start-submit" method="POST" enctype="multipart/form-data" target="_blank">
                <div class="form-group">
                    <label for="notes">Notes</label>
                    <input type="text" name="notes" class="form-control" id="notes" placeholder="Enter notes" required="required">
                </div>
                <hr>
                <div class="form-group mt-3">
                    <label class="mr-2">Upload Agreement</label>
                    <input type="file" name="agreement" required="required">
                </div>
                <div class="form-group mt-3">
                    <label class="mr-2">Upload PAN</label>
                    <input type="file" name="pan" required="required">
                </div>
                <div class="form-group mt-3">
                    <label class="mr-2">Upload GST</label>
                    <input type="file" name="gst" required="required">
                </div>
                <hr>
                <input type="hidden" name="employer_id" value={employer_id}>
                <button type="submit" class="btn btn-primary">Send for Approval</button>
            </form>
        </div> 
    '''

    return HTMLResponse(content=html_content, status_code=200)
