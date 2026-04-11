"""System control actions (volume, brightness, power)."""

import pyautogui
import logging
import subprocess
import ctypes
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

logger = logging.getLogger(__name__)


class SystemActions:
    def __init__(self):
        self.volume_step = 5
        
    def increase_volume(self, amount: int = None) -> str:
        try:
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = cast(interface, POINTER(IAudioEndpointVolume))
            
            current = volume.GetMasterVolumeLevelScalar()
            step = (amount or self.volume_step) / 100
            new_volume = min(1.0, current + step)
            volume.SetMasterVolumeLevelScalar(new_volume, None)
            
            return f"Volume increased to {int(new_volume * 100)}%"
        except Exception as e:
            logger.error(f"Volume increase failed: {e}")
            return "Volume বাড়ানো সম্ভব হয়নি"
            
    def decrease_volume(self, amount: int = None) -> str:
        try:
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = cast(interface, POINTER(IAudioEndpointVolume))
            
            current = volume.GetMasterVolumeLevelScalar()
            step = (amount or self.volume_step) / 100
            new_volume = max(0.0, current - step)
            volume.SetMasterVolumeLevelScalar(new_volume, None)
            
            return f"Volume decreased to {int(new_volume * 100)}%"
        except Exception as e:
            logger.error(f"Volume decrease failed: {e}")
            return "Volume কমানো সম্ভব হয়নি"
            
    def mute_volume(self) -> str:
        try:
            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = cast(interface, POINTER(IAudioEndpointVolume))
            
            volume.SetMute(1, None)
            return "Volume muted"
        except Exception as e:
            logger.error(f"Mute failed: {e}")
            return "Mute করা সম্ভব হয়নি"
            
    def increase_brightness(self, amount: int = None) -> str:
        try:
            import screen_brightness_control as sbc
            current = sbc.get_brightness()[0]
            step = amount or 10
            new_brightness = min(100, current + step)
            sbc.set_brightness(new_brightness)
            return f"Brightness increased to {new_brightness}%"
        except ImportError:
            return "Brightness control requires screen-brightness-control package"
        except Exception as e:
            logger.error(f"Brightness increase failed: {e}")
            return "Brightness বাড়ানো সম্ভব হয়নি"
            
    def decrease_brightness(self, amount: int = None) -> str:
        try:
            import screen_brightness_control as sbc
            current = sbc.get_brightness()[0]
            step = amount or 10
            new_brightness = max(0, current - step)
            sbc.set_brightness(new_brightness)
            return f"Brightness decreased to {new_brightness}%"
        except ImportError:
            return "Brightness control requires screen-brightness-control package"
        except Exception as e:
            logger.error(f"Brightness decrease failed: {e}")
            return "Brightness কমানো সম্ভব হয়নি"
            
    def shutdown(self) -> str:
        try:
            subprocess.run(["shutdown", "/s", "/t", "30"], check=True)
            return "PC will shutdown in 30 seconds"
        except Exception as e:
            logger.error(f"Shutdown failed: {e}")
            return "Shutdown সম্ভব হয়নি"
            
    def restart(self) -> str:
        try:
            subprocess.run(["shutdown", "/r", "/t", "30"], check=True)
            return "PC will restart in 30 seconds"
        except Exception as e:
            logger.error(f"Restart failed: {e}")
            return "Restart সম্ভব হয়নি"
            
    def lock_pc(self) -> str:
        try:
            ctypes.windll.user32.LockWorkStation()
            return "PC locked"
        except Exception as e:
            logger.error(f"Lock failed: {e}")
            return "Lock করা সম্ভব হয়নি"
            
    def sleep(self) -> str:
        try:
            subprocess.run(["rundll32.exe", "powrprof.dll,SetSuspendState", "0", "1", "0"])
            return "PC going to sleep"
        except Exception as e:
            logger.error(f"Sleep failed: {e}")
            return "Sleep করা সম্ভব হয়নি"
            
    def take_screenshot(self) -> str:
        try:
            import datetime
            screenshot = pyautogui.screenshot()
            filename = f"screenshot_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            screenshot.save(filename)
            return f"Screenshot saved as {filename}"
        except Exception as e:
            logger.error(f"Screenshot failed: {e}")
            return "Screenshot নেওয়া সম্ভব হয়নি"
