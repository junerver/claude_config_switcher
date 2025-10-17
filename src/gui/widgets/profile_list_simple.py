"""
Simple profile list widget using basic tkinter components.
"""

import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
from typing import Optional, Callable, List
import json

from models.profile import Profile
from services.profile_service import ProfileService
from services.config_service import ConfigService
from utils.logger import get_logger
from utils.exceptions import ConfigSwitcherError

logger = get_logger(__name__)

class SimpleProfileListWidget(ctk.CTkFrame):
    """Simple profile list widget using basic tkinter components."""

    def __init__(
        self,
        parent,
        profile_service: ProfileService,
        config_service: ConfigService,
        on_profile_selected: Optional[Callable[[Profile], None]] = None,
        on_profile_activated: Optional[Callable[[Profile], None]] = None
    ):
        """
        Initialize simple profile list widget.

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
        # Title label
        self.title_label = ctk.CTkLabel(
            self,
            text="Configuration Profiles",
            font=ctk.CTkFont(size=16, weight="bold")
        )

        # Create scrollable frame using Canvas and Scrollbar
        self.canvas = tk.Canvas(self, bg="#212121", highlightthickness=0)
        self.scrollbar = ctk.CTkScrollbar(self, command=self.canvas.yview)

        # Connect canvas to scrollbar
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Profile items container - inside canvas
        self.profile_frame = ctk.CTkFrame(self.canvas)
        self.canvas_window = self.canvas.create_window(
            (0, 0), window=self.profile_frame, anchor="nw"
        )

        # Bind events
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        self.profile_frame.bind("<Configure>", self._on_profile_frame_configure)

        # Bind mouse wheel events for scrolling
        # Windows uses <MouseWheel>
        self.canvas.bind("<MouseWheel>", self._on_mousewheel_windows)
        self.canvas.bind("<Button-4>", self._on_mousewheel_linux)  # Linux scroll up
        self.canvas.bind("<Button-5>", self._on_mousewheel_linux)  # Linux scroll down

        # Also bind mouse wheel to the frame for better coverage
        self.profile_frame.bind("<MouseWheel>", self._on_mousewheel_windows)
        self.profile_frame.bind("<Button-4>", self._on_mousewheel_linux)
        self.profile_frame.bind("<Button-5>", self._on_mousewheel_linux)

        # Bind to all child widgets recursively for complete coverage
        self.canvas.bind("<Configure>", lambda e: self._bind_mousewheel_to_children())

        # Profile items
        self.profile_items: List[ctk.CTkFrame] = []

    def _setup_layout(self):
        """Setup widget layout."""
        # Configure grid weights exactly like the original CTkScrollableFrame
        self.grid_columnconfigure(0, weight=1)  # Canvas column expands to fill available space
        self.grid_columnconfigure(1, weight=0)  # Scrollbar column fixed size
        self.grid_rowconfigure(1, weight=1)      # Canvas row expands to fill available space

        self.title_label.grid(row=0, column=0, columnspan=2, sticky="ew", padx=0, pady=(0, 2))
        # Canvas in column 0, expands to fill available space
        self.canvas.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)
        # Scrollbar in column 1, fixed width
        self.scrollbar.grid(row=1, column=1, sticky="ns", padx=0, pady=0)

        # Set minimum height using configure (Canvas doesn't support minsize)
        # The grid layout with weight=1 will make it expand to fill available space

    def _on_canvas_configure(self, event):
        """Handle canvas resize."""
        # Update the profile frame width to match canvas width
        canvas_width = event.width
        if canvas_width > 1:
            # Since canvas is in column 0 with weight=1, it fills available space
            # The scrollbar is in column 1, so canvas automatically excludes scrollbar width
            self.canvas.itemconfig(self.canvas_window, width=canvas_width)
            logger.debug(f"Canvas resized to width: {canvas_width}")

        # Update scroll region to include all content
        self._update_scroll_region()

    def _on_profile_frame_configure(self, event):
        """Handle profile frame resize."""
        # Update scroll region when profile frame changes
        logger.debug(f"Profile frame resized, height: {event.height}")
        self._update_scroll_region()

    def _update_scroll_region(self):
        """Update the canvas scroll region to include all content."""
        try:
            # Force update of all widgets
            self.update_idletasks()
            self.profile_frame.update_idletasks()

            # Get the actual height of the profile frame
            frame_height = self.profile_frame.winfo_height()
            if frame_height <= 0:
                # If frame height is not available, calculate based on items
                frame_height = 0
                for item in self.profile_items:
                    if item.winfo_exists():
                        item.update_idletasks()
                        item_height = item.winfo_height()
                        if item_height > 0:
                            frame_height += item_height + 2
                        else:
                            frame_height += 120
                    else:
                        frame_height += 120

            # Get canvas dimensions
            canvas_width = self.canvas.winfo_width()
            if canvas_width <= 0:
                canvas_width = 400

            # Ensure minimum height
            if frame_height < 400:
                frame_height = 400

            # Set scroll region with actual dimensions
            self.canvas.configure(scrollregion=(0, 0, canvas_width, frame_height))
            logger.debug(f"Updated scroll region: 0,0,{canvas_width},{frame_height}")

        except Exception as e:
            logger.error(f"Failed to update scroll region: {e}")
            # Fallback: force a reasonable scroll region
            try:
                fallback_height = max(600, len(self.profile_items) * 120)
                self.canvas.configure(scrollregion=(0, 0, 400, fallback_height))
                logger.debug(f"Using fallback scroll region: 0,0,400,{fallback_height}")
            except Exception as fallback_e:
                logger.error(f"Fallback scroll region failed: {fallback_e}")

    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling."""
        try:
            # Windows/Mac: event.delta, Linux: event.num
            if event.num == 4:  # Linux scroll up
                delta = -1
            elif event.num == 5:  # Linux scroll down
                delta = 1
            else:  # Windows/Mac
                delta = -1 * (event.delta // 120)

            # Scroll the canvas
            self.canvas.yview_scroll(delta, "units")
        except Exception as e:
            logger.debug(f"Mouse wheel event failed: {e}")

    def _on_mousewheel_windows(self, event):
        """Handle Windows mouse wheel scrolling."""
        try:
            # Windows mouse wheel
            delta = -1 * (event.delta // 120)
            self.canvas.yview_scroll(delta, "units")
        except Exception as e:
            logger.debug(f"Windows mouse wheel event failed: {e}")

    def _on_mousewheel_linux(self, event):
        """Handle Linux mouse wheel scrolling."""
        try:
            # Linux mouse wheel (button 4 = up, button 5 = down)
            if event.num == 4:
                delta = -1
            elif event.num == 5:
                delta = 1
            else:
                return
            self.canvas.yview_scroll(delta, "units")
        except Exception as e:
            logger.debug(f"Linux mouse wheel event failed: {e}")

    def _bind_mousewheel_to_children(self):
        """Recursively bind mouse wheel events to all child widgets."""
        def bind_to_widget(widget):
            try:
                widget.bind("<MouseWheel>", self._on_mousewheel_windows)
                widget.bind("<Button-4>", self._on_mousewheel_linux)
                widget.bind("<Button-5>", self._on_mousewheel_linux)

                # Recursively bind to children
                for child in widget.winfo_children():
                    bind_to_widget(child)
            except:
                pass  # Some widgets don't support binding

        bind_to_widget(self.profile_frame)

    def load_profiles(self):
        """Load and display all profiles."""
        try:
            # Clear existing profile items
            for item in self.profile_items:
                item.destroy()
            self.profile_items.clear()

            # Load profiles from service
            self.profiles = self.profile_service.get_all_profiles()
            active_profile = self.profile_service.get_active_profile()

            # Create profile item for each profile
            for profile in self.profiles:
                profile_item = self._create_profile_item(profile, active_profile)
                self.profile_items.append(profile_item)

            # Update scroll region after all profiles are added with multiple attempts
            self.after(50, self._update_scroll_region)
            self.after(200, self._update_scroll_region)
            self.after(500, self._update_scroll_region)

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
        item_frame = ctk.CTkFrame(self.profile_frame)
        item_frame.pack(fill="x", padx=2, pady=1)  # Small padding for visual separation
        # Configure frame to fill width completely
        item_frame.pack_configure(fill="x", expand=True)

        # Store profile ID in frame for easy identification
        item_frame.profile_id = profile.id

        # Configure frame appearance based on active status
        if profile.is_active:
            item_frame.configure(fg_color=("#2b2b2b", "#212121"))  # Highlight active

        # Profile info frame
        info_frame = ctk.CTkFrame(item_frame)
        info_frame.pack(fill="x", padx=2, pady=2)  # Small internal padding
        # Configure info_frame to fill width completely
        info_frame.pack_configure(fill="x", expand=True)

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
        name_label.pack(fill="x", pady=(0, 1))

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
            updated_label.pack(fill="x", pady=(1, 0))

        # Bind events
        self._bind_profile_events(item_frame, profile)

        return item_frame

    def _bind_profile_events(self, frame: ctk.CTkFrame, profile: Profile):
        """Bind events to profile item."""
        def on_click(event):
            self._select_profile(profile)

        def on_double_click(event):
            self._activate_profile(profile)

        # Bind click and double-click events
        frame.bind("<Button-1>", on_click)
        frame.bind("<Double-Button-1>", on_double_click)

        # Bind events to all child widgets
        self._bind_recursive(frame, on_click, on_double_click)

    def _bind_recursive(self, widget, on_click, on_double_click):
        """Recursively bind events to widget and its children."""
        try:
            widget.bind("<Button-1>", on_click)
            widget.bind("<Double-Button-1>", on_double_click)
        except:
            pass  # Some widgets don't support binding

        for child in widget.winfo_children():
            self._bind_recursive(child, on_click, on_double_click)

    def _select_profile(self, profile: Profile):
        """Handle profile selection."""
        # Clear previous selection from all items
        for item in self.profile_items:
            if hasattr(item, 'profile_id'):
                # Reset to default or active styling
                is_active = any(p.id == item.profile_id and p.is_active for p in self.profiles)
                if is_active:
                    # Active profile gets special color
                    item.configure(fg_color=("#2b2b2b", "#212121"))
                else:
                    # Non-active items become transparent
                    item.configure(fg_color="transparent")

        # Highlight selected profile with strong color
        for item in self.profile_items:
            if hasattr(item, 'profile_id') and item.profile_id == profile.id:
                # Check if this profile is active
                is_active = any(p.id == profile.id and p.is_active for p in self.profiles)
                if is_active:
                    # Active profile gets different highlight
                    item.configure(fg_color=("#1e40af", "#1e3a8a"))  # Blue highlight for active
                else:
                    # Selected non-active profile gets strong highlight
                    item.configure(fg_color=("#dc2626", "#991b1b"))  # Red highlight for selected
                break

        self.selected_profile = profile

        # Notify parent
        if self.on_profile_selected:
            self.on_profile_selected(profile)

        logger.info(f"Selected profile: {profile.name}")

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