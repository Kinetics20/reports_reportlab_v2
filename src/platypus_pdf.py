from pathlib import Path
from typing import ClassVar

from pydantic import BaseModel, Field, ConfigDict, field_validator
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


class FontSpec(BaseModel):
    """Specification of a TrueType/OpenType font to be registered in ReportLab.

        The model is immutable (``frozen``) and validates the given font path:
        it ensures that the file exists, is a regular file, and has one of the
        supported extensions (``.ttf``, ``.otf``, ``.ttc``). The path is also
        normalized (via ``expanduser()`` and ``resolve()``) to avoid ambiguity
        across CI/CD environments and different platforms.

        Example
        -------
        ```python
        from pathlib import Path

        spec = FontSpec(
            name="Roboto-Light-Italic",
            file_path=Path("./fonts/Roboto-LightItalic.ttf"),
        )
        # spec.file_path is now absolute and validated
        ```
        """
    model_config = ConfigDict(
        frozen=True,
        extra='forbid'
    )

    _ALLOWED_EXTENSIONS: ClassVar[set[str]] = {".ttf", ".otf", ".ttc"}

    name: str = Field(
        ...,
        min_length=5,
        title="Font name",
        description=(
            "Logical name under which the font will be registered in ReportLab "
            "and later used in styles (e.g. in ``style.fontName``)."
        ),
        examples=["Roboto-Light-Italic", "Inter-Regular"],
    )
    file_path: Path = Field(
        ...,
        title="Font file path",
        description=(
            "Path to a valid .ttf/.otf/.ttc file. The path will be normalized "
            "to an absolute path and validated for existence and extension."
        ),
        examples=[Path("./fonts/Roboto-LightItalic.ttf")],
    )

    @field_validator("file_path")
    @classmethod
    def _validate_and_normalize_path(cls, v: Path) -> Path:
        """Normalize and validate the font path.

        Steps performed:
        - Expands ``~`` (home directory) and resolves to an absolute path.
        - Verifies that the file exists and is a regular file.
        - Ensures that the extension is one of the allowed values
          (``.ttf``, ``.otf``, ``.ttc``).

        Args:
            v: The raw path provided by the user.

        Returns:
            A validated and normalized absolute path.

        Raises:
            ValueError: If the file does not exist, is not a file, or has
            an unsupported extension.
        """
        normalized = v.expanduser().resolve()

        if not normalized.exists():
            raise ValueError(f"Font file does not exist: {normalized}")
        if not normalized.is_file():
            raise ValueError(f"Path is not a file: {normalized}")

        ext = normalized.suffix.lower()
        if ext not in cls._ALLOWED_EXTENSIONS:
            raise ValueError(
                f"Unsupported font extension '{ext}'. Allowed: {sorted(cls._ALLOWED_EXTENSIONS)}"
            )

        return normalized


# from pprint import pprint as pp

# pdfmetrics.registerFont(TTFont("Roboto-Light-Italic", "./fonts/Roboto-LightItalic.ttf"))
#
# doc = SimpleDocTemplate("pdf/platypus_intro.pdf", pagesize=A4)
# styles = getSampleStyleSheet()
#
# styles["Title"].fontName = "Roboto-Light-Italic"
# styles["BodyText"].fontName = "Roboto-Light-Italic"
#
# # pp(vars(styles["Title"]))
#
# img = ImageReader("img/ml_alg.jpg")
# iw, ih = img.getSize()
# scale = 300 / ih
#
# story = [
#     Paragraph("Tytuł dokumentu", styles["Title"]),
#     Spacer(1, 12),
#     Paragraph("To jest akapit treści. Platypus automatycznie zawija tekst i obsługuje style." * 30,
#               styles["BodyText"]),
#     Spacer(1, 24),
#     Image("img/ml_alg.jpg", width=iw * scale, height=ih * scale)
# ]
#
# doc.build(story)