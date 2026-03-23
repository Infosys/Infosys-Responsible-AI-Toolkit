import time

from src.dao.DataDb import Data as DataDb


def test_datadb_findone_not_found_returns_none():
    # Use a random id unlikely to exist
    random_id = time.time() + 12345
    result = DataDb.findOne(random_id)
    assert result is None
