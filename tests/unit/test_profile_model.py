"""
Unit tests for the Profile model.
"""

import pytest
import json
from datetime import datetime

from src.models.profile import Profile

class TestProfile:
    """Test cases for Profile model."""

    def test_create_new_profile(self):
        """Test creating a new profile."""
        name = "Test Profile"
        config_json = '{"env": {"ANTHROPIC_BASE_URL": "https://api.anthropic.com"}}'

        profile = Profile.create_new(name, config_json)

        assert profile.name == name
        assert profile.config_json == config_json
        assert profile.content_hash is not None
        assert len(profile.content_hash) == 64  # SHA-256 hex length
        assert profile.is_active is False
        assert profile.created_at is not None
        assert profile.updated_at is not None

    def test_calculate_content_hash(self):
        """Test content hash calculation."""
        config_json = '{"model": "claude-3-opus-20240229"}'
        hash1 = Profile.calculate_content_hash(config_json)
        hash2 = Profile.calculate_content_hash(config_json)

        assert hash1 == hash2
        assert len(hash1) == 64

        # Different JSON should produce different hash
        different_json = '{"model": "claude-3-sonnet-20240229"}'
        hash3 = Profile.calculate_content_hash(different_json)
        assert hash1 != hash3

    def test_from_dict(self):
        """Test creating profile from dictionary."""
        data = {
            'id': 1,
            'name': 'Test Profile',
            'config_json': '{"model": "claude-3-opus-20240229"}',
            'content_hash': 'abc123',
            'is_active': True,
            'created_at': '2025-10-17T14:30:00',
            'updated_at': '2025-10-17T14:30:00'
        }

        profile = Profile.from_dict(data)

        assert profile.id == 1
        assert profile.name == 'Test Profile'
        assert profile.config_json == '{"model": "claude-3-opus-20240229"}'
        assert profile.content_hash == 'abc123'
        assert profile.is_active is True
        assert isinstance(profile.created_at, datetime)
        assert isinstance(profile.updated_at, datetime)

    def test_to_dict(self):
        """Test converting profile to dictionary."""
        profile = Profile.create_new(
            "Test Profile",
            '{"model": "claude-3-opus-20240229"}'
        )
        profile.id = 1

        data = profile.to_dict()

        assert data['id'] == 1
        assert data['name'] == 'Test Profile'
        assert data['config_json'] == '{"model": "claude-3-opus-20240229"}'
        assert data['content_hash'] is not None
        assert data['is_active'] is False
        assert 'created_at' in data
        assert 'updated_at' in data

    def test_get_config_dict(self):
        """Test getting configuration as dictionary."""
        config_json = '{"model": "claude-3-opus-20240229", "max_tokens": 4096}'
        profile = Profile.create_new("Test", config_json)

        config_dict = profile.get_config_dict()

        assert isinstance(config_dict, dict)
        assert config_dict['model'] == 'claude-3-opus-20240229'
        assert config_dict['max_tokens'] == 4096

    def test_get_config_dict_invalid_json(self):
        """Test getting config dict with invalid JSON."""
        profile = Profile.create_new("Test", "invalid json")

        config_dict = profile.get_config_dict()

        assert config_dict == {}

    def test_update_config(self):
        """Test updating profile configuration."""
        profile = Profile.create_new("Test", '{"model": "claude-3-opus-20240229"}')
        original_hash = profile.content_hash
        original_updated = profile.updated_at

        new_config = '{"model": "claude-3-sonnet-20240229"}'
        profile.update_config(new_config)

        assert profile.config_json == new_config
        assert profile.content_hash != original_hash
        assert profile.updated_at > original_updated

    def test_get_base_url(self):
        """Test extracting base URL from configuration."""
        config_json = '''
        {
            "env": {
                "ANTHROPIC_BASE_URL": "https://api.anthropic.com"
            }
        }
        '''
        profile = Profile.create_new("Test", config_json)

        base_url = profile.get_base_url()
        assert base_url == "https://api.anthropic.com"

        # Test with no base URL
        config_json_no_url = '{"model": "claude-3-opus-20240229"}'
        profile.update_config(config_json_no_url)

        base_url = profile.get_base_url()
        assert base_url == ""

    def test_get_auth_token_masked(self):
        """Test masking authentication token."""
        config_json = '''
        {
            "env": {
                "ANTHROPIC_AUTH_TOKEN": "sk-ant-api03-9471eac03e6b1611038a7681eac1ce3d782bcb135fe1c2bcd0c9d4fa74709029"
            }
        }
        '''
        profile = Profile.create_new("Test", config_json)

        masked_token = profile.get_auth_token_masked()
        assert masked_token.startswith("sk-ant") and "..." in masked_token and masked_token.endswith("9029")

        # Test with no token
        config_json_no_token = '{"model": "claude-3-opus-20240229"}'
        profile.update_config(config_json_no_token)

        masked_token = profile.get_auth_token_masked()
        assert masked_token == ""

    def test_get_model(self):
        """Test extracting model from configuration."""
        config_json = '{"model": "claude-3-opus-20240229"}'
        profile = Profile.create_new("Test", config_json)

        model = profile.get_model()
        assert model == "claude-3-opus-20240229"

        # Test with no model
        config_json_no_model = '{"max_tokens": 4096}'
        profile.update_config(config_json_no_model)

        model = profile.get_model()
        assert model == ""

    def test_validate_valid_profile(self):
        """Test validating a valid profile."""
        config_json = '''
        {
            "env": {
                "ANTHROPIC_BASE_URL": "https://api.anthropic.com",
                "ANTHROPIC_AUTH_TOKEN": "sk-ant-api03-token"
            },
            "model": "claude-3-opus-20240229"
        }
        '''
        profile = Profile.create_new("Valid Profile", config_json)

        errors = profile.validate()
        assert len(errors) == 0

    def test_validate_invalid_name(self):
        """Test validating profile with invalid name."""
        profile = Profile.create_new("", '{"model": "claude-3-opus-20240229"}')

        errors = profile.validate()
        assert len(errors) > 0
        assert any("name is required" in error.lower() for error in errors)

        # Test name too long
        long_name = "x" * 101
        profile.name = long_name
        errors = profile.validate()
        assert any("100 characters" in error for error in errors)

    def test_validate_invalid_json(self):
        """Test validating profile with invalid JSON."""
        profile = Profile.create_new("Test", "invalid json")

        errors = profile.validate()
        assert len(errors) > 0
        assert any("invalid json" in error.lower() for error in errors)

    def test_str_representation(self):
        """Test string representation of profile."""
        profile = Profile.create_new("Test Profile", '{"model": "claude-3-opus-20240229"}')
        profile.id = 1

        str_repr = str(profile)
        assert "Test Profile" in str_repr
        assert "id=1" in str_repr

    def test_repr_representation(self):
        """Test detailed string representation of profile."""
        profile = Profile.create_new("Test Profile", '{"model": "claude-3-opus-20240229"}')
        profile.id = 1

        repr_str = repr(profile)
        assert "Test Profile" in repr_str
        assert "id=1" in repr_str
        assert "hash=" in repr_str