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
        words = self._sort_reading_order(words)
        return {"text": " ".join(w["text"] for w in words), "words": words}

    @staticmethod
    def _sort_reading_order(words: list[dict]) -> list[dict]:
        """EasyOCR returns boxes in detection order, not reading order - fix that here."""
        if not words:
            return words

        def top_y(w):
            ys = [p[1] for p in w["bbox"]]
            return min(ys)

        def left_x(w):
            xs = [p[0] for p in w["bbox"]]
            return min(xs)

        def height(w):
            ys = [p[1] for p in w["bbox"]]
            return max(ys) - min(ys)

        avg_h = sum(height(w) for w in words) / len(words) or 20
        words = sorted(words, key=top_y)
        lines, current, current_top = [], [words[0]], top_y(words[0])
        for w in words[1:]:
            if abs(top_y(w) - current_top) <= avg_h * 0.6:
                current.append(w)
            else:
                lines.append(current)
                current, current_top = [w], top_y(w)
        lines.append(current)
        return [w for line in lines for w in sorted(line, key=left_x)]
