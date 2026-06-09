'''
Copyright 2024-2025 Infosys Ltd.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), 
to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, 
and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies 
or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, 
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE 
AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, 
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, 
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

import pytest
import sys
import os
import json
from unittest.mock import patch, MagicMock
from pydantic import ValidationError

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

from llm.mapper.mapper import (
    OpenAiRequest,
    Choice,
    ImageGenerationRequest,
    ImageGenerationResponse
)


class TestOpenAiRequest:
    """Test suite for OpenAiRequest Pydantic model"""
    
    def test_openai_request_valid_creation(self):
        """Test creating valid OpenAiRequest"""
        payload = OpenAiRequest(
            messages='[{"role": "user", "content": "Hello"}]',
            temperature=0.7,
            model="gpt4",
            max_tokens=100,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0,
            stop=None
        )
        assert payload.messages == '[{"role": "user", "content": "Hello"}]'
        assert payload.temperature == 0.7
        assert payload.model == "gpt4"
    
    def test_openai_request_required_fields(self):
        """Test OpenAiRequest with only required fields"""
        payload = OpenAiRequest(
            messages='[{"role": "user", "content": "Test"}]',
            temperature=0.5,
            model="gpt3"
        )
        assert payload.messages is not None
        assert payload.temperature == 0.5
        assert payload.model == "gpt3"
    
    def test_openai_request_optional_fields(self):
        """Test OpenAiRequest optional fields are optional"""
        payload = OpenAiRequest(
            messages='[{"role": "user", "content": "Test"}]',
            temperature=0.5,
            model="gpt4",
            max_tokens=None,
            top_p=None,
            frequency_penalty=None,
            presence_penalty=None,
            stop=None
        )
        assert payload.max_tokens is None
        assert payload.top_p is None
    
    def test_openai_request_valid_json_messages(self):
        """Test OpenAiRequest with valid JSON messages"""
        messages_json = json.dumps([
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": "What is AI?"}
        ])
        payload = OpenAiRequest(
            messages=messages_json,
            temperature=0.7,
            model="gpt4"
        )
        assert isinstance(payload.messages, str)
    
    def test_openai_request_missing_required_fields(self):
        """Test OpenAiRequest raises error when required fields missing"""
        with pytest.raises(ValidationError):
            OpenAiRequest(
                temperature=0.5,
                model="gpt4"
                # messages is required but missing
            )
    
    def test_openai_request_temperature_variations(self):
        """Test OpenAiRequest with different temperature values"""
        temperatures = [0.0, 0.5, 1.0, 2.0]
        for temp in temperatures:
            payload = OpenAiRequest(
                messages='[{"role": "user", "content": "Test"}]',
                temperature=temp,
                model="gpt4"
            )
            assert payload.temperature == temp
    
    def test_openai_request_model_variations(self):
        """Test OpenAiRequest with different model names"""
        models = ["gpt3", "gpt4", "gpt4O", "custom-model"]
        for model in models:
            payload = OpenAiRequest(
                messages='[{"role": "user", "content": "Test"}]',
                temperature=0.5,
                model=model
            )
            assert payload.model == model


class TestChoice:
    """Test suite for Choice Pydantic model"""
    
    def test_choice_valid_creation(self):
        """Test creating valid Choice"""
        choice = Choice(
            text="Russia is the biggest country",
            index=0,
            finishReason="length"
        )
        assert choice.text == "Russia is the biggest country"
        assert choice.index == 0
        assert choice.finishReason == "length"
    
    def test_choice_with_different_finish_reasons(self):
        """Test Choice with various finish reasons"""
        finish_reasons = ["length", "stop", "content_filter", "tool_calls"]
        for reason in finish_reasons:
            choice = Choice(
                text="Sample response",
                index=0,
                finishReason=reason
            )
            assert choice.finishReason == reason
    
    def test_choice_with_different_indices(self):
        """Test Choice with different index values"""
        for idx in range(5):
            choice = Choice(
                text=f"Response {idx}",
                index=idx,
                finishReason="stop"
            )
            assert choice.index == idx
    
    def test_choice_with_long_text(self):
        """Test Choice with long text"""
        long_text = "A" * 1000
        choice = Choice(
            text=long_text,
            index=0,
            finishReason="stop"
        )
        assert len(choice.text) == 1000
    
    def test_choice_missing_required_fields(self):
        """Test Choice raises error when required fields missing"""
        with pytest.raises(ValidationError):
            Choice(text="Sample")  # Missing index and finishReason
    
    def test_choice_with_special_characters(self):
        """Test Choice with special characters in text"""
        special_text = "Test with special chars: !@#$%^&*()"
        choice = Choice(
            text=special_text,
            index=0,
            finishReason="stop"
        )
        assert choice.text == special_text


class TestImageGenerationRequest:
    """Test suite for ImageGenerationRequest Pydantic model"""
    
    def test_image_generation_request_valid_creation(self):
        """Test creating valid ImageGenerationRequest"""
        request = ImageGenerationRequest(
            prompt="Generate an image of a doctor",
            model="DALL-E-2"
        )
        assert request.prompt == "Generate an image of a doctor"
        assert request.model == "DALL-E-2"
    
    def test_image_generation_request_required_fields(self):
        """Test ImageGenerationRequest with required fields"""
        request = ImageGenerationRequest(
            prompt="A beautiful landscape",
            model="DALL-E-3"
        )
        assert request.prompt is not None
        assert request.model is not None
    
    def test_image_generation_request_missing_prompt(self):
        """Test ImageGenerationRequest raises error when prompt missing"""
        with pytest.raises(ValidationError):
            ImageGenerationRequest(model="DALL-E-2")
    
    def test_image_generation_request_missing_model(self):
        """Test ImageGenerationRequest raises error when model missing"""
        with pytest.raises(ValidationError):
            ImageGenerationRequest(prompt="Test prompt")
    
    def test_image_generation_request_with_detailed_prompt(self):
        """Test ImageGenerationRequest with detailed prompt"""
        detailed_prompt = "A doctor in a white coat with a stethoscope in a hospital setting"
        request = ImageGenerationRequest(
            prompt=detailed_prompt,
            model="DALL-E-2"
        )
        assert detailed_prompt in request.prompt
    
    def test_image_generation_request_model_variations(self):
        """Test ImageGenerationRequest with different model names"""
        models = ["DALL-E-2", "DALL-E-3", "custom-model"]
        for model in models:
            request = ImageGenerationRequest(
                prompt="Test",
                model=model
            )
            assert request.model == model


class TestImageGenerationResponse:
    """Test suite for ImageGenerationResponse Pydantic model"""
    
    def test_image_generation_response_valid_creation(self):
        """Test creating valid ImageGenerationResponse"""
        base64_image = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
        response = ImageGenerationResponse(image=base64_image)
        assert response.image == base64_image
    
    def test_image_generation_response_with_long_base64(self):
        """Test ImageGenerationResponse with long base64 string"""
        long_base64 = "A" * 10000
        response = ImageGenerationResponse(image=long_base64)
        assert len(response.image) == 10000
    
    def test_image_generation_response_missing_field(self):
        """Test ImageGenerationResponse raises error when image missing"""
        with pytest.raises(ValidationError):
            ImageGenerationResponse()
    
    def test_image_generation_response_empty_string(self):
        """Test ImageGenerationResponse with empty image string"""
        response = ImageGenerationResponse(image="")
        assert response.image == ""


class TestMapperIntegration:
    """Integration tests for mapper models"""
    
    def test_openai_request_to_dict(self):
        """Test converting OpenAiRequest to dictionary"""
        payload = OpenAiRequest(
            messages='[{"role": "user", "content": "Test"}]',
            temperature=0.7,
            model="gpt4"
        )
        payload_dict = payload.model_dump()
        assert "messages" in payload_dict
        assert "temperature" in payload_dict
        assert "model" in payload_dict
    
    def test_image_generation_request_to_dict(self):
        """Test converting ImageGenerationRequest to dictionary"""
        request = ImageGenerationRequest(
            prompt="Test prompt",
            model="DALL-E-2"
        )
        request_dict = request.model_dump()
        assert "prompt" in request_dict
        assert "model" in request_dict
        assert request_dict["prompt"] == "Test prompt"
    
    def test_image_generation_response_to_dict(self):
        """Test converting ImageGenerationResponse to dictionary"""
        response = ImageGenerationResponse(image="base64_data")
        response_dict = response.model_dump()
        assert "image" in response_dict
        assert response_dict["image"] == "base64_data"
    
    def test_pydantic_from_attributes_config(self):
        """Test models have from_attributes config"""
        assert hasattr(OpenAiRequest, 'model_config')
        assert hasattr(Choice, 'model_config')
        assert hasattr(ImageGenerationRequest, 'model_config')
        assert hasattr(ImageGenerationResponse, 'model_config')
    
    def test_multiple_requests_independence(self):
        """Test multiple request objects are independent"""
        request1 = OpenAiRequest(
            messages='[{"role": "user", "content": "First"}]',
            temperature=0.5,
            model="gpt4"
        )
        request2 = OpenAiRequest(
            messages='[{"role": "user", "content": "Second"}]',
            temperature=0.7,
            model="gpt3"
        )
        
        assert request1.temperature != request2.temperature
        assert request1.model != request2.model
