def convert_id_field_collection(documents):
    for d in documents:
        convert_id_field_single(d)


def convert_id_field_single(document):
    document["id"] = str(document["_id"])
    del document["_id"]
