"""
Unit tests for the ValidationService.
"""

import pytest
import json

from src.services.validation_service import ValidationService

class TestValidationService:
    """Test cases for ValidationService."""

    def test_validate_json_syntax_valid(self):
        """Test validating valid JSON."""
        valid_json = '{"model": "claude-3-opus-20240229", "max_tokens": 4096}'

        errors = ValidationService.validate_json_syntax(valid_json)

        assert len(errors) == 0

    def test_validate_json_syntax_invalid(self):
        """Test validating invalid JSON."""
        invalid_json = '{"model": "claude-3-opus-20240229", "max_tokens":}'  # Trailing comma

        errors = ValidationService.validate_json_syntax(invalid_json)

        assert len(errors) > 0
        assert any("json syntax error" in error.lower() for error in errors)

    def test_validate_json_syntax_empty(self):
        """Test validating empty JSON."""
        errors = ValidationService.validate_json_syntax("")

        assert len(errors) > 0
        assert any("empty" in error.lower() for error in errors)

    def test_validate_profile_name_valid(self):
        """Test validating valid profile names."""
        valid_names = [
            "Production",
            "Development",
            "test-profile",
            "Profile 123",
            "a" * 100  # Maximum length
        ]

        for name in valid_names:
            errors = ValidationService.validate_profile_name(name)
            assert len(errors) == 0, f"Name '{name}' should be valid"

    def test_validate_profile_name_invalid(self):
        """Test validating invalid profile names."""
        invalid_cases = [
            ("", "empty name"),
            ("   ", "whitespace only"),
            ("a" * 101, "too long"),
            ("profile/name", "contains slash"),
            ("profile\\name", "contains backslash"),
            ("profile..name", "contains double dots"),
        ]

        for name, description in invalid_cases:
            errors = ValidationService.validate_profile_name(name)
            assert len(errors) > 0, f"Name '{name}' ({description}) should be invalid"

    def test_validate_config_structure_valid(self):
        """Test validating valid configuration structure."""
        valid_config = {
            "env": {
                "ANTHROPIC_BASE_URL": "https://api.anthropic.com",
                "ANTHROPIC_AUTH_TOKEN": "sk-ant-api03-token"
            },
            "model": "claude-3-opus-20240229",
            "max_tokens": 4096,
            "temperature": 0.7
        }

        errors = ValidationService.validate_config_structure(valid_config)

        assert len(errors) == 0

    def test_validate_config_structure_invalid_env(self):
        """Test validating configuration with invalid env section."""
        invalid_config = {
            "env": "not an object",  # Should be dict
            "model": "claude-3-opus-20240229"
        }

        errors = ValidationService.validate_config_structure(invalid_config)

        assert len(errors) > 0
        assert any("env.*must be a json object" in error.lower() for error in errors)

    def test_validate_config_structure_invalid_base_url(self):
        """Test validating configuration with invalid base URL."""
        invalid_config = {
            "env": {
                "ANTHROPIC_BASE_URL": "not-a-url"
            }
        }

        errors = ValidationService.validate_config_structure(invalid_config)

        assert len(errors) > 0
        assert any("base_url.*url" in error.lower() for error in errors)

    def test_validate_config_structure_invalid_token(self):
        """Test validating configuration with invalid auth token."""
        invalid_config = {
            "env": {
                "ANTHROPIC_AUTH_TOKEN": 123  # Should be string
            }
        }

        errors = ValidationService.validate_config_structure(invalid_config)

        assert len(errors) > 0
        assert any("auth_token.*must be a string" in error.lower() for error in errors)

    def test_validate_config_structure_invalid_model(self):
        """Test validating configuration with invalid model."""
        invalid_config = {
            "model": 123  # Should be string
        }

        errors = ValidationService.validate_config_structure(invalid_config)

        assert len(errors) > 0
        assert any("model.*must be a string" in error.lower() for error in errors)

    def test_validate_config_structure_invalid_max_tokens(self):
        """Test validating configuration with invalid max_tokens."""
        invalid_configs = [
            {"max_tokens": "not a number"},
            {"max_tokens": -100},
            {"max_tokens": 300000}  # Too large
        ]

        for config in invalid_configs:
            errors = ValidationService.validate_config_structure(config)
            assert len(errors) > 0

    def test_validate_config_structure_invalid_temperature(self):
        """Test validating configuration with invalid temperature."""
        invalid_configs = [
            {"temperature": "not a number"},
            {"temperature": -0.1},
            {"temperature": 2.1}
        ]

        for config in invalid_configs:
            errors = ValidationService.validate_config_structure(config)
            assert len(errors) > 0

    def test_detect_sensitive_data(self):
        """Test detecting sensitive data in JSON."""
        json_with_secrets = '''
        {
            "env": {
                "ANTHROPIC_AUTH_TOKEN": "sk-ant-api03-9471eac03e6b1611038a7681eac1ce3d782bcb135fe1c2bcd0c9d4fa74709029",
                "API_KEY": "secret-key-12345"
            }
        }
        '''

        sensitive_items = ValidationService.detect_sensitive_data(json_with_secrets)

        assert len(sensitive_items) >= 2

        # Check for Anthropic token
        anthropic_tokens = [item for item in sensitive_items if item['type'] == 'anthropic_api_token']
        assert len(anthropic_tokens) > 0

        # Check for API key
        api_keys = [item for item in sensitive_items if item['type'] == 'api_key']
        assert len(api_keys) > 0

    def test_mask_sensitive_data(self):
        """Test masking sensitive data."""
        json_with_token = '{"token": "sk-ant-api03-verylongtoken123456789"}'

        masked = ValidationService.mask_sensitive_data(json_with_token)

        assert "sk-ant-api03-veryl...6789" in masked
        assert "verylongtoken123456789" not in masked

    def test_validate_profile_completeness_complete(self):
        """Test validating complete profile."""
        complete_config = {
            "env": {
                "ANTHROPIC_BASE_URL": "https://api.anthropic.com",
                "ANTHROPIC_AUTH_TOKEN": "sk-ant-api03-token"
            },
            "model": "claude-3-opus-20240229",
            "max_tokens": 4096,
            "temperature": 0.7
        }

        warnings = ValidationService.validate_profile_completeness(complete_config)

        # Should have minimal warnings for complete config
        assert len(warnings) == 0 or len(warnings) <= 1

    def test_validate_profile_completeness_incomplete(self):
        """Test validating incomplete profile."""
        incomplete_config = {
            "model": "claude-3-opus-20240229",
            "max_tokens": 50,  # Very low
            "temperature": 1.8  # High temperature
        }

        warnings = ValidationService.validate_profile_completeness(incomplete_config)

        assert len(warnings) > 0

        # Should warn about missing env section
        warning_texts = ' '.join(warnings).lower()
        assert "env" in warning_texts or "environment" in warning_texts

    def test_get_validation_summary_valid(self):
        """Test getting validation summary for valid profile."""
        name = "Valid Profile"
        config_json = json.dumps({
            "env": {
                "ANTHROPIC_BASE_URL": "https://api.anthropic.com"
            },
            "model": "claude-3-opus-20240229"
        })

        summary = ValidationService.get_validation_summary(name, config_json)

        assert summary['valid'] is True
        assert len(summary['errors']) == 0
        assert 'sensitive_data' in summary
        assert 'warnings' in summary
        assert 'suggestions' in summary

    def test_get_validation_summary_invalid(self):
        """Test getting validation summary for invalid profile."""
        name = "Invalid Profile"
        config_json = '{"invalid": json}'  # Invalid JSON

        summary = ValidationService.get_validation_summary(name, config_json)

        assert summary['valid'] is False
        assert len(summary['errors']) > 0
        assert any("json" in error.lower() for error in summary['errors'])

    def test_validate_url_valid(self):
        """Test validating valid URLs."""
        valid_urls = [
            "https://api.anthropic.com",
            "http://localhost:8080",
            "https://api.example.com/v1"
        ]

        for url in valid_urls:
            errors = ValidationService.validate_url(url)
            assert len(errors) == 0, f"URL '{url}' should be valid"

    def test_validate_url_invalid(self):
        """Test validating invalid URLs."""
        invalid_urls = [
            "not-a-url",
            "ftp://api.anthropic.com",
            "api.anthropic.com"
        ]

        for url in invalid_urls:
            errors = ValidationService.validate_url(url)
            assert len(errors) > 0, f"URL '{url}' should be invalid"