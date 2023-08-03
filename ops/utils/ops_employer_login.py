from dal.models.ops_employer_login import OpsEmployerLogins


def get_ops_employer_login_info(employer_id):
    # fetch ops_employer_login_info from db
    ops_employer_login_info = OpsEmployerLogins.find_one(
        {"employer_id": employer_id}, {"_id": 0})

    return ops_employer_login_info
