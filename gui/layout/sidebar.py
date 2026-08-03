from __future__ import annotations

import customtkinter as ctk


class Sidebar(ctk.CTkFrame):
    """
    Application Left Navigation Sidebar
    """

    WIDTH = 220

    MENU_ITEMS = [
        ("Dashboard", "dashboard"),
        ("Projects", "projects"),
        ("BOQ", "boq"),
        ("Materials", "materials"),
        ("Calculators", "calculators"),
        ("Reports", "reports"),
        ("Settings", "settings"),
    ]

    def __init__(
        self,
        master,
        on_navigate=None,
        **kwargs,
    ):
        super().__init__(
            master,
            width=self.WIDTH,
            corner_radius=0,
            **kwargs,
        )

        self.on_navigate = on_navigate
        self.buttons: dict[str, ctk.CTkButton] = {}

        self.grid_propagate(False)
        self.grid_columnconfigure(0, weight=1)

        self._create_widgets()
            # --------------------------------------------------
    # Widgets
    # --------------------------------------------------

    def _create_widgets(self):

        row = 0

        for text, page in self.MENU_ITEMS:

            button = ctk.CTkButton(
                self,
                text=text,
                height=40,
                corner_radius=8,
                anchor="w",
                fg_color="transparent",
                hover_color=("gray80", "gray25"),
                command=lambda p=page: self.navigate(p),
            )

            button.grid(
                row=row,
                column=0,
                padx=10,
                pady=5,
                sticky="ew",
            )

            self.buttons[page] = button

            row += 1

        row += 1

        self.exit_button = ctk.CTkButton(
            self,
            text="Exit",
            height=40,
            corner_radius=8,
            fg_color="#B22222",
            hover_color="#8B0000",
            command=self.master.on_close,
        )

        self.exit_button.grid(
            row=row,
            column=0,
            padx=10,
            pady=20,
            sticky="ew",
        )
            # --------------------------------------------------
    # Navigation
    # --------------------------------------------------

    def navigate(
        self,
        page_name: str,
    ) -> None:
        """
        Trigger page navigation callback.
        """

        if callable(self.on_navigate):
            self.on_navigate(page_name)

        self.select(page_name)

    # --------------------------------------------------
    # Selection
    # --------------------------------------------------

    def select(
        self,
        page_name: str,
    ) -> None:
        """
        Highlight active navigation button.
        """

        for key, button in self.buttons.items():

            if key == page_name:

                button.configure(
                    fg_color=("gray70", "gray30"),
                    text_color=("black", "white"),
                )

            else:

                button.configure(
                    fg_color="transparent",
                    text_color=("black", "white"),
                )