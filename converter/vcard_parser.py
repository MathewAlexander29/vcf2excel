import re
import quopri

def decode_qp(value: str, charset: str = 'UTF-8') -> str:
    """Decodes Quoted-Printable encoded string with the given charset."""
    try:
        # quopri decodes byte strings, so we encode value to ascii first (QP is ASCII)
        decoded_bytes = quopri.decodestring(value.encode('ascii', errors='ignore'))
        return decoded_bytes.decode(charset, errors='replace')
    except Exception:
        return value

def split_unescaped(text: str, delimiter: str = ';') -> list[str]:
    """Splits a string by a delimiter only if it is not preceded by an unescaped backslash."""
    parts = []
    current = []
    escaped = False
    for char in text:
        if escaped:
            current.append(char)
            escaped = False
        elif char == '\\':
            current.append(char)
            escaped = True
        elif char == delimiter:
            parts.append(''.join(current))
            current = []
        else:
            current.append(char)
    parts.append(''.join(current))
    return parts

def unescape_vcf_value(value: str) -> str:
    """Unescapes standard vCard escape characters like \\, \\;, \\n, \\N."""
    parts = []
    escaped = False
    for char in value:
        if escaped:
            if char in ['n', 'N']:
                parts.append('\n')
            else:
                parts.append(char)
            escaped = False
        elif char == '\\':
            escaped = True
        else:
            parts.append(char)
    if escaped:
        parts.append('\\')
    return ''.join(parts)

def unfold_vcf_lines(raw_content: str) -> list[str]:
    """Normalizes line endings and unfolds folded lines in a vCard content string."""
    # Split by LF after normalizing CR LF and CR to LF
    raw_lines = raw_content.replace('\r\n', '\n').replace('\r', '\n').split('\n')
    
    # 1. Unfold standard folded lines (lines starting with space or tab)
    unfolded = []
    for line in raw_lines:
        if not line:
            continue
        if (line.startswith(' ') or line.startswith('\t')) and unfolded:
            unfolded[-1] += line[1:]
        else:
            unfolded.append(line)
            
    # 2. Unfold Quoted-Printable soft line breaks (lines ending with '=')
    qp_unfolded = []
    for line in unfolded:
        # If the previous line ends with '=' and it contains ENCODING=QUOTED-PRINTABLE
        if qp_unfolded and qp_unfolded[-1].endswith('=') and ('ENCODING=QUOTED-PRINTABLE' in qp_unfolded[-1].upper() or '=' in qp_unfolded[-1]):
            # Strip the trailing '=' and append current line
            qp_unfolded[-1] = qp_unfolded[-1][:-1] + line
        else:
            qp_unfolded.append(line)
            
    return qp_unfolded

