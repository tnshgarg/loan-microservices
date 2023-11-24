
import bson
from services.storage.uploads.drive_upload_service import DriveUploadService
from services.storage.uploads.media_upload_service import MediaUploadService


class StoryUploadService(MediaUploadService):

    def __init__(self,
                 user_story,
                 unipe_employee_id: bson.ObjectId,
                 gdrive_upload_service: DriveUploadService,
                 ) -> None:
        super().__init__(unipe_employee_id, None, gdrive_upload_service, None, None)
        self.user_story = user_story
        self.unipe_employee_id = unipe_employee_id
        self.gdrive_upload_service = gdrive_upload_service

    def upload_user_story(self, user_story):
        user_story_drive_url = self._upload_media(
            form_file=user_story,
            filename="user_story"
        )
        return user_story_drive_url
