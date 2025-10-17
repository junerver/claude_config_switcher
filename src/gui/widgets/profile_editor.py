"""
Profile editor dialog for creating and editing configuration profiles.
"""

import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
from typing import Optional, Dict, Any
import json

from models.profile import Profile
from utils.logger import get_logger
from utils.exceptions import ValidationError, InvalidJSONError

logger = get_logger(__name__)

class ProfileEditorDialog(ctk.CTkToplevel):
    """Dialog for creating and editing configuration profiles."""

    def __init__(
        self,
        parent,
        title: str = "Create Profile",
        profile: Optional[Profile] = None
    ):
        """
        Initialize profile editor dialog.

        Args:
            parent: Parent window
            title: Dialog title
            profile: Existing profile to edit (None for new profile)
        """
        super().__init__(parent)

        self.profile = profile
        self.result_profile = None
        self.is_edit_mode = profile is not None

        self._setup_dialog(title)
        self._create_widgets()
        self._load_profile_data()

    def _setup_dialog(self, title: str):
        """Setup dialog properties."""
        self.title(title)
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

        # Title
        title_text = "Edit Profile" if self.is_edit_mode else "Create New Profile"
        title_label = ctk.CTkLabel(
            main_frame,
            text=title_text,
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(fill="x", pady=(0, 20))

        # Profile name frame
        name_frame = ctk.CTkFrame(main_frame)
        name_frame.pack(fill="x", pady=(0, 15))

        name_label = ctk.CTkLabel(
            name_frame,
            text="Profile Name:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        name_label.pack(anchor="w", padx=15, pady=(15, 5))

        self.name_var = tk.StringVar()
        self.name_entry = ctk.CTkEntry(
            name_frame,
            textvariable=self.name_var,
            placeholder_text="Enter profile name (e.g., Production, Development, Testing)"
        )
        self.name_entry.pack(fill="x", padx=15, pady=(0, 15))

        # JSON configuration frame
        config_frame = ctk.CTkFrame(main_frame)
        config_frame.pack(fill="both", expand=True, pady=(0, 15))

        config_label = ctk.CTkLabel(
            config_frame,
            text="JSON Configuration:",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        config_label.pack(anchor="w", padx=15, pady=(15, 5))

        # JSON editor with line numbers
        editor_frame = ctk.CTkFrame(config_frame)
        editor_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        # Line numbers
        self.line_numbers = ctk.CTkTextbox(
            editor_frame,
            width=50,
            font=ctk.CTkFont(family="Consolas, monospace", size=12)
        )
        self.line_numbers.pack(side="left", fill="y")
        self.line_numbers.configure(state="disabled")

        # JSON text editor
        self.json_text = ctk.CTkTextbox(
            editor_frame,
            font=ctk.CTkFont(family="Consolas, monospace", size=12)
        )
        self.json_text.pack(side="left", fill="both", expand=True)

        # Bind events
        self.json_text.bind("<KeyRelease>", self._on_text_change)
        self.json_text.bind("<Button-1>", self._on_text_change)
        self.json_text.bind("<MouseWheel>", self._on_text_change)

        # Validation and helper frame
        validation_frame = ctk.CTkFrame(main_frame)
        validation_frame.pack(fill="x", pady=(0, 15))

        # Validate button
        validate_button = ctk.CTkButton(
            validation_frame,
            text="Validate JSON",
            command=self._validate_json
        )
        validate_button.pack(side="left", padx=15, pady=10)

        # Format button
        format_button = ctk.CTkButton(
            validation_frame,
            text="Format JSON",
            command=self._format_json
        )
        format_button.pack(side="left", padx=5, pady=10)

        # Show/hide tokens button
        self.show_tokens_var = tk.BooleanVar(value=False)
        tokens_button = ctk.CTkButton(
            validation_frame,
            text="Show Auth Tokens",
            command=self._toggle_token_visibility
        )
        tokens_button.pack(side="left", padx=5, pady=10)

        # Template dropdown
        template_label = ctk.CTkLabel(validation_frame, text="Templates:")
        template_label.pack(side="left", padx=(20, 5), pady=10)

        self.template_var = tk.StringVar()
        template_dropdown = ctk.CTkOptionMenu(
            validation_frame,
            values=["Empty", "Development", "Production", "Testing"],
            variable=self.template_var,
            command=self._load_template
        )
        template_dropdown.pack(side="left", padx=5, pady=10)

        # Status label
        self.status_label = ctk.CTkLabel(
            validation_frame,
            text="",
            font=ctk.CTkFont(size=11)
        )
        self.status_label.pack(side="right", padx=15, pady=10)

        # Button frame
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(fill="x", pady=(15, 0))

        # Cancel button
        cancel_button = ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=self._on_cancel
        )
        cancel_button.pack(side="right", padx=(10, 15), pady=15)

        # Save button
        save_button = ctk.CTkButton(
            button_frame,
            text="Save Profile",
            command=self._on_save
        )
        save_button.pack(side="right", padx=15, pady=15)

        # Initial line numbers update
        self._update_line_numbers()

    # Syntax highlighting removed - CustomTkinter CTkTextbox doesn't support tag_configure

    def _load_profile_data(self):
        """Load existing profile data into form."""
        if self.profile:
            self.name_var.set(self.profile.name)
            self.json_text.insert("1.0", self.profile.config_json)
            self._update_line_numbers()
            self._apply_syntax_highlighting()

    def _load_template(self, template_name: str):
        """Load a configuration template."""
        templates = {
            "Empty": "{}",
            "Development": {
                "env": {
                    "ANTHROPIC_BASE_URL": "https://api.dev.anthropic.com",
                    "ANTHROPIC_AUTH_TOKEN": "sk-ant-api03-dev-token"
                },
                "model": "claude-3-haiku-20240307",
                "max_tokens": 4096,
                "temperature": 0.7
            },
            "Production": {
                "env": {
                    "ANTHROPIC_BASE_URL": "https://api.anthropic.com",
                    "ANTHROPIC_AUTH_TOKEN": "sk-ant-api03-prod-token"
                },
                "model": "claude-3-opus-20240229",
                "max_tokens": 8192,
                "temperature": 0.1
            },
            "Testing": {
                "env": {
                    "ANTHROPIC_BASE_URL": "https://api.test.anthropic.com",
                    "ANTHROPIC_AUTH_TOKEN": "sk-ant-api03-test-token"
                },
                "model": "claude-3-sonnet-20240229",
                "max_tokens": 2048,
                "temperature": 0.5
            }
        }

        if template_name in templates:
            template_content = json.dumps(templates[template_name], indent=2)
            self.json_text.delete("1.0", "end")
            self.json_text.insert("1.0", template_content)
            self._update_line_numbers()
            self.status_label.configure(text=f"Loaded {template_name} template", text_color=("green", "green"))

    def _on_text_change(self, event=None):
        """Handle text change events."""
        self._update_line_numbers()

    def _update_line_numbers(self):
        """Update line numbers display."""
        # Get current text
        content = self.json_text.get("1.0", "end-1c")
        lines = content.split('\n')

        # Generate line numbers
        line_numbers = '\n'.join(str(i + 1) for i in range(len(lines)))

        # Update line numbers display
        self.line_numbers.configure(state="normal")
        self.line_numbers.delete("1.0", "end")
        self.line_numbers.insert("1.0", line_numbers)
        self.line_numbers.configure(state="disabled")

    # Syntax highlighting methods removed - CustomTkinter doesn't support text tagging

    def _get_string_start(self, content, current_pos):
        """Get the start position of the current string."""
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

    def _validate_json(self):
        """Validate JSON syntax."""
        content = self.json_text.get("1.0", "end-1c").strip()

        if not content:
            self.status_label.configure(text="Please enter JSON configuration", text_color=("orange", "orange"))
            return False

        try:
            json.loads(content)
            self.status_label.configure(text="✓ Valid JSON", text_color=("green", "green"))
            return True
        except json.JSONDecodeError as e:
            self.status_label.configure(text=f"✗ JSON Error: {e.msg}", text_color=("red", "red"))
            return False

    def _format_json(self):
        """Format JSON with proper indentation."""
        content = self.json_text.get("1.0", "end-1c").strip()

        if not content:
            return

        try:
            # Parse and reformat JSON
            parsed = json.loads(content)
            formatted = json.dumps(parsed, indent=2, sort_keys=True)

            # Update text widget
            self.json_text.delete("1.0", "end")
            self.json_text.insert("1.0", formatted)

            # Update line numbers
            self._update_line_numbers()

            self.status_label.configure(text="✓ JSON formatted", text_color=("green", "green"))

        except json.JSONDecodeError as e:
            self.status_label.configure(text=f"✗ Cannot format invalid JSON: {e.msg}", text_color=("red", "red"))

    def _toggle_token_visibility(self):
        """Toggle visibility of authentication tokens."""
        content = self.json_text.get("1.0", "end-1c")

        try:
            data = json.loads(content)

            if 'env' in data and 'ANTHROPIC_AUTH_TOKEN' in data['env']:
                token = data['env']['ANTHROPIC_AUTH_TOKEN']

                if self.show_tokens_var.get():
                    # Show full token
                    # (Token is already shown)
                    self.status_label.configure(text="Auth tokens visible", text_color=("orange", "orange"))
                else:
                    # Mask token
                    if token and len(token) > 10:
                        masked_token = f"{token[:8]}...{token[-4:]}"
                        data['env']['ANTHROPIC_AUTH_TOKEN'] = masked_token
                        content = json.dumps(data, indent=2)
                        self.json_text.delete("1.0", "end")
                        self.json_text.insert("1.0", content)
                        self._update_line_numbers()
                        self._apply_syntax_highlighting()

                    self.status_label.configure(text="Auth tokens masked", text_color=("green", "green"))

        except json.JSONDecodeError:
            self.status_label.configure(text="Cannot mask tokens in invalid JSON", text_color=("red", "red"))

    def _validate_form(self) -> bool:
        """Validate form data."""
        # Validate profile name
        name = self.name_var.get().strip()
        if not name:
            self.status_label.configure(text="Profile name is required", text_color=("red", "red"))
            return False

        if len(name) > 100:
            self.status_label.configure(text="Profile name must be 100 characters or less", text_color=("red", "red"))
            return False

        # Validate JSON
        if not self._validate_json():
            return False

        return True

    def _on_save(self):
        """Handle save button click."""
        if not self._validate_form():
            return

        try:
            name = self.name_var.get().strip()
            config_json = self.json_text.get("1.0", "end-1c")

            # Create profile object
            if self.is_edit_mode:
                # Update existing profile
                self.profile.name = name
                self.profile.update_config(config_json)
                self.result_profile = self.profile
            else:
                # Create new profile
                self.result_profile = Profile.create_new(name, config_json)

            self.status_label.configure(text="Profile saved successfully", text_color=("green", "green"))
            logger.info(f"Profile '{name}' saved successfully")

            # Close dialog after a short delay
            self.after(1000, self.destroy)

        except Exception as e:
            self.status_label.configure(text=f"Failed to save profile: {str(e)}", text_color=("red", "red"))
            logger.error(f"Failed to save profile: {e}")

    def _on_cancel(self):
        """Handle cancel button click."""
        self.result_profile = None
        self.destroy()