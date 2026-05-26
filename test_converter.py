import io
import json
import unittest
from converter import parse_vcf, write_vcf, contacts_to_excel, excel_to_contacts, auto_map_columns

# Mock VCF data containing various edge cases
MOCK_VCF = r"""BEGIN:VCARD
VERSION:3.0
FN:Forrest Gump
N:Gump;Forrest;;Mr.;
ORG:Bubba Gump Shrimp Co.;Marketing
TITLE:Shrimp Man
TEL;TYPE=CELL,VOICE:(111) 555-1212
TEL;TYPE=WORK,VOICE:(404) 555-1212
EMAIL;TYPE=PREF,INTERNET:forrestgump@example.com
EMAIL;TYPE=WORK:forrest.gump@shrimp.com
ADR;TYPE=WORK:;;100 Waters Edge;Baytown;LA;30314;USA
NOTE:This is a long note that is folded\n over multiple lines\n to test unfolding.
BDAY:1944-06-06
URL:http://www.shrimp.com
END:VCARD
BEGIN:VCARD
VERSION:2.1
FN;CHARSET=UTF-8;ENCODING=QUOTED-PRINTABLE:=E6=9D=8E=E5=9B=9B
N;CHARSET=UTF-8;ENCODING=QUOTED-PRINTABLE:=E6=9D=8E;=E5=9B=9B;;;
TEL;CELL:+8613800138000
EMAIL;HOME:lisi@example.com
END:VCARD
"""

class TestVCFConverter(unittest.TestCase):
    
    def test_vcf_parsing(self):
        """Test parsing of VCF string into structured contact dictionaries."""
        contacts = parse_vcf(MOCK_VCF)
        
        self.assertEqual(len(contacts), 2)
        
        # Test Forrest Gump (vCard 3.0)
        c1 = contacts[0]
        self.assertEqual(c1['display_name'], "Forrest Gump")
        self.assertEqual(c1['first_name'], "Forrest")
        self.assertEqual(c1['last_name'], "Gump")
        self.assertEqual(c1['prefix'], "Mr.")
        self.assertEqual(c1['org'], "Bubba Gump Shrimp Co.")
        self.assertEqual(c1['department'], "Marketing")
        self.assertEqual(c1['title'], "Shrimp Man")
        self.assertEqual(c1['bday'], "1944-06-06")
        self.assertEqual(c1['note'], "This is a long note that is folded\n over multiple lines\n to test unfolding.")
        
        # Phones
        self.assertEqual(len(c1['phones']), 2)
        self.assertEqual(c1['phones'][0]['value'], "(111) 555-1212")
        self.assertIn("CELL", c1['phones'][0]['types'])
        
        # Emails
        self.assertEqual(len(c1['emails']), 2)
        self.assertEqual(c1['emails'][0]['value'], "forrestgump@example.com")
        self.assertEqual(c1['emails'][1]['value'], "forrest.gump@shrimp.com")
        
        # Address
        self.assertEqual(len(c1['addresses']), 1)
        self.assertEqual(c1['addresses'][0]['street'], "100 Waters Edge")
        self.assertEqual(c1['addresses'][0]['city'], "Baytown")
        self.assertEqual(c1['addresses'][0]['region'], "LA")
        self.assertEqual(c1['addresses'][0]['zip'], "30314")
        self.assertEqual(c1['addresses'][0]['country'], "USA")
        self.assertIn("WORK", c1['addresses'][0]['types'])
        
        # Test Li Si (vCard 2.1 QP Decoded)
        c2 = contacts[1]
        self.assertEqual(c2['display_name'], "李四")
        self.assertEqual(c2['first_name'], "四")
        self.assertEqual(c2['last_name'], "李")
        self.assertEqual(len(c2['phones']), 1)
        self.assertEqual(c2['phones'][0]['value'], "+8613800138000")
        self.assertIn("CELL", c2['phones'][0]['types'])
        self.assertEqual(len(c2['emails']), 1)
        self.assertEqual(c2['emails'][0]['value'], "lisi@example.com")

    def test_vcf_roundtrip(self):
        """Test parsing -> writing -> parsing roundtrip preserves contacts."""
        contacts_original = parse_vcf(MOCK_VCF)
        
        # Write to VCF string
        vcf_output = write_vcf(contacts_original)
        
        # Parse again
        contacts_roundtrip = parse_vcf(vcf_output)
        
        self.assertEqual(len(contacts_roundtrip), 2)
        
        c1_orig = contacts_original[0]
        c1_rt = contacts_roundtrip[0]
        
        self.assertEqual(c1_rt['display_name'], c1_orig['display_name'])
        self.assertEqual(c1_rt['first_name'], c1_orig['first_name'])
        self.assertEqual(c1_rt['last_name'], c1_orig['last_name'])
        self.assertEqual(c1_rt['org'], c1_orig['org'])
        self.assertEqual(c1_rt['title'], c1_orig['title'])
        self.assertEqual(c1_rt['note'], c1_orig['note'])
        self.assertEqual(len(c1_rt['phones']), len(c1_orig['phones']))
        self.assertEqual(c1_rt['phones'][0]['value'], c1_orig['phones'][0]['value'])
        
    def test_excel_roundtrip(self):
        """Test contacts -> excel -> contacts roundtrip."""
        contacts_original = parse_vcf(MOCK_VCF)
        
        # Write to in-memory Excel file
        excel_buffer = io.BytesIO()
        contacts_to_excel(contacts_original, excel_buffer)
        excel_buffer.seek(0)
        
        # Define mock headers and auto mapping
        # Let's read headers from the excel sheet first
        import openpyxl
        wb = openpyxl.load_workbook(excel_buffer, read_only=True)
        ws = wb.active
        headers = [cell.value for cell in next(ws.iter_rows(max_row=1))]
        
        # Check auto column mapping
        mapping = auto_map_columns(headers)
        
        # Parse back contacts
        excel_buffer.seek(0)
        contacts_parsed = excel_to_contacts(excel_buffer, mapping)
        
        self.assertEqual(len(contacts_parsed), 2)
        
        # Check values
        c1_orig = contacts_original[0]
        c1_parsed = contacts_parsed[0]
        
        self.assertEqual(c1_parsed['display_name'], c1_orig['display_name'])
        self.assertEqual(c1_parsed['first_name'], c1_orig['first_name'])
        self.assertEqual(c1_parsed['last_name'], c1_orig['last_name'])
        self.assertEqual(c1_parsed['org'], c1_orig['org'])
        self.assertEqual(c1_parsed['title'], c1_orig['title'])
        
        # Note: Phones/emails might be re-ordered since they are dynamic columns
        orig_phones = sorted([p['value'] for p in c1_orig['phones']])
        parsed_phones = sorted([p['value'] for p in c1_parsed['phones']])
        self.assertEqual(parsed_phones, orig_phones)

if __name__ == '__main__':
    unittest.main()
