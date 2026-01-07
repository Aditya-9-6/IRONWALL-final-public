from bs4 import BeautifulSoup
import hashlib
import time
from state_manager import state_db

# Removed global morph_map dict

def obfuscate_html(html_content: bytes) -> bytes:
    """
    Parses HTML, randomizes IDs, updates persistent state.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Generate a session-like salt
    salt = str(time.time())
    
    for tag in soup.find_all(['input', 'button']):
        # Generate new ID
        original_id = tag.get('id', '')
        if not original_id:
             original_id = tag.get('name', 'unknown')
             
        new_id = hashlib.sha256((original_id + salt).encode()).hexdigest()[:8]
        
        # Update tag
        if tag.has_attr('id'):
            tag['id'] = new_id
            state_db.set_morph_id(new_id, original_id)
        
        if tag.has_attr('name'):
             state_db.set_morph_id(new_id + "_name", tag['name'])
             tag['name'] = new_id
    
    # DLC Module G: The Minefield (Honeypot)
    # Inject a hidden input field that looks legitimate to a bot
    # but is invisible to humans.
    if soup.body:
        honeypot = soup.new_tag("input", attrs={
            "type": "text", 
            "name": "b_birthday_honey", 
            "style": "display:none; position:absolute; left:-9999px",
            "tabindex": "-1",
            "autocomplete": "off"
        })
        soup.body.append(honeypot)

    return str(soup).encode('utf-8')



def restore_form_data(form_data: dict) -> dict:
    """
    Restores obfuscated form keys from persistent state.
    """
    cleaned_data = {}
    for k, v in form_data.items():
        # Check if key is a morphed name
        original_key = state_db.get_morph_id(k + "_name")
        if original_key:
            cleaned_data[original_key] = v
        else:
            cleaned_data[k] = v
    return cleaned_data
