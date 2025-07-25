"""
Daily update script for the AI Model Tracker.

This script is intended to run once per day (e.g. via cron).  It
performs the following steps:

1. Fetch the current list of models from the OpenRouter API.
2. Scrape or otherwise discover new models on Fal.ai.
3. Compare with the existing `models.json` to identify new names.
4. Query the Perplexity API for structured metadata about each new
   model (provider, modality, benchmarks, pricing, etc.).
5. Append new entries to `models.json` and save the file.
6. Optionally regenerate the dashboard (not needed because the front‑
   end fetches data dynamically).
7. Commit and push the updated JSON to GitHub.

Note: This implementation includes placeholders for API calls and
scraping logic.  Replace the `pass` statements with real code.  The
Perplexity API requires an API key; set it via the PERPLEXITY_API_KEY
environment variable or directly in the code below.  The GitHub
Personal Access Token (PAT) should also be set via environment
variables or inserted directly in the repo URL.
"""

import json
import os
import requests
import subprocess
from datetime import date
from typing import List, Dict, Any


# Constants: adjust these as necessary
OPENROUTER_MODELS_URL = 'https://openrouter.ai/api/v1/models'
FAL_MODELS_URL = 'https://fal.ai'  # Placeholder; scraping required
PERPLEXITY_API_URL = 'https://api.perplexity.ai/chat/completions'

# GitHub configuration
GITHUB_REPO = 'adamholtergmailcom/ai-model-tracker'
# Insert your token here or set via environment variable
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')


def load_models(json_path: str) -> List[Dict[str, Any]]:
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_models(json_path: str, models: List[Dict[str, Any]]) -> None:
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(models, f, indent=2)


