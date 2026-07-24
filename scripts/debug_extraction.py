"""Debug script to see exactly what's being sent to LLM and what it returns."""
import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv

# Load environment
PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / "graphrag_workspace" / ".env")

# Get API key
api_key = os.getenv("GRAPHRAG_API_KEY")
if not api_key:
    print("ERROR: GRAPHRAG_API_KEY not found in environment")
    sys.exit(1)

print(f"✓ API Key loaded: {api_key[:20]}...")

# Read medical prompt
prompt_file = PROJECT_ROOT / "graphrag_workspace" / "prompts" / "extract_graph_medical.txt"
with open(prompt_file) as f:
    system_prompt = f.read()

# Read patient data
patient_file = PROJECT_ROOT / "graphrag_workspace" / "input" / "patient_0000.txt"
with open(patient_file) as f:
    patient_text = f.read()

# Get first 1200 tokens (approx chars) for testing
test_text = patient_text[:2000]

print("\n" + "="*80)
print("SYSTEM PROMPT (first 500 chars):")
print("="*80)
print(system_prompt[:500])

print("\n" + "="*80)
print("PATIENT TEXT BEING SENT TO LLM:")
print("="*80)
print(test_text)

print("\n" + "="*80)
print("CALLING GPT-4.1...")
print("="*80)

# Call Azure OpenAI directly
try:
    from openai import AzureOpenAI
    
    client = AzureOpenAI(
        api_key=api_key,
        api_version="2024-12-01-preview",
        azure_endpoint="https://uhgsphere-aif1.openai.azure.com"
    )
    
    response = client.chat.completions.create(
        model="gpt-4.1",
        deployment_id="gpt-4.1",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Extract entities and relationships from this medical document:\n\n{test_text}"}
        ],
        temperature=0,
        max_tokens=2000
    )
    
    print("\n" + "="*80)
    print("LLM RESPONSE:")
    print("="*80)
    print(response.choices[0].message.content)
    
    print("\n" + "="*80)
    print("ANALYSIS:")
    print("="*80)
    content = response.choices[0].message.content
    entities = [line for line in content.split('\n') if 'entity' in line.lower()]
    relationships = [line for line in content.split('\n') if 'relationship' in line.lower()]
    print(f"Entities found: {len(entities)}")
    print(f"Relationships found: {len(relationships)}")
    
    if len(entities) > 0:
        print("\nFirst entity:")
        print(entities[0])
    if len(relationships) > 0:
        print("\nFirst relationship:")
        print(relationships[0])
    
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
