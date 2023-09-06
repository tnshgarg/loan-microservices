
import json
import os

from services.otp.route_mobile.route_mobile_api import RouteMobileApi


class RouteMobileApiMock(RouteMobileApi):

    def merge_url(self, val):
        return val + "=" + self.params[val]

    def generate_otp(self, mobile_number: str):
        return self.parse_response_string(f'1701|91{mobile_number}:78df527d-4d9a-47dc-8fa4-4d6a13a9d341')

    def verify_otp(self, mobile_number: str, otp: str):
        res = self.parse_response_string('101', request_type="verify")
        if otp == "999999":
            res = self.parse_response_string('103', request_type="verify")
        if otp == "888888":
            res = self.parse_response_string('102', request_type="verify")
        res["response"]["phone"] = mobile_number
        return res
