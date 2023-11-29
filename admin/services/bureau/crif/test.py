from admin.services.bureau.crif.payload_builders.request_payload_builder import \
    RequestPayloadBuilder


def test_payload_builder():
    xml_string = RequestPayloadBuilder(stage="dev").build_payload()
    print(xml_string)


if __name__ == "__main__":
    test_payload_builder()
