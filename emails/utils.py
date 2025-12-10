"""
Utility functions for email processing and AI integration.
"""
import markdown
import requests
from django.conf import settings


def markdown_to_html(markdown_text):
    """Convert markdown to HTML."""
    return markdown.markdown(markdown_text, extensions=['extra', 'nl2br'])


def render_email_html(content_markdown, template=None):
    """Render full email HTML with template (header/footer)."""
    html_content = markdown_to_html(content_markdown)
    
    if template:
        header = template.header_html or ''
        footer = template.footer_html or ''
        return f"{header}\n{html_content}\n{footer}"
    
    return html_content


def clean_ollama_response(text):
    """
    Clean up Ollama response by removing unwanted markdown artifacts.
    
    Removes:
    - Code fences (```plaintext, ```markdown, ```, etc.) at start/end
    - Extra whitespace
    - Markdown code block indicators
    """
    import re
    
    if not text:
        return text
    
    # Remove leading/trailing whitespace
    text = text.strip()
    
    # Remove code fences at the very beginning of the text
    # Matches: ```plaintext, ```markdown, ```, etc. followed by optional newline
    text = re.sub(r'^```[a-zA-Z]*\s*\n?', '', text)
    
    # Remove code fences at the very end of the text
    # Matches: optional newline followed by ```
    text = re.sub(r'\n?```\s*$', '', text)
    
    # Also check for code fences on their own lines at start/end
    # Remove lines that are just code fences
    lines = text.split('\n')
    if lines and re.match(r'^```[a-zA-Z]*\s*$', lines[0]):
        lines = lines[1:]
    if lines and re.match(r'^```\s*$', lines[-1]):
        lines = lines[:-1]
    text = '\n'.join(lines)
    
    # Final cleanup of any remaining whitespace
    return text.strip()


def rewrite_with_ollama(seed_content, recipient_name=None, additional_prompt=None):
    """
    Use Ollama to rewrite the seed email content, making it unique per recipient.
    
    Args:
        seed_content: The original seed email markdown content
        recipient_name: Optional recipient name for personalization
        additional_prompt: Optional additional instructions for the AI
    
    Returns:
        Rewritten markdown content
    """
    api_url = getattr(settings, 'OLLAMA_API_URL', 'http://localhost:11434/api/generate')
    model = getattr(settings, 'OLLAMA_MODEL', 'granite4:1b')
    
    # Build the prompt
    prompt = f"""Rewrite the following email content to make it unique and personalized, while keeping the same core message and information. Make it sound natural and engaging.

Original email content:
{seed_content}
"""
    
    if recipient_name:
        prompt += f"\nPersonalize this email for: {recipient_name}\n"
    
    if additional_prompt:
        prompt += f"\nAdditional instructions: {additional_prompt}\n"
    
    prompt += "\nReturn ONLY the rewritten email content in markdown format. Do NOT wrap it in code blocks, do NOT use ``` markers. Return the markdown content directly, maintaining the same structure and key information."
    
    try:
        response = requests.post(
            api_url,
            json={
                'model': model,
                'prompt': prompt,
                'stream': False
            },
            timeout=120  # Increased timeout for longer responses
        )
        response.raise_for_status()
        result = response.json()
        
        # Handle both streaming and non-streaming responses
        if isinstance(result, dict):
            rewritten = result.get('response', '')
            if rewritten:
                # Clean up the response to remove code fences and other artifacts
                cleaned = clean_ollama_response(rewritten)
                return cleaned if cleaned else seed_content
        
        # If no response, return original
        return seed_content
        
    except requests.exceptions.HTTPError as e:
        error_msg = f"HTTP Error calling Ollama API: {str(e)}"
        if e.response.status_code == 404:
            available = get_available_models()
            error_msg += f"\nModel '{model}' not found. Available models: {available}"
            error_msg += f"\nUpdate OLLAMA_MODEL in your .env file to use one of the available models."
        print(error_msg)
        return seed_content
    except requests.exceptions.ConnectionError as e:
        error_msg = f"Cannot connect to Ollama at {api_url}"
        error_msg += f"\nMake sure Ollama is running: ollama serve"
        print(error_msg)
        return seed_content
    except requests.exceptions.RequestException as e:
        print(f"Error calling Ollama API: {str(e)}")
        print(f"Make sure Ollama is running at {api_url}")
        return seed_content
    except Exception as e:
        print(f"Unexpected error calling Ollama API: {str(e)}")
        import traceback
        traceback.print_exc()
        return seed_content


