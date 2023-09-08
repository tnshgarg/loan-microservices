import abc
from datetime import datetime, timedelta

import jwt
from dal.models.employees import Employee

from .payloads import MobileGenerateOtpPayload, MobileVerifyOtpPayload


class MobileVerificationService(abc.ABC):
    """
    Interface to be used for creating payment services
    """

    @classmethod
    def __subclasshook__(cls, subclass):
        return (hasattr(subclass, 'generate_otp') and
                callable(subclass.generate_otp) and
                hasattr(subclass, 'verify_otp') and
                callable(subclass.verify_otp)) or NotImplemented

    @abc.abstractmethod
    def generate_otp(self, payload: MobileGenerateOtpPayload):
        """generate aadhaar otp for a user"""
        raise NotImplementedError

    @abc.abstractmethod
    def verify_otp(self, payload: MobileVerifyOtpPayload, secret):
        """submit aadhaar otp received on registered mobile for a user"""
        raise NotImplementedError

    def is_mobile_registered(self, mobile_number):
        employee = Employee.find_one({"mobile": mobile_number})
        if employee is None:
            return False
        return True

    def generate_jwt_token(self, mobile_number, secret):
        employee = Employee.find_one({"mobile": mobile_number})
        if employee is None:
            return None, None
        employee_details = {
            "unipeEmployeeId": employee["_id"],
            "name": employee.get("employeeName"),
            "verified": employee.get("verified"),
            "onboarded": employee.get("onboarded")
        }
        payload = {
            "unipeEmployeeId": str(employee["_id"]),
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(days=3)
        }
        token = jwt.encode(
            payload, secret, algorithm="HS256")
        return token, employee_details