def get_openrouter_models() -> List[str]:
    """
    Query the OpenRouter models API and return a list of model names.
    """
    try:
        resp = requests.get(OPENROUTER_MODELS_URL, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        
        # OpenRouter API returns a 'data' field containing the models array
        if 'data' in data:
            models = data['data']
        else:
            models = data
        
        # Each item should have an 'id' field
        names = []
        for item in models:
            if isinstance(item, dict):
                model_id = item.get('id') or item.get('name')
                if model_id:
                    names.append(model_id)
        
        print(f"Found {len(names)} models on OpenRouter")
        return names
        
    except Exception as e:
        print(f"Failed to fetch OpenRouter models: {e}")
        # Return some known OpenRouter models as fallback
        return [
            'anthropic/claude-3-5-sonnet',
            'openai/gpt-4-turbo',
            'meta-llama/llama-3.1-405b-instruct',
            'google/gemini-pro-1.5',
            'mistralai/mistral-large'
        ]


def get_falai_models() -> List[str]:
    """
    Discover models available on fal.ai by scraping their models page.
    Since fal.ai doesn't have a public API for listing all models,
    we scrape their main models page to find new model endpoints.
    """
    try:
        import re
        from urllib.parse import urljoin
        
        # Try to scrape the fal.ai models page
        models_url = 'https://fal.ai/models'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        resp = requests.get(models_url, headers=headers, timeout=30)
        resp.raise_for_status()
        
        # Look for model names in the HTML
        # This is a basic implementation - may need adjustment based on fal.ai's actual HTML structure
        model_names = []
        
        # Common patterns for model names on fal.ai
        patterns = [
            r'fal-ai/([a-zA-Z0-9\-_]+)',  # fal-ai/model-name format
            r'/models/([a-zA-Z0-9\-_]+)', # /models/model-name format
            r'data-model="([^"]+)"',       # data-model attribute
            r'"model_id":\s*"([^"]+)"',    # JSON model_id
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, resp.text, re.IGNORECASE)
            model_names.extend(matches)
        
        # Remove duplicates and filter out common non-model strings
        exclude_terms = {'api', 'docs', 'about', 'pricing', 'login', 'signup', 'dashboard', 'settings'}
        unique_models = list(set([
            name for name in model_names
            if name.lower() not in exclude_terms and len(name) > 2
        ]))
        
        print(f"Found {len(unique_models)} potential models on fal.ai")
        return unique_models[:10]  # Limit to 10 to avoid overwhelming the system
        
    except Exception as e:
        print(f"Failed to scrape fal.ai models: {e}")
        # Return some known fal.ai models as fallback
        return [
            'flux-1-1-pro',
            'flux-kontext',
            'luma-ray2',
            'kling-video',
            'ideogram-v2',
            'minimax-video-01'
        ]


def call_perplexity(model_name: str) -> Dict[str, Any]:
    """
    Query the Perplexity API with a prompt asking for structured
    information about the given model.  Parse the response and return
    a dictionary matching the schema of an entry in models.json.
    """
    api_key = os.environ.get('PERPLEXITY_API_KEY')
    if not api_key:
        raise RuntimeError('PERPLEXITY_API_KEY environment variable is not set')
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    prompt = f"""Please provide structured information about the AI model '{model_name}' in JSON format with the following fields:

{{
  "provider": "company or organization name",
  "modality": "language/image/video/audio/multimodal",
  "release_date": "YYYY-MM-DD format",
  "context_window": number or null,
  "parameters": "parameter count description or null",
  "model_type": "brief category description",
  "swe_bench_verified": number or null,
  "livecodebench": number or null,
  "aime_2025": number or null,
  "math500": number or null,
  "mmlu": number or null,
  "intelligence_index": number or null,
  "humanity_last_exam": number or null,
  "gpqa": number or null,
  "input_price_per_million_tokens": number or null,
  "output_price_per_million_tokens": number or null,
  "summary": "brief description of the model's capabilities and notable features",
  "community_comments": ["array of notable community feedback or empty array"]
}}

Only return the JSON object, no additional text."""

    payload = {
        'model': 'llama-3.1-sonar-small-128k-online',
        'messages': [
            {
                'role': 'user',
                'content': prompt
            }
        ],
        'max_tokens': 1000,
        'temperature': 0.1,
        'top_p': 0.9,
        'return_citations': True,
        'search_domain_filter': ['perplexity.ai'],
        'return_images': False,
        'return_related_questions': False,
        'search_recency_filter': 'month',
        'top_k': 0,
        'stream': False,
        'presence_penalty': 0,
        'frequency_penalty': 1
    }
    
    try:
        resp = requests.post(PERPLEXITY_API_URL, headers=headers, json=payload, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        
        # Extract the content from the response
        if 'choices' in data and len(data['choices']) > 0:
            content = data['choices'][0]['message']['content']
            # Try to parse the JSON response
            try:
                import json
                # Remove any markdown code blocks if present
                if '```json' in content:
                    content = content.split('```json')[1].split('```')[0].strip()
                elif '```' in content:
                    content = content.split('```')[1].split('```')[0].strip()
                
                parsed_data = json.loads(content)
                return parsed_data
            except json.JSONDecodeError as je:
                print(f"Failed to parse JSON response for {model_name}: {je}")
                print(f"Raw content: {content}")
                return {}
        else:
            print(f"No choices in Perplexity response for {model_name}")
            return {}
            
    except Exception as e:
        print(f"Failed to query Perplexity for {model_name}: {e}")
        return {}


def commit_and_push(file_paths: List[str]) -> None:
    """
    Commit and push the specified files to the configured GitHub repository.
    This function assumes that `git` is installed and that the working
    directory is the root of the repository.
    """
    repo_url = f'https://{GITHUB_TOKEN}@github.com/{GITHUB_REPO}.git'
    subprocess.run(['git', 'config', 'user.name', 'AI Tracker Bot'], check=True)
    subprocess.run(['git', 'config', 'user.email', 'bot@example.com'], check=True)
    subprocess.run(['git', 'add'] + file_paths, check=True)
    subprocess.run(['git', 'commit', '-m', f'auto: update models ({date.today()})'], check=True)
    subprocess.run(['git', 'push', repo_url, 'HEAD:main'], check=True)


def update_models(json_path: str) -> None:
    """
    Main function to update the models.json file.  It reads the existing
    models, queries providers for new models, enriches them via
    Perplexity and writes back the updated list.  Finally, it commits
    and pushes the changes to GitHub.
    """
    existing = load_models(json_path)
    existing_names = {m['model_name'] for m in existing}
    # Discover new models from OpenRouter and fal.ai
    discovered = set(get_openrouter_models()) | set(get_falai_models())
    new_names = [name for name in discovered if name and name not in existing_names]
    print(f"Discovered {len(new_names)} new models")
    for name in new_names:
        info = call_perplexity(name)
        if not info:
            continue
        # Map the Perplexity response to our schema.  Example fields below;
        # adjust based on the actual API output.
        entry = {
            'model_name': name,
            'provider': info.get('provider'),
            'release_date': info.get('release_date'),
            'modality': info.get('modality'),
            'context_window': info.get('context_window'),
            'parameters': info.get('parameters'),
            'model_type': 'language' if info.get('modality') == 'text' else 'media',
            'performance': {
                'swe_bench_verified': info.get('swe_bench_verified'),
                'livecodebench': info.get('livecodebench'),
                'aime_2025': info.get('aime_2025'),
                'math500': info.get('math500'),
                'mmlu': info.get('mmlu'),
                'intelligence_index': info.get('intelligence_index'),
                'humanity_last_exam': info.get('humanity_last_exam'),
                'gpqa': info.get('gpqa')
            },
            'price': {
                'input_per_million_tokens': info.get('input_price_per_million_tokens'),
                'output_per_million_tokens': info.get('output_price_per_million_tokens')
            },
            'notes': info.get('summary') or info.get('notes'),
            'community_comments': info.get('community_comments', [])
        }
        existing.append(entry)
        print(f"Added {name}")
    # Save if any new entries
    if new_names:
        save_models(json_path, existing)
        # Commit and push updates
        commit_and_push([json_path])
    else:
        print("No new models to add.")


if __name__ == '__main__':
    # Compute the path to the models.json relative to this script
    json_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'models.json')
    update_models(json_path)