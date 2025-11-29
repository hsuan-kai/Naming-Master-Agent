# namer_agent/tools.py
# ==============================================================================
# 🛠️ ATOMIC TOOL
# ==============================================================================
from typing import Dict
import re
import json
import ast
import google.generativeai as genai
from .knowledge_base import kb
from .config import MODEL_NAME

def generate_and_analyze_names(gender: str, full_name: str) -> Dict[str, dict]:
    """Atomic Tool: Generates 5 Concise Chinese names and analyzes them."""
    print(f"⚡ Atomic Tool: Processing {full_name}...")
    
    # 1. Mapping
    mapped_surname, logic = kb.analyze_input_name(full_name)
    
    # Context Preparation
    parts = full_name.split()
    first_name_eng = parts[0]
    
    surname_instruction = f"User's Surname is '{mapped_surname}'. **YOU MUST USE THIS CHARACTER AS THE SURNAME.**" if mapped_surname else "Pick a phonetic surname."
    
    # Check for specific shortenings (Abraham -> BoHan)
    short_name_suggestion = kb.get_short_name(first_name_eng)
    short_instruction = f"Note: '{first_name_eng}' is often translated as '{short_name_suggestion}'." if short_name_suggestion else ""

    model = genai.GenerativeModel(MODEL_NAME)
    gen_prompt = f"""
    Task: Generate exact 5 distinct Chinese names for "{full_name}" ({gender}).
    
    **RULES:**
    1. **Surname:** {surname_instruction}
    2. **Given Name:** {short_instruction} Must sound like "{first_name_eng}".
    3. **Length:** **STRICTLY 3 CHARACTERS MAX** (1 Surname + 2 Given Name). 
    4. **Script:** Traditional Chinese (繁體) ONLY.
    5. **Style:** Elegant, Meaningful, Native-sounding.
    
    Return ONLY a Python list of strings. Example: ["柯博翰", "柯伯韓"]
    """

    candidates = []
    try:
        res = model.generate_content(gen_prompt)
        text = res.text.replace("```json", "").replace("```python", "").replace("```", "").strip()
        try:
            candidates = ast.literal_eval(text)
        except:
            match = re.search(r'\[.*?\]', text, re.DOTALL)
            candidates = ast.literal_eval(match.group(0)) if match else []
    except:
        candidates = []

    if not candidates: return {"Error": "Generation Failed"}

    # 2. Analyze (Updated Prompt for Breakdown)
    results = {}
    ling_prompt = f"""
    Analyze these names: {candidates}
    
    **CRITICAL FORMATTING INSTRUCTION:**
    For 'meaning', you MUST break down EACH character separately with a colon.
    Example: "史: History; 梅: Plum; 莉: Jasmine"
    
    For 'safety': Check for bad homophones.
    Example: No obvious bad homophones. However, 馬 (mǎ) can sometimes be associated with negative concepts like '馬子' (mǎ zǐ - vulgar terms for girlfriend, and the old name for "toilet") in certain contexts, but it's not a direct or strong negative homophone in this name.
    Return ONLY a JSON object keyed by name.
    """
    try:
        res = model.generate_content(ling_prompt)
        text = res.text.replace("```json", "").replace("```", "").strip()
        try:
            linguistic_data = json.loads(text)
        except:
            linguistic_data = ast.literal_eval(text)
        
        if isinstance(linguistic_data, list):
            new_data = {}
            for item in linguistic_data:
                if isinstance(item, dict) and 'name' in item: new_data[item['name']] = item
            linguistic_data = new_data
    except:
        linguistic_data = {}

# 3. Merge (The Robust Loop)
    for name in candidates: # Loop over CANDIDATES, not DATA
        math_data = kb.calculate_math_luck(name)
        
        # Safe Fetch: If analysis failed for this name, use fallback
        ling_data = linguistic_data.get(name, {"meaning": "Standard Transliteration", "safety": "Safe"})
        
        meaning = ling_data.get("meaning", "Standard Transliteration")
        if len(meaning) < 10 or "Name" in meaning: meaning = "Phonetic match with elegant characters."

        results[name] = {
            "meaning": meaning,
            "safety": ling_data.get("safety", "Safe"),
            "strokes": math_data["strokes"],
            "score": math_data["score"],
            "verdict": math_data["verdict"]
        }
        
    return results


    
