from admin.services.offers.queries import EMPLOYEE_DETAILS_FOR_OFFER_PIPELINE
from dal.models.employees import Employee
from starlette_admin.exceptions import StarletteAdminException
from datetime import datetime
from dal.models.offer import Offers


def deprecate_previous_live_offer(unipe_employee_id, due_date, loan_type):
    filter_ = {
        "unipeEmployeeId": unipe_employee_id,
        "live": True,
        "loanType": {"$in": [loan_type, None]},
        "dueDate": {"$lt": due_date},
    }
    previous_live_offer = Offers.find_one(filter_)

    if previous_live_offer:
        update_ = {
            "$set": {
                "live": False,
            }
        }
        Offers.update_one(filter_, update_)

    if previous_live_offer:
        return previous_live_offer['_id']
    return None


def create_or_update_offer(unipe_employee_id, year, month, limit_amount, eligible_amount, employer_id, employment_id, fees, due_date, loan_provider, loan_type):
    filter_ = {
        "unipeEmployeeId": unipe_employee_id,
        "year": year,
        "month": month,
        "dueDate": due_date
    }

    offer = {
        "live": True,
        "availed": False,
        "availedAt": None,
        "disbursed": False,
        "limitAmount": limit_amount,
        "eligibleAmount": eligible_amount,
        "employerId": employer_id,
        "employmentId": employment_id,
        "fees": fees,
        "loanAmount": 0,
        "paid": False,
        "stage": None,
        "provider": loan_provider,
        "loanType": loan_type
    }

    existing_offer = Offers.find_one(filter_, sort=[('_id', -1)])
    if not existing_offer:
        offer_insert_res = Offers.insert_one(filter_ | offer)
        print(f'offer_insert_res: {offer_insert_res.inserted_id}')
        return offer_insert_res, offer_insert_res.inserted_id
    elif not existing_offer.get("availed", False):
        filter_["_id"] = existing_offer["_id"]
        if (existing_offer["limitAmount"] - existing_offer["eligibleAmount"]) < limit_amount:
            offer["eligibleAmount"] = existing_offer["eligibleAmount"] + \
                (limit_amount - existing_offer["limitAmount"])
            offer_update_res = Offers.update_one(filter_, {"$set": offer})
            print(
                f'offer_update_res.acknowledged: {offer_update_res.acknowledged}')
            return offer_update_res, existing_offer["_id"]
        elif existing_offer["live"]:
            offer_update_res = Offers.update_one(
                filter_, {"$set": {"live": False}})
            return offer_update_res, existing_offer["_id"]


def create_offer(unipe_employee_id, due_date, limit_amount, eligible_amount, fees, employer_id, loan_type, loan_provider, year, month):
    employees_cur = Employee.aggregate([{
        "$match": {
            "_id": unipe_employee_id
        }
    }] + EMPLOYEE_DETAILS_FOR_OFFER_PIPELINE)

    employee = None
    for emp in employees_cur:
        employee = emp
        break
    if employee is None:
        raise StarletteAdminException("No Employee Found in DB")

    employment = employee.get("employment", None)

    if employment is None or not employment.get("active", False):
        raise StarletteAdminException("Employment is not active")

    previous_live_id = deprecate_previous_live_offer(
        unipe_employee_id,
        due_date,
        loan_type
    )

    create_or_update_offer_res, updated_offer_id = create_or_update_offer(
        unipe_employee_id, year, month, limit_amount, eligible_amount, employer_id, employment[
            "_id"], fees, due_date, loan_provider, loan_type

    )
