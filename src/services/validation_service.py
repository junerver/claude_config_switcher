"""
Validation service for JSON configurations and profile data.
"""

import json
import re
from typing import List, Dict, Any, Tuple, Optional

from ..utils.logger import get_logger
from ..utils.exceptions import ValidationError, InvalidJSONError

logger = get_logger(__name__)

class ValidationService:
    """Service for validating JSON configurations and profile data."""

    # Patterns for detecting sensitive data
    SENSITIVE_PATTERNS = [
        r'sk-ant-api03-[a-zA-Z0-9_-]+',  # Anthropic API tokens
        r'sk-[a-zA-Z0-9_-]+',           # General API keys
        r'[a-zA-Z0-9_-]{20,}',         # Long alphanumeric strings (likely keys)
        r'password\s*[:=]\s*[^\s,}]+',  # Password fields
        r'secret\s*[:=]\s*[^\s,}]+',    # Secret fields
        r'token\s*[:=]\s*[^\s,}]+',     # Token fields
        r'key\s*[:=]\s*[^\s,}]+',       # Key fields
    ]

    @staticmethod
    def validate_json_syntax(json_str: str) -> List[str]:
        """
        Validate JSON syntax.

        Args:
            json_str: JSON string to validate

        Returns:
            List of validation error messages
        """
        errors = []

        if not json_str or not json_str.strip():
            errors.append("JSON content is empty")
            return errors

        try:
            parsed = json.loads(json_str)
        except json.JSONDecodeError as e:
            errors.append(f"JSON syntax error: {e.msg} at line {e.lineno}, column {e.colno}")
        except Exception as e:
            errors.append(f"Unexpected error parsing JSON: {str(e)}")

        return errors

    @staticmethod
    def validate_profile_name(name: str) -> List[str]:
        """
        Validate profile name.

        Args:
            name: Profile name to validate

        Returns:
            List of validation error messages
        """
        errors = []

        if not name or not name.strip():
            errors.append("Profile name is required")
            return errors

        name = name.strip()

        if len(name) > 100:
            errors.append("Profile name must be 100 characters or less")

        # Check for invalid characters
        invalid_chars = ['/', '\\', '..', '\0', '\n', '\r', '\t']
        for char in invalid_chars:
            if char in name:
                errors.append(f"Profile name contains invalid character: {repr(char)}")

        # Check for control characters
        if any(ord(c) < 32 for c in name):
            errors.append("Profile name contains control characters")

        return errors

    @staticmethod
    def validate_config_structure(config_data: Dict[str, Any]) -> List[str]:
        """
        Validate Claude Code configuration structure.

        Args:
            config_data: Parsed configuration dictionary

        Returns:
            List of validation error messages
        """
        errors = []

        if not isinstance(config_data, dict):
            errors.append("Configuration must be a JSON object")
            return errors

        # Validate env section if present
        if 'env' in config_data:
            env = config_data['env']
            if not isinstance(env, dict):
                errors.append("'env' section must be a JSON object")
            else:
                # Validate common environment variables
                if 'ANTHROPIC_BASE_URL' in env:
                    base_url = env['ANTHROPIC_BASE_URL']
                    if not isinstance(base_url, str):
                        errors.append("ANTHROPIC_BASE_URL must be a string")
                    elif not base_url.strip():
                        errors.append("ANTHROPIC_BASE_URL cannot be empty")
                    else:
                        # Basic URL validation
                        url_validation = ValidationService.validate_url(base_url)
                        if url_validation:
                            errors.extend([f"ANTHROPIC_BASE_URL: {err}" for err in url_validation])

                if 'ANTHROPIC_AUTH_TOKEN' in env:
                    token = env['ANTHROPIC_AUTH_TOKEN']
                    if not isinstance(token, str):
                        errors.append("ANTHROPIC_AUTH_TOKEN must be a string")
                    elif not token.strip():
                        errors.append("ANTHROPIC_AUTH_TOKEN cannot be empty")

        # Validate model if present
        if 'model' in config_data:
            model = config_data['model']
            if not isinstance(model, str):
                errors.append("Model must be a string")
            elif not model.strip():
                errors.append("Model cannot be empty")

        # Validate max_tokens if present
        if 'max_tokens' in config_data:
            max_tokens = config_data['max_tokens']
            if not isinstance(max_tokens, int):
                errors.append("max_tokens must be an integer")
            elif max_tokens <= 0:
                errors.append("max_tokens must be greater than 0")
            elif max_tokens > 200000:  # Reasonable upper limit
                errors.append("max_tokens is unusually large (maximum 200000)")

        # Validate temperature if present
        if 'temperature' in config_data:
            temperature = config_data['temperature']
            if not isinstance(temperature, (int, float)):
                errors.append("temperature must be a number")
            elif not (0.0 <= temperature <= 2.0):
                errors.append("temperature must be between 0.0 and 2.0")

        return errors

    @staticmethod
    def validate_url(url: str) -> List[str]:
        """
        Validate URL format.

        Args:
            url: URL to validate

        Returns:
            List of validation error messages
        """
        errors = []

        if not url.startswith(('http://', 'https://')):
            errors.append("URL must start with http:// or https://")
        else:
            # Basic URL structure validation
            url_pattern = re.compile(
                r'^https?://'  # http:// or https://
                r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
                r'localhost|'  # localhost...
                r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
                r'(?::\d+)?'  # optional port
                r'(?:/?|[/?]\S+)$', re.IGNORECASE)

            if not url_pattern.match(url):
                errors.append("URL format is invalid")

        return errors

    @staticmethod
    def detect_sensitive_data(json_str: str) -> List[Dict[str, Any]]:
        """
        Detect potentially sensitive data in JSON.

        Args:
            json_str: JSON string to scan

        Returns:
            List of detected sensitive data items
        """
        sensitive_items = []

        for pattern in ValidationService.SENSITIVE_PATTERNS:
            matches = re.finditer(pattern, json_str, re.IGNORECASE)
            for match in matches:
                # Get context around the match
                start = max(0, match.start() - 50)
                end = min(len(json_str), match.end() + 50)
                context = json_str[start:end]

                sensitive_items.append({
                    'pattern': pattern,
                    'match': match.group(),
                    'start': match.start(),
                    'end': match.end(),
                    'context': context,
                    'type': ValidationService._classify_sensitive_data(match.group())
                })

        return sensitive_items

    @staticmethod
    def _classify_sensitive_data(match: str) -> str:
        """Classify the type of sensitive data."""
        if match.startswith('sk-ant-api03'):
            return 'anthropic_api_token'
        elif match.startswith('sk-'):
            return 'api_key'
        elif 'password' in match.lower():
            return 'password'
        elif 'secret' in match.lower():
            return 'secret'
        elif 'token' in match.lower():
            return 'token'
        elif 'key' in match.lower():
            return 'key'
        else:
            return 'unknown'

    @staticmethod
    def mask_sensitive_data(json_str: str, visible_chars: int = 8) -> str:
        """
        Mask sensitive data in JSON string.

        Args:
            json_str: JSON string to mask
            visible_chars: Number of characters to show at beginning and end

        Returns:
            JSON string with sensitive data masked
        """
        masked_json = json_str
        sensitive_items = ValidationService.detect_sensitive_data(json_str)

        # Sort by position in reverse order to avoid offset issues
        sensitive_items.sort(key=lambda x: x['start'], reverse=True)

        for item in sensitive_items:
            match = item['match']
            if len(match) > visible_chars * 2:
                masked_value = f"{match[:visible_chars]}...{match[-visible_chars:]}"
            else:
                masked_value = f"{match[:visible_chars]}..."

            # Replace the sensitive data
            start = item['start']
            end = item['end']
            masked_json = masked_json[:start] + masked_value + masked_json[end:]

        return masked_json

    @staticmethod
    def validate_profile_completeness(profile_data: Dict[str, Any]) -> List[str]:
        """
        Validate profile completeness for usability.

        Args:
            profile_data: Profile data dictionary

        Returns:
            List of warning messages (not errors)
        """
        warnings = []

        # Check for essential configuration
        if 'env' not in profile_data:
            warnings.append("No 'env' section found - environment variables may not be set")
        else:
            env = profile_data['env']
            if 'ANTHROPIC_BASE_URL' not in env:
                warnings.append("ANTHROPIC_BASE_URL not set in environment variables")
            if 'ANTHROPIC_AUTH_TOKEN' not in env:
                warnings.append("ANTHROPIC_AUTH_TOKEN not set in environment variables")

        # Check for model configuration
        if 'model' not in profile_data:
            warnings.append("No model specified - will use default model")

        # Check for potentially problematic configurations
        if profile_data.get('temperature', 1.0) > 1.5:
            warnings.append("High temperature setting may produce unpredictable results")

        if profile_data.get('max_tokens', 4096) < 100:
            warnings.append("Very low max_tokens setting may truncate responses")

        return warnings

    @staticmethod
    def get_validation_summary(
        name: str,
        config_json: str
    ) -> Dict[str, Any]:
        """
        Get comprehensive validation summary for a profile.

        Args:
            name: Profile name
            config_json: JSON configuration string

        Returns:
            Validation summary dictionary
        """
        summary = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'sensitive_data': [],
            'suggestions': []
        }

        # Validate profile name
        name_errors = ValidationService.validate_profile_name(name)
        summary['errors'].extend(name_errors)

        # Validate JSON syntax
        json_errors = ValidationService.validate_json_syntax(config_json)
        summary['errors'].extend(json_errors)

        # If JSON is valid, validate structure
        if not json_errors:
            try:
                config_data = json.loads(config_json)

                # Validate structure
                structure_errors = ValidationService.validate_config_structure(config_data)
                summary['errors'].extend(structure_errors)

                # Check completeness
                warnings = ValidationService.validate_profile_completeness(config_data)
                summary['warnings'].extend(warnings)

                # Detect sensitive data
                sensitive_data = ValidationService.detect_sensitive_data(config_json)
                summary['sensitive_data'] = sensitive_data

                # Add suggestions based on configuration
                suggestions = ValidationService._get_suggestions(config_data)
                summary['suggestions'] = suggestions

            except Exception as e:
                summary['errors'].append(f"Error analyzing configuration: {str(e)}")

        # Overall validity
        summary['valid'] = len(summary['errors']) == 0

        return summary

    @staticmethod
    def _get_suggestions(config_data: Dict[str, Any]) -> List[str]:
        """Get suggestions for improving configuration."""
        suggestions = []

        # Model suggestions
        if 'model' not in config_data:
            suggestions.append("Consider specifying a model for consistent behavior")

        # Token suggestions
        if 'max_tokens' not in config_data:
            suggestions.append("Consider setting max_tokens to control response length")
        elif config_data['max_tokens'] > 100000:
            suggestions.append("Very high max_tokens value - consider reducing for cost control")

        # Temperature suggestions
        if 'temperature' not in config_data:
            suggestions.append("Consider setting temperature for response consistency")

        return suggestions