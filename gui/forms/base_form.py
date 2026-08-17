"""
=========================================================
Civil Estimate Suite Pro v4.0
---------------------------------------------------------
Module    : Base Form
Purpose   : Base Dialog for all forms
Author    : OpenAI + Moula Bakhsh
Version   : 4.0.0
=========================================================
"""

from __future__ import annotations

import customtkinter as ctk


class BaseForm(ctk.CTkToplevel):
    """
    Base dialog window for all forms.

    All forms such as:
        - Project Form
        - BOQ Form
        - Material Form
        - Vendor Form

    should inherit from this class.
    """

    DEFAULT_WIDTH = 750
    DEFAULT_HEIGHT = 600

    def __init__(
        self,
        parent,
        title: str = "Form",
        width: int = DEFAULT_WIDTH,
        height: int = DEFAULT_HEIGHT,
    ):

        super().__init__(parent)

        self.parent = parent

        self.form_title = title
        self.form_width = width
        self.form_height = height

        self.result = None
        self._is_dirty = False

        self._configure_window()
        self._center_window()
        self._make_modal()

        self._create_header()
        self._create_content()
        self._create_footer()

        self._bind_events()

        self.protocol(
         "WM_DELETE_WINDOW",
          self.cancel,
)

    # ---------------------------------------------------------
    # Window Configuration
    # ---------------------------------------------------------

    def _configure_window(self):

        self.title(self.form_title)

        self.geometry(
            f"{self.form_width}x{self.form_height}"
        )

        self.resizable(True, True)

        # Keep the form usable on smaller screens while allowing
        # normal Windows minimize/maximize/resize behaviour.
        self.minsize(760, 620)

    # ---------------------------------------------------------
    # Center Window
    # ---------------------------------------------------------

    def _center_window(self):

        self.update_idletasks()

        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        x = int(
            (screen_width - self.form_width) / 2
        )

        y = int(
            (screen_height - self.form_height) / 2
        )

        self.geometry(
            f"{self.form_width}x{self.form_height}+{x}+{y}"
        )

    # ---------------------------------------------------------
    # Modal Behaviour
    # ---------------------------------------------------------

    def _make_modal(self):

        self.transient(self.parent)

        self.grab_set()

        self.focus_force()

    # ---------------------------------------------------------
    # Header
    # ---------------------------------------------------------

    def _create_header(self):

        self.header_frame = ctk.CTkFrame(
            self,
            corner_radius=0,
            height=60
        )

        self.header_frame.pack(
            fill="x"
        )

        self.header_label = ctk.CTkLabel(
            self.header_frame,
            text=self.form_title,
            font=ctk.CTkFont(
                size=22,
                weight="bold"
            )
        )

        self.header_label.pack(
            padx=20,
            pady=15,
            anchor="w"
        )
       
            # ---------------------------------------------------------
    # Content Area
    # ---------------------------------------------------------

    def _create_content(self):

        self.content_frame = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        self.content_frame.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=15
        )

        self.content_frame.grid_columnconfigure(
            0,
            weight=1
        )
            # ---------------------------------------------------------
    # Footer
    # ---------------------------------------------------------

    def _create_footer(self):

        self.footer_frame = ctk.CTkFrame(
            self,
            corner_radius=0,
            height=60
        )

        self.footer_frame.pack(
            fill="x",
            side="bottom"
        )

        self.footer_frame.grid_columnconfigure(
            0,
            weight=1
        )

        self._create_status_label()

        self._create_buttons()
        
            # ---------------------------------------------------------
    # Status Label
    # ---------------------------------------------------------

    def _create_status_label(self):

        self.status_label = ctk.CTkLabel(
            self.footer_frame,
            text="Ready",
            anchor="w"
        )

        self.status_label.grid(
            row=0,
            column=0,
            padx=20,
            pady=15,
            sticky="w"
        )
            # ---------------------------------------------------------
    # Buttons
    # ---------------------------------------------------------

    def _create_buttons(self):

        self.cancel_button = ctk.CTkButton(
            self.footer_frame,
            text="Cancel",
            width=110,
            command=self.cancel,
    )

        self.cancel_button.grid(
            row=0,
            column=1,
            padx=(10, 5),
            pady=10,
    )

        self.save_button = ctk.CTkButton(
            self.footer_frame,
            text="Save",
            width=110,
            command=self.save,
    )

        self.save_button.grid(
            row=0,
        column=2,
            padx=(5, 20),
            pady=10,
        )
            # ---------------------------------------------------------
            # Default Actions
            # ---------------------------------------------------------

    def save(self):

        if not self.validate():
         return

        self.result = self.collect_data()

        self.clear_dirty()

        self.close()

    def cancel(self):

        self.close()
    # ---------------------------------------------------------
    # Keyboard Events
    # ---------------------------------------------------------

    def _bind_events(self):

        self.bind("<Escape>", self._on_escape)

        self.bind("<Return>", self._on_enter)
    def _on_escape(self, event=None):

        self.cancel()
    def _on_enter(self, event=None):

        self.save()
    # ---------------------------------------------------------
    # Dirty State
    # ---------------------------------------------------------

    def set_dirty(self):

        self._is_dirty = True

        self.set_status("Unsaved changes")

    def clear_dirty(self):

        self._is_dirty = False

        self.set_status("Ready")

    @property
    def is_dirty(self):

        return self._is_dirty
    # ---------------------------------------------------------
    # Status
    # ---------------------------------------------------------

    def set_status(
        self,
        message: str
    ):

        self.status_label.configure(
            text=message
        )

    def clear_status(self):

        self.status_label.configure(
            text="Ready"
        )
    # ---------------------------------------------------------
    # Validation
    # ---------------------------------------------------------

    def validate(self):
        """
        Child forms should override this method.
        """
        return True

    # ---------------------------------------------------------
    # Helpers
    # ---------------------------------------------------------

    def mark_modified(self, event=None):

        self.set_dirty()
            # ---------------------------------------------------------
    # Data Hooks
    # ---------------------------------------------------------

    def load_data(self, data=None):
       """
       Child class should populate controls
       from the supplied object.
       """
       raise NotImplementedError(
        "Child form must implement load_data()."
    )


    def collect_data(self):
       """
       Child class should return
       model object or dictionary.
       """
       raise NotImplementedError(
        "Child form must implement collect_data()."
    )

    def reset(self):
        """
        Child class should clear controls.
       """
        raise NotImplementedError(
        "Child form must implement reset()."
    )
    def _build_form(self):
        """
        Child forms should override this method to build their specific UI.
        This method is called after the header, content, and footer frames are created.
        """
        pass
   
        # ---------------------------------------------------------
    # Messages
    # ---------------------------------------------------------

    def show_error(self, message: str):

        self.set_status(message)

        self.status_label.configure(
            text_color="red"
        )

    def show_success(self, message: str):

        self.set_status(message)

        self.status_label.configure(
            text_color="green"
        )

    def show_info(self, message: str):

        self.set_status(message)

        self.status_label.configure(
            text_color=("gray20", "gray80"))
            # ---------------------------------------------------------
    # Buttons
    # ---------------------------------------------------------

    def enable_save(self):

        self.save_button.configure(
            state="normal"
        )

    def disable_save(self):

        self.save_button.configure(
            state="disabled"
        )
            # ---------------------------------------------------------
    # Window Title
    # ---------------------------------------------------------

    def set_title(self, title: str):

        self.form_title = title

        self.title(title)

        self.header_label.configure(
            text=title
        )
            # ---------------------------------------------------------
    # Close
    # ---------------------------------------------------------

    def close(self):

        self.grab_release()

        self.destroy()
    def _build_form(self):
         pass 