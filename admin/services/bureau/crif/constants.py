from dataclasses import dataclass
from datetime import datetime
from random import randint


class RequestActionType:
    CREATE_NEW_REQUEST = "SUBMIT"
    SEND_REPORT = "ISSUE"


@dataclass
class TestFlag:
    stage: str

    @property
    def test_flag(self):
        test_flag = None
        if self.stage in ["dev", "qa"]:
            test_flag = "HMTEST"
        else:
            test_flag = "HMLIVE"
        return test_flag


class LegalConstitution:
    PRIVATE_LIMITED = "11"
    PUBLIC_LIMITED = "12"
    BUSINESS_ENTITIES_CREATED_BY_STATUTE = "20"
    PROPRIETORSHIP = "30"
    PARTNERSHIP = "40"
    TRUST = "50"
    HINDU_UNDIVIDED_FAMILY = "55"
    CO_OPERATIVE_SOCIETY = "60"
    ASSOCIATION_OF_PERSONS = "70"
    GOVERNMENT = "80"
    NOT_CLASSIFIED = "99"


class IDType:
    PAN = "ID07"
    CIN = "ID08"
    DIN = "ID09"
    GSTIN = "ID10"
    CKYC = "ID13"
    UDYAM_REG_NO = "ID14"


class ActivityClass:
    AGRICULTURE_AND_FORESTRY = "AGRICULTURE AND FORESTRY"
    CONSTRUCTION = "CONSTRUCTION"
    EDUCATION = "EDUCATION"
    ELECTRICITY_GAS_WATER_SUPPLY = "ELECTRICITY, GAS AND WATER SUPPLY"
    FINANCIAL_INTERMEDIATION = "FINANCIAL INTERMEDIATION"
    FISHING = "FISHING"
    HEALTH_SOCIAL_WORK = "HEALTH AND SOCIAL WORK"
    HOTELS_RESTAURANTS = "HOTELS AND RESTAURANTS"
    MANUFACTURING = "MANUFACTURING"
    MINING_QUARRYING = "MINING AND QUARRYING"
    OTHER_COMMUNITY = "OTHER COMMUNITY, SOCIAL AND PERSONAL SERVICE ACTIVITIES"
    PUBLIC_ADMINISTRATION = "PUBLIC ADMINISTRATION AND DEFENCE; COMPULSORY SOCIAL SECURITY"
    REAL_ESTATE = "REAL ESTATE, RENTING AND BUSINESS ACTIVITIES"
    TRANSPORT_STORAGE_COMMUNICATIONS = "TRANSPORT, STORAGE AND COMMUNICATIONS"
    WHOLESALE_RETAIL_TRADE_MOTOR_VEHICLES_PERSONAL_HOUSEHOLD_GOODS = "WHOLESALE AND RETAIL TRADE; REPAIR OF MOTOR VEHICLES, MOTORCYCLES AND PERSONAL / HOUSEHOLD GOODS"


class PhoneNumberType:
    RESIDENCE = "P01"
    COMPANY = "P02"
    MOBILE = "P03"
    PERMANENT = "P04"
    FOREIGN = "P05"
    OTHER = "P07"
    UNTAGGED = "P08"


class AddressType:
    RESIDENCE = "D01"
    COMPANY = "D02"
    RESIDENCE_CUM_OFFICE = "D03"
    PERMANENT = "D04"
    CURRENT = "D05"
    FOREIGN = "D06"
    MILITARY = "D07"
    OTHER = "D08"


