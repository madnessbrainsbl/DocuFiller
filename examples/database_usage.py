from database_manager import DatabaseManager
from document_filler import DocumentFiller

db = DatabaseManager('company_data.db')

org_id = db.add_organization({
    'name': 'ООО "Рога и Копыта"',
    'full_name': 'Общество с ограниченной ответственностью "Рога и Копыта"',
    'inn': '7701234567',
    'kpp': '770101001',
    'ogrn': '1027700123456',
    'address': 'г. Москва, ул. Ленина, д. 10',
    'phone': '+7 (495) 123-45-67',
    'email': 'info@rogaikopyta.ru',
    'bank_name': 'ПАО Сбербанк',
    'bank_bik': '044525225',
    'account_number': '40702810400000123456',
    'director_name': 'Иванов Иван Иванович',
    'director_position': 'Генеральный директор'
})

person_id = db.add_person({
    'full_name': 'Петров Петр Петрович',
    'first_name': 'Петр',
    'last_name': 'Петров',
    'middle_name': 'Петрович',
    'position': 'Менеджер по продажам',
    'organization_id': org_id,
    'phone': '+7 (495) 765-43-21',
    'email': 'petrov@rogaikopyta.ru'
})

card_id = db.add_data_card(
    card_name='Договор поставки №1',
    data={
        'contract_number': 'ДП-2025-001',
        'contract_date': '08.11.2025',
        'delivery_date': '15.11.2025',
        'amount': 150000.00,
        'product_name': 'Канцелярские товары'
    },
    card_type='supply_contract'
)

complete_data = db.get_complete_data_for_document(
    organization_id=org_id,
    person_id=person_id,
    data_card_id=card_id
)

filler = DocumentFiller()
output_path = filler.fill_document(
    'supply_contract_template.docx',
    complete_data,
    'filled_supply_contract.docx'
)

db.add_document_history(
    template_path='supply_contract_template.docx',
    output_path=output_path,
    data_card_id=card_id,
    organization_id=org_id,
    person_id=person_id,
    status='completed'
)

print(f'Contract created: {output_path}')
print(f'Organization: {complete_data["organization"]}')
print(f'Person: {complete_data["full_name"]}')
print(f'Contract number: {complete_data["contract_number"]}')

db.close()
