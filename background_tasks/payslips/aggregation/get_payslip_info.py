def get_payslip_aggregation_info(payslips):
    return [
        {"$match": {"_id": {"$in": payslips}}},
        {
            "$lookup": {
                "from": "employers",
                "localField": "employerId",
                "foreignField": "_id",
                "as": "employerDetails"
            }
        },
        {"$unwind": {"path": "$employerDetails"}},
        {
            "$lookup": {
                "from": "employees",
                "localField": "unipeEmployeeId",
                "foreignField": "_id",
                "as": "employeeDetails"
            }
        },
        {"$unwind": {"path": "$employeeDetails"}},
        {
            "$lookup": {
                "from": "attendance",
                "localField": "unipeEmployeeId",
                "foreignField": "unipeEmployeeId",
                "as": "attendanceDetails",
            },
        },
        {
            "$unwind": {
                "path": "$attendanceDetails",
            },
        },
        {
            '$lookup': {
                'from': 'employments',
                'localField': 'employmentId',
                'foreignField': '_id',
                'as': 'employmentDetails',
            },
        },
        {
            '$unwind': {
                'path': '$employmentDetails',
            },
        },
        {
            '$lookup': {
                'from': 'governmentIds',
                'localField': 'unipeEmployeeId',
                'foreignField': 'pId',
                'as': 'governmentIdData',
            },
        },
        {
            '$unwind': {
                'path': '$governmentIdData',
            },
        },
        {
            '$match': {
                'governmentIdData.type': 'pan',
            },
        },
        {
            '$limit': 1,
        },
        {
            "$project": {
                "header": {
                    "date": {
                        "$dateToString": {
                            "date": "$dateCredited"
                        }
                    },
                    "company_name": "$employerDetails.companyName",
                    "company_address": "$employerDetails.street"
                },
                "employee_details": {
                    "employee_name": "$employeeDetails.employeeName",
                    "employee_no": "$employerEmployeeId",
                    "date_joined": "$employmentDetails.doj",
                    "department": "$employmentDetails.department",
                    "sub_department": "$employmentDetails.department",
                    "designation": "$employmentDetails.designation",
                    "pan": "$governmentIdData.number",
                    "uan": "N/A"
                },
                "attendance_details": {
                    "actual_payable_days": {
                        "$toString": {
                            "$arrayElemAt": [
                                "$attendanceDetails.uploads.summary.totalPresentDays",
                                -1
                            ]
                        }
                    },
                    "total_working_days": {
                        "$toString": {
                            "$arrayElemAt": [
                                "$attendanceDetails.uploads.summary.totalWorkingDays",
                                -1
                            ]
                        }
                    },
                    "loss_of_pay_days": {
                        "$toString": {
                            "$arrayElemAt": [
                                "$attendanceDetails.uploads.summary.totalAbsentDays",
                                -1
                            ]
                        }
                    },
                    "days_payable": {
                        "$toString": {
                            "$arrayElemAt": [
                                "$attendanceDetails.uploads.summary.totalPresentDays",
                                -1
                            ]
                        }
                    },
                },

                "earnings": {
                    "basic": {
                        "$concat": [
                            "₹",
                            {"$toString": "$earnings.basicSalary"}
                        ]
                    },
                    "hra": {
                        "$concat": [
                            "₹",
                            {"$toString": "$earnings.hra"}
                        ]
                    },
                    "other_allowance": {
                        "$concat": [
                            "₹",
                            {"$toString": "$earnings.otherAllowance"}
                        ]
                    },
                    "total_earnings": {
                        "$concat": [
                            "₹",
                            {"$toString": "$earnings.totalEarnings"}
                        ]
                    }
                },
                "deductions": {
                    "tax_deducted": {"$toString": "$deductions.taxDeducted"},
                    "pf_contribution": {
                        "$concat": [
                            "₹",
                            {"$toString": "$deductions.pfContribution"}
                        ]
                    },
                    "professional_tax": {
                        "$concat": [
                            "₹",
                            {"$toString": "$deductions.professionalTax"}
                        ]
                    },
                    "other_deductions": {"$toString": "$deductions.otherDeductions"},
                    "total_deductions": {
                        "$concat": [
                            "₹",
                            {"$toString": "$deductions.totalDeductions"}
                        ]
                    }
                },
                "final": {
                    "net_pay": {
                        "$concat": [
                            "₹",
                            {"$toString": "$netPay.netPayPostTax"}
                        ]
                    }
                },
                "employment_details": {
                    "employment_id": {
                        "$toString": "$employmentDetails._id"
                    }
                }
            }
        }
    ]


attendance_details = {
    "attendance_details": {
        "actual_payable_days": {
            "$toString": {
                "$arrayElemAt": [
                    "$attendanceDetails.uploads.summary.totalWorkingDays",
                    -1
                ]
            }
        },
        "total_working_days": {
            "$toString": {
                "$arrayElemAt": [
                    "$attendanceDetails.uploads.summary.totalWorkingDays",
                    -1
                ]
            }
        },
        "loss_of_pays_data": {
            "$toString": {
                "$arrayElemAt": [
                    "$attendanceDetails.uploads.summary.totalWorkingDays",
                    -1
                ]
            }
        },
        "days_payable": {
            "$toString": {
                "$arrayElemAt": [
                    "$attendanceDetails.uploads.summary.totalWorkingDays",
                    -1
                ]
            }
        },
    },
}
