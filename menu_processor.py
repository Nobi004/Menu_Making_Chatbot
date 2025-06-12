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
        """Process menu file in chunks to handle large files"""
        # Extract text
        raw_text = extract_text(file, filename=filename)
        if not raw_text.strip():
            raise ValueError("No text could be extracted from the uploaded file.")
        
        # Split text into chunks if too long (approx 2000 chars per chunk)
        chunks = [raw_text[i:i+2000] for i in range(0, len(raw_text), 2000)]
        all_items = []
        
        # Process each chunk
        for chunk in chunks:
            try:
                prompt = self._build_prompt(chunk)
                response_text = self.llm.generate_text(prompt=prompt)
                items = self._parse_llm_response(response_text)
                all_items.extend(items)
            except Exception as e:
                st.warning(f"Warning: Some items might not be processed correctly: {str(e)}")
                continue
        
        return all_items
    
    def _build_prompt(self, menu_text: str) -> str:
        prompt = f"""
        You are a restaurant menu parser.

        Extract all food and beverage items from the following menu text.
        For each item, provide the following fields:
        - NAME: shorten to max 20 characters, remove filler words, keep main words.
          If multiple sizes or quantities are listed for the same item (e.g., 0.23L and 0.5L for Coca Cola),
          create separate entries with the size as prefix in the name (e.g., "0.23L Coca Cola", "0.5L Coca Cola").
        - QUANTITY: if available, else 1
        - PRICE: in cents, no decimals or separators (e.g., 7.20 EUR -> 720)
        - WARENGRUPPE: product group inferred from item or menu context
        - HAUPTGRUPPE: 'KÜCHE' for food, 'THEKE' for beverages
        - STEUERSATZ: 7 for food, 19 for beverages
        - ORDERGRUPPE: 'KÜCHE WARM' for food, 'THEKE' for beverages
        - AUSSER_HAUS: 1 for food, 0 for drinks

        Additionally, correct any German grammatical mistakes in the item names and output data automatically.

        Output ONLY a JSON array of objects with these keys:
        name, quantity, price, warengruppe, hauptgruppe, steuersatz, ordergruppe, ausser_haus

        Make sure ALL data from the menu is included — no item, size, or price should be missed.

        Menu text:
        \"\"\"
        {menu_text}
        \"\"\"

        Please be concise and consistent with the output format.
        """
        return prompt



    
    def _parse_llm_response(self, response_text: str) -> List[Dict]:
        """Parse LLM response with improved error handling and JSON cleaning"""
        import json
        try:
            # Clean and normalize the response text
            cleaned = response_text.strip()
            
            # Fix common JSON formatting issues
            cleaned = re.sub(r',\s*}', '}', cleaned)  # Remove trailing commas in objects
            cleaned = re.sub(r',\s*]', ']', cleaned)  # Remove trailing commas in arrays
            cleaned = re.sub(r'}\s*{', '},{', cleaned)  # Fix missing commas between objects
            
            # Ensure the text starts with [ and ends with ]
            if not cleaned.startswith('['):
                cleaned = '[' + cleaned
            if not cleaned.endswith(']'):
                cleaned = cleaned + ']'
            
            # Handle truncated JSON
            if '"' in cleaned and not cleaned.count('"') % 2 == 0:
                # Find last complete object
                last_complete = cleaned.rfind('}')+1
                if last_complete > 0:
                    cleaned = cleaned[:last_complete] + ']'
            
            items = json.loads(cleaned)
            
            if not isinstance(items, list):
                raise ValueError("LLM response is not a list")
                
            # Validate each item has required fields
            required_fields = {'name', 'price', 'warengruppe', 'hauptgruppe', 'steuersatz', 'ordergruppe', 'ausser_haus'}
            items = [item for item in items if all(field in item for field in required_fields)]
            
            return items
        
        except json.JSONDecodeError as e:
            # More specific error message for JSON parsing issues
            raise RuntimeError(f"JSON parsing error at position {e.pos}: {str(e)}\nResponse text:\n{response_text[:500]}...")
        except Exception as e:
            raise RuntimeError(f"Failed to parse LLM response: {str(e)}\nResponse text:\n{response_text[:500]}...")
            
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