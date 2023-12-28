from background_tasks.background_task import BackgroundTask
from dal.models.credentials import Credentials

class SaveEmployerCreds(BackgroundTask):

    def run(self, payload):
        employer_id: str = payload["employer_id"]
        portal : str = payload["portal"]
        username : str = payload["username"]
        password : str = payload["password"]
        public_key : str = payload["public_key"] 

        employer_creds_update_result = Credentials.update_one({
            "pId": employer_id,
            "portal": portal
        }, {
            "$set": {
                "username": username,
                "password": password,
                "public_key": public_key,
            }
        }, upsert=True)

        self.logger.info("Employer Creds Updated", extra={
            "data": {
                "employer_creds_update_result": {
                    "upserted_id": employer_creds_update_result.upserted_id,
                    "matched_count": employer_creds_update_result.matched_count
                }
            }
        })
