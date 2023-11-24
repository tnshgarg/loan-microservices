from PIL import Image, ExifTags
from io import BytesIO


class DummyFormFile:
    content_type = "image/jpeg"

    def __init__(self, fd) -> None:
        self.file = fd


class ImageWidths:
    THUMBNAIL = 320
    LOW_RES = 720


class ImageService:

    @staticmethod
    def fix_image_orientation(image):
        if hasattr(image, '_getexif'):
            exif = image._getexif()
            if exif:
                for tag, label in ExifTags.TAGS.items():
                    if label == 'Orientation':
                        orientation = tag
                        break
                if orientation in exif:
                    if exif[orientation] == 3:
                        image = image.rotate(180, expand=True)
                    elif exif[orientation] == 6:
                        image = image.rotate(270, expand=True)
                    elif exif[orientation] == 8:
                        image = image.rotate(90, expand=True)
        return image

    @staticmethod
    def get_low_res_file(fd, fixed_width=320):
        fd.seek(0)
        image = Image.open(fd)
        image = ImageService.fix_image_orientation(image)
        height, width = image.size
        aspect_ratio = height/width
        calculated_height = int(fixed_width * aspect_ratio)
        low_res_image = image.resize(size=(calculated_height, fixed_width))
        out_fd = BytesIO()
        low_res_image.save(out_fd, format="jpeg")
        out_fd.seek(0)
        return out_fd

    @staticmethod
    def get_liveness_check_file(fd):
        out_fd = ImageService.get_low_res_file(
            fd,
            fixed_width=ImageWidths.LOW_RES
        )
        return DummyFormFile(out_fd)

    @staticmethod
    def get_thumbnail(fd):
        out_fd = ImageService.get_low_res_file(
            fd,
            fixed_width=ImageWidths.THUMBNAIL
        )
        return DummyFormFile(out_fd)
