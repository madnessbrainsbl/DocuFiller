import re
from typing import Dict, List, Tuple, Optional, Any
from docx import Document
from docx.text.paragraph import Paragraph
from docx.table import Table
import pymupdf as fitz
import llm
import json


class FieldDetector:
    
    def __init__(self):
        self.patterns = {
            'long_underscore': r'_{5,}',
            'medium_underscore': r'_{3,4}',
            'short_underscore': r'_{2}',
            'double_braces': r'\{\{([a-zA-Zа-яА-Я0-9_]+)\}\}',
            'single_braces': r'\{([a-zA-Zа-яА-Я0-9_]+)\}',
            'square_brackets': r'\[([^\]]+)\]',
            'angle_brackets': r'<([^>]+)>',
            'dots': r'\.{3,}',
            'dashes': r'-{3,}',
            'fio_marker': r'(ФИО|Ф\.И\.О\.|фио)',
            'date_marker': r'(Дата|дата|ДАТА)',
            'signature_marker': r'(Подпись|подпись|ПОДПИСЬ)',
            'position_marker': r'(Должность|должность|ДОЛЖНОСТЬ)',
            'organization_marker': r'(Организация|организация|ОРГАНИЗАЦИЯ)',
        }
        
        self.marker_to_field = {
            'fio_marker': 'full_name',
            'date_marker': 'date',
            'signature_marker': 'signature',
            'position_marker': 'position',
            'organization_marker': 'organization',
        }
    
    def detect_fields_in_text(self, text: str) -> List[Dict]:
        fields = []
        
        for pattern_name, pattern in self.patterns.items():
            matches = re.finditer(pattern, text)
            for match in matches:
                field_info = {
                    'type': pattern_name,
                    'start': match.start(),
                    'end': match.end(),
                    'text': match.group(0),
                    'value': match.group(1) if match.groups() else None,
                    'field_name': self._infer_field_name(pattern_name, match.group(0), text, match.start())
                }
                fields.append(field_info)
        
        # Enhance with LLM for unnamed fields
        unnamed = [f for f in fields if not f['field_name']]
        if unnamed:
            contexts = [f"{f['type']}: {f['text']} (context before: {text[max(0,f['start']-50):f['start']]}, after: {text[f['end']:f['end']+50]})" for f in unnamed]
            prompt = f"""Infer field names for these unnamed fields in a document:
{'; '.join(contexts)}

Output JSON list of field names in order."""
            try:
                model = llm.get_model('gpt-3.5-turbo')
                response = model.prompt(prompt)
                inferred_names = json.loads(response.text())
                for i, name in enumerate(inferred_names):
                    if name:
                        unnamed[i]['field_name'] = name
            except Exception as e:
                print(f"LLM inference failed: {e}. Skipping.")
        
        return sorted(fields, key=lambda x: x['start'])
    
    def detect_fields_in_docx(self, doc: Document) -> List[Dict]:
        fields = []
        
        for para_idx, para in enumerate(doc.paragraphs):
            para_fields = self._detect_in_paragraph(para, para_idx)
            fields.extend(para_fields)
        
        for table_idx, table in enumerate(doc.tables):
            table_fields = self._detect_in_table(table, table_idx)
            fields.extend(table_fields)
        
        return fields
    
    def _detect_in_paragraph(self, para: Paragraph, para_idx: int) -> List[Dict]:
        fields = []
        text = para.text
        
        for pattern_name, pattern in self.patterns.items():
            matches = re.finditer(pattern, text)
            for match in matches:
                field_info = {
                    'type': pattern_name,
                    'location': 'paragraph',
                    'paragraph_index': para_idx,
                    'start': match.start(),
                    'end': match.end(),
                    'text': match.group(0),
                    'value': match.group(1) if match.groups() else None,
                    'field_name': self._infer_field_name(pattern_name, match.group(0), text, match.start()),
                    'context': self._get_context(text, match.start(), match.end())
                }
                fields.append(field_info)
        
        return fields
    
    def _detect_in_table(self, table: Table, table_idx: int) -> List[Dict]:
        fields = []
        
        for row_idx, row in enumerate(table.rows):
            for cell_idx, cell in enumerate(row.cells):
                text = cell.text
                
                for pattern_name, pattern in self.patterns.items():
                    matches = re.finditer(pattern, text)
                    for match in matches:
                        field_info = {
                            'type': pattern_name,
                            'location': 'table',
                            'table_index': table_idx,
                            'row_index': row_idx,
                            'cell_index': cell_idx,
                            'start': match.start(),
                            'end': match.end(),
                            'text': match.group(0),
                            'value': match.group(1) if match.groups() else None,
                            'field_name': self._infer_field_name(pattern_name, match.group(0), text, match.start()),
                            'context': self._get_context(text, match.start(), match.end())
                        }
                        fields.append(field_info)
        
        return fields
    
    def _infer_field_name(self, pattern_type: str, matched_text: str, 
                          full_text: str, position: int) -> Optional[str]:
        
        if pattern_type in self.marker_to_field:
            return self.marker_to_field[pattern_type]
        
        if pattern_type in ['double_braces', 'single_braces', 'square_brackets', 'angle_brackets']:
            match = re.search(self.patterns[pattern_type], matched_text)
            if match and match.groups():
                return match.group(1).lower().strip()
        
        context_before = full_text[max(0, position-50):position].lower()
        
        if any(word in context_before for word in ['фио', 'ф.и.о', 'имя']):
            return 'full_name'
        elif any(word in context_before for word in ['дата', 'число']):
            return 'date'
        elif any(word in context_before for word in ['подпись']):
            return 'signature'
        elif any(word in context_before for word in ['должность']):
            return 'position'
        elif any(word in context_before for word in ['организация', 'компания']):
            return 'organization'
        elif any(word in context_before for word in ['адрес']):
            return 'address'
        elif any(word in context_before for word in ['телефон', 'тел']):
            return 'phone'
        elif any(word in context_before for word in ['email', 'почта']):
            return 'email'
        elif any(word in context_before for word in ['инн']):
            return 'inn'
        elif any(word in context_before for word in ['кпп']):
            return 'kpp'
        elif any(word in context_before for word in ['огрн']):
            return 'ogrn'
        elif any(word in context_before for word in ['счет', 'р/с', 'расчетный']):
            return 'account_number'
        elif any(word in context_before for word in ['банк', 'бик']):
            return 'bank'
        elif any(word in context_before for word in ['сумма']):
            return 'amount'
        elif any(word in context_before for word in ['номер', '№']):
            return 'number'
        
        return None
    
    def _get_context(self, text: str, start: int, end: int, 
                     context_length: int = 30) -> Dict[str, str]:
        before = text[max(0, start-context_length):start]
        after = text[end:min(len(text), end+context_length)]
        
        return {
            'before': before.strip(),
            'after': after.strip()
        }
    
    def smart_field_mapping(self, detected_fields: List[Dict], 
                           data: Dict) -> List[Tuple[Dict, Any]]:
        field_names = [f.get('field_name') for f in detected_fields if f.get('field_name')]
        data_keys = list(data.keys())
        
        prompt = f"""You are an expert in field mapping for documents.
Detected fields: {', '.join(field_names)}
Available data keys: {', '.join(data_keys)}

Map each detected field to the best matching data key, or null if no good match.
Output as JSON object where keys are field_names and values are data_keys or null."""
        
        try:
            model = llm.get_model('gpt-3.5-turbo')
            response = model.prompt(prompt)
            mapping_dict = json.loads(response.text())
        except Exception as e:
            print(f"LLM mapping failed: {e}. Falling back to rule-based mapping.")
            return self._rule_based_mapping(detected_fields, data)
        
        mappings = []
        for field in detected_fields:
            fn = field.get('field_name')
            if fn and fn in mapping_dict:
                key = mapping_dict[fn]
                if key and key in data:
                    mappings.append((field, data[key]))
                else:
                    mappings.append((field, None))
            else:
                mappings.append((field, None))
        
        return mappings
    
    def _rule_based_mapping(self, detected_fields: List[Dict], 
                           data: Dict) -> List[Tuple[Dict, Any]]:
        mappings = []
        for field in detected_fields:
            field_name = field.get('field_name')
            
            if field_name and field_name in data:
                mappings.append((field, data[field_name]))
                continue
            
            if field_name:
                for key in data.keys():
                    if self._fields_similar(field_name, key):
                        mappings.append((field, data[key]))
                        break
            else:
                mappings.append((field, None))
        
        return mappings
    
    def _fields_similar(self, field1: str, field2: str) -> bool:
        field1 = field1.lower().replace('_', '').replace('-', '')
        field2 = field2.lower().replace('_', '').replace('-', '')
        
        return field1 == field2 or field1 in field2 or field2 in field1

    def detect_fields_in_pdf(self, pdf_path: str) -> List[Dict]:
        doc = fitz.open(pdf_path)
        fields = []
        for page_num, page in enumerate(doc):
            text_dict = page.get_text("dict")
            for block in text_dict["blocks"]:
                if "lines" in block:
                    for line in block["lines"]:
                        for span in line["spans"]:
                            text = span["text"]
                            bbox = span["bbox"]  # (x0, y0, x1, y1)
                            for pattern_name, pattern in self.patterns.items():
                                matches = re.finditer(pattern, text)
                                for match in matches:
                                    # Calculate approximate bbox for the field
                                    rel_start = match.start() / len(text) if len(text) > 0 else 0
                                    rel_end = match.end() / len(text) if len(text) > 0 else 0
                                    field_bbox = (
                                        bbox[0] + rel_start * (bbox[2] - bbox[0]),
                                        bbox[1],
                                        bbox[0] + rel_end * (bbox[2] - bbox[0]),
                                        bbox[3]
                                    )
                                    field_info = {
                                        'type': pattern_name,
                                        'page': page_num,
                                        'bbox': field_bbox,
                                        'text': match.group(0),
                                        'value': match.group(1) if match.groups() else None,
                                        'field_name': self._infer_field_name(pattern_name, match.group(0), text, match.start()),
                                        'context': self._get_context(text, match.start(), match.end())
                                    }
                                    fields.append(field_info)
        doc.close()
        return fields
