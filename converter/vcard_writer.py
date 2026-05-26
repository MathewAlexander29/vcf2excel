def escape_vcf_value(value: str) -> str:
    """Escapes characters in a text value for vCard 3.0 representation."""
    if not value:
        return ''
    val = str(value)
    # Replace backslashes first, then other items
    val = val.replace('\\', '\\\\')
    val = val.replace(';', '\\;')
    val = val.replace(',', '\\,')
    val = val.replace('\n', '\\n').replace('\r', '')
    return val

def fold_line(line: str) -> str:
    """Folds a vCard line to keep it within the 75 character limit (RFC 2426)."""
    if len(line) <= 75:
        return line
    parts = [line[:75]]
    remaining = line[75:]
    while len(remaining) > 74:
        parts.append(' ' + remaining[:74])
        remaining = remaining[74:]
    if remaining:
        parts.append(' ' + remaining)
    return '\r\n'.join(parts)

def contact_to_vcard(contact: dict) -> str:
    """Converts a single contact dictionary to a vCard 3.0 string representation."""
    lines = ['BEGIN:VCARD', 'VERSION:3.0']
    
    # FN (Formatted Name)
    display_name = contact.get('display_name', '').strip()
    first_name = contact.get('first_name', '').strip()
    last_name = contact.get('last_name', '').strip()
    
    if not display_name:
        # Construct FN if missing
        parts = [contact.get('prefix', '').strip(), 
                 first_name, 
                 contact.get('middle_name', '').strip(), 
                 last_name, 
                 contact.get('suffix', '').strip()]
        display_name = ' '.join([p for p in parts if p])
        
    if display_name:
        lines.append(f"FN:{escape_vcf_value(display_name)}")
        
    # N (Structured Name: Family;Given;Additional;Prefix;Suffix)
    n_parts = [
        escape_vcf_value(contact.get('last_name', '')),
        escape_vcf_value(contact.get('first_name', '')),
        escape_vcf_value(contact.get('middle_name', '')),
        escape_vcf_value(contact.get('prefix', '')),
        escape_vcf_value(contact.get('suffix', ''))
    ]
    lines.append(f"N:{';'.join(n_parts)}")
    
    # ORG (Organization: Name;Department)
    org = contact.get('org', '').strip()
    dept = contact.get('department', '').strip()
    if org or dept:
        org_parts = [escape_vcf_value(org)]
        if dept:
            org_parts.append(escape_vcf_value(dept))
        lines.append(f"ORG:{';'.join(org_parts)}")
        
    # TITLE
    title = contact.get('title', '').strip()
    if title:
        lines.append(f"TITLE:{escape_vcf_value(title)}")
        
    # BDAY
    bday = contact.get('bday', '').strip()
    if bday:
        lines.append(f"BDAY:{escape_vcf_value(bday)}")
        
    # NOTE
    note = contact.get('note', '').strip()
    if note:
        lines.append(f"NOTE:{escape_vcf_value(note)}")
        
    # TEL
    for phone in contact.get('phones', []):
        val = phone.get('value', '').strip()
        if not val:
            continue
        types = phone.get('types', [])
        if types:
            # Join types with comma
            type_str = ','.join(types).upper()
            lines.append(f"TEL;TYPE={type_str}:{escape_vcf_value(val)}")
        else:
            lines.append(f"TEL:{escape_vcf_value(val)}")
            
    # EMAIL
    for email in contact.get('emails', []):
        val = email.get('value', '').strip()
        if not val:
            continue
        types = email.get('types', [])
        if types:
            type_str = ','.join(types).upper()
            lines.append(f"EMAIL;TYPE={type_str}:{escape_vcf_value(val)}")
        else:
            lines.append(f"EMAIL:{escape_vcf_value(val)}")
            
    # URL
    for url in contact.get('urls', []):
        val = url.get('value', '').strip()
        if not val:
            continue
        types = url.get('types', [])
        if types:
            type_str = ','.join(types).upper()
            lines.append(f"URL;TYPE={type_str}:{escape_vcf_value(val)}")
        else:
            lines.append(f"URL:{escape_vcf_value(val)}")
            
    # ADR (Structured Address: PO Box;Extended;Street;Locality;Region;PostalCode;Country)
    for addr in contact.get('addresses', []):
        street = addr.get('street', '').strip()
        city = addr.get('city', '').strip()
        region = addr.get('region', '').strip()
        zip_code = addr.get('zip', '').strip()
        country = addr.get('country', '').strip()
        
        # Check if address has any content
        if not any([street, city, region, zip_code, country]):
            continue
            
        addr_parts = [
            '',  # PO Box
            '',  # Extended Address
            escape_vcf_value(street),
            escape_vcf_value(city),
            escape_vcf_value(region),
            escape_vcf_value(zip_code),
            escape_vcf_value(country)
        ]
        
        types = addr.get('types', [])
        if types:
            type_str = ','.join(types).upper()
            lines.append(f"ADR;TYPE={type_str}:{';'.join(addr_parts)}")
        else:
            lines.append(f"ADR:{';'.join(addr_parts)}")
            
    # Custom / Other properties
    for cust in contact.get('custom', []):
        tag = cust.get('tag', '').upper()
        if not tag or tag in ['BEGIN', 'END', 'VERSION', 'FN', 'N', 'ORG', 'TITLE', 'BDAY', 'NOTE', 'TEL', 'EMAIL', 'URL', 'ADR']:
            continue
        val = cust.get('value', '')
        # Formulate parameters if any
        params = cust.get('params', {})
        param_str = ''
        if params:
            param_list = []
            for k, v in params.items():
                if v is True:
                    param_list.append(k)
                else:
                    param_list.append(f"{k}={v}")
            param_str = ';' + ';'.join(param_list)
            
        group_str = f"{cust.get('group')}." if cust.get('group') else ""
        lines.append(f"{group_str}{tag}{param_str}:{escape_vcf_value(val)}")
        
    lines.append('END:VCARD')
    
    # Fold lines and join with CRLF
    folded_lines = [fold_line(line) for line in lines]
    return '\r\n'.join(folded_lines)

def write_vcf(contacts: list[dict]) -> str:
    """Converts a list of contacts to a single vCard 3.0 content string."""
    cards = [contact_to_vcard(contact) for contact in contacts]
    return '\r\n'.join(cards) + '\r\n'
