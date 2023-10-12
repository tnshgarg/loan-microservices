from dal.models.employer import Employer


def get_employer_ewa_type(employer_id):
    employer_find_res = Employer.find_one({"_id": employer_id})
    employer_ewa_type = employer_find_res.get(
        "ewaType", Employer.EwaType.AUTO_DEDUCTION)

    return employer_ewa_type
