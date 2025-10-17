"""
Profile list widget for displaying and managing configuration profiles.
"""

import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
from typing import Optional, Callable, List
import json

from ...models.profile import Profile
from ...services.profile_service import ProfileService
from ...services.config_service import ConfigService
from ...utils.logger import get_logger
from ...utils.exceptions import ConfigSwitcherError
from .profile_preview import ProfilePreviewDialog

logger = get_logger(__name__)

class ProfileListWidget(ctk.CTkFrame):
    """Widget for displaying and interacting with profile list."""

    def __init__(
        self,
        parent,
        profile_service: ProfileService,
        config_service: ConfigService,
        on_profile_selected: Optional[Callable[[Profile], None]] = None,
        on_profile_activated: Optional[Callable[[Profile], None]] = None
    ):
        """
        Initialize profile list widget.

        Args:
            parent: Parent widget
            profile_service: Profile service instance
            config_service: Configuration service instance
            on_profile_selected: Callback when profile is selected
            on_profile_activated: Callback when profile is activated
        """
        super().__init__(parent)

        self.profile_service = profile_service
        self.config_service = config_service
        self.on_profile_selected = on_profile_selected
        self.on_profile_activated = on_profile_activated

        self.profiles: List[Profile] = []
        self.selected_profile: Optional[Profile] = None

        self._create_widgets()
        self._setup_layout()

    def _create_widgets(self):
        """Create widget components."""
        # Scrollable frame for profile list
        self.scroll_frame = ctk.CTkScrollableFrame(self)
        self.scroll_frame.pack(fill="both", expand=True, padx=5, pady=5)

        # Profile item frames will be added dynamically
        self.profile_frames: List[ctk.CTkFrame] = []

    def _setup_layout(self):
        """Setup widget layout."""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.scroll_frame.grid(row=0, column=0, sticky="nsew")

    def load_profiles(self):
        """Load and display all profiles."""
        try:
            # Clear existing profile frames
            for frame in self.profile_frames:
                frame.destroy()
            self.profile_frames.clear()

            # Load profiles from service
            self.profiles = self.profile_service.get_all_profiles()
            active_profile = self.profile_service.get_active_profile()

            # Create profile item for each profile
            for profile in self.profiles:
                profile_frame = self._create_profile_item(profile, active_profile)
                self.profile_frames.append(profile_frame)

            logger.info(f"Loaded {len(self.profiles)} profiles")

        except Exception as e:
            logger.error(f"Failed to load profiles: {e}")
            messagebox.showerror("Error", f"Failed to load profiles: {e}")

    def _create_profile_item(self, profile: Profile, active_profile: Optional[Profile]) -> ctk.CTkFrame:
        """
        Create a profile item widget.

        Args:
            profile: Profile data
            active_profile: Currently active profile

        Returns:
            Profile item frame
        """
        # Main frame for profile item
        item_frame = ctk.CTkFrame(self.scroll_frame)
        item_frame.pack(fill="x", padx=5, pady=3)

        # Configure frame appearance based on active status
        if profile.is_active:
            item_frame.configure(fg_color=("#2b2b2b", "#212121"))  # Highlight active

        # Profile info frame
        info_frame = ctk.CTkFrame(item_frame)
        info_frame.pack(fill="x", padx=10, pady=8)

        # Name label
        name_text = profile.name
        if profile.is_active:
            name_text = f"✓ {name_text}"  # Add checkmark for active

        name_label = ctk.CTkLabel(
            info_frame,
            text=name_text,
            font=ctk.CTkFont(size=14, weight="bold" if profile.is_active else "normal"),
            anchor="w"
        )
        name_label.pack(fill="x", pady=(0, 3))

        # Details frame
        details_frame = ctk.CTkFrame(info_frame)
        details_frame.pack(fill="x")

        # Base URL
        base_url = profile.get_base_url()
        if base_url:
            base_url_label = ctk.CTkLabel(
                details_frame,
                text=f"URL: {base_url}",
                font=ctk.CTkFont(size=11),
                anchor="w",
                text_color=("#6b7280", "#9ca3af")
            )
            base_url_label.pack(fill="x", pady=1)

        # Auth token (masked)
        auth_token = profile.get_auth_token_masked()
        if auth_token:
            token_label = ctk.CTkLabel(
                details_frame,
                text=f"Token: {auth_token}",
                font=ctk.CTkFont(size=11),
                anchor="w",
                text_color=("#6b7280", "#9ca3af")
            )
            token_label.pack(fill="x", pady=1)

        # Model
        model = profile.get_model()
        if model:
            model_label = ctk.CTkLabel(
                details_frame,
                text=f"Model: {model}",
                font=ctk.CTkFont(size=11),
                anchor="w",
                text_color=("#6b7280", "#9ca3af")
            )
            model_label.pack(fill="x", pady=1)

        # Updated timestamp
        if profile.updated_at:
            updated_label = ctk.CTkLabel(
                details_frame,
                text=f"Updated: {profile.updated_at.strftime('%Y-%m-%d %H:%M')}",
                font=ctk.CTkFont(size=10),
                anchor="w",
                text_color=("#9ca3af", "#6b7280")
            )
            updated_label.pack(fill="x", pady=(3, 0))

        # Bind events
        self._bind_profile_events(item_frame, profile)

        return item_frame

    def _bind_profile_events(self, frame: ctk.CTkFrame, profile: Profile):
        """Bind events to profile item."""
        def on_click(event):
            self._select_profile(profile)

        def on_double_click(event):
            self._activate_profile(profile)

        def on_right_click(event):
            # Show context menu
            self._show_context_menu(event, profile)

        # Bind click and double-click events
        frame.bind("<Button-1>", on_click)
        frame.bind("<Double-Button-1>", on_double_click)
        frame.bind("<Button-3>", on_right_click)  # Right-click

        # Bind events to all child widgets
        for widget in frame.winfo_children():
            self._bind_recursive(widget, on_click, on_double_click, on_right_click)

    def _bind_recursive(self, widget, on_click, on_double_click, on_right_click):
        """Recursively bind events to widget and its children."""
        try:
            widget.bind("<Button-1>", on_click)
            widget.bind("<Double-Button-1>", on_double_click)
            widget.bind("<Button-3>", on_right_click)
        except:
            pass  # Some widgets don't support binding

        for child in widget.winfo_children():
            self._bind_recursive(child, on_click, on_double_click, on_right_click)

    def _select_profile(self, profile: Profile):
        """Handle profile selection."""
        # Clear previous selection
        for frame in self.profile_frames:
            frame.configure(fg_color="transparent")

        # Highlight selected profile
        for i, p in enumerate(self.profiles):
            if p.id == profile.id:
                if self.profile_frames[i].winfo_exists():
                    self.profile_frames[i].configure(fg_color=("#3b3b3b", "#2a2a2a"))
                break

        self.selected_profile = profile

        # Notify parent
        if self.on_profile_selected:
            self.on_profile_selected(profile)

        logger.debug(f"Selected profile: {profile.name}")

    def _activate_profile(self, profile: Profile):
        """Handle profile activation (double-click)."""
        if profile.is_active:
            logger.info(f"Profile '{profile.name}' is already active")
            return

        try:
            # Confirm activation
            if messagebox.askyesno(
                "Activate Profile",
                f"Apply profile '{profile.name}' to Claude Code configuration?\n\n"
                "This will replace your current configuration and create a backup."
            ):
                # Create backup
                try:
                    backup_path = self.config_service.create_backup()
                    logger.info(f"Created backup: {backup_path}")
                except Exception as e:
                    logger.warning(f"Failed to create backup: {e}")

                # Apply profile configuration
                config_json = profile.config_json
                success = self.config_service.write_settings(config_json)

                if success:
                    # Update active status in database
                    self.profile_service.set_active_profile(profile.id)

                    # Reload profiles to update display
                    self.load_profiles()

                    # Re-select the activated profile
                    self._select_profile(profile)

                    # Notify parent
                    if self.on_profile_activated:
                        self.on_profile_activated(profile)

                    messagebox.showinfo(
                        "Success",
                        f"Profile '{profile.name}' has been activated successfully."
                    )
                    logger.info(f"Activated profile: {profile.name}")
                else:
                    messagebox.showerror(
                        "Error",
                        "Failed to apply profile configuration."
                    )

        except Exception as e:
            logger.error(f"Failed to activate profile '{profile.name}': {e}")
            messagebox.showerror("Error", f"Failed to activate profile: {e}")

    def get_selected_profile(self) -> Optional[Profile]:
        """
        Get currently selected profile.

        Returns:
            Selected profile or None if no selection
        """
        return self.selected_profile

    def refresh_profiles(self):
        """Refresh the profile list."""
        self.load_profiles()

    def select_profile_by_id(self, profile_id: int) -> bool:
        """
        Select profile by ID.

        Args:
            profile_id: Profile ID to select

        Returns:
            True if profile found and selected
        """
        for profile in self.profiles:
            if profile.id == profile_id:
                self._select_profile(profile)
                return True
        return False

    def select_profile_by_name(self, name: str) -> bool:
        """
        Select profile by name.

        Args:
            name: Profile name to select

        Returns:
            True if profile found and selected
        """
        for profile in self.profiles:
            if profile.name == name:
                self._select_profile(profile)
                return True
        return False

    def get_profile_count(self) -> int:
        """
        Get number of profiles.

        Returns:
            Number of profiles
        """
        return len(self.profiles)

    def scroll_to_profile(self, profile: Profile):
        """
        Scroll to make profile visible.

        Args:
            profile: Profile to scroll to
        """
        try:
            # Find profile frame
            for i, p in enumerate(self.profiles):
                if p.id == profile.id and i < len(self.profile_frames):
                    frame = self.profile_frames[i]
                    # Calculate scroll position
                    frame_y = frame.winfo_y()
                    canvas = self.scroll_frame._canvas
                    canvas_height = canvas.winfo_height()
                    scroll_position = frame_y / canvas_height
                    canvas.yview_moveto(scroll_position)
                    break
        except Exception as e:
            logger.debug(f"Failed to scroll to profile: {e}")

    def _show_context_menu(self, event, profile: Profile):
        """Show context menu for profile."""
        try:
            import tkinter as tk

            # Create context menu
            context_menu = tk.Menu(self, tearoff=0)

            # Add menu items
            context_menu.add_command(
                label="Preview Profile",
                command=lambda: self._preview_profile(profile)
            )
            context_menu.add_separator()
            context_menu.add_command(
                label="Activate Profile",
                command=lambda: self._activate_profile(profile)
            )
            context_menu.add_command(
                label="Edit Profile",
                command=lambda: self._edit_profile(profile)
            )
            context_menu.add_separator()
            context_menu.add_command(
                label="Duplicate Profile",
                command=lambda: self._duplicate_profile(profile)
            )
            context_menu.add_command(
                label="Delete Profile",
                command=lambda: self._delete_profile(profile)
            )

            # Show menu at cursor position
            try:
                context_menu.tk_popup(event.x_root, event.y_root)
            finally:
                context_menu.grab_release()

        except Exception as e:
            logger.error(f"Failed to show context menu: {e}")

    def _preview_profile(self, profile: Profile):
        """Show profile preview dialog."""
        try:
            dialog = ProfilePreviewDialog(self, profile)
            # Dialog is modal, no need to wait_window
        except Exception as e:
            logger.error(f"Failed to show profile preview: {e}")
            messagebox.showerror("Error", f"Failed to show profile preview: {e}")

    def _edit_profile(self, profile: Profile):
        """Edit profile callback."""
        # This would typically be handled by the parent application
        # For now, just log the action
        logger.info(f"Edit profile requested: {profile.name}")

    def _duplicate_profile(self, profile: Profile):
        """Duplicate profile callback."""
        # This would typically be handled by the parent application
        # For now, just log the action
        logger.info(f"Duplicate profile requested: {profile.name}")

    def _delete_profile(self, profile: Profile):
        """Delete profile callback."""
        # This would typically be handled by the parent application
        # For now, just log the action
        logger.info(f"Delete profile requested: {profile.name}")