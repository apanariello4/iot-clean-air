from datetime import datetime
from uuid import UUID


def is_valid_uuid(uuid_to_test: str, version=4) -> bool:
    """Check to see if a string is a valid uuid

    Args:
        uuid_to_test (str): uuid to test
        version (int, optional): uuid version to use. Defaults to 4.

    Returns:
        bool: is a valid uuid or not
    """
    uuid_to_test = uuid_to_test.replace('-', '')
    try:
        val = UUID(uuid_to_test, version=version)
        return True
    except ValueError:
        return False


def is_valid_date(date: str, date_format='%Y-%m-%d %H:%M:%S') -> bool:
    """Check if string is valid date given a date_format

    Args:
        date (str): date string
        date_format (str, optional): format to validate against. Defaults to '%Y-%m-%dT%H%M%S'.

    Returns:
        bool: true if valid date, false otherwise
    """
    try:
        date_obj = datetime.strptime(date, date_format)
        return date_obj
    except ValueError:
        return False
