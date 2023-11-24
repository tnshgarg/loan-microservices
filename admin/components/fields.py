from starlette_admin import URLField


class CustomUrlField(URLField):
    display_template: str = "templates/admin/url"