# ComfyUI Save Original MP4 + RIFE FPS Controller

Two lightweight ComfyUI custom nodes designed for batch video upscaling and frame interpolation. Developed for **Ultimate Image - Video Upscaler** by **AI WaifuHen**, with assistance from ChatGPT.

## Included nodes

### Save Original MP4 (VHS)
Finalizes a VideoHelperSuite MP4 with muxed audio, using the input video's original filename instead of the extra VHS numbering.

- Takes **VHS Video Combine → Filenames** (`VHS_FILENAMES`)
- Takes **FolderBatch Video Queue → file_name** (`STRING`)
- Saves `ComfyUI/output/RelayVSR_Upscaled/<source-filename>.mp4` by default
- Supports `skip`, `overwrite`, or `rename` when a target exists
- Optional `remove_intermediates`: deletes only the related silent MP4, PNG preview, and source muxed MP4, after copying and checking the output
- Never intentionally deletes the input video
- Does **not** encode or upscale videos itself; VHS handles encoding and audio

**Important:** This implementation expects VHS to produce exactly one `-audio.mp4` file. If the input video has no audio and VHS does not create that file, the node raises an error and preserves intermediates. The optional `ffprobe` validation runs only if `ffprobe` is on PATH. Test with short disposable videos before batch processing.

### RIFE FPS Controller
Calculates output FPS for native ComfyUI RIFE frame interpolation.

- Inputs: original `fps` and `multiplier` (2, 3, or 4)
- Outputs: `output_fps = fps × multiplier` and the same integer `multiplier`
- Connect `multiplier` to the native `FrameInterpolate` node
- Connect `output_fps` to the FPS selection switch, and the selected FPS to `VHS Video Combine.frame_rate`
- Put the controller and native RIFE nodes in an optional/bypass group, keeping the switches outside it, so disabling interpolation selects the original FPS and images

For example, 24 FPS with RIFE x2 becomes 48 FPS; with RIFE x3 it becomes 72 FPS.

## Requirements

- ComfyUI
- [ComfyUI-VideoHelperSuite](https://github.com/Kosinkadink/ComfyUI-VideoHelperSuite) for the `VHS_FILENAMES` input and MP4/audio creation
- A folder/video queue that provides the source video filename, such as [ComfyUI-FolderBatch](https://github.com/aiai-r/ComfyUI-FolderBatch), for source-name automation
- Native `FrameInterpolationModelLoader` and `FrameInterpolate` nodes if you use RIFE

There are no additional Python packages required by these two nodes. External libraries required by VHS and ComfyUI must be installed separately.

## Installation

**ComfyUI Manager / Registry:** Once this repository is published to Comfy Registry, search for **Save Original MP4** in Manager.

**Manual installation:**

```bash
cd ComfyUI/custom_nodes
git clone https://github.com/aiwaifuhen-oss/ComfyUI-SaveOriginalMP4.git
```

Restart ComfyUI after installation. If a manually installed copy of the same node is already present, remove that old copy before installing through Manager to avoid duplicate node identifiers.

## Example workflow

```text
FolderBatch Video Queue → VHS Load Video → (optional RIFE) → RelayVSR → VHS Video Combine
             └─ file_name ────────────────────────────────────────────────┐
                                       VHS Filenames ─────────────────────┤
                                                               Save Original MP4
```

Connect the original audio and the correctly selected FPS to VHS Video Combine. The RIFE FPS Controller changes the declared output frame rate; it does not itself interpolate frames.

## Notes and safety

- Use output subfolders inside ComfyUI's configured `output` directory.
- When `on_existing=skip`, the existing final output remains, and VHS intermediate files are deliberately retained.
- `overwrite` replaces an existing output; `rename` adds a numbered suffix.
- Avoid processing a source folder that includes previous upscaled outputs.
- If VHS fails to mux audio or the saved MP4 is invalid, inspect the retained intermediate files.
- Always make a backup before enabling cleanup for the first time.

## Version

**1.1.0** – Save Original MP4 (VHS) and RIFE FPS Controller.

## Contributing / Issues

Use GitHub Issues and include ComfyUI version, VideoHelperSuite version, and reproducible steps. Do not post private file paths or prompts.

## License

[MIT](LICENSE).
