import csv 
import re  
from typing import List, Dict, Optional
from extract_text import extract_text
from llm_clients.factory import get_llm_client
import os      

class MenuProcessor:
    def __init__(self, llm_provider: str = 'openai', api_key: Optional[str] = None):
        self.llm = get_llm_client(provider=llm_provider, api_key=api_key)
        
    def process_menu_file(self, file, filename: Optional[str] = None) -> List[Dict]:
        """Process an uploaded menu file and extract structured data."""
        if hasattr(file, 'read'):
            # If file is file-like object (e.g. BytesIO, StreamIO)
            content = file.read()
            if isinstance(content, bytes):
                raw_text = extract_text(content, filename=filename)
            else:
                raw_text = content.decode('utf-8')
        else:
            # If file is already bytes or string
            raw_text = extract_text(file, filename=filename)

        if not raw_text.strip():
            raise ValueError("No text could be extracted from the uploaded file.")
    
        # Build prompt and get LLM response
        prompt = self._build_prompt(raw_text)
        response_text = self.llm.generate_text(prompt=prompt)
        
        # Parse response into structured data
        items = self._parse_llm_response(response_text)
        return items
    
    def _build_prompt(self, menu_text: str) -> str:
        prompt = f"""
                You are a restaurant menu parser.

                Extract all food and beverage items from the following menu text.
                For each item, provide the following fields:
                - NAME: shorten to max 20 characters, remove filler words, keep main words
                - QUANTITY: if available, else 1
                - PRICE: in cents, no decimals or separators (e.g. 7.20 EUR -> 720)
                - WARENGRUPPE: product group inferred from item or menu context
                - HAUPTGRUPPE: 'KÜCHE' for food, 'THEKE' for beverages
                - STEUERSATZ: 7 for food, 19 for beverages
                - ORDERGRUPPE: 'KÜCHE WARM' for food, 'THEKE' for beverages
                - AUSSER_HAUS: 1 for food, 0 for drinks

                Output ONLY a JSON array of objects with these keys:
                name, quantity, price, warengruppe, hauptgruppe, steuersatz, ordergruppe, ausser_haus

                Menu text:
                \"\"\"
                {menu_text}
                \"\"\"

                Please be concise and consistent.
                """
        return prompt
    
    def _parse_llm_response(self, response_text: str) -> List[Dict]:
        import json
        try:
            # Clean common issues (like trailing commas)
            cleaned = re.sub(r",\s*}", "}", response_text)
            cleaned = re.sub(r",\s*]", "]", cleaned)

            items = json.loads(cleaned)
            
            if not isinstance(items, list):
                raise ValueError("LLM response is not a list")
            return items
        except Exception as e:
            raise RuntimeError(f"Failed to parse LLM response as JSON: {e}\nResponse:\n{response_text}")
        
    def generate_csv(self, items: List[Dict], template_path: str) -> str:
        """
        Given a list of items, generate the CSV content as a string,
        following the template CSV structure.
        """
        # Read the template CSV file (items_empty.csv)
        with open(template_path, newline='', encoding='utf-8') as f:
            lines = list(csv.reader(f))

        # lines[0], lines[1], lines[2] should be header and fixed rows
        fixed_rows = lines[:3]
        output_rows = fixed_rows[:]

        # Append items starting at line 4
        for item in items:
            row = [
                item.get("name", ""),                       # NAME (max 20 chars enforced by LLM)
                "1",                                        # NACHLASS ERLAUBT = 1 fixed
                str(item.get("ausser_haus", 0)),           # AUSSER HAUS
                "1",                                        # FREIE PREISEINGABE = 1 fixed
                "1",                                        # 0 PREIS VERBOTEN = 1 fixed
                "1",                                        # MEHRFACHNACHLASS VERBOTEN = 1 fixed
                "0",                                        # MAX BETRAG = 0 fixed
                "",                                         # BUCHUNGSTEXT empty
                "71x57_yellow.bmp",                        # BILDNAME fixed
                "",                                         # SCHRIFTGROESSE empty
                "",                                         # SCHRIFTFARBE empty
                "",                                         # HINTERGRUNDFARBE empty
                "",                                         # X / Y empty
                "0",                                        # MINUSPREIS = 0 fixed
                "0",                                        # VERSTECKEN = 0 fixed
                item.get("warengruppe", ""),               # WARENGRUPPE
                "",                                         # PFANDBETRAG empty
                "0",                                        # UNTERARTIKEL = 0 fixed
                "0",                                        # FOLGT WG = 0 fixed
                "",                                         # ORDERTEXT empty
                "0",                                        # NUR GANZE MENGEN = 0 fixed
                "",                                         # UWG empty
                "",                                         # TASTENTEXT empty
                "0",                                        # MINDESTMENGE = 0 fixed
                "0",                                        # GESPERRT = 0 fixed
                "0",                                        # HAUPTMENUE = 0 fixed
                "0",                                        # PROVISION = 0 fixed
                "0",                                        # NEGATIVBESTAND = 0 fixed
                "0",                                        # MINIMALBESTAND = 0 fixed
                "",                                         # BESTANDSWARNFARBE empty
                "0",                                        # ARTIKELBENE = 0 fixed
                "",                                         # STARTZEIT / ENDZEIT empty
                "0",                                        # EINKAUFSPREIS = 0 fixed
                "0",                                        # KEINNULLPREISDRUCK = 0 fixed
                item.get("ordergruppe", ""),               # ORDERGRUPPE
                "",                                         # ORDERREIHENFOLGE empty
                str(item.get("steuersatz", "")),           # STEUERSATZ
                str(item.get("price", "")),                # PREIS1 (price in cents)
            ]
            output_rows.append(row)

        # Write CSV to string
        import io
        output = io.StringIO()
        writer = csv.writer(output, delimiter=';')  # Semicolon delimiter assumed from typical German CSV
        writer.writerows(output_rows)
        csv_content = output.getvalue()
        output.close()

        return csv_content