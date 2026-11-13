"""Finalize VideoHelperSuite output, preserving the source filename."""
from pathlib import Path
import os
import shutil
import subprocess
import uuid
import folder_paths


class SaveOriginalMP4:
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "filenames": ("VHS_FILENAMES",),
            "base_name": ("STRING", {"forceInput": True}),
            "subfolder": ("STRING", {"default": "RelayVSR_Upscaled"}),
            "on_existing": (["skip", "overwrite", "rename"],),
            "remove_intermediates": ("BOOLEAN", {"default": True}),
        }}

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("saved_path",)
    FUNCTION = "finalize"
    OUTPUT_NODE = True
    CATEGORY = "video/save"

    def _paths(self, obj):
        if isinstance(obj, (str, os.PathLike)):
            yield Path(obj)
        elif isinstance(obj, (tuple, list)):
            for item in obj:
                yield from self._paths(item)
        elif isinstance(obj, dict):
            for key in ("files", "filenames", "output_files", "paths", "fullpath"):
                if key in obj:
                    yield from self._paths(obj[key])

    def finalize(self, filenames, base_name, subfolder, on_existing, remove_intermediates):
        output = Path(folder_paths.get_output_directory()).resolve()
        stem = Path(str(base_name).replace('\\', '/')).name.strip()
        if stem.lower().endswith('.mp4'):
            stem = stem[:-4]
        if stem in ('', '.', '..'):
            raise ValueError('Invalid original filename')

        folder = output / subfolder.strip().replace('\\', '/')
        folder = folder.resolve()
        if folder != output and output not in folder.parents:
            raise ValueError('Subfolder must be inside ComfyUI output')
        folder.mkdir(parents=True, exist_ok=True)

        candidates = []
        for raw in self._paths(filenames):
            path = raw if raw.is_absolute() else output / raw
            path = path.resolve()
            if path.is_file() and (path == output or output in path.parents):
                candidates.append(path)

        audio_files = [p for p in candidates if p.name.lower().endswith('-audio.mp4')]
        if len(audio_files) != 1:
            raise RuntimeError(f'Expected one muxed -audio.mp4 from VHS, found {len(audio_files)}. VHS_FILENAMES={filenames!r}')
        source = audio_files[0]
        if source.stat().st_size == 0:
            raise RuntimeError('Muxed video is empty; intermediates preserved')

        probe = shutil.which('ffprobe')
        if probe:
            check = subprocess.run(
                [probe, '-v', 'error', '-show_entries', 'format=duration',
                 '-of', 'default=noprint_wrappers=1', str(source)],
                capture_output=True, text=True
            )
            if check.returncode != 0 or 'duration=' not in check.stdout:
                raise RuntimeError('ffprobe validation failed; intermediates preserved: ' + check.stderr[-500:])

        target = folder / (stem + '.mp4')
        if target.exists():
            if on_existing == 'skip':
                print(f'[SaveOriginalMP4] Existing file skipped: {target}; source intermediates retained')
                return (str(target),)
            if on_existing == 'rename':
                i = 2
                while target.exists():
                    target = folder / f'{stem}_{i:03d}.mp4'
                    i += 1

        temp = folder / f'.{target.name}.{uuid.uuid4().hex}.tmp'
        try:
            shutil.copy2(source, temp)
            if temp.stat().st_size != source.stat().st_size:
                raise RuntimeError('Copied video size mismatch')
            os.replace(temp, target)
        finally:
            if temp.exists():
                temp.unlink()

        if remove_intermediates:
            prefix = source.name[:-len('-audio.mp4')]
            for suffix in ('.mp4', '.png'):
                p = source.with_name(prefix + suffix)
                if p.is_file() and p != target:
                    try:
                        p.unlink()
                    except OSError as exc:
                        print(f'[SaveOriginalMP4] Could not delete {p}: {exc}')
            if source != target:
                try:
                    source.unlink()
                except OSError as exc:
                    print(f'[SaveOriginalMP4] Could not delete {source}: {exc}')

        print(f'[SaveOriginalMP4] Saved: {target}')
        return (str(target),)
