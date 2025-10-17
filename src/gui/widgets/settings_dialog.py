"""
Settings dialog for application configuration.
"""

import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
from pathlib import Path
from typing import Optional

from ...models.config import AppConfig
from ...utils.logger import get_logger
from ...utils.paths import detect_claude_config_path
from ...utils.exceptions import ConfigSwitcherError

logger = get_logger(__name__)

class SettingsDialog(ctk.CTkToplevel):
    """Settings dialog for application configuration."""

    def __init__(
        self,
        parent,
        app_config: AppConfig,
        claude_config_path: Path,
        app_config_path: Path
    ):
        """
        Initialize settings dialog.

        Args:
            parent: Parent window
            app_config: Current application configuration
            claude_config_path: Current Claude Code config path
            app_config_path: Application config file path
        """
        super().__init__(parent)

        self.app_config = app_config
        self.claude_config_path = claude_config_path
        self.app_config_path = app_config_path
        self.result = False

        self._setup_dialog()
        self._create_widgets()
        self._load_current_settings()

    def _setup_dialog(self):
        """Setup dialog properties."""
        self.title("Settings")
        self.geometry("600x500")
        self.resizable(False, False)

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
        # Main container with scrollbar
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Title
        title_label = ctk.CTkLabel(
            main_frame,
            text="Application Settings",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title_label.pack(fill="x", pady=(0, 20))

        # Scrollable content area
        scroll_frame = ctk.CTkScrollableFrame(main_frame, height=400)
        scroll_frame.pack(fill="both", expand=True)

        # Claude Code Configuration Section
        claude_frame = ctk.CTkFrame(scroll_frame)
        claude_frame.pack(fill="x", pady=(0, 15))

        claude_title = ctk.CTkLabel(
            claude_frame,
            text="Claude Code Configuration",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        claude_title.pack(fill="x", padx=15, pady=(15, 10))

        # Claude config path
        path_frame = ctk.CTkFrame(claude_frame)
        path_frame.pack(fill="x", padx=15, pady=(0, 15))

        path_label = ctk.CTkLabel(path_frame, text="Settings File:")
        path_label.pack(side="left", padx=(0, 10))

        self.claude_path_var = tk.StringVar()
        self.claude_path_entry = ctk.CTkEntry(
            path_frame,
            textvariable=self.claude_path_var,
            width=300
        )
        self.claude_path_entry.pack(side="left", fill="x", expand=True)

        browse_button = ctk.CTkButton(
            path_frame,
            text="Browse",
            width=80,
            command=self._browse_claude_config
        )
        browse_button.pack(side="right", padx=(10, 0))

        detect_button = ctk.CTkButton(
            path_frame,
            text="Auto Detect",
            width=100,
            command=self._detect_claude_config
        )
        detect_button.pack(side="right", padx=(5, 0))

        # Application Settings Section
        app_frame = ctk.CTkFrame(scroll_frame)
        app_frame.pack(fill="x", pady=(0, 15))

        app_title = ctk.CTkLabel(
            app_frame,
            text="Application Settings",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        app_title.pack(fill="x", padx=15, pady=(15, 10))

        # Theme selection
        theme_frame = ctk.CTkFrame(app_frame)
        theme_frame.pack(fill="x", padx=15, pady=(0, 10))

        theme_label = ctk.CTkLabel(theme_frame, text="Theme:")
        theme_label.pack(side="left", padx=(0, 10))

        self.theme_var = tk.StringVar()
        self.theme_option = ctk.CTkOptionMenu(
            theme_frame,
            values=["System", "Light", "Dark"],
            variable=self.theme_var,
            width=200
        )
        self.theme_option.pack(side="left")

        # Log level
        log_frame = ctk.CTkFrame(app_frame)
        log_frame.pack(fill="x", padx=15, pady=(0, 10))

        log_label = ctk.CTkLabel(log_frame, text="Log Level:")
        log_label.pack(side="left", padx=(0, 10))

        self.log_level_var = tk.StringVar()
        self.log_level_option = ctk.CTkOptionMenu(
            log_frame,
            values=["DEBUG", "INFO", "WARNING", "ERROR"],
            variable=self.log_level_var,
            width=200
        )
        self.log_level_option.pack(side="left")

        # Backup retention
        backup_frame = ctk.CTkFrame(app_frame)
        backup_frame.pack(fill="x", padx=15, pady=(0, 15))

        backup_label = ctk.CTkLabel(backup_frame, text="Backup Retention:")
        backup_label.pack(side="left", padx=(0, 10))

        self.backup_retention_var = tk.StringVar()
        self.backup_retention_entry = ctk.CTkEntry(
            backup_frame,
            textvariable=self.backup_retention_var,
            width=100
        )
        self.backup_retention_entry.pack(side="left")

        backup_count_label = ctk.CTkLabel(backup_frame, text="backups")
        backup_count_label.pack(side="left", padx=(5, 0))

        # Advanced Settings Section
        advanced_frame = ctk.CTkFrame(scroll_frame)
        advanced_frame.pack(fill="x", pady=(0, 15))

        advanced_title = ctk.CTkLabel(
            advanced_frame,
            text="Advanced Settings",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        advanced_title.pack(fill="x", padx=15, pady=(15, 10))

        # Auto refresh
        self.auto_refresh_var = tk.BooleanVar()
        auto_refresh_check = ctk.CTkCheckBox(
            advanced_frame,
            text="Auto-refresh profile list",
            variable=self.auto_refresh_var
        )
        auto_refresh_check.pack(anchor="w", padx=15, pady=(0, 10))

        # Show confirmations
        self.show_confirmations_var = tk.BooleanVar()
        confirmations_check = ctk.CTkCheckBox(
            advanced_frame,
            text="Show confirmation dialogs",
            variable=self.show_confirmations_var
        )
        confirmations_check.pack(anchor="w", padx=15, pady=(0, 15))

        # Status label
        self.status_label = ctk.CTkLabel(
            main_frame,
            text="",
            text_color=("red", "red")
        )
        self.status_label.pack(fill="x", pady=(10, 0))

        # Button frame
        button_frame = ctk.CTkFrame(main_frame)
        button_frame.pack(fill="x", pady=(15, 0))

        # Test connection button
        test_button = ctk.CTkButton(
            button_frame,
            text="Test Connection",
            command=self._test_connection
        )
        test_button.pack(side="left", padx=(0, 10))

        # Reset button
        reset_button = ctk.CTkButton(
            button_frame,
            text="Reset to Defaults",
            command=self._reset_to_defaults
        )
        reset_button.pack(side="left", padx=(0, 10))

        # Cancel button
        cancel_button = ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=self._on_cancel
        )
        cancel_button.pack(side="right", padx=(10, 0))

        # Save button
        save_button = ctk.CTkButton(
            button_frame,
            text="Save",
            command=self._on_save
        )
        save_button.pack(side="right")

    def _load_current_settings(self):
        """Load current settings into dialog controls."""
        # Claude config path
        self.claude_path_var.set(str(self.claude_config_path))

        # Application settings
        self.theme_var.set(self.app_config.theme.title())
        self.log_level_var.set(self.app_config.log_level)
        self.backup_retention_var.set(str(self.app_config.backup_retention_count))
        self.auto_refresh_var.set(self.app_config.auto_refresh)
        self.show_confirmations_var.set(self.app_config.show_confirmations)

    def _browse_claude_config(self):
        """Browse for Claude Code configuration file."""
        file_path = filedialog.askopenfilename(
            title="Select Claude Code Settings File",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if file_path:
            self.claude_path_var.set(file_path)

    def _detect_claude_config(self):
        """Auto-detect Claude Code configuration path."""
        detected_path = detect_claude_config_path()
        if detected_path:
            self.claude_path_var.set(str(detected_path))
            self.status_label.configure(text="Auto-detection successful", text_color=("green", "green"))
        else:
            self.status_label.configure(text="Auto-detection failed", text_color=("red", "red"))

    def _test_connection(self):
        """Test connection to Claude Code configuration."""
        try:
            claude_path = Path(self.claude_path_var.get())
            if not claude_path.exists():
                self.status_label.configure(text="Settings file not found", text_color=("red", "red"))
                return

            # Try to read the file
            with open(claude_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Validate JSON
            import json
            json.loads(content)

            self.status_label.configure(text="Connection successful", text_color=("green", "green"))
            logger.info(f"Successfully tested connection to {claude_path}")

        except Exception as e:
            self.status_label.configure(text=f"Connection failed: {str(e)}", text_color=("red", "red"))
            logger.error(f"Connection test failed: {e}")

    def _reset_to_defaults(self):
        """Reset settings to default values."""
        if messagebox.askyesno(
            "Reset Settings",
            "Are you sure you want to reset all settings to their default values?"
        ):
            # Reset to default values
            self.theme_var.set("System")
            self.log_level_var.set("INFO")
            self.backup_retention_var.set("10")
            self.auto_refresh_var.set(True)
            self.show_confirmations_var.set(True)

            # Auto-detect Claude config path
            self._detect_claude_config()

            self.status_label.configure(text="Settings reset to defaults", text_color=("green", "green"))

    def _validate_settings(self) -> bool:
        """Validate settings before saving."""
        try:
            # Validate backup retention count
            backup_count = int(self.backup_retention_var.get())
            if backup_count < 1 or backup_count > 50:
                self.status_label.configure(
                    text="Backup retention must be between 1 and 50",
                    text_color=("red", "red")
                )
                return False

            # Validate Claude config path
            claude_path = Path(self.claude_path_var.get())
            if not claude_path.exists():
                self.status_label.configure(
                    text="Claude Code settings file does not exist",
                    text_color=("red", "red")
                )
                return False

            # Validate JSON content
            with open(claude_path, 'r', encoding='utf-8') as f:
                content = f.read()
            import json
            json.loads(content)

            return True

        except ValueError:
            self.status_label.configure(
                text="Backup retention must be a number",
                text_color=("red", "red")
            )
            return False
        except Exception as e:
            self.status_label.configure(
                text=f"Invalid Claude config file: {str(e)}",
                text_color=("red", "red")
            )
            return False

    def _on_save(self):
        """Handle save button click."""
        if not self._validate_settings():
            return

        try:
            # Update application config
            self.app_config.claude_config_path = self.claude_path_var.get()
            self.app_config.theme = self.theme_var.get().lower()
            self.app_config.log_level = self.log_level_var.get()
            self.app_config.backup_retention_count = int(self.backup_retention_var.get())
            self.app_config.auto_refresh = self.auto_refresh_var.get()
            self.app_config.show_confirmations = self.show_confirmations_var.get()

            # Save configuration
            if self.app_config.save_to_file(self.app_config_path):
                self.result = True
                self.status_label.configure(
                    text="Settings saved successfully",
                    text_color=("green", "green")
                )
                logger.info("Settings saved successfully")

                # Close dialog after a short delay
                self.after(1000, self.destroy)
            else:
                self.status_label.configure(
                    text="Failed to save settings",
                    text_color=("red", "red")
                )

        except Exception as e:
            self.status_label.configure(
                text=f"Failed to save settings: {str(e)}",
                text_color=("red", "red")
            )
            logger.error(f"Failed to save settings: {e}")

    def _on_cancel(self):
        """Handle cancel button click."""
        self.result = False
        self.destroy()