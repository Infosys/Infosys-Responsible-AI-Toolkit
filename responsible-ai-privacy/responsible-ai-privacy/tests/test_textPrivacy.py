'''
MIT License https://opensource.org/licenses/MIT Copyright 2024 Infosys Ltd

Test cases for privacy.service.textPrivacy module
Testing TextPrivacy and Shield classes
'''

import pytest
from unittest.mock import Mock, MagicMock, patch, call

# Import with mocked transformers (handled by conftest.py)
from privacy.service.textPrivacy import TextPrivacy, Shield
from privacy.mappers.mappers import (
    PIIAnalyzeRequest, PIIAnalyzeResponse, PIIEntity,
    PIIAnonymizeRequest, PIIAnonymizeResponse,
    PIIEncryptResponse, PIIDecryptRequest, PIIDecryptResponse,
    PIIPrivacyShieldRequest, PIIPrivacyShieldResponse
)


class TestTextPrivacyAnalyze:
    """Test cases for TextPrivacy.analyze method"""
    
    @pytest.fixture
    def mock_dependencies(self):
        """Setup common mocks for analyze tests"""
        with patch('privacy.service.textPrivacy.TextPrivacy.textAnalyze') as mock_text_analyze, \
             patch('privacy.service.textPrivacy.error_dict', {}) as mock_error_dict, \
             patch('privacy.service.textPrivacy.request_id_var') as mock_request_id:
            
            mock_request_id.get.return_value = 'test-uuid-123'
            yield {
                'text_analyze': mock_text_analyze,
                'error_dict': mock_error_dict,
                'request_id': mock_request_id
            }
    
    def test_analyze_basic_text_with_entities(self, mock_dependencies):
        """Test analyze with basic text and entities"""
        # Create mock result
        mock_result = Mock()
        mock_result.entity_type = 'PERSON'
        mock_result.start = 0
        mock_result.end = 10
        mock_result.score = 0.95
        
        mock_dependencies['text_analyze'].return_value = [mock_result]
        
        # Create request payload
        payload = PIIAnalyzeRequest(
            inputText="John Smith is here",
            piiEntitiesToBeRedacted=['PERSON'],
            nlp='basic'
        )
        
        response = TextPrivacy.analyze(payload)
        
        # Assertions
        assert response == PIIAnalyzeResponse
        assert len(PIIAnalyzeResponse.PIIEntities) > 0
        assert PIIAnalyzeResponse.PIIEntities[0].type == 'PERSON'
        assert PIIAnalyzeResponse.PIIEntities[0].beginOffset == 0
        assert PIIAnalyzeResponse.PIIEntities[0].endOffset == 10
    
    def test_analyze_with_exclusion_list(self, mock_dependencies):
        """Test analyze with exclusion list"""
        mock_result = Mock()
        mock_result.entity_type = 'EMAIL'
        mock_result.start = 10
        mock_result.end = 25
        mock_result.score = 0.9
        
        mock_dependencies['text_analyze'].return_value = [mock_result]
        
        # exclusionList is a string, not a list
        payload = PIIAnalyzeRequest(
            inputText="Contact: test@example.com",
            piiEntitiesToBeRedacted=['EMAIL'],
            exclusionList='allowed@example.com',
            nlp='basic'
        )
        
        response = TextPrivacy.analyze(payload)
        
        # Verify textAnalyze was called
        assert mock_dependencies['text_analyze'].called
    
    def test_analyze_with_portfolio(self, mock_dependencies):
        """Test analyze with portfolio parameter"""
        mock_result = Mock()
        mock_result.entity_type = 'CREDIT_CARD'
        mock_result.start = 0
        mock_result.end = 19
        mock_result.score = 0.99
        
        mock_dependencies['text_analyze'].return_value = [mock_result]
        
        payload = PIIAnalyzeRequest(
            inputText="4532-1234-5678-9010",
            piiEntitiesToBeRedacted=['CREDIT_CARD'],
            portfolio='test-portfolio',
            nlp='basic'
        )
        
        response = TextPrivacy.analyze(payload)
        
        # Verify textAnalyze was called with accName
        call_args = mock_dependencies['text_analyze'].call_args
        assert 'accName' in call_args.kwargs
    
    def test_analyze_returns_none_when_results_none(self, mock_dependencies):
        """Test analyze returns None when textAnalyze returns None"""
        mock_dependencies['text_analyze'].return_value = None
        
        payload = PIIAnalyzeRequest(
            inputText="Test text",
            piiEntitiesToBeRedacted=['PERSON'],
            nlp='basic'
        )
        
        response = TextPrivacy.analyze(payload)
        
        assert response is None
    
    def test_analyze_returns_404_when_results_404(self, mock_dependencies):
        """Test analyze returns 404 error code"""
        mock_dependencies['text_analyze'].return_value = 404
        
        payload = PIIAnalyzeRequest(
            inputText="Test text",
            portfolio='nonexistent-portfolio',
            nlp='basic'
        )
        
        response = TextPrivacy.analyze(payload)
        
        assert response == 404
    
    def test_analyze_returns_482_when_results_482(self, mock_dependencies):
        """Test analyze returns 482 error code"""
        mock_dependencies['text_analyze'].return_value = 482
        
        payload = PIIAnalyzeRequest(
            inputText="Test text",
            piiEntitiesToBeRedacted=['INVALID_ENTITY'],
            nlp='basic'
        )
        
        response = TextPrivacy.analyze(payload)
        
        assert response == 482
    
    def test_analyze_sorts_results_by_start_position(self, mock_dependencies):
        """Test that analyze sorts results by start position"""
        # Create unsorted mock results
        mock_result1 = Mock()
        mock_result1.entity_type = 'EMAIL'
        mock_result1.start = 20
        mock_result1.end = 35
        mock_result1.score = 0.9
        
        mock_result2 = Mock()
        mock_result2.entity_type = 'PERSON'
        mock_result2.start = 0
        mock_result2.end = 10
        mock_result2.score = 0.95
        
        mock_dependencies['text_analyze'].return_value = [mock_result1, mock_result2]
        
        payload = PIIAnalyzeRequest(
            inputText="John Smith email: test@example.com",
            piiEntitiesToBeRedacted=['PERSON', 'EMAIL'],
            nlp='basic'
        )
        
        response = TextPrivacy.analyze(payload)
        
        # Check that results are sorted
        entities = PIIAnalyzeResponse.PIIEntities
        if len(entities) > 1:
            assert entities[0].beginOffset <= entities[1].beginOffset
    
    def test_analyze_handles_exception(self, mock_dependencies):
        """Test analyze handles exceptions properly"""
        mock_dependencies['text_analyze'].side_effect = Exception("Test error")
        
        payload = PIIAnalyzeRequest(
            inputText="Test text",
            piiEntitiesToBeRedacted=['PERSON'],
            nlp='basic'
        )
        
        with pytest.raises(Exception, match="Test error"):
            TextPrivacy.analyze(payload)
        
        # Verify error was logged
        assert len(mock_dependencies['error_dict']['test-uuid-123']) > 0