def get_available_models():
    """Get list of available Ollama models."""
    try:
        api_url = getattr(settings, 'OLLAMA_API_URL', 'http://localhost:11434/api/generate')
        base_url = api_url.replace('/api/generate', '')
        response = requests.get(f"{base_url}/api/tags", timeout=5)
        if response.status_code == 200:
            data = response.json()
            models = [model.get('name', '') for model in data.get('models', [])]
            return ', '.join(models[:5])  # Return first 5 models
    except:
        pass
    return "Unable to fetch models"


def detect_variables(content):
    """
    Detect variables in seed email content.
    Supports patterns like:
    - [insert dates]
    - %recipients name%
    - (insert value)
    - {variable name}
    
    Returns a list of unique variable names found.
    """
    import re
    
    # Patterns to match: [text], %text%, (text), {text}
    patterns = [
        r'\[([^\]]+)\]',  # [text]
        r'%([^%]+)%',     # %text%
        r'\(([^)]+)\)',   # (text)
        r'\{([^}]+)\}',   # {text}
    ]
    
    variables = set()
    for pattern in patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        for match in matches:
            # Normalize variable name (lowercase, strip whitespace)
            var_name = match.strip().lower()
            if var_name:
                variables.add(var_name)
    
    return sorted(list(variables))


def replace_variables(content, variable_mappings, recipient=None):
    """
    Replace variables in content with actual values.
    
    Args:
        content: The content string with variables
        variable_mappings: Dict mapping variable names to values or recipient field paths
        recipient: Optional Recipient instance for field-based mappings
    
    Returns:
        Content with variables replaced (brackets/formatting removed, replaced with actual value)
    """
    import re
    
    result = content
    
    for var_name, var_value in variable_mappings.items():
        # Get the actual value
        actual_value = str(var_value) if var_value else ''
        
        # If it's a recipient field path, get the value from recipient
        if recipient and var_value.startswith('recipient.'):
            field_name = var_value.replace('recipient.', '')
            if hasattr(recipient, field_name):
                field_val = getattr(recipient, field_name)
                actual_value = str(field_val) if field_val else ''
        
        # Replace all occurrences of this variable in all formats (case-insensitive)
        # Pattern: [variable name] -> actual_value
        result = re.sub(
            r'\[([^\]]+)\]',
            lambda m: actual_value if m.group(1).strip().lower() == var_name.lower() else m.group(0),
            result,
            flags=re.IGNORECASE
        )
        
        # Pattern: %variable name% -> actual_value
        result = re.sub(
            r'%([^%]+)%',
            lambda m: actual_value if m.group(1).strip().lower() == var_name.lower() else m.group(0),
            result,
            flags=re.IGNORECASE
        )
        
        # Pattern: (variable name) -> actual_value
        result = re.sub(
            r'\(([^)]+)\)',
            lambda m: actual_value if m.group(1).strip().lower() == var_name.lower() else m.group(0),
            result,
            flags=re.IGNORECASE
        )
        
        # Pattern: {variable name} -> actual_value
        result = re.sub(
            r'\{([^}]+)\}',
            lambda m: actual_value if m.group(1).strip().lower() == var_name.lower() else m.group(0),
            result,
            flags=re.IGNORECASE
        )
    
    return result

