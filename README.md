# DocuFiller

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-production--ready-brightgreen.svg)

Intelligent document filling system with LLM-powered field mapping. Automatically fills DOC/DOCX/PDF templates with data from JSON, supports OCR for scanned documents, and batch processing.

## Features

- **Multi-format Support**: DOC, DOCX, PDF
- **Smart Field Detection**: 14 pattern types including placeholders, underscores, brackets
- **LLM Integration**: GigaChat for intelligent field mapping with rule-based fallback
- **OCR Support**: Process scanned PDFs with Tesseract
- **Batch Processing**: Fill multiple documents at once
- **Database Management**: Store organizations, persons, and data templates
- **Cross-platform**: Windows and Ubuntu support

## Quick Start

### Installation

```bash
pip install -r requirements.txt
```

### Ubuntu Additional Setup

```bash
sudo apt install libreoffice tesseract-ocr tesseract-ocr-rus tesseract-ocr-eng
```

### Windows Additional Setup

1. Install [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki)
2. Add Tesseract to PATH

### LLM Setup (Optional)

```bash
pip install llm llm-gigachat
llm keys set gigachat YOUR_API_KEY
```

## Usage

### Basic Example

```python
from document_filler import DocumentFiller

data = {
    'full_name': 'John Doe',
    'organization': 'Acme Corp',
    'date': '08.11.2025',
    'contract_number': 'CT-2025-001'
}

filler = DocumentFiller()
filler.fill_document('template.docx', data, 'output.docx')
```

### Batch Processing

```python
templates = ['contract.docx', 'invoice.pdf', 'agreement.doc']
filler.fill_multiple(templates, data, output_dir='filled_docs')
```

### Using Database

```python
from database_manager import DatabaseManager

db = DatabaseManager()

org_id = db.add_organization({
    'name': 'Acme Corp',
    'inn': '1234567890',
    'address': '123 Main St'
})

person_id = db.add_person({
    'full_name': 'John Doe',
    'position': 'Director',
    'organization_id': org_id
})

data = db.get_complete_data_for_document(
    organization_id=org_id,
    person_id=person_id
)

filler.fill_document('template.docx', data, 'output.docx')
```

## Supported Field Patterns

- `{{field_name}}` - Double braces
- `{field_name}` - Single braces
- `[field_name]` - Square brackets
- `<field_name>` - Angle brackets
- `_____` - Underscores (3+ chars)
- `...` - Dots (3+ chars)
- `---` - Dashes (3+ chars)
- Context markers: ФИО, Дата, Подпись, Должность, etc.

## Project Structure

```
docufiller/
├── document_processor.py    # Document format handling
├── field_detector.py         # Field detection and mapping
├── document_filler.py        # Main filling logic
├── database_manager.py       # Database operations
├── requirements.txt          # Dependencies
├── test.py                   # Test suite
└── data/
    └── example_data.json     # Sample data
```

## API Reference

### DocumentFiller

```python
fill_document(template_path: str, data: Dict, output_path: str, mapping: Optional[Dict] = None) -> str
```

Fills a single document with provided data.

```python
fill_multiple(template_paths: List[str], data: Dict, output_dir: str, mapping: Optional[Dict] = None) -> List[str]
```

Batch processes multiple documents.

### FieldDetector

```python
detect_fields_in_docx(doc: Document) -> List[Dict]
detect_fields_in_pdf(pdf_path: str) -> List[Dict]
smart_field_mapping(detected_fields: List[Dict], data: Dict) -> List[Tuple[Dict, Any]]
```

### DatabaseManager

```python
add_organization(org_data: Dict) -> int
add_person(person_data: Dict) -> int
add_data_card(card_name: str, data: Dict, card_type: str = 'general') -> int
get_complete_data_for_document(organization_id: int, person_id: int, data_card_id: int) -> Dict
```

## Testing

```bash
python test.py
```

All tests passed successfully. See `TEST_REPORT.txt` for details.

## Use Cases

- Legal contracts and agreements
- HR documents (employment contracts, NDAs)
- Invoices and financial documents
- Government forms and applications
- Medical records and prescriptions
- Real estate documents

## Roadmap

- [ ] Web interface
- [ ] REST API
- [ ] More LLM providers (OpenAI, Claude)
- [ ] Excel template support
- [ ] Digital signature integration
- [ ] Template editor GUI
- [ ] Cloud storage integration

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Support

For issues and questions, please open an issue on GitHub.

---

Made with ❤️ for document automation
