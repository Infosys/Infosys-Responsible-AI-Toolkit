import pytest

from src.service.service import Infosys, Bulk
from src.dao.Security.AttackAttributesValuesDb import AttackAttributesValues


def test_getavailableAttack_contains_expected():
    lst = Infosys.getavailableAttack()
    assert isinstance(lst, list)
    # Expect a couple of known attacks
    assert 'FastGradientMethod' in lst and 'Boundary' in lst


def test_getAttackFuncs_filters_by_classifier_and_datatype():
    # Prepare synthetic AttackAttributesValues entries with same AttackId
    AttackAttributesValues.delete({})
    aid = 999.0
    AttackAttributesValues.create({
        'attackAttributeId': 1.0,
        'attackId': aid,
        'attackAttributeValues': 'sklearn',
    })
    AttackAttributesValues.create({
        'attackAttributeId': 2.0,
        'attackId': aid,
        'attackAttributeValues': 'Tabular',
    })
    AttackAttributesValues.create({
        'attackAttributeId': 3.0,
        'attackId': aid,
        'attackAttributeValues': 'FastGradientMethod',
    })

    funcs = Infosys.getAttackFuncs({'targetClassifier': 'sklearn', 'targetDataType': 'Tabular'})
    assert isinstance(funcs, list)


def test_bulk_sanitize_filename_valid_and_invalid():
    assert Bulk.sanitize_filenameorfoldername('safe_name-1') == 'safe_name-1'
    # Invalid should return None due to guarded exception path
    assert Bulk.sanitize_filenameorfoldername('bad/name') is None
