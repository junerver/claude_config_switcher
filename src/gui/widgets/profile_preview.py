"""
Profile preview dialog for viewing formatted JSON configurations.
"""

import tkinter as tk
from tkinter import messagebox, scrolledtext
import customtkinter as ctk
from typing import Optional, Dict, Any
import json

from models.profile import Profile
from services.validation_service import ValidationService
from utils.logger import get_logger

logger = get_logger(__name__)

class ProfilePreviewDialog(ctk.CTkToplevel):
    """Dialog for previewing profile configurations."""

    def __init__(
        self,
        parent,
        profile: Profile,
        show_secrets: bool = False
    ):
        """
        Initialize profile preview dialog.

        Args:
            parent: Parent window
            profile: Profile to preview
            show_secrets: Whether to show sensitive data
        """
        super().__init__(parent)

        self.profile = profile
        self.show_secrets = show_secrets

        self._setup_dialog()
        self._create_widgets()
        self._load_profile_data()

    def _setup_dialog(self):
        """Setup dialog properties."""
        self.title(f"Profile Preview: {self.profile.name}")
        self.geometry("800x600")
        self.resizable(True, True)

        # Minimum size
        self.minsize(600, 500)

        # Make dialog modal
        self.transient(self.master)
        self.grab_set()

        # Center dialog on parent
        self._center_dialog()

    def _center_dialog(self):
        """Center dialog on parent window."""
        self.update_idletasks()
        x = (self.master.winfo_screenwidth() // 2) - (self.winfo_width() // 2)
        y = (self.master.winfo_screenheight() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")

    def _create_widgets(self):
        """Create dialog widgets."""
        # Main container
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Header frame
        header_frame = ctk.CTkFrame(main_frame)
        header_frame.pack(fill="x", pady=(0, 15))

        # Profile name and status
        name_text = self.profile.name
        if self.profile.is_active:
            name_text = f"✓ {name_text} (Active)"

        name_label = ctk.CTkLabel(
            header_frame,
            text=name_text,
            font=ctk.CTkFont(size=18, weight="bold")
        )
        name_label.pack(anchor="w", padx=15, pady=(15, 5))

        # Profile metadata
        metadata_frame = ctk.CTkFrame(header_frame)
        metadata_frame.pack(fill="x", padx=15, pady=(0, 15))

        # Created date
        if self.profile.created_at:
            created_label = ctk.CTkLabel(
                metadata_frame,
                text=f"Created: {self.profile.created_at.strftime('%Y-%m-%d %H:%M:%S')}",
                font=ctk.CTkFont(size=11),
                text_color=("#6b7280", "#9ca3af")
            )
            created_label.pack(anchor="w")

        # Updated date
        if self.profile.updated_at:
            updated_label = ctk.CTkLabel(
                metadata_frame,
                text=f"Updated: {self.profile.updated_at.strftime('%Y-%m-%d %H:%M:%S')}",
                font=ctk.CTkFont(size=11),
                text_color=("#6b7280", "#9ca3af")
            )
            updated_label.pack(anchor="w")

        # Content hash
        hash_label = ctk.CTkLabel(
            metadata_frame,
            text=f"Hash: {self.profile.content_hash[:16]}...",
            font=ctk.CTkFont(size=10, family="monospace"),
            text_color=("#9ca3af", "#6b7280")
        )
        hash_label.pack(anchor="w", pady=(5, 0))

        # Configuration preview frame
        config_frame = ctk.CTkFrame(main_frame)
        config_frame.pack(fill="both", expand=True, pady=(0, 15))

        config_label = ctk.CTkLabel(
            config_frame,
            text="Configuration JSON:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        config_label.pack(anchor="w", padx=15, pady=(15, 5))

        # JSON display with line numbers
        json_display_frame = ctk.CTkFrame(config_frame)
        json_display_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        # Line numbers
        self.line_numbers = ctk.CTkTextbox(
            json_display_frame,
            width=50,
            font=ctk.CTkFont(family="Consolas, monospace", size=11)
        )
        self.line_numbers.pack(side="left", fill="y")
        self.line_numbers.configure(state="disabled")

        # JSON text display
        self.json_text = ctk.CTkTextbox(
            json_display_frame,
            font=ctk.CTkFont(family="Consolas, monospace", size=11)
        )
        self.json_text.pack(side="left", fill="both", expand=True)

        # Validation and info frame
        info_frame = ctk.CTkFrame(main_frame)
        info_frame.pack(fill="x", pady=(0, 15))

        # Validation status
        self.validation_label = ctk.CTkLabel(
            info_frame,
            text="",
            font=ctk.CTkFont(size=11)
        )
        self.validation_label.pack(anchor="w", padx=15, pady=(10, 5))

        # Sensitive data warning
        sensitive_data = ValidationService.detect_sensitive_data(self.profile.config_json)
        if sensitive_data:
            warning_label = ctk.CTkLabel(
                info_frame,
                text=f"⚠️ Contains {len(sensitive_data)} potentially sensitive data items",
                font=ctk.CTkFont(size=11),
                text_color=("#f59e0b", "#f59e0b")
            )
            warning_label.pack(anchor="w", padx=15, pady=(0, 10))

        # Button frame
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(fill="x", pady=(15, 0))

        # Toggle secrets button
        self.toggle_button = ctk.CTkButton(
            button_frame,
            text="Show Sensitive Data" if not self.show_secrets else "Hide Sensitive Data",
            command=self._toggle_secrets
        )
        self.toggle_button.pack(side="left", padx=15, pady=15)

        # Copy button
        copy_button = ctk.CTkButton(
            button_frame,
            text="Copy JSON",
            command=self._copy_json
        )
        copy_button.pack(side="left", padx=5, pady=15)

        # Validate button
        validate_button = ctk.CTkButton(
            button_frame,
            text="Validate",
            command=self._validate_configuration
        )
        validate_button.pack(side="left", padx=5, pady=15)

        # Close button
        close_button = ctk.CTkButton(
            button_frame,
            text="Close",
            command=self.destroy
        )
        close_button.pack(side="right", padx=15, pady=15)

    # Syntax highlighting removed - CustomTkinter CTkTextbox doesn't support tagging

    def _load_profile_data(self):
        """Load profile data into dialog."""
        try:
            # Parse and format JSON
            config_data = json.loads(self.profile.config_json)
            formatted_json = json.dumps(config_data, indent=2, sort_keys=True)

            # Mask sensitive data if needed
            if not self.show_secrets:
                formatted_json = ValidationService.mask_sensitive_data(formatted_json)

            # Display JSON
            self.json_text.insert("1.0", formatted_json)
            self._update_line_numbers()

            # Perform basic validation
            self._show_validation_status()

        except Exception as e:
            logger.error(f"Failed to load profile data: {e}")
            self.json_text.insert("1.0", f"Error loading configuration: {e}")

    def _update_line_numbers(self):
        """Update line numbers display."""
        content = self.json_text.get("1.0", "end-1c")
        lines = content.split('\n')
        line_numbers = '\n'.join(str(i + 1) for i in range(len(lines)))

        self.line_numbers.configure(state="normal")
        self.line_numbers.delete("1.0", "end")
        self.line_numbers.insert("1.0", line_numbers)
        self.line_numbers.configure(state="disabled")

    # Syntax highlighting methods removed - CustomTkinter doesn't support tagging

    def _get_string_length(self, content, current_pos):
        """Get the length of the current string."""
        # Find the last unmatched quote
        string_start = current_pos - 1
        while string_start >= 0:
            if content[string_start] == '"':
                # Check if it's escaped
                escaped = False
                escape_check = string_start - 1
                while escape_check >= 0 and content[escape_check] == '\\':
                    escaped = not escaped
                    escape_check -= 1
                if not escaped:
                    break
            string_start -= 1
        return current_pos - string_start

    def _get_keyword_at_position(self, content, pos):
        """Get keyword at position."""
        keywords = ['true', 'false', 'null']
        for keyword in keywords:
            if content.startswith(keyword, pos):
                return keyword
        return ''

    def _show_validation_status(self):
        """Show validation status."""
        try:
            validation_summary = ValidationService.get_validation_summary(
                self.profile.name,
                self.profile.config_json
            )

            if validation_summary['valid']:
                self.validation_label.configure(
                    text="✓ Configuration is valid",
                    text_color=("#16a34a", "#16a34a")
                )
            else:
                error_count = len(validation_summary['errors'])
                self.validation_label.configure(
                    text=f"✗ {error_count} validation error(s)",
                    text_color=("#dc2626", "#dc2626")
                )

            if validation_summary['warnings']:
                warning_text = f"⚠️ {len(validation_summary['warnings'])} warning(s)"
                # Could add additional display for warnings if needed

        except Exception as e:
            self.validation_label.configure(
                text="Validation check failed",
                text_color=("#dc2626", "#dc2626")
            )

    def _toggle_secrets(self):
        """Toggle visibility of sensitive data."""
        self.show_secrets = not self.show_secrets

        # Update button text
        self.toggle_button.configure(
            text="Hide Sensitive Data" if self.show_secrets else "Show Sensitive Data"
        )

        # Reload JSON content
        self.json_text.delete("1.0", "end")
        self._load_profile_data()

    def _copy_json(self):
        """Copy JSON to clipboard."""
        try:
            # Get original JSON (unmasked)
            config_data = json.loads(self.profile.config_json)
            formatted_json = json.dumps(config_data, indent=2, sort_keys=True)

            # Copy to clipboard
            self.clipboard_clear()
            self.clipboard_append(formatted_json)

            # Show success message briefly
            original_text = self.toggle_button.cget("text")
            self.toggle_button.configure(text="✓ Copied!")
            self.after(2000, lambda: self.toggle_button.configure(text=original_text))

        except Exception as e:
            logger.error(f"Failed to copy JSON: {e}")
            messagebox.showerror("Error", f"Failed to copy JSON: {e}")

    def _validate_configuration(self):
        """Validate configuration and show detailed results."""
        try:
            validation_summary = ValidationService.get_validation_summary(
                self.profile.name,
                self.profile.config_json
            )

            # Create validation results dialog
            results_dialog = ctk.CTkToplevel(self)
            results_dialog.title("Validation Results")
            results_dialog.geometry("500x400")
            results_dialog.transient(self)
            results_dialog.grab_set()

            # Results container
            results_frame = ctk.CTkScrollableFrame(results_dialog)
            results_frame.pack(fill="both", expand=True, padx=20, pady=20)

            # Overall status
            status_text = "✓ Valid" if validation_summary['valid'] else "✗ Invalid"
            status_color = ("#16a34a", "#16a34a") if validation_summary['valid'] else ("#dc2626", "#dc2626")

            status_label = ctk.CTkLabel(
                results_frame,
                text=f"Configuration Status: {status_text}",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color=status_color
            )
            status_label.pack(anchor="w", pady=(0, 15))

            # Errors
            if validation_summary['errors']:
                errors_label = ctk.CTkLabel(
                    results_frame,
                    text=f"Errors ({len(validation_summary['errors'])}):",
                    font=ctk.CTkFont(size=12, weight="bold"),
                    text_color=("#dc2626", "#dc2626")
                )
                errors_label.pack(anchor="w", pady=(10, 5))

                for error in validation_summary['errors']:
                    error_label = ctk.CTkLabel(
                        results_frame,
                        text=f"• {error}",
                        font=ctk.CTkFont(size=11),
                        text_color=("#dc2626", "#dc2626")
                    )
                    error_label.pack(anchor="w", padx=(20, 0))

            # Warnings
            if validation_summary['warnings']:
                warnings_label = ctk.CTkLabel(
                    results_frame,
                    text=f"Warnings ({len(validation_summary['warnings'])}):",
                    font=ctk.CTkFont(size=12, weight="bold"),
                    text_color=("#f59e0b", "#f59e0b")
                )
                warnings_label.pack(anchor="w", pady=(10, 5))

                for warning in validation_summary['warnings']:
                    warning_label = ctk.CTkLabel(
                        results_frame,
                        text=f"• {warning}",
                        font=ctk.CTkFont(size=11),
                        text_color=("#f59e0b", "#f59e0b")
                    )
                    warning_label.pack(anchor="w", padx=(20, 0))

            # Suggestions
            if validation_summary['suggestions']:
                suggestions_label = ctk.CTkLabel(
                    results_frame,
                    text=f"Suggestions ({len(validation_summary['suggestions'])}):",
                    font=ctk.CTkFont(size=12, weight="bold")
                )
                suggestions_label.pack(anchor="w", pady=(10, 5))

                for suggestion in validation_summary['suggestions']:
                    suggestion_label = ctk.CTkLabel(
                        results_frame,
                        text=f"• {suggestion}",
                        font=ctk.CTkFont(size=11)
                    )
                    suggestion_label.pack(anchor="w", padx=(20, 0))

            # Close button
            close_button = ctk.CTkButton(
                results_dialog,
                text="Close",
                command=results_dialog.destroy
            )
            close_button.pack(pady=15)

        except Exception as e:
            logger.error(f"Failed to validate configuration: {e}")
            messagebox.showerror("Error", f"Failed to validate configuration: {e}")