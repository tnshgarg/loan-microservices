class OpsException(Exception):

    def __init__(self, context, exception_name="OpsException") -> None:
        super().__init__(f"{exception_name} with context={context}")
        self.ops_context = context


class DevOpsException(OpsException):

    def __init__(self, context) -> None:
        super().__init__(context, "DevOpsException")