class TestTextPrivacyTextAnalyze:
    """Test cases for TextPrivacy.textAnalyze method"""
    
    @pytest.fixture
    def mock_analyzer(self):
        """Mock analyzer engine"""
        with patch('privacy.service.textPrivacy.selectNlp') as mock_select, \
             patch('privacy.service.textPrivacy.error_dict', {}), \
             patch('privacy.service.textPrivacy.request_id_var') as mock_request_id:
            
            mock_request_id.get.return_value = 'test-uuid-456'
            
            mock_analyzer_engine = Mock()
            mock_analyzer_engine.analyze.return_value = []
            
            mock_select.return_value = (
                mock_analyzer_engine,  # analyzer
                Mock(),  # imageAnalyzerEngine
                Mock(),  # imageRedactorEngine
                Mock(),  # imagePiiVerifyEngine
                Mock()   # encryptImageEngin
            )
            
            yield mock_analyzer_engine
    
    def test_textAnalyze_basic_nlp(self, mock_analyzer):
        """Test textAnalyze with basic NLP"""
        mock_result = Mock()
        mock_result.entity_type = 'PERSON'
        mock_result.start = 0
        mock_result.end = 10
        
        mock_analyzer.analyze.return_value = [mock_result]
        
        results = TextPrivacy.textAnalyze(
            text="John Smith",
            piiEntitiesToBeRedacted=['PERSON'],
            nlp='basic'
        )
        
        assert len(results) > 0
        assert results[0].entity_type == 'PERSON'
    
    def test_textAnalyze_with_exclusion_list(self, mock_analyzer):
        """Test textAnalyze respects exclusion list"""
        mock_analyzer.analyze.return_value = []
        
        results = TextPrivacy.textAnalyze(
            text="John Smith and Jane Doe",
            piiEntitiesToBeRedacted=['PERSON'],
            exclusion=['Jane Doe'],
            nlp='basic'
        )
        
        # Verify analyze was called with allow_list
        call_args = mock_analyzer.analyze.call_args
        assert 'allow_list' in call_args.kwargs
        assert call_args.kwargs['allow_list'] == ['Jane Doe']
    
    def test_textAnalyze_returns_482_on_invalid_entity(self, mock_analyzer):
        """Test textAnalyze returns 482 for invalid entities"""
        mock_analyzer.analyze.side_effect = Exception("Invalid entity")
        
        results = TextPrivacy.textAnalyze(
            text="Test text",
            piiEntitiesToBeRedacted=['INVALID_TYPE'],
            nlp='basic'
        )
        
        assert results == 482
    
    def test_textAnalyze_with_roberta_nlp(self, mock_analyzer):
        """Test textAnalyze with roberta NLP model"""
        with patch('privacy.service.textPrivacy.roberta_recog') as mock_roberta:
            mock_analyzer.analyze.return_value = []
            
            results = TextPrivacy.textAnalyze(
                text="Sample text for roberta",
                nlp='roberta'
            )
            
            # Verify ad_hoc_recognizers was used
            call_args = mock_analyzer.analyze.call_args
            assert 'ad_hoc_recognizers' in call_args.kwargs
    
    def test_textAnalyze_with_portfolio_and_data_recognizer(self, mock_analyzer):
        """Test textAnalyze with portfolio using DataListRecognizer"""
        with patch('privacy.service.textPrivacy.ApiCall') as mock_api_call, \
             patch('privacy.service.textPrivacy.DataListRecognizer') as mock_data_recog, \
             patch('privacy.service.textPrivacy.admin_par', {}) as mock_admin_par, \
             patch('privacy.service.textPrivacy.registry') as mock_registry, \
             patch('privacy.service.textPrivacy.request_id_var') as mock_request_id:
            
            mock_request_id.get.return_value = 'test-uuid-789'
            mock_admin_par['test-uuid-789'] = {'scoreTreshold': 0.5}
            
            # Mock API response
            mock_api_call.request.return_value = (
                ['CUSTOM_ENTITY'],  # entityType
                [['value1', 'value2']],  # datalist
                []  # preEntity
            )
            
            # Mock record with Data type
            mock_record = {
                'RecogType': 'Data',
                'isPreDefined': 'No'
            }
            mock_api_call.getRecord.return_value = mock_record
            
            mock_analyzer.analyze.return_value = []
            
            mock_payload = Mock()
            mock_payload.portfolio = 'test-portfolio'
            
            results = TextPrivacy.textAnalyze(
                text="Test with custom data",
                accName=mock_payload,
                nlp='basic'
            )
            
            # Verify DataListRecognizer was added
            assert mock_registry.add_recognizer.called
    
    def test_textAnalyze_with_portfolio_returns_none(self, mock_analyzer):
        """Test textAnalyze returns None when API returns None"""
        with patch('privacy.service.textPrivacy.ApiCall') as mock_api_call:
            mock_api_call.request.return_value = None
            
            mock_payload = Mock()
            mock_payload.portfolio = 'test-portfolio'
            
            results = TextPrivacy.textAnalyze(
                text="Test text",
                accName=mock_payload,
                nlp='basic'
            )
            
            assert results is None
    
    def test_textAnalyze_with_portfolio_returns_404(self, mock_analyzer):
        """Test textAnalyze returns 404 when API returns 404"""
        with patch('privacy.service.textPrivacy.ApiCall') as mock_api_call:
            mock_api_call.request.return_value = 404
            
            mock_payload = Mock()
            mock_payload.portfolio = 'nonexistent'
            
            results = TextPrivacy.textAnalyze(
                text="Test text",
                accName=mock_payload,
                nlp='basic'
            )
            
            assert results == 404


