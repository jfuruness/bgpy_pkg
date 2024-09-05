from pathlib import Path

from PIL import Image, ImageFile


class DiagramAggregator:
    """Aggregates diagrams"""

    def __init__(self, base_dir: Path):
        # Needed to aggregate all diagrams
        self.base_dir: Path = base_dir
        self.base_dir.mkdir(parents=True, exist_ok=True)
        # Fix to allow loading of truncated images
        # https://stackoverflow.com/questions/60584155/oserror-image-file-is-truncated
        ImageFile.LOAD_TRUNCATED_IMAGES = True

    def aggregate_diagrams(self):
        """Aggregates all test diagrams for readability into a PDF"""

        # Because we have too many tests, we need to aggregate them for
        # readability
        # https://stackoverflow.com/a/47283224/8903959
        images = [Image.open(x) for x in self.image_paths]
        assert images, "No images were present"
        converted_images = list()
        for img in images:
            if img.mode == "RGBA":
                converted_images.append(img.convert("RGB"))
                img.close()
            else:
                converted_images.append(img)

        # Aggregate all images into a PDF
        converted_images[0].save(
            self.aggregated_diagrams_path,
            "PDF",
            resolution=100.0,
            save_all=True,
            append_images=converted_images[1:],
        )
        for img in converted_images:  # type: ignore
            img.close()

    @property
    def aggregated_diagrams_path(self) -> Path:
        """Returns the path to the aggregated diagrams PDF"""

        return self.base_dir / "aggregated_diagrams.pdf"

    @property
    def image_paths(self) -> list[Path]:
        """Returns paths as strings for all images"""

        return sorted(self.base_dir.glob("*/*png"))
