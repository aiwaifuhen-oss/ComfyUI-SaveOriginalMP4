class RIFEFPSController:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "fps": ("FLOAT", {"default": 24.0, "min": 0.01, "max": 1000.0, "forceInput": True}),
                "multiplier": ("INT", {"default": 2, "min": 2, "max": 4, "step": 1}),
            }
        }

    RETURN_TYPES = ("FLOAT", "INT")
    RETURN_NAMES = ("output_fps", "multiplier")
    FUNCTION = "calculate"
    CATEGORY = "video/utility"

    def calculate(self, fps, multiplier):
        return (float(fps) * int(multiplier), int(multiplier))
