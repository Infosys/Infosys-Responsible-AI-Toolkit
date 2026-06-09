'''
MIT License
https://mit-license.org/
Copyright © 2025 Infosys Ltd.
 
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
 
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
 
THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

"""
test_constants.py - Tests for constants module (local_constants.py and exception/constants.py)
"""

import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

class TestLocalConstants:
    """Tests for local_constants.py"""

    def test_deleted_success_message_exists(self):
        """Test DELETED_SUCCESS_MESSAGE constant exists"""
        from explain.constants.local_constants import DELTED_SUCCESS_MESSAGE
        
        assert DELTED_SUCCESS_MESSAGE is not None
        assert isinstance(DELTED_SUCCESS_MESSAGE, str)
        assert 'Successfully' in DELTED_SUCCESS_MESSAGE

    def test_usecase_already_exists(self):
        """Test USECASE_ALREADY_EXISTS constant"""
        from explain.constants.local_constants import USECASE_ALREADY_EXISTS
        
        assert USECASE_ALREADY_EXISTS is not None
        assert 'PLACEHOLDER_TEXT' in USECASE_ALREADY_EXISTS

    def test_usecase_not_found_error(self):
        """Test USECASE_NOT_FOUND_ERROR constant"""
        from explain.constants.local_constants import USECASE_NOT_FOUND_ERROR
        
        assert USECASE_NOT_FOUND_ERROR is not None
        assert 'PLACEHOLDER_TEXT' in USECASE_NOT_FOUND_ERROR
        assert 'Not Found' in USECASE_NOT_FOUND_ERROR

    def test_usecase_name_validation_error(self):
        """Test USECASE_NAME_VALIDATION_ERROR constant"""
        from explain.constants.local_constants import USECASE_NAME_VALIDATION_ERROR
        
        assert USECASE_NAME_VALIDATION_ERROR is not None
        assert 'empty' in USECASE_NAME_VALIDATION_ERROR.lower()

    def test_space_delimiter(self):
        """Test SPACE_DELIMITER constant"""
        from explain.constants.local_constants import SPACE_DELIMITER
        
        assert SPACE_DELIMITER == " "

    def test_placeholder_text(self):
        """Test PLACEHOLDER_TEXT constant"""
        from explain.constants.local_constants import PLACEHOLDER_TEXT
        
        assert PLACEHOLDER_TEXT == "PLACEHOLDER_TEXT"


class TestMethodDescriptions:
    """Tests for method description constants"""

    def test_anchor_tabular_description(self):
        """Test ANCHOR_TABULAR_DES constant"""
        from explain.constants.local_constants import ANCHOR_TABULAR_DES
        
        assert ANCHOR_TABULAR_DES is not None
        assert isinstance(ANCHOR_TABULAR_DES, str)
        assert len(ANCHOR_TABULAR_DES) > 50  # Should be a meaningful description
        assert 'Anchor' in ANCHOR_TABULAR_DES

    def test_local_kernel_shap_description(self):
        """Test LOCAL_KERNEL_SHAP_DES constant"""
        from explain.constants.local_constants import LOCAL_KERNEL_SHAP_DES
        
        assert LOCAL_KERNEL_SHAP_DES is not None
        assert 'SHAP' in LOCAL_KERNEL_SHAP_DES
        assert 'feature' in LOCAL_KERNEL_SHAP_DES.lower()

    def test_global_kernel_shap_description(self):
        """Test GLOBAL_KERNEL_SHAP_DES constant"""
        from explain.constants.local_constants import GLOBAL_KERNEL_SHAP_DES
        
        assert GLOBAL_KERNEL_SHAP_DES is not None
        assert 'Global' in GLOBAL_KERNEL_SHAP_DES
        assert 'SHAP' in GLOBAL_KERNEL_SHAP_DES

    def test_local_tree_shap_description(self):
        """Test LOCAL_TREE_SHAP_DES constant"""
        from explain.constants.local_constants import LOCAL_TREE_SHAP_DES
        
        assert LOCAL_TREE_SHAP_DES is not None
        assert 'Tree' in LOCAL_TREE_SHAP_DES
        assert 'SHAP' in LOCAL_TREE_SHAP_DES

    def test_global_tree_shap_description(self):
        """Test GLOBAL_TREE_SHAP_DES constant"""
        from explain.constants.local_constants import GLOBAL_TREE_SHAP_DES
        
        assert GLOBAL_TREE_SHAP_DES is not None
        assert 'Global' in GLOBAL_TREE_SHAP_DES
        assert 'tree' in GLOBAL_TREE_SHAP_DES.lower()

    def test_lime_tabular_description(self):
        """Test LIME_TABULAR_DES constant"""
        from explain.constants.local_constants import LIME_TABULAR_DES
        
        assert LIME_TABULAR_DES is not None
        assert 'LIME' in LIME_TABULAR_DES
        assert 'Local' in LIME_TABULAR_DES

    def test_global_pd_variance_description(self):
        """Test GLOBAL_PD_VARIANCE_DES constant"""
        from explain.constants.local_constants import GLOBAL_PD_VARIANCE_DES
        
        assert GLOBAL_PD_VARIANCE_DES is not None
        assert 'Partial Dependence' in GLOBAL_PD_VARIANCE_DES

    def test_global_permutation_importance_description(self):
        """Test GLOBAL_PERMUTATION_IMPORTANCE_DES constant"""
        from explain.constants.local_constants import GLOBAL_PERMUTATION_IMPORTANCE_DES
        
        assert GLOBAL_PERMUTATION_IMPORTANCE_DES is not None
        assert 'Permutation' in GLOBAL_PERMUTATION_IMPORTANCE_DES
        assert 'importance' in GLOBAL_PERMUTATION_IMPORTANCE_DES.lower()

    def test_local_ts_lime_explainer_description(self):
        """Test LOCAL_TS_LIME_EXPLAINER_DES constant"""
        from explain.constants.local_constants import LOCAL_TS_LIME_EXPLAINER_DES
        
        assert LOCAL_TS_LIME_EXPLAINER_DES is not None
        assert 'time' in LOCAL_TS_LIME_EXPLAINER_DES.lower()

    def test_integrated_gradient_description(self):
        """Test INTEGRATED_GRADIENT_DES constant"""
        from explain.constants.local_constants import INTEGRATED_GRADIENT_DES
        
        assert INTEGRATED_GRADIENT_DES is not None
        assert 'Integrated Gradients' in INTEGRATED_GRADIENT_DES


class TestExplanationConstants:
    """Tests for explanation help text constants"""

    def test_anchor_explanation(self):
        """Test ANCHOR_EXPLANATION constant"""
        from explain.constants.local_constants import ANCHOR_EXPLANATION
        
        assert ANCHOR_EXPLANATION is not None
        assert 'anchor' in ANCHOR_EXPLANATION.lower()
        assert 'prediction' in ANCHOR_EXPLANATION.lower()

    def test_integrated_gradient_explanation(self):
        """Test INTEGRATED_GRADIENT_EXPLANATION constant"""
        from explain.constants.local_constants import INTEGRATED_GRADIENT_EXPLANATION
        
        assert INTEGRATED_GRADIENT_EXPLANATION is not None
        assert 'Integrated Gradients' in INTEGRATED_GRADIENT_EXPLANATION

    def test_feature_importance_explanation(self):
        """Test FEATURE_IMPORTANCE_EXPLANATION constant"""
        from explain.constants.local_constants import FEATURE_IMPORTANCE_EXPLANATION
        
        assert FEATURE_IMPORTANCE_EXPLANATION is not None
        assert 'feature' in FEATURE_IMPORTANCE_EXPLANATION.lower()
        assert 'importance' in FEATURE_IMPORTANCE_EXPLANATION.lower()

    def test_feature_importance_global_explanation(self):
        """Test FEATURE_IMPORTANCE_GLOBAL_EXPLANATION constant"""
        from explain.constants.local_constants import FEATURE_IMPORTANCE_GLOBAL_EXPLANATION
        
        assert FEATURE_IMPORTANCE_GLOBAL_EXPLANATION is not None
        assert 'feature' in FEATURE_IMPORTANCE_GLOBAL_EXPLANATION.lower()


class TestHttpStatusCodes:
    """Tests for HTTP status codes constants"""

    def test_status_code_ok(self):
        """Test OK status code"""
        from explain.exception.constants import HTTP_STATUS_CODES
        
        assert HTTP_STATUS_CODES['OK'] == 200

    def test_status_code_not_found(self):
        """Test NOT_FOUND status code"""
        from explain.exception.constants import HTTP_STATUS_CODES
        
        assert HTTP_STATUS_CODES['NOT_FOUND'] == 404

    def test_status_code_method_not_allowed(self):
        """Test METHOD_NOT_ALLOWED status code"""
        from explain.exception.constants import HTTP_STATUS_CODES
        
        assert HTTP_STATUS_CODES['METHOD_NOT_ALLOWED'] == 405

    def test_status_code_bad_request(self):
        """Test BAD_REQUEST status code"""
        from explain.exception.constants import HTTP_STATUS_CODES
        
        assert HTTP_STATUS_CODES['BAD_REQUEST'] == 400

    def test_status_code_conflict(self):
        """Test CONFLICT status code"""
        from explain.exception.constants import HTTP_STATUS_CODES
        
        assert HTTP_STATUS_CODES['CONFLICT'] == 409

    def test_status_code_unsupported_media_type(self):
        """Test UNSUPPORTED_MEDIA_TYPE status code"""
        from explain.exception.constants import HTTP_STATUS_CODES
        
        assert HTTP_STATUS_CODES['UNSUPPORTED_MEDIA_TYPE'] == 415

    def test_status_code_unprocessable_entity(self):
        """Test UNPROCESSABLE_ENTITY status code"""
        from explain.exception.constants import HTTP_STATUS_CODES
        
        assert HTTP_STATUS_CODES['UNPROCESSABLE_ENTITY'] == 422

    def test_status_code_service_unavailable(self):
        """Test SERVICE_UNAVAILABLE status code"""
        from explain.exception.constants import HTTP_STATUS_CODES
        
        assert HTTP_STATUS_CODES['SERVICE_UNAVAILABLE'] == 503

    def test_status_code_internal_server_error(self):
        """Test INTERNAL_SERVER_ERROR status code"""
        from explain.exception.constants import HTTP_STATUS_CODES
        
        assert HTTP_STATUS_CODES['INTERNAL_SERVER_ERROR'] == 500

    def test_status_code_data_error(self):
        """Test DATA_ERROR status code"""
        from explain.exception.constants import HTTP_STATUS_CODES
        
        assert HTTP_STATUS_CODES['DATA_ERROR'] == 500


class TestHttpStatusMessages:
    """Tests for HTTP status messages constants"""

    def test_message_ok(self):
        """Test OK message"""
        from explain.exception.constants import HTTP_STATUS_MESSAGES
        
        assert HTTP_STATUS_MESSAGES['OK'] == "Request processed successfully"

    def test_message_not_found(self):
        """Test NOT_FOUND message"""
        from explain.exception.constants import HTTP_STATUS_MESSAGES
        
        assert HTTP_STATUS_MESSAGES['NOT_FOUND'] == "Resource not found"

    def test_message_method_not_allowed(self):
        """Test METHOD_NOT_ALLOWED message"""
        from explain.exception.constants import HTTP_STATUS_MESSAGES
        
        assert HTTP_STATUS_MESSAGES['METHOD_NOT_ALLOWED'] == "Method not allowed"

    def test_message_bad_request(self):
        """Test BAD_REQUEST message"""
        from explain.exception.constants import HTTP_STATUS_MESSAGES
        
        assert HTTP_STATUS_MESSAGES['BAD_REQUEST'] == "Bad request"

    def test_message_internal_server_error(self):
        """Test INTERNAL_SERVER_ERROR message"""
        from explain.exception.constants import HTTP_STATUS_MESSAGES
        
        assert HTTP_STATUS_MESSAGES['INTERNAL_SERVER_ERROR'] == "Internal server error"

    def test_message_database_connection_refused(self):
        """Test DATABASE_CONNECTION_REFUSED message"""
        from explain.exception.constants import HTTP_STATUS_MESSAGES
        
        assert HTTP_STATUS_MESSAGES['DATABASE_CONNECTION_REFUSED'] == "Database connection refused"

    def test_all_status_codes_have_messages(self):
        """Test that all status codes have corresponding messages"""
        from explain.exception.constants import HTTP_STATUS_CODES, HTTP_STATUS_MESSAGES
        
        # Most status codes should have messages (except DATA_ERROR which maps to same as INTERNAL_SERVER_ERROR)
        core_codes = ['OK', 'NOT_FOUND', 'METHOD_NOT_ALLOWED', 'BAD_REQUEST', 
                      'CONFLICT', 'UNSUPPORTED_MEDIA_TYPE', 'UNPROCESSABLE_ENTITY', 
                      'SERVICE_UNAVAILABLE', 'INTERNAL_SERVER_ERROR']
        
        for code in core_codes:
            assert code in HTTP_STATUS_CODES
            assert code in HTTP_STATUS_MESSAGES


class TestConstantsIntegrity:
    """Integration tests for constants consistency"""

    def test_http_status_codes_are_integers(self):
        """Test all HTTP status codes are integers"""
        from explain.exception.constants import HTTP_STATUS_CODES
        
        for key, value in HTTP_STATUS_CODES.items():
            assert isinstance(value, int), f"{key} should be an integer"

    def test_http_status_messages_are_strings(self):
        """Test all HTTP status messages are strings"""
        from explain.exception.constants import HTTP_STATUS_MESSAGES
        
        for key, value in HTTP_STATUS_MESSAGES.items():
            assert isinstance(value, str), f"{key} should be a string"

    def test_method_descriptions_are_non_empty(self):
        """Test all method descriptions are non-empty strings"""
        from explain.constants.local_constants import (
            ANCHOR_TABULAR_DES, LOCAL_KERNEL_SHAP_DES, GLOBAL_KERNEL_SHAP_DES,
            LOCAL_TREE_SHAP_DES, GLOBAL_TREE_SHAP_DES, LIME_TABULAR_DES,
            GLOBAL_PD_VARIANCE_DES, GLOBAL_PERMUTATION_IMPORTANCE_DES,
            LOCAL_TS_LIME_EXPLAINER_DES, INTEGRATED_GRADIENT_DES
        )
        
        descriptions = [
            ANCHOR_TABULAR_DES, LOCAL_KERNEL_SHAP_DES, GLOBAL_KERNEL_SHAP_DES,
            LOCAL_TREE_SHAP_DES, GLOBAL_TREE_SHAP_DES, LIME_TABULAR_DES,
            GLOBAL_PD_VARIANCE_DES, GLOBAL_PERMUTATION_IMPORTANCE_DES,
            LOCAL_TS_LIME_EXPLAINER_DES, INTEGRATED_GRADIENT_DES
        ]
        
        for desc in descriptions:
            assert len(desc) > 0, "Description should not be empty"
            assert isinstance(desc, str), "Description should be a string"
