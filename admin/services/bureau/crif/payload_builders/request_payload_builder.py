from collections import defaultdict
from datetime import datetime

from dict2xml import dict2xml

from admin.services.bureau.crif.constants import (ActivityClass, AddressType,
                                                  IDType, IndividualEntityType,
                                                  InquiryNumber,
                                                  LegalConstitution, LoanType,
                                                  PhoneNumberType,
                                                  RequestActionType,
                                                  StateCodes, TestFlag)


class RequestPayloadBuilder:
    def __init__(self, stage) -> None:
        self.stage = stage
        self.payload = defaultdict(lambda: defaultdict(dict))

    def _add_header(self):
        member_id = "XXX"  # TODO : fetch
        member_name = "XXX"  # TODO : fetch
        inquiry_date_time = datetime.now().strftime("%d-%m-%Y")
        test_flag = TestFlag(self.stage).test_flag
        user_id = "XXX"  # TODO : fetch
        password = "XXX"  # TODO : fetch

        self.payload["HEADER-SEGMENT"] = {
            "PRODUCT-TYP": "COMM_ACE_PLUS_REPORT",
            "PRODUCT-VER": "4.0",
            "REQ-MBR": member_id,
            "SUB-MBR-ID": member_name,
            "INQ-DT-TM": inquiry_date_time,
            "REQ-VOL-TYP": "INDV",
            "REQ-ACTN-TYP": RequestActionType.CREATE_NEW_REQUEST,
            "TEST-FLG": test_flag,
            "USER-ID": user_id,
            "PWD": password,
            "AUTH-FLG": "Y",
            "AUTH-TITLE": "USER",
            "RES-FRMT": "XML",
            "MEMBER-PRE-OVERRIDE": "N",
            "RES-FRMT-EMBD": "N",
            "COMMERCIAL": {
                "CIR": "TRUE",
                "SCORE": "TRUE"
            },
            "CONSUMER": {
                "CIR": "TRUE",
                "SCORE": "TRUE"
            }
        }

    def _add_company_details(self):
        borrower_name = "SMINGIL"  # TODO : fetch
        legal_constitution = LegalConstitution.BUSINESS_ENTITIES_CREATED_BY_STATUTE  # TODO : fetch
        pan = "HNVCL2321H"  # TODO : fetch
        class_of_activity = ActivityClass.OTHER_COMMUNITY  # TODO : fetch
        mobile = "5663489474"  # TODO : fetch
        address_line = "D NO 1-68-28/1 PLOT NO 39 SECTOR 3 M V P COLONY"  # TODO : fetch
        city = "VISAKHAPATNAM"  # TODO : fetch
        state = StateCodes.STATE_CODE_MAP["Andhra Pradesh"]  # TODO : fetch
        pincode = "530017"  # TODO : fetch

        self.payload["INQUIRY"]["COMM-APPLICANT-SEGMENT"] = {
            "BORROWER-NAME": borrower_name,
            "LEGAL-CONSTITUTION": legal_constitution,
            "IDS": {
                "ID": {
                    "TYPE": IDType.PAN,
                    "VALUE": pan
                }
            },
            "CLASS-OF-ACTIVITY-1": class_of_activity,
            "PHONES": {
                "PHONE": {
                    "TELE-NO": mobile,
                    "TELE-NO-TYPE": PhoneNumberType.RESIDENCE
                }
            }
        }
        self.payload["INQUIRY"]["COMM-ADDRESS-SEGMENT"] = {
            "ADDRESS": {
                "TYPE": AddressType.RESIDENCE,
                "ADDRESS-LINE": address_line,
                "CITY": city,
                "STATE": state,
                "PIN": pincode
            }
        }

    def _add_application_details(self):
        inquiry_unique_reference_number = InquiryNumber().unique_reference_number
        loan_purpose_description = "Personal Loan"  # TODO : fetch
        credit_report_id = "CRDRQINQR"  # TODO : fetch
        credit_transaction_date_time = datetime.now().strftime(
            "%d-%m-%Y %H:%M:%S")  # TODO : fetch
        member_id = "PRB0000027"  # TODO : fetch
        los_application_id = "0507RE2015003215"  # TODO : fetch
        loan_type = LoanType.OTHERS  # TODO : fetch
        loan_amount = 10000  # TODO : fetch

        self.payload["INQUIRY"]["APPLICATION-SEGMENT"] = {
            "INQUIRY-UNIQUE-REF-NO": inquiry_unique_reference_number,
            "CREDT-INQ-PURPS-TYP": "ACCT-ORIG",
            "CREDT-INQ-PURPS-TYP-DESC": loan_purpose_description,
            "CREDIT-INQUIRY-STAGE": "PRE-SCREEN",
            "CREDT-RPT-ID": credit_report_id,
            "CREDT-REQ-TYP": "INDV",
            "CREDT-RPT-TRN-DT-TM": credit_transaction_date_time,
            "MBR-ID": member_id,
            "LOS-APP-ID": los_application_id,
            "LOAN-TYPE": loan_type,
            "LOAN-AMOUNT": loan_amount
        }

    def _add_individual_entity_details(self):
        individual_entity_type = IndividualEntityType.DIRECTOR
        din = "HNVCL2321H"  # TODO : fetch
        applicant_name = "DIBYALATA SAIKIA"  # TODO : fetch
        dob = "15-08-1974"  # TODO : fetch
        pan = "HNVCL2321H"  # TODO : fetch
        mobile = "5663489474"  # TODO : fetch
        address_line = "W O NIKHIL SAIKIA VILL 15 NO JALONI GRANT AMRJYOTI GAON PO LILAPUR DIST DIBRUGARH 786602"  # TODO : fetch
        city = "DIBRUGARH"  # TODO : fetch
        state = StateCodes.STATE_CODE_MAP["Assam"]  # TODO : fetch
        pincode = "786602"  # TODO : fetch

        self.payload["INQUIRY"]["INDIVIDUAL-ENTITIES-SEGMENT"] = {
            "INDIVIDUAL-ENTITY": {
                "INDIVIDUAL-ENTITY-TYPE": individual_entity_type,
                "DIN": din,
                # TODO : check the following tag name
                "INDV-APPLICANT-SEGMENT": {
                    "APPLICANT-NAME": {
                        "NAME-1": applicant_name
                    },
                    "DOB": {
                        "DOB-DATE": dob
                    },
                    "IDS": {
                        "ID": {
                            "TYPE": IDType.PAN,
                            "VALUE": pan
                        }
                        # TODO : check how can add DIN ID key as well
                    },
                    "PHONES": {
                        "PHONE": {
                            "TELE-NO": mobile,
                            "TELE-NO-TYPE": PhoneNumberType.RESIDENCE
                        }
                    }
                },
                "INDV-ADDRESS-SEGMENT": {
                    "ADDRESS": {
                        "TYPE": AddressType.RESIDENCE,
                        "ADDRESS-LINE": address_line,
                        "CITY": city,
                        "STATE": state,
                        "PIN": pincode
                    }
                }
            }
        }

    def build_payload(self):
        self._add_header()
        self._add_company_details()
        self._add_application_details()
        self._add_individual_entity_details()
        xml_payload = dict2xml(
            self.payload, wrap="REQUEST-REQUEST-FILE", newlines=False)
        return xml_payload
