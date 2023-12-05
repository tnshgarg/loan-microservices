
from bson import ObjectId
from dal.models.db_manager import DBManager
from services.ewa.apollo.document_handling.loan_agreement_service import ApolloLoanAgreementService

LOAN_APPLICATION_DOC = {
    "_id": ObjectId("652d30666f6a8969a059d74e"),
    "unipeEmployeeId": ObjectId("652d30282a156d21e23c8fb7"),
    "provider": "apollo",
    "creditLimit": 10000,
    "creditUtilization": 0,
    "year": 2023,
    "month": 10,
    "asset": None,
    "data": {
        "partnerLoanId": "0564648",
        "bureauFetchDetails": {
            "application_details": {
                "partner_loan_id": "0564648",
                "S3 Key": "UEC/0564648/parsed_crif.json"
            },
            "apollo_score": "5",
            "phone": {
                "Has the phone number been verified before?": "Yes"
            },
            "email": {
                "Does the email belong to the borrower?": "No"
            },
            "address": {
                "Has the address been verified bunipe_employee_idefore?": "No"
            },
            "accounts_summary": {
                "INQUIRIES-IN-LAST-SIX-MONTHS": "0",
                "LENGTH-OF-CREDIT-HISTORY-YEAR": "6",
                "LENGTH-OF-CREDIT-HISTORY-MONTH": "6",
                "AVERAGE-ACCOUNT-AGE-YEAR": "3",
                "AVERAGE-ACCOUNT-AGE-MONTH": "3",
                "NEW-ACCOUNTS-IN-LAST-SIX-MONTHS": "0",
                "NEW-DELINQ-ACCOUNT-IN-LAST-SIX-MONTHS": "0"
            },
            "primary_account_summary": {
                "Microfinance Others": {
                    "number_of_active_accounts": 2,
                    "number_of_inactive_accounts": 0,
                    "highest_sanctioned_limit": 600000,
                    "lowest_sanctioned_limit": 600000
                },
                "Consumer Loan": {
                    "number_of_active_accounts": 2,
                    "number_of_inactive_accounts": 0,
                    "highest_sanctioned_limit": 600000,
                    "lowest_sanctioned_limit": 200000
                },
                "primary_numer_of_overdue_accounts": "0",
                "primary_numer_of_secured_accounts": "0",
                "primary_numer_of_unsecured_accounts": "4",
                "primary_numer_of_untagged_accounts": "0"
            },
            "secondary_account_summary": {
                "secondary_numer_of_overdue_accounts": "0",
                "secondary_numer_of_secured_accounts": "0",
                "secondary_numer_of_unsecured_accounts": "0",
                "secondary_numer_of_untagged_accounts": "0"
            },
            "enquiries": {
                "Total Enquiries made in last 12 months": 0
            },
            "repayments": {
                "No. Repayments made within 0 days": 45,
                "No. of repayments made within 1-15 days": 0,
                "No. of repayments made within 16-30 days": 0,
                "No. of repayments made within 31-60 days": 0,
                "No. of repayments made within 61-90 days": 0,
                "No. of repayments made after 90 days": 0,
                "No. of repayments not reported i.e XXX": 99
            }
        },
        "documentUrls": {
            "loc": {
                "selfie": "UEC/ML/TEST007/selfie.jpg",
                "pan_uidai_xml": "UEC/ML/TEST007/poi.json",
                "salary_slip": "UEC/ML/TEST007/salary_slip1.pdf",
                "aadhar_uidai_xml": "UEC/ML/TEST007/aadhar_uidai_xml.zip",
                "crif": "UEC/TEST007/parsed_crif.json",
                "liveliness_output": "UEC/ML/TEST007/salary_slip1.pdf"
            }
        },
        "loanDocumentsUploaded": True,
        "payloads": {
            "loc": {
                "action": "create",
                "document_urls": {
                    "selfie": "UEC/ML/TEST007/selfie.jpg",
                    "pan_uidai_xml": "UEC/ML/TEST007/poi.json",
                    "salary_slip": "UEC/ML/TEST007/salary_slip1.pdf",
                    "aadhar_uidai_xml": "UEC/ML/TEST007/aadhar_uidai_xml.zip",
                    "crif": "UEC/TEST007/parsed_crif.json",
                    "liveliness_output": "UEC/ML/TEST007/salary_slip1.pdf"
                },
                "loan_type": "ML",
                "partner_loan_id": "0564648",
                "customer_information": {
                    "customer_id": "652d30282a156d21e23c8fb7",
                    "first_name": "REKHA",
                    "last_name": "DEVI",
                    "fathers_name": "RAMESHKUMAR",
                    "gender": "female",
                    "date_of_birth": "14/02/1978",
                    "aadhar_number": "123412341234",
                    "aadhar_uidai_xml_password": "1234",
                    "phone": "6688493648",
                    "email": "you@you.com",
                    "marital_status": "unmarried",
                    "pan": "HLPPE3069Z",
                    "address_type": "permanent",
                    "residence_type": "owned",
                    "address": "HNO 2043 7 13 QUATER PAHAD GANJ Q UATER AJMER 305001 AJMER AJMER 305001 RJ",
                    "city": "Pune",
                    "address_state": "Maharashtra",
                    "pincode": "411047",
                    "monthly_income": 12345,
                    "occupation": "employed",
                    "employee_id": "EMPTEST12345",
                    "designation": "Delivery Associate",
                    "employer_name": "ABC",
                    "employer_state": "Uttar Pradesh",
                    "agency_name": "ABC",
                    "agency_state": "Uttar Pradesh",
                    "date_of_joining": "10/08/2022",
                    "pay_cycle": "Monthly",
                    "customer_bank_account_name": "Rekha Devi",
                    "customer_bank_name": "TEST Bank",
                    "bank_account_number": "50501010789",
                    "ifsc_code": "HDFC0078910",
                    "bank_account_type": "savings"
                },
                "loan_information": {
                    "loan_amount": 10000,
                    "loan_tenure_in_days": "365",
                    "tenure": 1,
                    "interest_type": "reducing",
                    "interest_rate": 0,
                    "partner_computed_interest_amount": 0,
                    "partner_computed_emi_amount": 10000,
                    "fees": {
                        "processing_fee": {
                            "fee_amount": 10,
                            "gst_amount": 2
                        }
                    },
                    "partner_computed_disbursement_amount": 9988,
                    "disbursement_date": "16/10/2023",
                    "emi_frequency": "custom",
                    "first_emi_date": "15/10/2024",
                    "partner_computed_pre-emi_amount": 0,
                    "non_mf_criteria": True
                },
                "partner_tag": "UEC"
            }
        }
    }

}


def test_apollo_loan_agreement_generation():
    DBManager.init(stage="dev")
    ApolloLoanAgreementService(
        LOAN_APPLICATION_DOC
    ).generate_document()
