import json
import sqlite3
import os
from typing import Dict, List, Optional, Any
from datetime import datetime


class DatabaseManager:
    
    def __init__(self, db_path: str = 'documents_data.db'):
        self.db_path = db_path
        self.connection = None
        self._init_database()
    
    def _init_database(self):
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = sqlite3.Row
        cursor = self.connection.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS organizations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                full_name TEXT,
                inn TEXT,
                kpp TEXT,
                ogrn TEXT,
                address TEXT,
                phone TEXT,
                email TEXT,
                bank_name TEXT,
                bank_bik TEXT,
                account_number TEXT,
                corr_account TEXT,
                director_name TEXT,
                director_position TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS persons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name TEXT NOT NULL,
                first_name TEXT,
                last_name TEXT,
                middle_name TEXT,
                position TEXT,
                organization_id INTEGER,
                phone TEXT,
                email TEXT,
                passport_series TEXT,
                passport_number TEXT,
                passport_issued_by TEXT,
                passport_date TEXT,
                address TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (organization_id) REFERENCES organizations (id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS data_cards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                card_name TEXT NOT NULL,
                card_type TEXT,
                data_json TEXT NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS document_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                template_path TEXT NOT NULL,
                output_path TEXT NOT NULL,
                data_card_id INTEGER,
                organization_id INTEGER,
                person_id INTEGER,
                status TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (data_card_id) REFERENCES data_cards (id),
                FOREIGN KEY (organization_id) REFERENCES organizations (id),
                FOREIGN KEY (person_id) REFERENCES persons (id)
            )
        ''')
        
        self.connection.commit()
    
    def add_organization(self, org_data: Dict) -> int:
        cursor = self.connection.cursor()
        
        fields = ', '.join(org_data.keys())
        placeholders = ', '.join(['?' for _ in org_data])
        
        query = f'INSERT INTO organizations ({fields}) VALUES ({placeholders})'
        cursor.execute(query, list(org_data.values()))
        
        self.connection.commit()
        return cursor.lastrowid
    
    def get_organization(self, org_id: int) -> Optional[Dict]:
        cursor = self.connection.cursor()
        cursor.execute('SELECT * FROM organizations WHERE id = ?', (org_id,))
        
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None
    
    def get_all_organizations(self) -> List[Dict]:
        cursor = self.connection.cursor()
        cursor.execute('SELECT * FROM organizations ORDER BY name')
        
        return [dict(row) for row in cursor.fetchall()]
    
    def update_organization(self, org_id: int, org_data: Dict) -> bool:
        cursor = self.connection.cursor()
        
        set_clause = ', '.join([f'{key} = ?' for key in org_data.keys()])
        query = f'UPDATE organizations SET {set_clause}, updated_at = CURRENT_TIMESTAMP WHERE id = ?'
        
        cursor.execute(query, list(org_data.values()) + [org_id])
        self.connection.commit()
        
        return cursor.rowcount > 0
    
    def add_person(self, person_data: Dict) -> int:
        cursor = self.connection.cursor()
        
        fields = ', '.join(person_data.keys())
        placeholders = ', '.join(['?' for _ in person_data])
        
        query = f'INSERT INTO persons ({fields}) VALUES ({placeholders})'
        cursor.execute(query, list(person_data.values()))
        
        self.connection.commit()
        return cursor.lastrowid
    
    def get_person(self, person_id: int) -> Optional[Dict]:
        cursor = self.connection.cursor()
        cursor.execute('SELECT * FROM persons WHERE id = ?', (person_id,))
        
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None
    
    def get_all_persons(self) -> List[Dict]:
        cursor = self.connection.cursor()
        cursor.execute('SELECT * FROM persons ORDER BY full_name')
        
        return [dict(row) for row in cursor.fetchall()]
    
    def add_data_card(self, card_name: str, data: Dict, 
                     card_type: str = 'general', description: str = '') -> int:
        cursor = self.connection.cursor()
        
        data_json = json.dumps(data, ensure_ascii=False)
        
        cursor.execute('''
            INSERT INTO data_cards (card_name, card_type, data_json, description)
            VALUES (?, ?, ?, ?)
        ''', (card_name, card_type, data_json, description))
        
        self.connection.commit()
        return cursor.lastrowid
    
    def get_data_card(self, card_id: int) -> Optional[Dict]:
        cursor = self.connection.cursor()
        cursor.execute('SELECT * FROM data_cards WHERE id = ?', (card_id,))
        
        row = cursor.fetchone()
        if row:
            result = dict(row)
            result['data'] = json.loads(result['data_json'])
            return result
        return None
    
    def get_data_card_by_name(self, card_name: str) -> Optional[Dict]:
        cursor = self.connection.cursor()
        cursor.execute('SELECT * FROM data_cards WHERE card_name = ?', (card_name,))
        
        row = cursor.fetchone()
        if row:
            result = dict(row)
            result['data'] = json.loads(result['data_json'])
            return result
        return None
    
    def get_all_data_cards(self) -> List[Dict]:
        cursor = self.connection.cursor()
        cursor.execute('SELECT * FROM data_cards ORDER BY card_name')
        
        cards = []
        for row in cursor.fetchall():
            result = dict(row)
            result['data'] = json.loads(result['data_json'])
            cards.append(result)
        
        return cards
    
    def add_document_history(self, template_path: str, output_path: str,
                           data_card_id: Optional[int] = None,
                           organization_id: Optional[int] = None,
                           person_id: Optional[int] = None,
                           status: str = 'completed') -> int:
        cursor = self.connection.cursor()
        
        cursor.execute('''
            INSERT INTO document_history 
            (template_path, output_path, data_card_id, organization_id, person_id, status)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (template_path, output_path, data_card_id, organization_id, person_id, status))
        
        self.connection.commit()
        return cursor.lastrowid
    
    def get_document_history(self, limit: int = 50) -> List[Dict]:
        cursor = self.connection.cursor()
        cursor.execute('''
            SELECT * FROM document_history 
            ORDER BY created_at DESC 
            LIMIT ?
        ''', (limit,))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_complete_data_for_document(self, organization_id: Optional[int] = None,
                                      person_id: Optional[int] = None,
                                      data_card_id: Optional[int] = None) -> Dict:
        result = {}
        
        if organization_id:
            org_data = self.get_organization(organization_id)
            if org_data:
                result.update({f'org_{k}': v for k, v in org_data.items()})
                result['organization'] = org_data.get('name')
                result['organization_full'] = org_data.get('full_name')
                result['inn'] = org_data.get('inn')
                result['kpp'] = org_data.get('kpp')
                result['address'] = org_data.get('address')
        
        if person_id:
            person_data = self.get_person(person_id)
            if person_data:
                result.update({f'person_{k}': v for k, v in person_data.items()})
                result['full_name'] = person_data.get('full_name')
                result['position'] = person_data.get('position')
        
        if data_card_id:
            card = self.get_data_card(data_card_id)
            if card:
                result.update(card['data'])
        
        result['date'] = datetime.now().strftime('%d.%m.%Y')
        result['current_date'] = datetime.now()
        
        return result
    
    def load_from_json(self, json_path: str) -> Dict:
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def close(self):
        if self.connection:
            self.connection.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