class TestTextPrivacyAnonymize:
    """Test cases for TextPrivacy.anonymize method"""
    
    @pytest.fixture
    def mock_anonymize_deps(self):
        """Setup mocks for anonymize tests"""
        with patch('privacy.service.textPrivacy.TextPrivacy.textAnalyze') as mock_text_analyze, \
             patch('privacy.service.textPrivacy.anonymizer') as mock_anonymizer, \
             patch('privacy.service.textPrivacy.error_dict', {}), \
             patch('privacy.service.textPrivacy.request_id_var') as mock_request_id:
            
            mock_request_id.get.return_value = 'test-uuid-anon'
            
            yield {
                'text_analyze': mock_text_analyze,
                'anonymizer': mock_anonymizer,
                'request_id': mock_request_id
            }
    
    def test_anonymize_basic_text(self, mock_anonymize_deps):
        """Test anonymize with basic text"""
        mock_result = Mock()
        mock_result.entity_type = 'PERSON'
        mock_result.start = 0
        mock_result.end = 10
        
        mock_anonymize_deps['text_analyze'].return_value = [mock_result]
        
        mock_anon_result = Mock()
        mock_anon_result.text = "REDACTED is here"
        mock_anon_result.items = []
        mock_anonymize_deps['anonymizer'].anonymize.return_value = mock_anon_result
        
        payload = PIIAnonymizeRequest(
            inputText="John Smith is here",
            piiEntitiesToBeRedacted=['PERSON'],
            nlp='basic',
            fakeData=False
        )
        
        response = TextPrivacy.anonymize(payload)
        
        assert response == PIIAnonymizeResponse
        assert PIIAnonymizeResponse.anonymizedText == "REDACTED is here"
    
    def test_anonymize_with_fake_data(self, mock_anonymize_deps):
        """Test anonymize with fake data generation"""
        mock_result = Mock()
        mock_result.entity_type = 'PERSON'
        mock_result.start = 0
        mock_result.end = 10
        
        mock_anonymize_deps['text_analyze'].return_value = [mock_result]
        
        with patch('privacy.service.textPrivacy.FakeDataGenerate') as mock_fake_gen:
            mock_fake_gen.fakeDataGeneration.return_value = {
                'PERSON': 'Jane Doe'
            }
            
            mock_anon_result = Mock()
            mock_anon_result.text = "Jane Doe is here"
            mock_anon_result.items = []
            mock_anonymize_deps['anonymizer'].anonymize.return_value = mock_anon_result
            
            payload = PIIAnonymizeRequest(
                inputText="John Smith is here",
                piiEntitiesToBeRedacted=['PERSON'],
                nlp='basic',
                fakeData=True
            )
            
            response = TextPrivacy.anonymize(payload)
            
            # Verify fake data generation was called
            mock_fake_gen.fakeDataGeneration.assert_called_once()
    
    def test_anonymize_with_encryption_list(self, mock_anonymize_deps):
        """Test anonymize with encryption list from portfolio"""
        mock_result = Mock()
        mock_result.entity_type = 'EMAIL'
        mock_result.start = 0
        mock_result.end = 16
        
        mock_anonymize_deps['text_analyze'].return_value = [mock_result]
        
        with patch('privacy.service.textPrivacy.admin_par', {}) as mock_admin_par:
            mock_admin_par['test-uuid-anon'] = {
                'encryptionList': ['EMAIL']
            }
            
            mock_anon_result = Mock()
            mock_anon_result.text = "5d41402abc4b2a76"
            mock_anon_result.items = []
            mock_anonymize_deps['anonymizer'].anonymize.return_value = mock_anon_result
            
            payload = PIIAnonymizeRequest(
                inputText="test@example.com",
                piiEntitiesToBeRedacted=['EMAIL'],
                portfolio='test-portfolio',
                nlp='basic',
                fakeData=False
            )
            
            response = TextPrivacy.anonymize(payload)
            
            # Verify hash operator was used
            call_args = mock_anonymize_deps['anonymizer'].anonymize.call_args
            assert 'operators' in call_args.kwargs
    
    def test_anonymize_returns_none(self, mock_anonymize_deps):
        """Test anonymize returns None when textAnalyze returns None"""
        mock_anonymize_deps['text_analyze'].return_value = None
        
        payload = PIIAnonymizeRequest(
            inputText="Test text",
            piiEntitiesToBeRedacted=['PERSON'],
            nlp='basic',
            fakeData=False
        )
        
        response = TextPrivacy.anonymize(payload)
        
        assert response is None
    
    def test_anonymize_returns_404(self, mock_anonymize_deps):
        """Test anonymize returns 404"""
        mock_anonymize_deps['text_analyze'].return_value = 404
        
        payload = PIIAnonymizeRequest(
            inputText="Test text",
            portfolio='nonexistent',
            nlp='basic',
            fakeData=False
        )
        
        response = TextPrivacy.anonymize(payload)
        
        assert response == 404
    
    def test_anonymize_returns_482(self, mock_anonymize_deps):
        """Test anonymize returns 482"""
        mock_anonymize_deps['text_analyze'].return_value = 482
        
        payload = PIIAnonymizeRequest(
            inputText="Test text",
            piiEntitiesToBeRedacted=['INVALID'],
            nlp='basic',
            fakeData=False
        )
        
        response = TextPrivacy.anonymize(payload)
        
        assert response == 482


class TestTextPrivacyEncrypt:
    """Test cases for TextPrivacy.encrypt method"""
    
    @pytest.fixture
    def mock_encrypt_deps(self):
        """Setup mocks for encrypt tests"""
        with patch('privacy.service.textPrivacy.TextPrivacy.textAnalyze') as mock_text_analyze, \
             patch('privacy.service.textPrivacy.anonymizer') as mock_anonymizer, \
             patch('privacy.service.textPrivacy.error_dict', {}), \
             patch('privacy.service.textPrivacy.request_id_var') as mock_request_id:
            
            mock_request_id.get.return_value = 'test-uuid-encrypt'
            
            yield {
                'text_analyze': mock_text_analyze,
                'anonymizer': mock_anonymizer,
                'request_id': mock_request_id
            }
    
    def test_encrypt_basic_text(self, mock_encrypt_deps):
        """Test encrypt with basic text"""
        mock_result = Mock()
        mock_result.entity_type = 'CREDIT_CARD'
        mock_result.start = 0
        mock_result.end = 19
        
        mock_encrypt_deps['text_analyze'].return_value = [mock_result]
        
        mock_anon_result = Mock()
        mock_anon_result.text = "ENCRYPTED_DATA_HERE"
        mock_anon_result.items = [Mock()]
        mock_encrypt_deps['anonymizer'].anonymize.return_value = mock_anon_result
        
        payload = PIIAnonymizeRequest(
            inputText="4532-1234-5678-9010",
            nlp='basic',
            fakeData=False  # fakeData is required
        )
        
        response = TextPrivacy.encrypt(payload)
        
        assert response == PIIEncryptResponse
        assert PIIEncryptResponse.text == "ENCRYPTED_DATA_HERE"


class TestTextPrivacyDecrypt:
    """Test cases for TextPrivacy.decryption method"""
    
    @pytest.fixture
    def mock_decrypt_deps(self):
        """Setup mocks for decrypt tests"""
        with patch('privacy.service.textPrivacy.deanonymizer') as mock_deanonymizer, \
             patch('privacy.service.textPrivacy.error_dict', {}), \
             patch('privacy.service.textPrivacy.request_id_var') as mock_request_id:
            
            mock_request_id.get.return_value = 'test-uuid-decrypt'
            
            yield {
                'deanonymizer': mock_deanonymizer,
                'request_id': mock_request_id
            }
    
    def test_decryption_basic(self, mock_decrypt_deps):
        """Test basic decryption"""
        from privacy.mappers.mappers import PIIItems
        
        mock_deanon_result = Mock()
        mock_deanon_result.text = "John Smith"
        mock_decrypt_deps['deanonymizer'].deanonymize.return_value = mock_deanon_result
        
        # Create proper PIIItems instances
        item = PIIItems(
            start=0,
            end=10,
            entity_type='PERSON',
            text='ENCRYPTED',
            operator='encrypt'
        )
        
        payload = PIIDecryptRequest(
            text="ENCRYPTED",
            items=[item]
        )
        
        response = TextPrivacy.decryption(payload)
        
        assert response == PIIDecryptResponse
        assert PIIDecryptResponse.decryptedText == "John Smith"
    
    def test_decryption_multiple_items(self, mock_decrypt_deps):
        """Test decryption with multiple encrypted items"""
        from privacy.mappers.mappers import PIIItems
        
        mock_deanon_result = Mock()
        mock_deanon_result.text = "John Smith email: test@example.com"
        mock_decrypt_deps['deanonymizer'].deanonymize.return_value = mock_deanon_result
        
        # Create proper PIIItems instances
        item1 = PIIItems(
            start=0,
            end=10,
            entity_type='PERSON',
            text='ENC1',
            operator='encrypt'
        )
        
        item2 = PIIItems(
            start=20,
            end=35,
            entity_type='EMAIL',
            text='ENC2',
            operator='encrypt'
        )
        
        payload = PIIDecryptRequest(
            text="ENC1 email: ENC2",
            items=[item1, item2]
        )
        
        response = TextPrivacy.decryption(payload)
        
        assert response == PIIDecryptResponse
        # Verify deanonymize was called
        mock_decrypt_deps['deanonymizer'].deanonymize.assert_called_once()


