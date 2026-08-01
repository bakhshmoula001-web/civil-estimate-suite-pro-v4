# main_window.py
from __future__ import annotations

import customtkinter as ctk

from app.application_context import ApplicationContext
from gui.layout.header import Header
from gui.layout.sidebar import Sidebar
from gui.window_manager import WindowManager
from gui.layout.statusbar import StatusBar

class MainWindow(ctk.CTk):
    WIDTH = 1400
    HEIGHT = 850

    def __init__(self, context: ApplicationContext):
        super().__init__()
        self.context = context
        self.window_manager = None
        self._configure_window()
        self._create_layout()
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def _configure_window(self):
        self.title(f"{self.context.application_name} {self.context.version}")
        self.geometry(f"{self.WIDTH}x{self.HEIGHT}")
        self.minsize(1200, 700)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(1, weight=1)

    def _create_layout(self):
        self.header = Header(self, self.context)
        self.header.grid(row=0, column=0, columnspan=2, sticky="ew")

        self.sidebar = Sidebar(self, on_navigate=self.on_navigate)
        self.sidebar.grid(row=1, column=0, sticky="ns")
        self.sidebar.grid_propagate(False)

        self.content_frame = ctk.CTkFrame(self, corner_radius=0)
        self.content_frame.grid(row=1, column=1, sticky="nsew")
        self.content_frame.grid_rowconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(0, weight=1)

        self.window_manager = WindowManager(self.content_frame, self.context)
        self.window_manager.show_page("dashboard")

        self.statusbar = StatusBar(self, self.context)
        self.statusbar.grid(row=2, column=0, columnspan=2, sticky="ew")

    def on_navigate(self, page_name: str):
        if hasattr(self.sidebar, "select"):
            self.sidebar.select(page_name)
        if hasattr(self.header, "set_title"):
         self.header.set_title(page_name.replace("_", " ").title())

        if hasattr(self.header, "set_breadcrumb"):
         self.header.set_breadcrumb(f"Home > {page_name.title()}")
        if self.window_manager:
            self.window_manager.show_page(page_name)
        if getattr(self.context, "logger", None):
            self.context.logger.info(f"Navigate -> {page_name}")
        if hasattr(self, "statusbar"):
         self.statusbar.set_status(f"Current Page : {page_name.title()}")    

    def on_close(self):
        if getattr(self.context, "logger", None):
            self.context.logger.info("Application closed.")
        self.destroy()
