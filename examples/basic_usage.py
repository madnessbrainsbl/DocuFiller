from document_filler import DocumentFiller

data = {
    'full_name': 'Иванов Иван Иванович',
    'organization': 'ООО "Моя Компания"',
    'date': '08.11.2025',
    'contract_number': 'ДГ-2025-001',
    'position': 'Генеральный директор',
    'inn': '1234567890',
    'kpp': '123456789',
    'address': 'г. Москва, ул. Примерная, д. 1'
}

filler = DocumentFiller()

filler.fill_document('template.docx', data, 'filled_contract.docx')

print('Document filled successfully!')