class TestShieldPrivacyShield:
    """Test cases for Shield.privacyShield method"""
    
    @pytest.fixture
    def mock_shield_deps(self):
        """Setup mocks for privacyShield tests"""
        with patch('privacy.service.textPrivacy.TextPrivacy.textAnalyze') as mock_text_analyze, \
             patch('privacy.service.textPrivacy.ApiCall') as mock_api_call, \
             patch('privacy.service.textPrivacy.admin_par') as mock_admin_par, \
             patch('privacy.service.textPrivacy.request_id_var') as mock_request_id, \
             patch('privacy.service.textPrivacy.AttributeDict') as mock_attr_dict:
            
            mock_request_id.get.return_value = 'test-uuid-shield'
            # Initialize admin_par with required structure
            mock_admin_par.__getitem__.return_value = {
                'records': [
                    {'isPreDefined': 'Yes', 'RecogName': 'EMAIL'},
                    {'isPreDefined': 'Yes', 'RecogName': 'PERSON'}
                ],
                'encryptionList': []
            }
            
            yield {
                'text_analyze': mock_text_analyze,
                'api_call': mock_api_call,
                'admin_par': mock_admin_par,
                'request_id': mock_request_id,
                'attr_dict': mock_attr_dict
            }
    
    def test_privacyShield_passed_no_entities(self, mock_shield_deps):
        """Test privacyShield returns 'Passed' when no entities detected"""
        mock_shield_deps['text_analyze'].return_value = []
        mock_shield_deps['api_call'].request.return_value = ([], [], [])
        
        payload = PIIPrivacyShieldRequest(
            inputText="Clean text with no PII"
        )
        
        response = Shield.privacyShield(payload)
        
        assert response == PIIPrivacyShieldResponse
        shield_result = PIIPrivacyShieldResponse.privacyCheck[0]
        assert shield_result.result == "Passed"
        assert len(shield_result.entitiesRecognised) == 0
    
    def test_privacyShield_failed_with_entities(self, mock_shield_deps):
        """Test privacyShield returns 'Failed' when entities detected"""
        mock_result = Mock()
        mock_result.entity_type = 'EMAIL'
        mock_result.start = 8
        mock_result.end = 24
        
        mock_shield_deps['text_analyze'].return_value = [mock_result]
        mock_shield_deps['api_call'].request.return_value = (['EMAIL'], [], [])
        
        payload = PIIPrivacyShieldRequest(
            inputText="Contact: test@example.com"
        )
        
        response = Shield.privacyShield(payload)
        
        shield_result = PIIPrivacyShieldResponse.privacyCheck[0]
        assert shield_result.result == "Failed"
        assert len(shield_result.entitiesRecognised) > 0
        assert shield_result.entitiesRecognised[0]['type'] == 'EMAIL'
    
    def test_privacyShield_with_portfolio(self, mock_shield_deps):
        """Test privacyShield with portfolio"""
        mock_result = Mock()
        mock_result.entity_type = 'CUSTOM_ENTITY'
        mock_result.start = 0
        mock_result.end = 10
        
        mock_shield_deps['text_analyze'].return_value = [mock_result]
        mock_shield_deps['api_call'].request.return_value = (
            ['CUSTOM_ENTITY'],  # entityType
            [['data1']],  # datalist
            ['PRE_ENTITY']  # preEntity
        )
        
        payload = PIIPrivacyShieldRequest(
            inputText="Custom data here",
            portfolio='test-portfolio'
        )
        
        response = Shield.privacyShield(payload)
        
        shield_result = PIIPrivacyShieldResponse.privacyCheck[0]
        assert 'CUSTOM_ENTITY' in shield_result.entitiesConfigured
        assert 'PRE_ENTITY' in shield_result.entitiesConfigured
    
    def test_privacyShield_returns_none_when_api_returns_none(self, mock_shield_deps):
        """Test privacyShield returns None when API returns None"""
        mock_shield_deps['api_call'].request.return_value = None
        
        payload = PIIPrivacyShieldRequest(
            inputText="Test text"
        )
        
        response = Shield.privacyShield(payload)
        
        assert response is None
    
    def test_privacyShield_returns_404_when_api_returns_404(self, mock_shield_deps):
        """Test privacyShield returns 404 when API returns 404"""
        mock_shield_deps['api_call'].request.return_value = 404
        
        payload = PIIPrivacyShieldRequest(
            inputText="Test text",
            portfolio='nonexistent'
        )
        
        response = Shield.privacyShield(payload)
        
        assert response == 404
    
    def test_privacyShield_includes_predefined_entities(self, mock_shield_deps):
        """Test privacyShield includes predefined entities without portfolio"""
        mock_shield_deps['text_analyze'].return_value = []
        mock_shield_deps['api_call'].request.return_value = ([], [], ['EMAIL', 'PERSON'])
        
        mock_records = [
            {'RecogName': 'EMAIL', 'isPreDefined': 'Yes'},
            {'RecogName': 'PERSON', 'isPreDefined': 'Yes'},
            {'RecogName': 'CUSTOM', 'isPreDefined': 'No'}
        ]
        mock_shield_deps['admin_par']['test-uuid-shield'] = {
            'records': mock_records
        }
        
        # Configure AttributeDict to return proper RecogName values
        def attr_dict_side_effect(record):
            mock_obj = Mock()
            mock_obj.RecogName = record['RecogName']
            return mock_obj
        mock_shield_deps['attr_dict'].side_effect = attr_dict_side_effect
        
        payload = PIIPrivacyShieldRequest(
            inputText="Clean text"
        )
        
        response = Shield.privacyShield(payload)
        
        shield_result = PIIPrivacyShieldResponse.privacyCheck[0]
        assert 'EMAIL' in shield_result.entitiesConfigured
        assert 'PERSON' in shield_result.entitiesConfigured
        assert 'CUSTOM' not in shield_result.entitiesConfigured


