from flask import Blueprint, request
from flask_restful import Api, Resource

aadhaar_ocr_blueprint = Blueprint("aadhaar_ocr", __name__)
api = Api(aadhaar_ocr_blueprint)

class AadhaarOCR(Resource):

    def get(self,unipe_employee_id):
        return {"foo": "bar"}, 200