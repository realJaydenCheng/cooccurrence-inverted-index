DEFAULT_INDEX = "co_occ_test"

DEFAULT_FIELD = "content"

DEFAULT_ANALYZER = "ik_smart"

DEFAULT_TYPE = "text"

DEFAULT_AGG_NAME = "word_count"

DEFAULT_MAPPING = {
    "properties": {
        DEFAULT_FIELD: {
            "type": DEFAULT_TYPE,
            "analyzer": DEFAULT_ANALYZER,
            "fielddata": True,
        }
    }
}

DEFAULT_AGG = {
    DEFAULT_AGG_NAME: {
        "terms": {
            "field": DEFAULT_FIELD,
        },
    },
}

DEFAULT_DEPTH = 5