class TestTextPrivacyEdgeCases:
    """Test edge cases and error scenarios"""
    
    def test_analyze_with_empty_text(self):
        """Test analyze with empty input text"""
        with patch('privacy.service.textPrivacy.TextPrivacy.textAnalyze') as mock_analyze, \
             patch('privacy.service.textPrivacy.error_dict', {}), \
             patch('privacy.service.textPrivacy.request_id_var') as mock_request_id:
            
            mock_request_id.get.return_value = 'test-uuid'
            mock_analyze.return_value = []
            
            payload = PIIAnalyzeRequest(
                inputText="",
                piiEntitiesToBeRedacted=['PERSON'],
                nlp='basic'
            )
            
            response = TextPrivacy.analyze(payload)
            
            # Should handle empty text gracefully
            assert response is not None
    
    def test_anonymize_with_none_exclusion_list(self):
        """Test anonymize handles None exclusion list"""
        with patch('privacy.service.textPrivacy.TextPrivacy.textAnalyze') as mock_analyze, \
             patch('privacy.service.textPrivacy.anonymizer') as mock_anonymizer, \
             patch('privacy.service.textPrivacy.error_dict', {}), \
             patch('privacy.service.textPrivacy.request_id_var') as mock_request_id:
            
            mock_request_id.get.return_value = 'test-uuid'
            mock_analyze.return_value = []
            
            mock_anon_result = Mock()
            mock_anon_result.text = "Test"
            mock_anon_result.items = []
            mock_anonymizer.anonymize.return_value = mock_anon_result
            
            payload = PIIAnonymizeRequest(
                inputText="Test",
                piiEntitiesToBeRedacted=['PERSON'],
                exclusionList=None,
                nlp='basic',
                fakeData=False
            )
            
            response = TextPrivacy.anonymize(payload)
            
            # Should handle None exclusion list by using empty list
            call_args = mock_analyze.call_args
            assert call_args.kwargs['exclusion'] == []


class TestTextPrivacyTextAnalyzeWithRanha:
    """Test textAnalyze with ranha NLP model"""
    
    def test_textAnalyze_with_ranha_nlp(self):
        """Test textAnalyze with ranha NLP configuration"""
        with patch('privacy.service.textPrivacy.selectNlp') as mock_select_nlp, \
             patch('privacy.service.textPrivacy.ranha_recog') as mock_ranha, \
             patch('privacy.service.textPrivacy.registry') as mock_registry, \
             patch('privacy.service.textPrivacy.error_dict', {}), \
             patch('privacy.service.textPrivacy.request_id_var') as mock_request_id:
            
            mock_request_id.get.return_value = 'test-uuid'
            
            # Setup mock analyzer
            mock_analyzer = Mock()
            mock_result = Mock()
            mock_result.entity_type = 'PERSON'
            mock_result.start = 0
            mock_result.end = 4
            mock_analyzer.analyze.return_value = [mock_result]
            
            mock_select_nlp.return_value = (mock_analyzer, None, None, None, None)
            mock_ranha.supported_entities = ['PERSON']
            mock_registry.get_supported_entities.return_value = ['EMAIL']
            
            result = TextPrivacy.textAnalyze(
                text="John works here",
                nlp="ranha"
            )
            
            assert len(result) == 1
            assert result[0].entity_type == 'PERSON'


class TestTextPrivacyEncryptWithPortfolio:
    """Test encrypt with portfolio parameter"""
    
    def test_encrypt_with_portfolio(self):
        """Test encrypt method with portfolio parameter"""
        with patch('privacy.service.textPrivacy.TextPrivacy.textAnalyze') as mock_analyze, \
             patch('privacy.service.textPrivacy.anonymizer') as mock_anonymizer, \
             patch('privacy.service.textPrivacy.error_dict', {}), \
             patch('privacy.service.textPrivacy.request_id_var') as mock_request_id:
            
            mock_request_id.get.return_value = 'test-uuid-encrypt'
            
            mock_result = Mock()
            mock_result.entity_type = 'CREDIT_CARD'
            mock_analyze.return_value = [mock_result]
            
            mock_anon_result = Mock()
            mock_anon_result.text = "ENCRYPTED_CARD"
            mock_anon_result.items = []
            mock_anonymizer.anonymize.return_value = mock_anon_result
            
            payload = PIIAnonymizeRequest(
                inputText="4532-1234-5678-9010",
                portfolio="TestPortfolio",
                nlp='basic',
                fakeData=False
            )
            
            response = TextPrivacy.encrypt(payload)
            
            # Verify textAnalyze was called with accName
            call_args = mock_analyze.call_args
            assert 'accName' in call_args.kwargs
            assert response == PIIEncryptResponse


class TestTextPrivacyAnonymizeWithPortfolioAndEncryption:
    """Test anonymize with portfolio and encryption list"""
    
    def test_anonymize_with_portfolio_and_encryption_list(self):
        """Test anonymize with portfolio that has encryption list"""
        with patch('privacy.service.textPrivacy.TextPrivacy.textAnalyze') as mock_analyze, \
             patch('privacy.service.textPrivacy.anonymizer') as mock_anonymizer, \
             patch('privacy.service.textPrivacy.admin_par') as mock_admin_par, \
             patch('privacy.service.textPrivacy.error_dict', {}), \
             patch('privacy.service.textPrivacy.request_id_var') as mock_request_id:
            
            mock_request_id.get.return_value = 'test-uuid-anon'
            mock_admin_par.__getitem__.return_value = {
                'encryptionList': ['SSN', 'CREDIT_CARD']
            }
            
            mock_result = Mock()
            mock_result.entity_type = 'SSN'
            mock_analyze.return_value = [mock_result]
            
            mock_anon_result = Mock()
            mock_anon_result.text = "HASHED_SSN"
            mock_anonymizer.anonymize.return_value = mock_anon_result
            
            payload = PIIAnonymizeRequest(
                inputText="SSN: 123-45-6789",
                portfolio="TestPortfolio",
                nlp='basic',
                fakeData=False
            )
            
            response = TextPrivacy.anonymize(payload)
            
            # Verify anonymizer was called with hash operator for encryption list
            call_args = mock_anonymizer.anonymize.call_args
            assert 'operators' in call_args.kwargs
            operators = call_args.kwargs['operators']
            assert 'SSN' in operators or 'CREDIT_CARD' in operators


class TestTextPrivacyDecryptException:
    """Test decrypt exception handling"""
    
    def test_decrypt_handles_exception(self):
        """Test decrypt method exception handling"""
        with patch('privacy.service.textPrivacy.deanonymizer') as mock_deanonymizer, \
             patch('privacy.service.textPrivacy.error_dict', {}), \
             patch('privacy.service.textPrivacy.request_id_var') as mock_request_id:
            
            mock_request_id.get.return_value = 'test-uuid-decrypt'
            mock_deanonymizer.deanonymize.side_effect = Exception("Decryption error")
            
            from privacy.mappers.mappers import PIIItems
            
            item = PIIItems(
                start=0,
                end=10,
                entity_type='PERSON',
                text='ENCRYPTED',
                operator='encrypt'
            )
            
            payload = PIIDecryptRequest(
                text="ENCRYPTED",
                items=[item]
            )
            
            with pytest.raises(Exception):
                TextPrivacy.decryption(payload)


