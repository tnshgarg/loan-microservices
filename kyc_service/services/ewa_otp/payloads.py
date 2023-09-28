from dataclasses import dataclass


@dataclass
class MobileGenerateOtpPayload:
    mandatory = ["mobileNumber"]
    optional = []

    mobile_number: str

    @classmethod
    def parser(cls, body):
        return cls(
            mobile_number=body["mobileNumber"],
        )


@dataclass
class MobileVerifyOtpPayload:
    mandatory = ["mobileNumber", "otp"]
    optional = []

    mobile_number: str
    otp: str

    @classmethod
    def parser(cls, body):
        return cls(
            mobile_number=body["mobileNumber"],
            otp=body["otp"],
        )
