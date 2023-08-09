
import requests


class SlackService:

    def __init__(self,incoming_webhook_url) -> None:
        self.base_url = incoming_webhook_url

    def post_message(self,text):
        response = requests.post(
            url=self.base_url,
            headers={
                "Content-Type": "application/json"
            },
            json={
                "text": text
            }
        )
        return response.status_code, response.json()