from document_filler import DocumentFiller
import json

with open('../data/example_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

templates = [
    'contract_template.docx',
    'invoice_template.pdf',
    'agreement_template.doc'
]

filler = DocumentFiller()
results = filler.fill_multiple(templates, data, output_dir='filled_documents')

print(f'Processed {len(results)} documents:')
for result in results:
    print(f'  - {result}')
