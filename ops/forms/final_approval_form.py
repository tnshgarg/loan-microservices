from fastapi.responses import HTMLResponse

from ops.utils.ops_employer_login import \
    get_all_pending_ops_employer_login_info
from ops.utils.urls import get_ops_microservice_url
from services.comms.html_blocks_service import HTMLBlocksService


def get_single_approval_form(ops_employer_login_info, ops_microservice_url):
    employer_id = ops_employer_login_info["employer_id"]
    html_blocks = HTMLBlocksService.compile_html_blocks(
        [
            ("Employer Information Received",
             ops_employer_login_info),
        ]
    )
    ops_employer_login_info_html_content = '\n'.join(html_blocks)

    html_content = f'''
            <br>
            {ops_employer_login_info_html_content}
            <form accept-charset="UTF-8" action="{ops_microservice_url}/approve-submit" method="POST" enctype="multipart/form-data" target="_blank">
                <div class="form-group">
                    <label for="notes">Select an action</label>
                    <br>
                    <div class="custom-control custom-radio custom-control-inline">
                        <input type="radio" id="approve_{employer_id}" name="approve_or_deny" value="approve" class="custom-control-input">
                        <label class="custom-control-label" for="approve_{employer_id}">Approve</label>
                    </div>
                    <div class="custom-control custom-radio custom-control-inline">
                        <input type="radio" id="deny_{employer_id}" name="approve_or_deny" value="deny" class="custom-control-input">
                        <label class="custom-control-label" for="deny_{employer_id}">Deny</label>
                    </div>
                </div>
                <hr>
                <input type="hidden" name="employer_id" value={employer_id}>
                <button type="submit" class="btn btn-primary">Submit</button>
            </form>
            <br>
    '''

    return html_content


def get_final_approval_form():
    # get cognito details
    all_pending_ops_employer_login_info = get_all_pending_ops_employer_login_info()
    ops_microservice_url = get_ops_microservice_url()

    approval_form_blocks = [
        get_single_approval_form(ops_employer_login_info, ops_microservice_url)
        for ops_employer_login_info in all_pending_ops_employer_login_info
    ]

    approval_forms_html_content = '\n'.join(approval_form_blocks)

    html_content = f'''
        <head>
            <title>Final Employer Approval</title>
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-EVSTQN3/azprG1Anm3QDgpJLIm9Nao0Yz1ztcQTwFspd3yD65VohhpuuCOmLASjC" crossorigin="anonymous">
            <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.0.2/dist/js/bootstrap.bundle.min.js" integrity="sha384-MrcW6ZMFYlzcLA8Nl+NtUVF0sA7MsXsP1UyJoMp4YLEuNSfAP+JcXn/tWtIaxVXM" crossorigin="anonymous"></script>
        </head>
        <div class="col-md-6 offset-md-3 mt-5">
            <h1>Final Employer Approval</h1>
            {approval_forms_html_content}
        </div> 
    '''

    return HTMLResponse(content=html_content, status_code=200)
