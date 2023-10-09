from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from dal.models.pincodes import Pincodes

router = APIRouter()


class PincodeRequest(BaseModel):
    pincode: int


@router.post("/pincode-details")
async def generate_otp(pincode_request: PincodeRequest):
    db_doc = Pincodes.find_one(
        filter_={"pincode": pincode_request.pincode},
        projection={"_id": 0}
    )
    if db_doc is None:
        raise HTTPException(
            status_code=404,
            detail="pincode not found in db"
        )
    return db_doc
