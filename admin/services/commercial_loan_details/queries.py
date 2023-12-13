COMMERCIAL_LOANS_VIEW_DEFAULT_FILTERS = [
    {
        '$match': {
            'commercialLoanDetails': {
                '$exists': 1
            }
        }
    }
]

COMMERCIAL_LOANS_VIEW_AGGREGATE_PIPELINE = [
    {
        '$lookup': {
            'from': 'employees',
            'localField': 'commercialLoanDetails.promoters',
            'foreignField': '_id',
            'as': 'fetched_promoters'
        }
    },
    {
        '$lookup': {
            'from': 'bankAccounts',
            'localField': '_id',
            'foreignField': 'pId',
            'as': 'bankAccounts'
        }
    }, {
        '$addFields': {
            'disbursement_bank_account': {
                '$first': {
                    '$filter': {
                        'input': '$bankAccounts',
                        'as': 'bankAccount',
                        'cond': {
                            '$eq': [
                                '$$bankAccount.uType', 'employer-disbursement'
                            ]
                        }
                    }
                }
            }
        }
    }, {
        '$lookup': {
            'from': 'governmentIds',
            'localField': '_id',
            'foreignField': 'pId',
            'as': 'governmentIds'
        }
    }, {
        '$addFields': {
            'employerPan': {
                '$first': {
                    '$filter': {
                        'input': '$governmentIds',
                        'as': 'governmentId',
                        'cond': {
                            '$and': [
                                {
                                    '$eq': [
                                        '$$governmentId.type', 'pan'
                                    ]
                                }, {
                                    '$eq': [
                                        '$$governmentId.provider', 'karza'
                                    ]
                                }
                            ]
                        }
                    }
                }
            }
        }
    }, {
        '$project': {
            '_id': 1,
            'companyName': 1,
            'commercial_loan_details': {
                'annual_turn_over': '$commercialLoanDetails.annual_turn_over',
                'business_category': '$commercialLoanDetails.business_category',
                'industry_type': '$commercialLoanDetails.industry_type',
                'constitution': '$commercialLoanDetails.constitution'
            },
            'employer_address': {
                'address': '$commercialLoanDetails.address',
                'city': '$commercialLoanDetails.city',
                'state': '$commercialLoanDetails.state',
                'pin': '$commercialLoanDetails.pin'
            },
            'disbursement_bank_account': {
                'account_number': '$disbursement_bank_account.data.accountNumber',
                'ifsc': '$disbursement_bank_account.data.ifsc'
            },
            'employer_ids': {
                'pan_number': '$employerPan.number',
                'pan_status': '$employerPan.verifyStatus',
                'gst_number': '$commercialLoanDetails.gstNumber',
                'registration_number': '$commercialLoanDetails.companyRegistrationNumber',
                'udyam_number': '$commercialLoanDetails.udyam_registration_number',
                'duns_number': '$commercialLoanDetails.duns_number'
            },
            "promoters": "$fetched_promoters",
            "keyPromoter": "$commercialLoanDetails.keyPromoter",
            "government_ids": 1,
            "document_uploads": 1,
        }
    }
]
