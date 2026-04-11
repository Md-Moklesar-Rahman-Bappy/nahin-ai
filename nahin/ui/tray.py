"""System tray interface for Nahin."""

import pystray
from PIL import Image, ImageDraw, ImageFont
import threading
import logging
import os

logger = logging.getLogger(__name__)


class TrayIcon:
    def __init__(self, on_start_callback=None, on_stop_callback=None, on_exit_callback=None):
        self.on_start_callback = on_start_callback
        self.on_stop_callback = on_stop_callback
        self.on_exit_callback = on_exit_callback
        self.icon = None
        self.is_listening = False
        self.tray_thread = None
        
    def _create_icon_image(self, listening: bool = False) -> Image:
        size = (64, 64)
        image = Image.new('RGB', size, color='#1a1a2e')
        draw = ImageDraw.Draw(image)
        
        if listening:
            color = '#00ff88'
        else:
            color = '#888888'
            
        draw.ellipse([8, 8, 56, 56], fill=color, outline='#ffffff', width=2)
        
        try:
            font = ImageFont.truetype("arial.ttf", 20)
        except:
            font = ImageFont.load_default()
            
        draw.text((24, 18), "N", fill='#1a1a2e', font=font, anchor='mm')
        
        return image
        
    def _create_menu(self):
        return pystray.Menu(
            pystray.MenuItem(
                "Nahin AI",
                lambda: None,
                default=True
            ),
            pystray.MenuItem(
                "Listening" if self.is_listening else "Not Listening",
                lambda: None,
                enabled=False
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(
                "Start" if not self.is_listening else "Stop",
                self._toggle_listening
            ),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(
                "Exit",
                self._exit
            )
        )
        
    def _toggle_listening(self, icon=None, item=None):
        if self.is_listening:
            if self.on_stop_callback:
                self.on_stop_callback()
            self.is_listening = False
        else:
            if self.on_start_callback:
                self.on_start_callback()
            self.is_listening = True
            
        self._update_icon()
        
    def _update_icon(self):
        if self.icon:
            self.icon.icon = self._create_icon_image(self.is_listening)
            self.icon.menu = self._create_menu()
            
    def _exit(self, icon=None, item=None):
        self.is_listening = False
        if self.on_exit_callback:
            self.on_exit_callback()
        if self.icon:
            self.icon.stop()
            
    def show_notification(self, title: str, message: str):
        if self.icon:
            self.icon.notify(message, title)
            
    def run(self):
        self.icon = pystray.Icon(
            "nahin_ai",
            self._create_icon_image(),
            "Nahin AI Assistant",
            self._create_menu()
        )
        
        self.tray_thread = threading.Thread(target=self._run_icon, daemon=True)
        self.tray_thread.start()
        
    def _run_icon(self):
        try:
            self.icon.run()
        except Exception as e:
            logger.error(f"Tray icon error: {e}")
            
    def stop(self):
        self.is_listening = False
        if self.icon:
            self.icon.stop()
