from .save_original_mp4 import SaveOriginalMP4
from .fps_controller import RIFEFPSController

NODE_CLASS_MAPPINGS = {
    "SaveOriginalMP4": SaveOriginalMP4,
    "RIFEFPSController": RIFEFPSController,
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "SaveOriginalMP4": "Save Original MP4 (VHS)",
    "RIFEFPSController": "RIFE FPS Controller",
}
