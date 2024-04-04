class InconsistantData(ValueError):
    """
    The message and the schema doesn't match
    """

    def __str__(self) -> str:
        return "InconsistantData : \t The data types are not compatible. Kindly check you schema."


class SchemaSizeMismatch(Exception):
    """
    The data and the schema have mismatched sizes
    """


class TableAlreadyExists(Exception):
    """
    The table you are trying to create already exists
    """

    def __str__(self) -> str:
        return "TableAlreadyExists:\tThe table you are trying to create already exists"


class DataInsersionFailed(Exception):
    """
    The Data insersion has failed!
    """

    def __str__(self) -> str:
        return "DataInsersionFailed:\tThe data you are trying to insert has failed!"
