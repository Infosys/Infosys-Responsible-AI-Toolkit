import time

from src.dao.Tenet import Tenet


def test_tenet_get_all_and_findall():
    # Create a unique Tenet entry
    unique_name = f"Cov{int(time.time()*1000)}"
    Tenet.create({'tenetid': int(time.time()*1000), 'tenetname': unique_name, 'projectname': 'projX'})

    names = Tenet.get_all('TenetName')
    assert isinstance(names, list) and unique_name in names

    all_items = Tenet.findall({})
    assert isinstance(all_items, list) and len(all_items) >= 1
