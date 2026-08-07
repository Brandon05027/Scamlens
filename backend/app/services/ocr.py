#will not let the user permanently save the picture, it will temporaily save in the software
from io import BytesIO
from typing import Protocol

import pytesseract
from PIL import Image, UnidentifiedImageError


TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH


class OCRProvider(Protocol):
    name: str

    def extract_text(self, image_bytes: bytes) -> str:
        """Extract readable text from image bytes."""


class TesseractOCRProvider:
    name = "tesseract"

    def extract_text(self, image_bytes: bytes) -> str:
        try:
            with Image.open(BytesIO(image_bytes)) as image:
                image = image.convert("RGB")

                extracted_text = pytesseract.image_to_string(
                    image,
                    lang="eng",
                )

        except UnidentifiedImageError as exc:
            raise ValueError(
                "The uploaded file is not a valid image."
            ) from exc

        return extracted_text.strip()


def extract_text_from_image(
    image_bytes: bytes,
    provider: OCRProvider | None = None,
) -> tuple[str, str]:
    selected_provider = provider or TesseractOCRProvider()

    extracted_text = selected_provider.extract_text(
        image_bytes
    )

    return selected_provider.name, extracted_text