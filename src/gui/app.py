"""
Main application window for the Claude Code Configuration Switcher.
"""

import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
from pathlib import Path
from typing import Optional

from services.profile_service import ProfileService
from services.config_service import ConfigService
from models.config import AppConfig
from utils.logger import get_logger
from utils.exceptions import ConfigSwitcherError
from utils.environment import setup_environment
from gui.widgets.profile_list import ProfileListWidget
from gui.widgets.settings_dialog import SettingsDialog
from gui.widgets.profile_editor import ProfileEditorDialog

logger = get_logger(__name__)

class Application(ctk.CTk):
    """Main application window."""

    def __init__(
        self,
        claude_config_path: Path,
        app_config: AppConfig,
        app_config_path: Path
    ):
        """
        Initialize application.

        Args:
            claude_config_path: Path to Claude Code settings.json
            app_config: Application configuration
            app_config_path: Path to application config file
        """
        super().__init__()

        self.claude_config_path = claude_config_path
        self.app_config = app_config
        self.app_config_path = app_config_path

        # Initialize services
        self.profile_service = ProfileService()
        self.config_service = ConfigService(claude_config_path)

        # Setup window
        self._setup_window()
        self._create_widgets()
        self._setup_layout()

        # Load initial data
        self._load_profiles()

        logger.info("Application initialized successfully")

    def _setup_window(self):
        """Setup main window properties."""
        # Put path info in window title
        self.title(f"Claude Code Config Switcher - {self.claude_config_path}")
        self.geometry(f"{self.app_config.window_width}x{self.app_config.window_height}")
        # Set minimum size to accommodate all buttons (wider to fit button labels with shortcuts)
        self.minsize(800, 400)

        # Set theme
        theme = self.app_config.theme.lower()
        if theme == "dark":
            ctk.set_appearance_mode("Dark")
        elif theme == "light":
            ctk.set_appearance_mode("Light")
        else:  # system
            ctk.set_appearance_mode("System")

        # Handle window close
        self.protocol("WM_DELETE_WINDOW", self._on_closing)

        # Setup keyboard shortcuts
        self._setup_keyboard_shortcuts()

    def _setup_keyboard_shortcuts(self):
        """Setup keyboard shortcuts for common actions."""
        # Ctrl+N: New/Create Profile
        self.bind('<Control-n>', lambda e: self._create_profile())

        # Ctrl+E: Edit Profile
        self.bind('<Control-e>', lambda e: self._edit_profile())

        # Delete: Delete Profile
        self.bind('<Delete>', lambda e: self._delete_profile())

        # Ctrl+D: Duplicate Profile
        self.bind('<Control-d>', lambda e: self._duplicate_profile())

        # F5 or Ctrl+R: Refresh
        self.bind('<F5>', lambda e: self._refresh_profiles())
        self.bind('<Control-r>', lambda e: self._refresh_profiles())

        # Ctrl+,: Settings (common shortcut for settings)
        self.bind('<Control-comma>', lambda e: self._show_settings_dialog())

        # Ctrl+Q: Quit
        self.bind('<Control-q>', lambda e: self._on_closing())

        # Alt+F4 is handled by OS

        logger.debug("Keyboard shortcuts initialized")

    def _create_widgets(self):
        """Create main window widgets."""
        # Main content frame - 直接作为主容器
        self.content_frame = ctk.CTkFrame(self)

        # Profile list widget
        self.profile_list = ProfileListWidget(
            self.content_frame,
            self.profile_service,
            self.config_service,
            on_profile_selected=self._on_profile_selected,
            on_profile_activated=self._on_profile_activated
        )

        # Bottom frame for action buttons
        self.action_frame = ctk.CTkFrame(self)

        # Create profile button
        self.create_button = ctk.CTkButton(
            self.action_frame,
            text="Create Profile (Ctrl+N)",
            command=self._create_profile
        )
        self.create_button.grid(row=0, column=0, padx=1, pady=1)

        # Edit profile button
        self.edit_button = ctk.CTkButton(
            self.action_frame,
            text="Edit Profile (Ctrl+E)",
            command=self._edit_profile,
            state="disabled"
        )
        self.edit_button.grid(row=0, column=1, padx=1, pady=1)

        # Delete profile button
        self.delete_button = ctk.CTkButton(
            self.action_frame,
            text="Delete Profile (Del)",
            command=self._delete_profile,
            state="disabled"
        )
        self.delete_button.grid(row=0, column=2, padx=1, pady=1)

        # Duplicate profile button
        self.duplicate_button = ctk.CTkButton(
            self.action_frame,
            text="Duplicate (Ctrl+D)",
            command=self._duplicate_profile,
            state="disabled"
        )
        self.duplicate_button.grid(row=0, column=3, padx=1, pady=1)

        # Refresh button
        self.refresh_button = ctk.CTkButton(
            self.action_frame,
            text="Refresh (F5)",
            command=self._refresh_profiles
        )
        self.refresh_button.grid(row=0, column=4, padx=1, pady=1)

        # Settings button
        self.settings_button = ctk.CTkButton(
            self.action_frame,
            text="⚙️ Settings",
            width=80,
            command=self._show_settings_dialog
        )
        self.settings_button.grid(row=0, column=5, padx=1, pady=1)

    def _setup_layout(self):
        """Setup widget layout."""
        # Configure grid weights for responsive layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Content frame with profile list - 占用主要空间
        self.content_frame.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)

        # Profile list widget should fill the content frame
        self.profile_list.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)

        # Action frame - 底部按钮
        self.action_frame.grid(row=1, column=0, sticky="ew", padx=0, pady=0)
        self.action_frame.grid_columnconfigure(0, weight=1)  # Create button
        self.action_frame.grid_columnconfigure(1, weight=0)  # Edit button
        self.action_frame.grid_columnconfigure(2, weight=0)  # Delete button
        self.action_frame.grid_columnconfigure(3, weight=0)  # Duplicate button
        self.action_frame.grid_columnconfigure(4, weight=0)  # Refresh button
        self.action_frame.grid_columnconfigure(5, weight=0)  # Settings button

    def _load_profiles(self):
        """Load and display profiles."""
        try:
            self.profile_list.load_profiles()
            self._update_status()
        except Exception as e:
            logger.error(f"Failed to load profiles: {e}")
            messagebox.showerror("Error", f"Failed to load profiles: {e}")

    def _on_profile_selected(self, profile):
        """Handle profile selection event."""
        # Enable action buttons when profile is selected
        self.edit_button.configure(state="normal")
        self.delete_button.configure(state="normal")
        self.duplicate_button.configure(state="normal")

    def _on_profile_activated(self, profile):
        """Handle profile activation event."""
        self._update_status()

    def _create_profile(self):
        """Handle create profile button click."""
        try:
            dialog = ProfileEditorDialog(self, title="Create New Profile")
            dialog.wait_window()

            if dialog.result_profile:
                try:
                    profile_id = self.profile_service.create_profile(
                        dialog.result_profile.name,
                        dialog.result_profile.config_json
                    )
                    self._load_profiles()
                    messagebox.showinfo(
                        "Success",
                        f"Profile '{dialog.result_profile.name}' created successfully"
                    )
                    logger.info(f"Created new profile: {dialog.result_profile.name}")

                except Exception as e:
                    logger.error(f"Failed to create profile: {e}")
                    messagebox.showerror("Error", f"Failed to create profile: {e}")

        except Exception as e:
            logger.error(f"Failed to show profile editor: {e}")
            messagebox.showerror("Error", f"Failed to show profile editor: {e}")

    def _edit_profile(self):
        """Handle edit profile button click."""
        selected_profile = self.profile_list.get_selected_profile()
        if not selected_profile:
            return

        try:
            dialog = ProfileEditorDialog(self, title="Edit Profile", profile=selected_profile)
            dialog.wait_window()

            if dialog.result_profile:
                try:
                    success = self.profile_service.update_profile(
                        selected_profile.id,
                        name=dialog.result_profile.name,
                        config_json=dialog.result_profile.config_json
                    )
                    if success:
                        self._load_profiles()
                        messagebox.showinfo(
                            "Success",
                            f"Profile '{dialog.result_profile.name}' updated successfully"
                        )
                        logger.info(f"Updated profile: {dialog.result_profile.name}")
                    else:
                        messagebox.showerror("Error", "Failed to update profile")

                except Exception as e:
                    logger.error(f"Failed to update profile: {e}")
                    messagebox.showerror("Error", f"Failed to update profile: {e}")

        except Exception as e:
            logger.error(f"Failed to show profile editor: {e}")
            messagebox.showerror("Error", f"Failed to show profile editor: {e}")

    def _delete_profile(self):
        """Handle delete profile button click."""
        selected_profile = self.profile_list.get_selected_profile()
        if selected_profile:
            if selected_profile.is_active:
                messagebox.showwarning("Warning", "Cannot delete the active profile")
                return

            if messagebox.askyesno(
                "Confirm Delete",
                f"Are you sure you want to delete the profile '{selected_profile.name}'?"
            ):
                try:
                    self.profile_service.delete_profile(selected_profile.id)
                    self._load_profiles()
                    messagebox.showinfo("Success", f"Profile '{selected_profile.name}' deleted successfully")
                except Exception as e:
                    logger.error(f"Failed to delete profile: {e}")
                    messagebox.showerror("Error", f"Failed to delete profile: {e}")

    def _duplicate_profile(self):
        """Handle duplicate profile button click."""
        selected_profile = self.profile_list.get_selected_profile()
        if not selected_profile:
            return

        # Simple input dialog for new name
        from tkinter import simpledialog

        new_name = simpledialog.askstring(
            "Duplicate Profile",
            f"Enter name for duplicate of '{selected_profile.name}':",
            parent=self
        )

        if not new_name or not new_name.strip():
            return

        try:
            profile_id = self.profile_service.duplicate_profile(selected_profile.id, new_name.strip())
            self._load_profiles()
            messagebox.showinfo(
                "Success",
                f"Profile '{new_name}' created successfully"
            )
            logger.info(f"Duplicated profile '{selected_profile.name}' to '{new_name}'")

        except Exception as e:
            logger.error(f"Failed to duplicate profile: {e}")
            messagebox.showerror("Error", f"Failed to duplicate profile: {e}")

    def _refresh_profiles(self):
        """Handle refresh button click."""
        self._load_profiles()

    def _show_settings_dialog(self):
        """Show settings dialog."""
        try:
            dialog = SettingsDialog(
                self,
                self.app_config,
                self.claude_config_path,
                self.app_config_path
            )
            dialog.wait_window()

            # Reload if configuration changed
            if dialog.result:
                self._reload_configuration()

        except Exception as e:
            logger.error(f"Failed to show settings dialog: {e}")
            messagebox.showerror("Error", f"Failed to show settings: {e}")

    def _update_status(self):
        """Update status information."""
        try:
            active_profile = self.profile_service.get_active_profile()
            profile_count = self.profile_service.get_profile_count()

            status_text = f"Profiles: {profile_count}"
            if active_profile:
                status_text += f" | Active: {active_profile.name}"

            # TODO: Add status bar if needed
            logger.debug(f"Status updated: {status_text}")

        except Exception as e:
            logger.error(f"Failed to update status: {e}")

    def _reload_configuration(self):
        """Reload application configuration."""
        try:
            # Reload app config
            self.app_config = AppConfig.load_from_file(self.app_config_path)

            # Update window geometry
            self.geometry(f"{self.app_config.window_width}x{self.app_config.window_height}")

            # Update theme
            theme = self.app_config.theme.lower()
            if theme == "dark":
                ctk.set_appearance_mode("Dark")
            elif theme == "light":
                ctk.set_appearance_mode("Light")
            else:  # system
                ctk.set_appearance_mode("System")

            # Reload profiles
            self._load_profiles()

            logger.info("Configuration reloaded successfully")

        except Exception as e:
            logger.error(f"Failed to reload configuration: {e}")

    def _on_closing(self):
        """Handle window closing event."""
        try:
            # Save window geometry
            self.app_config.window_width = self.winfo_width()
            self.app_config.window_height = self.winfo_height()
            self.app_config.save_to_file(self.app_config_path)

            # Close database connection
            self.profile_service.database.close_connection()

            logger.info("Application closing")

        except Exception as e:
            logger.error(f"Error during application shutdown: {e}")

        self.destroy()

    def run(self):
        """Start the application main loop."""
        try:
            # Setup environment
            if not setup_environment():
                messagebox.showerror(
                    "Setup Error",
                    "Failed to setup application environment. Check logs for details."
                )
                return

            logger.info("Starting application main loop")
            self.mainloop()

        except Exception as e:
            logger.error(f"Application error: {e}")
            messagebox.showerror("Application Error", f"An error occurred: {e}")