def parse_vcf(vcf_content_str: str) -> list[dict]:
    """Parses a vCard content string and returns a list of contact dictionaries."""
    lines = unfold_vcf_lines(vcf_content_str)
    
    contacts = []
    current_contact = None
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Split tag and parameters from the value at the first colon
        if ':' not in line:
            continue
        key_part, val_part = line.split(':', 1)
        
        # Split tag and parameters
        key_subparts = key_part.split(';')
        tag_with_group = key_subparts[0]
        
        # Extract group if present (e.g. item1.TEL -> group: item1, tag: TEL)
        group = None
        tag = tag_with_group
        if '.' in tag_with_group:
            group, tag = tag_with_group.split('.', 1)
        
        tag = tag.upper()
        
        # Parse parameters
        params = {}
        types = []
        for p in key_subparts[1:]:
            p_upper = p.upper()
            if '=' in p:
                pk, pv = p.split('=', 1)
                pk_upper = pk.upper()
                if pk_upper == 'TYPE':
                    # Split types (e.g. TYPE=CELL,WORK)
                    types.extend([t.strip().upper() for t in pv.split(',')])
                else:
                    params[pk_upper] = pv
            else:
                # vCard 2.1 style types (e.g. TEL;CELL;WORK)
                # Any parameter without '=' is treated as a type if it is standard,
                # or we just collect it as a type anyway
                types.append(p_upper)
                
        # Handle Quoted-Printable decoding
        encoding = params.get('ENCODING', '')
        if isinstance(encoding, str) and encoding.upper() == 'QUOTED-PRINTABLE':
            charset = params.get('CHARSET', 'UTF-8')
            val_part = decode_qp(val_part, charset)
            
        # Start of a new contact card
        if tag == 'BEGIN' and val_part.upper() == 'VCARD':
            current_contact = {
                'first_name': '',
                'middle_name': '',
                'last_name': '',
                'prefix': '',
                'suffix': '',
                'display_name': '',
                'org': '',
                'department': '',
                'title': '',
                'bday': '',
                'note': '',
                'phones': [],     # List of {'value': str, 'types': list}
                'emails': [],     # List of {'value': str, 'types': list}
                'addresses': [],  # List of {'street': str, 'city': str, 'region': str, 'zip': str, 'country': str, 'types': list}
                'urls': [],       # List of {'value': str, 'types': list}
                'custom': []      # List of {'tag': str, 'value': str, 'params': dict}
            }
            continue
            
        if current_contact is None:
            continue
            
        # End of contact card
        if tag == 'END' and val_part.upper() == 'VCARD':
            contacts.append(current_contact)
            current_contact = None
            continue
            
        # Process properties
        if tag == 'FN':
            current_contact['display_name'] = unescape_vcf_value(val_part)
            
        elif tag == 'N':
            # Structured Name: Family;Given;Additional;Prefix;Suffix
            parts = split_unescaped(val_part, ';')
            # Pad to 5 elements
            parts += [''] * (5 - len(parts))
            current_contact['last_name'] = unescape_vcf_value(parts[0])
            current_contact['first_name'] = unescape_vcf_value(parts[1])
            current_contact['middle_name'] = unescape_vcf_value(parts[2])
            current_contact['prefix'] = unescape_vcf_value(parts[3])
            current_contact['suffix'] = unescape_vcf_value(parts[4])
            
        elif tag == 'ORG':
            parts = split_unescaped(val_part, ';')
            if len(parts) > 0:
                current_contact['org'] = unescape_vcf_value(parts[0])
            if len(parts) > 1:
                current_contact['department'] = unescape_vcf_value(parts[1])
                
        elif tag == 'TITLE':
            current_contact['title'] = unescape_vcf_value(val_part)
            
        elif tag == 'BDAY':
            # Birthday could be in YYYY-MM-DD or YYYYMMDD
            current_contact['bday'] = unescape_vcf_value(val_part)
            
        elif tag == 'NOTE':
            current_contact['note'] = unescape_vcf_value(val_part)
            
        elif tag == 'TEL':
            # Normalize telephone values - keep format but strip extra whitespace if needed
            tel_val = unescape_vcf_value(val_part)
            current_contact['phones'].append({
                'value': tel_val,
                'types': types
            })
            
        elif tag == 'EMAIL':
            email_val = unescape_vcf_value(val_part)
            current_contact['emails'].append({
                'value': email_val,
                'types': types
            })
            
        elif tag == 'URL':
            url_val = unescape_vcf_value(val_part)
            current_contact['urls'].append({
                'value': url_val,
                'types': types
            })
            
        elif tag == 'ADR':
            # Structured Address: PO Box;Extended;Street;Locality;Region;PostalCode;Country
            parts = split_unescaped(val_part, ';')
            parts += [''] * (7 - len(parts))
            current_contact['addresses'].append({
                'street': unescape_vcf_value(parts[2]),
                'city': unescape_vcf_value(parts[3]),
                'region': unescape_vcf_value(parts[4]),
                'zip': unescape_vcf_value(parts[5]),
                'country': unescape_vcf_value(parts[6]),
                'types': types
            })
            
        else:
            # Custom/Other property
            current_contact['custom'].append({
                'tag': tag,
                'value': unescape_vcf_value(val_part),
                'params': params,
                'group': group
            })
            
    return contacts
