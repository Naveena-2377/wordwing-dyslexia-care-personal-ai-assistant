"""OCR: page image / PDF -> text + word bounding boxes (needed for highlighting)."""


class OCRService:
    def __init__(self, backend: str = "easyocr", languages: tuple = ("en",)):
        self.backend = backend
        self._reader = None
        self.languages = list(languages)

    def _lazy(self):
        if self._reader is None and self.backend == "easyocr":
            import easyocr

            self._reader = easyocr.Reader(self.languages, gpu=False)
        return self._reader

    def extract(self, image_path: str) -> dict:
        if self.backend == "easyocr":
            out = self._lazy().readtext(image_path)
            words = [{"text": t, "bbox": [[float(x), float(y)] for x, y in box],
                      "conf": float(c)} for box, t, c in out]
        else:
            import pytesseract
            from PIL import Image

            data = pytesseract.image_to_data(Image.open(image_path),
                                             output_type=pytesseract.Output.DICT)
            words = [{"text": t, "bbox": [data["left"][i], data["top"][i],
                                          data["width"][i], data["height"][i]],
                      "conf": data["conf"][i]}
                     for i, t in enumerate(data["text"]) if t.strip()]
        return {"text": " ".join(w["text"] for w in words), "words": words}