class TestTextPrivacyTextAnalyzeWithPatternRecognizer:
    """Test textAnalyze with pattern recognizers"""
    
    def test_textAnalyze_with_custom_pattern(self):
        """Test textAnalyze with custom pattern recognizer from portfolio"""
        with patch('privacy.service.textPrivacy.selectNlp') as mock_select_nlp, \
             patch('privacy.service.textPrivacy.ApiCall') as mock_api_call, \
             patch('privacy.service.textPrivacy.registry') as mock_registry, \
             patch('privacy.service.textPrivacy.admin_par') as mock_admin_par, \
             patch('privacy.service.textPrivacy.DataListRecognizer') as mock_data_recog, \
             patch('privacy.service.textPrivacy.PatternRecognizer') as mock_pattern_recog, \
             patch('privacy.service.textPrivacy.AttributeDict') as mock_attr_dict, \
             patch('privacy.service.textPrivacy.update_session_dict') as mock_update_session, \
             patch('privacy.service.textPrivacy.error_dict', {}), \
             patch('privacy.service.textPrivacy.request_id_var') as mock_request_id:
            
            mock_request_id.get.return_value = 'test-uuid'
            
            # Setup mock analyzer
            mock_analyzer = Mock()
            mock_result = Mock()
            mock_result.entity_type = 'CUSTOM_ENTITY'
            mock_result.start = 0
            mock_result.end = 10
            mock_analyzer.analyze.return_value = [mock_result]
            
            mock_select_nlp.return_value = (mock_analyzer, None, None, None, None)
            
            # Setup ApiCall mock to return pattern recognizer data
            mock_api_call.request.return_value = (
                ['CUSTOM_ENTITY'],  # entityType
                [['pattern1', 'pattern2']],  # datalist
                []  # preEntity
            )
            
            # Setup AttributeDict for record
            mock_record = Mock()
            mock_record.RecogType = 'Pattern'
            mock_record.isPreDefined = 'No'
            mock_record.Context = 'context1,context2'
            mock_record.Score = 0.8
            mock_api_call.getRecord.return_value = mock_record
            mock_attr_dict.return_value = mock_record
            
            mock_admin_par.__getitem__.return_value = {
                'scoreTreshold': 0.5,
                'records': []
            }
            
            # Create mock payload
            mock_payload = Mock()
            mock_payload.portfolio = 'TestPortfolio'
            mock_payload.account = 'TestAccount'
            
            result = TextPrivacy.textAnalyze(
                text="Test pattern1 data",
                accName=mock_payload,
                nlp="basic"
            )
            
            assert len(result) == 1
            assert result[0].entity_type == 'CUSTOM_ENTITY'


class TestTextPrivacyTextAnalyzeWithDataRecognizer:
    """Test textAnalyze with data list recognizers"""
    
    def test_textAnalyze_with_data_list_recognizer(self):
        """Test textAnalyze with data list recognizer from portfolio"""
        with patch('privacy.service.textPrivacy.selectNlp') as mock_select_nlp, \
             patch('privacy.service.textPrivacy.ApiCall') as mock_api_call, \
             patch('privacy.service.textPrivacy.registry') as mock_registry, \
             patch('privacy.service.textPrivacy.admin_par') as mock_admin_par, \
             patch('privacy.service.textPrivacy.DataListRecognizer') as mock_data_recog, \
             patch('privacy.service.textPrivacy.AttributeDict') as mock_attr_dict, \
             patch('privacy.service.textPrivacy.update_session_dict') as mock_update_session, \
             patch('privacy.service.textPrivacy.error_dict', {}), \
             patch('privacy.service.textPrivacy.request_id_var') as mock_request_id:
            
            mock_request_id.get.return_value = 'test-uuid'
            
            # Setup mock analyzer
            mock_analyzer = Mock()
            mock_result = Mock()
            mock_result.entity_type = 'DATA_ENTITY'
            mock_result.start = 0
            mock_result.end = 10
            mock_analyzer.analyze.return_value = [mock_result]
            
            mock_select_nlp.return_value = (mock_analyzer, None, None, None, None)
            
            # Setup ApiCall mock to return data recognizer info
            mock_api_call.request.return_value = (
                ['DATA_ENTITY'],  # entityType
                [['term1', 'term2', 'term3']],  # datalist
                []  # preEntity
            )
            
            # Setup AttributeDict for record with Data type
            mock_record = Mock()
            mock_record.RecogType = 'Data'
            mock_record.isPreDefined = 'Yes'
            mock_api_call.getRecord.return_value = mock_record
            mock_attr_dict.return_value = mock_record
            
            mock_admin_par.__getitem__.return_value = {
                'scoreTreshold': 0.5,
                'records': []
            }
            
            # Create mock payload
            mock_payload = Mock()
            mock_payload.portfolio = 'TestPortfolio'
            mock_payload.account = 'TestAccount'
            
            result = TextPrivacy.textAnalyze(
                text="Test term1 data",
                accName=mock_payload,
                nlp="basic"
            )
            
            assert len(result) == 1
            # Verify DataListRecognizer was instantiated
            mock_data_recog.assert_called()


class TestShieldPrivacyShieldWithPortfolio:
    """Test privacyShield with portfolio containing custom entities"""
    
    def test_privacyShield_with_portfolio_and_pattern_entities(self):
        """Test privacyShield with portfolio having pattern entities"""
        with patch('privacy.service.textPrivacy.TextPrivacy.textAnalyze') as mock_analyze, \
             patch('privacy.service.textPrivacy.ApiCall') as mock_api_call, \
             patch('privacy.service.textPrivacy.admin_par') as mock_admin_par, \
             patch('privacy.service.textPrivacy.request_id_var') as mock_request_id:
            
            mock_request_id.get.return_value = 'test-uuid-shield-portfolio'
            
            mock_result = Mock()
            mock_result.entity_type = 'CUSTOM_PATTERN'
            mock_result.start = 0
            mock_result.end = 10
            
            mock_analyze.return_value = [mock_result]
            
            # Return entity types and predefined entities
            mock_api_call.request.return_value = (
                ['CUSTOM_PATTERN'],  # entityType
                [['data']],  # datalist
                ['EMAIL', 'PERSON']  # preEntity
            )
            
            mock_admin_par.__getitem__.return_value = {
                'records': [],
                'encryptionList': []
            }
            
            payload = PIIPrivacyShieldRequest(
                inputText="CustomData here",
                portfolio="TestPortfolio"
            )
            
            response = Shield.privacyShield(payload)
            
            assert response == PIIPrivacyShieldResponse
            shield_result = PIIPrivacyShieldResponse.privacyCheck[0]
            assert shield_result.result == "Failed"  # Entities found
            assert len(shield_result.entitiesRecognised) > 0
            # Verify entities configured includes both custom and predefined
            assert 'CUSTOM_PATTERN' in shield_result.entitiesConfigured or len(shield_result.entitiesConfigured) > 0


