from fastapi.responses import HTMLResponse

from ops.utils.ops_employer_login import get_ops_employer_login_info
from ops.utils.urls import get_ops_microservice_url
from services.comms.html_blocks_service import HTMLBlocksService


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
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-EVSTQN3/azprG1Anm3QDgpJLIm9Nao0Yz1ztcQTwFspd3yD65VohhpuuCOmLASjC" crossorigin="anonymous">
            <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/js/bootstrap.bundle.min.js" integrity="sha384-MrcW6ZMFYlzcLA8Nl+NtUVF0sA7MsXsP1UyJoMp4YLEuNSfAP+JcXn/tWtIaxVXM" crossorigin="anonymous"></script>
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
              <div class="row">
                <div class="col">
                    <label class="form-label" for="file-input-agreement">Upload Agreement</label>
                    <input class="form-control" type="file" name="agreement" required="required" id="file-input-agreement">
                </div>
                <div class="col">
                    <label class="form-label" for="file-input-pan">Upload PAN*</label>
                    <input class="form-control" type="file" name="pan" required="required" id="file-input-pan">
                </div>
                <div class="col">
                    <label class="form-label" for="file-input-gst">Upload GST</label>
                    <input class="form-control" type="file" name="gst" required="required" id="file-input-gst">
                </div>
                </div>
                <hr>
                <input type="hidden" name="employer_id" value={employer_id}>
                <button type="submit" class="btn btn-primary">Send for Approval</button>
            </form>
        </div> 
    '''

    return HTMLResponse(content=html_content, status_code=200)
