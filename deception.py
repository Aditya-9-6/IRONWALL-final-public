import asyncio
import uuid
import re

HONEYTOKEN_NAME = "auth_token_v2"
# HTML Injection Snippet (Hidden Input)
# We use a random value generator, but for the honeytoken detection logic,
# we simpler check if the field NAME exists in the POST body.
# The value doesn't matter as much as the fact that the bot submitted a hidden field.

class DeceptionManager:
    
    def inject_honeytoken(self, html_content: bytes) -> bytes:
        """
        Injects a hidden honeytoken field into HTML forms.
        Strategies:
        1. Find </form> and inject before it.
        """
        token_val = str(uuid.uuid4())
        honey_input = f'<input type="hidden" name="{HONEYTOKEN_NAME}" value="{token_val}" style="display:none;">'
        
        # Simple regex replacement to insert before the closing form tag
        # Use bytes for performance since aiohttp streams bytes
        pattern = b"(</form>)"
        replacement = f"{honey_input}\\1".encode('utf-8')
        
        # We only inject into the first form to minimize breakage
        # For a more robust solution, use BeautifulSoup, but regex is faster for proxy streaming
        return re.sub(pattern, replacement, html_content, count=1, flags=re.IGNORECASE)

    async def engage_tarpit(self, request):
        """
        The Tarpit: Wastes attacker's time by holding the connection open
        and sending data extremely slowly.
        """
        # Send a 200 OK headers first to keep them hooked
        # We can't easily send headers here if the caller expects a response object return
        # So we usually return a StreamResponse and manage it manually.
        pass # Logic handled in proxy_engine due to aiohttp StreamResponse structure

    def check_honeytoken(self, body_str: str) -> bool:
        """Returns True if the honeytoken POST parameter is present."""
        if f'{HONEYTOKEN_NAME}=' in body_str:
            return True
        return False