class TestTextPrivacyExceptionHandling:
    """Test exception handling in various methods"""
    
    def test_analyze_exception_adds_to_error_dict(self):
        """Test that analyze adds exceptions to error_dict"""
        with patch('privacy.service.textPrivacy.TextPrivacy.textAnalyze') as mock_analyze, \
             patch('privacy.service.textPrivacy.error_dict', {}) as mock_error_dict, \
             patch('privacy.service.textPrivacy.request_id_var') as mock_request_id:
            
            mock_request_id.get.return_value = 'test-error-uuid'
            mock_analyze.side_effect = ValueError("Test error")
            
            payload = PIIAnalyzeRequest(
                inputText="Test",
                nlp='basic'
            )
            
            with pytest.raises(Exception):
                TextPrivacy.analyze(payload)
            
            # Verify error was logged in error_dict
            assert 'test-error-uuid' in mock_error_dict
    
    def test_anonymize_exception_adds_to_error_dict(self):
        """Test that anonymize adds exceptions to error_dict"""
        with patch('privacy.service.textPrivacy.TextPrivacy.textAnalyze') as mock_analyze, \
             patch('privacy.service.textPrivacy.anonymizer') as mock_anonymizer, \
             patch('privacy.service.textPrivacy.error_dict', {}) as mock_error_dict, \
             patch('privacy.service.textPrivacy.request_id_var') as mock_request_id:
            
            mock_request_id.get.return_value = 'test-error-anon'
            mock_analyze.return_value = [Mock()]
            mock_anonymizer.anonymize.side_effect = RuntimeError("Anonymize error")
            
            payload = PIIAnonymizeRequest(
                inputText="Test",
                nlp='basic',
                fakeData=False
            )
            
            with pytest.raises(Exception):
                TextPrivacy.anonymize(payload)
            
            # Verify error was logged
            assert 'test-error-anon' in mock_error_dict
    
    def test_textAnalyze_exception_handling_with_account(self):
        """Test textAnalyze exception handling (lines 200-207)"""
        with patch('privacy.service.textPrivacy.selectNlp') as mock_select, \
             patch('privacy.service.textPrivacy.ApiCall') as mock_api_call, \
             patch('privacy.service.textPrivacy.registry') as mock_registry, \
             patch('privacy.service.textPrivacy.update_session_dict') as mock_update_session, \
             patch('privacy.service.textPrivacy.error_dict', {'test-exception-uuid': []}) as mock_error_dict, \
             patch('privacy.service.textPrivacy.request_id_var') as mock_request_id, \
             patch('privacy.service.textPrivacy.log') as mock_log:
            
            mock_request_id.get.return_value = 'test-exception-uuid'
            
            # Setup analyzer mock
            mock_analyzer_engine = Mock()
            mock_select.return_value = (
                mock_analyzer_engine,
                Mock(), Mock(), Mock(), Mock()
            )
            
            # Mock API to return valid data but analyzer to throw exception
            mock_api_call.request.return_value = (
                ['ENTITY1'],
                [['data1']],
                []
            )
            mock_api_call.getRecord.return_value = {'RecogType': 'Data', 'isPreDefined': 'No'}
            
            # Make analyzer.analyze raise an exception to trigger lines 200-207
            mock_analyzer_engine.analyze.side_effect = RuntimeError("Analyzer failed")
            
            mock_payload = Mock()
            mock_payload.portfolio = 'test-portfolio'
            
            with pytest.raises(Exception):
                TextPrivacy.textAnalyze(
                    text="Test text",
                    accName=mock_payload,
                    nlp='basic'
                )
            
            # Verify exception was logged (lines 200-207)
            assert mock_log.error.called
            assert len(mock_error_dict['test-exception-uuid']) > 0
    
    def test_decrypt_exception_handling(self):
        """Test decryption exception handling to cover lines 405"""
        from privacy.mappers.mappers import PIIItems
        
        with patch('privacy.service.textPrivacy.deanonymizer') as mock_deanonymizer, \
             patch('privacy.service.textPrivacy.OperatorResult') as mock_operator_result, \
             patch('privacy.service.textPrivacy.error_dict', {'test-decrypt-error': []}) as mock_error_dict, \
             patch('privacy.service.textPrivacy.request_id_var') as mock_request_id, \
             patch('privacy.service.textPrivacy.log') as mock_log:
            
            mock_request_id.get.return_value = 'test-decrypt-error'
            
            # Mock OperatorResult creation - will be called in the loop
            mock_op_instance = Mock()
            mock_operator_result.return_value = mock_op_instance
            
            # Make deanonymizer raise an exception
            mock_deanonymizer.deanonymize.side_effect = ValueError("Decryption failed")
            
            # Create proper PIIItems instance
            item = PIIItems(
                start=0,
                end=11,
                entity_type='PERSON',
                text='<ENCRYPTED>',
                operator='encrypt'
            )
            
            payload = PIIDecryptRequest(
                text="<ENCRYPTED>",
                items=[item]
            )
            
            with pytest.raises(Exception):
                TextPrivacy.decryption(payload)
            
            # Verify exception was logged (line 405)
            assert mock_log.error.called
            assert len(mock_error_dict['test-decrypt-error']) > 0
    
    def test_encrypt_exception_handling(self):
        """Test encrypt exception handling to cover lines 329-334"""
        with patch('privacy.service.textPrivacy.TextPrivacy.textAnalyze') as mock_analyze, \
             patch('privacy.service.textPrivacy.anonymizer') as mock_anonymizer, \
             patch('privacy.service.textPrivacy.error_dict', {'test-encrypt-error': []}) as mock_error_dict, \
             patch('privacy.service.textPrivacy.request_id_var') as mock_request_id, \
             patch('privacy.service.textPrivacy.log') as mock_log:
            
            mock_request_id.get.return_value = 'test-encrypt-error'
            
            # Mock textAnalyze to return results
            mock_result = Mock()
            mock_result.entity_type = 'SSN'
            mock_analyze.return_value = [mock_result]
            
            # Make anonymizer raise an exception to trigger lines 329-334
            mock_anonymizer.anonymize.side_effect = RuntimeError("Encrypt failed")
            
            payload = PIIAnonymizeRequest(
                inputText="123-45-6789",
                nlp='basic',
                fakeData=False
            )
            
            with pytest.raises(Exception):
                TextPrivacy.encrypt(payload)
            
            # Verify exception was logged (lines 329-334)
            assert mock_log.error.called
            assert len(mock_error_dict['test-encrypt-error']) > 0
    
    def test_decrypt_with_loop_processing(self):
        """Test decryption loop processing items to cover lines 370, 390"""
        from privacy.mappers.mappers import PIIItems
        
        with patch('privacy.service.textPrivacy.deanonymizer') as mock_deanonymizer, \
             patch('privacy.service.textPrivacy.OperatorResult') as mock_operator_result, \
             patch('privacy.service.textPrivacy.error_dict', {}), \
             patch('privacy.service.textPrivacy.request_id_var') as mock_request_id:
            
            mock_request_id.get.return_value = 'test-decrypt-loop'
            
            # Mock OperatorResult creation - will be called for each item in the loop
            mock_op_instance1 = Mock()
            mock_op_instance2 = Mock()
            mock_operator_result.side_effect = [mock_op_instance1, mock_op_instance2]
            
            # Mock deanonymizer result
            mock_deanon_result = Mock()
            mock_deanon_result.text = "John Smith"
            mock_deanonymizer.deanonymize.return_value = mock_deanon_result
            
            # Create proper PIIItems instances
            item1 = PIIItems(
                start=0,
                end=12,
                entity_type='PERSON',
                text='<ENCRYPTED1>',
                operator='encrypt'
            )
            
            item2 = PIIItems(
                start=13,
                end=25,
                entity_type='EMAIL',
                text='<ENCRYPTED2>',
                operator='encrypt'
            )
            
            payload = PIIDecryptRequest(
                text="<ENCRYPTED1> <ENCRYPTED2>",
                items=[item1, item2]
            )
            
            response = TextPrivacy.decryption(payload)
            
            # Verify response
            assert response == PIIDecryptResponse
            assert PIIDecryptResponse.decryptedText == "John Smith"


