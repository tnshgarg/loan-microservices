from starlette.datastructures import FormData


class DictToObj(object):
    """
    Turns a dictionary into a class
    """

    def __init__(self, dictionary):
        """Constructor"""
        for key in dictionary:
            setattr(self, key, dictionary[key])


class MultiFormDataParser:
    @staticmethod
    def parse(data: FormData, form_key: str):
        form_data_list = data._list
        form_value = next(
            (value for key, value in form_data_list if key == form_key), None)
        return form_value
