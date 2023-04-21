DEFAULT_INDEX = "co_occ_test"

DEFAULT_FIELD = "content"

DEFAULT_MAPPING = {
    "properties": {
        DEFAULT_FIELD: {
            "type": "text",
            "analyzer": "ik_smart",
        }
    }
}

DEFAULT_ANALYZER = "ik_smart"