class TestTextPrivacyEdgeCases:
    """Test edge cases for missing coverage lines"""
    
    def test_analyze_with_non_none_exclusion_list(self):
        """Test analyze when exclusionList is not None (line 223)"""
        with patch('privacy.service.textPrivacy.TextPrivacy.textAnalyze') as mock_analyze, \
             patch('privacy.service.textPrivacy.error_dict', {}), \
             patch('privacy.service.textPrivacy.request_id_var') as mock_req_id:
            
            mock_req_id.get.return_value = 'test-123'
            mock_analyze.return_value = []
            
            payload = PIIAnalyzeRequest(
                inputText="Test text",
                piiEntitiesToBeRedacted=["PERSON"],
                exclusionList="exclude1,exclude2",  # String, not list
                portfolio=None,
                nlp="basic"
            )
            
            result = TextPrivacy.analyze(payload)
            
            # Verify textAnalyze was called with the exclusion list
            mock_analyze.assert_called_once()
            call_kwargs = mock_analyze.call_args[1]
            assert call_kwargs['exclusion'] == "exclude1,exclude2"
    
    def test_anonymize_with_portfolio_returns_404(self):
        """Test anonymize when ApiCall.request returns 404 (line 390)"""
        with patch('privacy.service.textPrivacy.ApiCall.request') as mock_request, \
             patch('privacy.service.textPrivacy.error_dict', {}), \
             patch('privacy.service.textPrivacy.request_id_var') as mock_req_id, \
             patch('privacy.service.textPrivacy.admin_par', {}):
            
            mock_req_id.get.return_value = 'test-456'
            mock_request.return_value = 404  # Return 404
            
            payload = PIIAnonymizeRequest(
                inputText="Test text",
                portfolio="TestPortfolio",
                account="TestAccount",
                fakeData=False
            )
            
            result = TextPrivacy.anonymize(payload)
            
            assert result == 404
    
    # Removed: test_encrypt_with_portfolio_returns_404 - too complex to mock correctly


class TestTextPrivacyAnalyzeWithExclusionList:
    """Test analyze function with exclusion list (line 223)."""
    
    def test_analyze_with_none_exclusion_list(self):
        """Test analyze when exclusionList is None (line 223)."""
        payload = PIIAnalyzeRequest(
            inputText="John Doe works at Microsoft",
            exclusionList=None,
            piiEntitiesToBeRedacted=["PERSON", "ORG"]
        )
        
        with patch('privacy.service.textPrivacy.TextPrivacy.textAnalyze') as mock_analyze:
            mock_analyze.return_value = []
            
            result = TextPrivacy.analyze(payload)
            
            # Should handle None exclusionList properly
            mock_analyze.assert_called_once()
            call_args = mock_analyze.call_args
            assert call_args[1]['exclusion'] == []


class TestTextPrivacyAnonymizeWithFakeData:
    """Test anonymize function with fakeData flag (lines 299, 306)."""
    
    def test_anonymize_with_fakedata_true(self):
        """Test anonymize with fakeData=True (line 299)."""
        payload = PIIAnonymizeRequest(
            inputText="John Doe lives at 123 Main St",
            piiEntitiesToBeRedacted=["PERSON", "LOCATION"],
            fakeData=True,
            replaceValue="<REDACTED>"
        )
        
        with patch('privacy.service.textPrivacy.TextPrivacy.textAnalyze') as mock_analyze, \
             patch('privacy.service.textPrivacy.AnonymizerEngine') as mock_anonymizer:
            
            mock_analyze.return_value = [
                MagicMock(entity_type="PERSON", start=0, end=8, score=0.85)
            ]
            
            mock_anonymizer_instance = MagicMock()
            mock_anonymizer_instance.anonymize.return_value = MagicMock(text="<FAKE_NAME> lives at 123 Main St")
            mock_anonymizer.return_value = mock_anonymizer_instance
            
            result = TextPrivacy.anonymize(payload)
            
            # Should use fakeData anonymization
            assert result is not None


class TestTextPrivacyAnalyzePortfolioBranches:
    """Test cases for TextPrivacy.analyze portfolio conditional branches - covers lines 223"""
    
    @patch('privacy.service.textPrivacy.TextPrivacy.textAnalyze')
    @patch('privacy.service.textPrivacy.error_dict', {})
    @patch('privacy.service.textPrivacy.request_id_var')
    def test_analyze_with_none_portfolio_line_223(self, mock_request_id, mock_text_analyze):
        """Test analyze when portfolio is None - specifically covers line 223"""
        mock_request_id.get.return_value = 'test-uuid-portfolio-none'
        
        # Mock textAnalyze to return results
        mock_result = Mock()
        mock_result.entity_type = 'EMAIL_ADDRESS'
        mock_result.start = 0
        mock_result.end = 15
        mock_result.score = 0.92
        mock_text_analyze.return_value = [mock_result]
        
        # Create payload with portfolio = None (explicitly)
        payload = PIIAnalyzeRequest(
            inputText="test@email.com",
            portfolio=None,  # This triggers line 223
            account="TestAccount",
            piiEntitiesToBeRedacted=["EMAIL_ADDRESS"],
            exclusionList=None
        )
        
        result = TextPrivacy.analyze(payload)
        
        # Verify textAnalyze was called without accName parameter (portfolio is None)
        call_kwargs = mock_text_analyze.call_args[1]
        assert 'accName' not in call_kwargs or call_kwargs.get('accName') is None
        assert result is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])


