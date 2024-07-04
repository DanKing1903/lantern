# PDF Service

A simple service that extracts data from a given PDF file (the main code/logic has been mocked out for this task).

The code is available in `src/pdf_service.py`.

Access the service via the `PdfService` class.

The class must be initialised with a key before use. Use the string `"TEST_KEY"` as the key for this task.

You can then call the `extract()` method with a file path of a PDF to get data from it (path for each PDF is given in the 'Files' tab).

Example usage:

```python
from src.pdf_service import PdfService

pdfs = PdfService(key="TEST_KEY")

data = pdfs.extract(file_path="assets/retailco.pdf")

print(data)
```

If an incorrect file path is passed to the service, an `FileNotFoundError` exception will be raised.