class StateCodes:
    STATE_CODE_MAP = {
        "Andhra Pradesh": "AP",
        "Arunachal Pradesh": "AR",
        "Assam": "AS",
        "Bihar": "BR",
        "Chhattisgarh": "CG",
        "Goa": "GA",
        "Gujarat": "GJ",
        "Haryana": "HR",
        "Himachal Pradesh": "HP",
        "Jammu & Kashmir": "JK",
        "Jharkhand": "JH",
        "Karnataka": "KA",
        "Kerala": "KL",
        "Madhya Pradesh": "MP",
        "Maharashtra": "MH",
        "Manipur": "MN",
        "Meghalaya": "ML",
        "Mizoram": "MZ",
        "Nagaland": "NL",
        "Orissa": "OR",
        "Punjab": "PB",
        "Rajasthan": "RJ",
        "Sikkim": "SK",
        "Tamil Nadu": "TN",
        "Telangana": "TS",
        "Tripura": "TR",
        "Uttarakhand": "UK",
        "Uttar Pradesh": "UP",
        "West Bengal": "WB",
        "Andaman & Nicobar": "AN",
        "Chandigarh": "CH",
        "Dadra and Nagar Haveli": "DN",
        "Daman & Diu": "DD",
        "Delhi": "DL",
        "Lakshadweep": "LD",
        "Pondicherry": "PY",
        "Dadra & Nagar Haveli And Daman & Diu": "DNHDD"
    }

# TODO : check for LOS number format - DDMMYYYYHHmmSSLOSAppIDXXXXXX


@dataclass
class InquiryNumber:
    @property
    def unique_reference_number(self):
        current_time = datetime.now()
        current_time_string = current_time.strftime("%d%m%Y%H%M%S")
        random_number_string = "{:06d}".format(randint(1, 1000000))
        return f"{current_time_string}{random_number_string}"


class LoanType:
    LOAN_AGAINST_CARDS_DEPOSITS_RECEIPTS_RECEIVABLES = "0006"
    CASH_CREDIT = "0100"
    OVERDRAFT = "0200"
    PACKING_CREDIT = "0500"
    EXPORT_BILLS_DISCOUNTED_PURCHASED_ADVANCED_AGAINST = "0630"
    TERM_LOANS = "0640"
    INLAND_BILLS_DISCOUNTED_PURCHASED = "0710"
    ADVANCED_AGAINST_EXPORT_CASH_INCENTIVES_IMPORT_BILLS = "0800"
    WORKING_CAPITAL_LOANS = "0801"
    FOREIGN_CURRENCY_CHEQUE_DD_TC = "0900"
    HIRE_PURCHASE_LEASE = "1100"
    BANK_GUARANTEE = "2000"
    LETTERS_OF_CREDIT = "3000"
    COMMERCIAL_VEHICLE_LOAN = "4000"
    OTHERS = "9999"
    MUDRA_TERM_LOAN = "9022"
    MUDRA_WORKING_CAPITAL = "9023"
    TEMPORARY_OVERDRAFT = "9024"


class IndividualEntityType:
    DIRECTOR = "54"
    EXECUTIVE_DIRECTOR = "07"
    INDEPENDENT_DIRECTOR = "53"
    NOMINEE_DIRECTOR = "52"
    OTHER = "60"
    PARTNER = "30"
    PROMOTER = "01"
    PROMOTER_DIRECTOR = "51"
    PROPRIETOR = "20"
    SHAREHOLDER = "10"
    TRUSTEE = "40"
    KARTA_HUF = "61"


class Gender:
    MALE = "G01"
    FEMAILE = "G02"
    THIRD_GENDER = "G03"
    UNKNOWN = "G05"


class MaritalStatus:
    UNMARRIED = "Unmarried"
    WIDOWED = "Widowed"
    MARRIED = "Married"
    SINGLE = "Single"
    SEPARATED = "Separated"
    LIVING_WITH_PARTNER = "Living with Partner"
    DIVORCED = "Divorced"


class RelationType:
    FATHER = "K01"
    HUSBAND = "K02"
    MOTHER = "K03"
    SON = "K04"
    DAUGHTER = "K05"
    WIFE = "K06"
    BROTHER = "K07"
    MOTHER_IN_LAW = "K08"
    FATHER_IN_LAW = "K09"
    DAUGHTER_IN_LAW = "K10"
    SISTER_IN_LAW = "K11"
    SON_IN_LAW = "K12"
    BROTHER_IN_LAW = "K12"
    OTHER = "K15"


class OrganisationEntityType:
    SUBSIDIARY_COMPANY = "01"
    HOLDING_COMPANY = "02"
    GROUP_COMPANY = "03"
    STANDALONE_COMPANY = "04"
    SHAREHOLDER = "05"
    OTHER = "06"
