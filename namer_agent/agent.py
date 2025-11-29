# namer_agent/agent.py
# V25.2: Robust Output
from google.adk.agents import Agent
from google.adk.tools import AgentTool
from .config import get_model, configure_genai
from .tools import generate_and_analyze_names

# Ensure SDK is ready
configure_genai()

root_agent = Agent(
    model=get_model(),
    name="NamingConsultant",
    description="The lead consultant.",
    instruction="""
    You are 'The Cross-Cultural Namer'.
    
    **CORE BEHAVIOR: SMART MEMORY MANAGEMENT**
    
    **PHASE 1: INTRO & COLLECT INFO**
    * If user says "Hi": Provide Intro & 3 Examples.
    * **Scenario A (Full Info):** User gives Full Name + Gender -> IGNORE history. PROCEED.
    * **Scenario B (Partial - Intro):** User says "I am Jack" -> Ask for Last Name & Gender.
    * **Scenario C (Partial - Follow-up):** User says "Davis" -> Check memory for "Jack", combine -> "Jack Davis". Confirm.
    
    **PHASE 2: EXECUTION**
    * Call `generate_and_analyze_names`.
    
    **PHASE 3: OUTPUT**
    * Present Markdown table. Use `<br>` for meaning breaks.
    * Explicitly mention the English name processed.
    
    **Conclusion:** Recommend #1 choice.
    """,
    tools=[generate_and_analyze_names],
)

from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from google.adk.tools import AgentTool
from google.genai import types
import google.generativeai as genai
import os
from typing import List, Dict
import re
import json
import ast
import random

# --- Configuration ---
if "GOOGLE_API_KEY" in os.environ:
    genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

MODEL_NAME = "gemini-2.5-flash-lite"
retry_config = types.HttpRetryOptions(attempts=5, initial_delay=1, http_status_codes=[429, 500, 503])
gemini_model = Gemini(model=MODEL_NAME, retry_options=retry_config)

# ==============================================================================
# 🧠 KNOWLEDGE ENGINE
# ==============================================================================

class NamingKnowledgeBase:
    def __init__(self):
        self.surname_map = {
            # Western Surnames
            "smith": "史 (Shǐ)", "miller": "米 (Mǐ)", "johnson": "江 (Jiāng)",
            "williams": "韋 (Wéi)", "brown": "包 (Bāo)", "jones": "鍾 (Zhōng)",
            "davis": "戴 (Dài)", "wilson": "魏 (Wèi)", "moore": "莫 (Mò)",
            "taylor": "泰 (Tài)", "anderson": "安 (Ān)", "thomas": "唐 (Táng)",
            "jackson": "傑 (Jié)", "white": "白 (Bái)", "tayal": "戴 (Dài)",
            "cruz": "古 (Gǔ)", "plomecka": "普 (Pǔ)", "lukasz": "盧 (Lú)",
            "kamilky": "康 (Kāng)","arias": "艾 (Ài)", "ohsomoi": "歐 (Ōu)",
            "sala": "沙 (Shā)", "clark": "柯 (Kē)", "fardel": "方 (Fāng)",
            # Heritage Surnames
            "wu": "吳 (Wú)", "wang": "王 (Wáng)", "chang": "張 (Zhāng)",
            "chen": "陳 (Chén)", "lin": "林 (Lín)", "lee": "李 (Lǐ)",
            "li": "李 (Lǐ)", "liu": "劉 (Liú)", "huang": "黃 (Huáng)",
            "yang": "楊 (Yáng)", "tsai": "蔡 (Cài)"
        }
        # Special Shortenings for Long Names
        self.short_name_map = {
            "abraham": "博翰", "elizabeth": "麗莎", "alexander": "力山", 
            "christopher": "克非", "jonathan": "喬森"
        }
        
        self.stroke_db = {
            "史": 5, "米": 6, "江": 7, "韋": 9, "包": 5, "鍾": 17,
            "魏": 18, "莫": 11, "泰": 10, "安": 6, "唐": 10, "傑": 12, "白": 5,
            "吳": 7, "王": 4, "張": 11, "陳": 16, "李": 7, "劉": 15, "黃": 12,
            "古": 5, "普": 12, "盧": 16, "林": 8, "康": 11,
            "艾": 8, "戴": 18, "歐": 15, "沙": 8, "柯": 9, "方": 4,
            "博": 12, "翰": 16, "雅": 12, "大": 3, "衛": 15, "恩": 10, "美": 9, 
            "麗": 19, "思": 9, "提": 12, "夫": 4, "瑞": 14, "克": 7, "莎": 13, 
            "娜": 10, "文": 4, "洛": 10, "卡": 5, "子": 3, "恒": 9, "阿": 8, "曼": 11,
            "梅": 11, "莉": 11, "瑪": 15, "蕾": 19
        }
        
        self.lucky_numbers = [1, 3, 5, 6, 7, 8, 11, 13, 15, 16, 17, 18, 21, 23, 24, 25, 29, 31, 32, 33, 35, 37, 39, 41, 45, 47, 48, 52, 58, 61, 63, 65, 67, 68, 81]

    def analyze_input_name(self, name_input: str) -> tuple[str, str]:
        parts = name_input.strip().split()
        if not parts: return None, "No name provided"
        last_word = parts[-1].lower()
        first_word = parts[0].lower()
        if last_word in self.surname_map: return self.surname_map[last_word], "Mapped from Surname"
        if first_word in self.surname_map: return self.surname_map[first_word], "Mapped from First Name"
        return None, "Phonetic Translation"

    def get_short_name(self, first_name: str) -> str:
        return self.short_name_map.get(first_name.lower(), "")

    def get_strokes(self, char: str) -> int:
        return self.stroke_db.get(char, 10) 

    def calculate_math_luck(self, name: str) -> dict:
        chars = [c for c in name if '\u4e00' <= c <= '\u9fff']
        if not chars: return {"strokes": 0, "score": 0, "verdict": "Error"}
        total = sum(self.get_strokes(c) for c in chars)
        if total in self.lucky_numbers:
            score = 90 + (total % 10)
            verdict = "🌟 Auspicious"
        else:
            score = 70 + (total % 10)
            verdict = "✨ Balanced"
        return {"strokes": total, "score": score, "verdict": verdict}

kb = NamingKnowledgeBase()

# ==============================================================================
# 🛠️ ATOMIC TOOL
# ==============================================================================

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

# ==============================================================================
# 🤖 ROOT AGENT
# ==============================================================================

root_agent = Agent(
    model=gemini_model,
    name="NamingConsultant",
    description="The lead consultant.",
    instruction="""
    You are 'The Cross-Cultural Namer'.
    
    **CORE BEHAVIOR: STATELESS PROCESSING**
    Treat every user message as a NEW request.
    
    **PHASE 1: INTRO & COLLECT INFO**
    * If the user says "Hi" or "Hello": Provide the Intro & 3 Examples.
        * Intro: "👋 Hello! I am your Naming Master. I use **Sound, Meaning, and Numerology** to create your Chinese name. I need your **Full Name** and **Gender**."
        * Examples:
            1. "I am **Abraham Clark, Male**." 
            2. "My name is **Beatrice Smith (Female)**." 
            3. "I'm **Joel Fardel**. My gender is **Male**." 
    
    * **Scenario A (Full Info):** If the user provides Full Name AND Gender (e.g., "I am Mary Smith, Female"):
        * **IGNORE PREVIOUS NAMES.** Treat this as a brand new request.
        * PROCEED to Phase 2 immediately.
        
    * **Scenario B (Partial Name and Gender Only):** If the user says "I am Jack, Male":
        * Ask: "Hi Jack! What is your Full Name?" (Do NOT call tools).

    * **Scenario C (Partial - Follow-up):** If the user says "Davis":
        * Check memory. If found ("Jack", "Male"), combine -> "Jack Davis" and confirm.
        * Ask: "Hi Davis! you are Jack Davis, Male. Is the information correct?" (Do NOT call tools).
		* If user give positive feedback (e.g., "yes"), combine them ("Jack Davis", "Male") and PROCEED to Phase 2.
		* If user give negative feedback (e.g., "no"), ask user's Full name and Gender.
 
    * **Scenario D (Partial Name Only):** If the user says "I am Jack":
        * Ask: "Hi Jack! What is your Full Name? And are you Male or Female?"
    
    * **Scenario E (Name Only):** If the user says "I am Jack Davis":
        * Ask: "Hi Jack! Are you Male or Female?"
        
    * **Scenario F (Gender Only):** If the user says "Male":
        * Check memory for name. If found, combine and PROCEED.


    **PHASE 2: EXECUTION**
    * Call `generate_and_analyze_names` with the CURRENT Name and Gender.
    
    **PHASE 3: OUTPUT**
    * Explicitly mention the English name you just processed.
    * Present the Markdown table.
    * **CRITICAL FORMATTING:** - In the 'Meaning' column, use `<br>` to create line breaks between character definitions.
      - Add Pinyin in parentheses next to the Name.
    
    **TABLE TEMPLATE:**
    | Rank | Name | Meaning | Safety | Luck Score |
    | :--- | :--- | :--- | :--- | :--- |
    | 🥇 | 史梅莉 (Shǐ-méi-lì) | 史: History <br> 梅: Plum <br> 莉: Jasmine | No obvious bad homophones. | 95 |
    
    **Conclusion:** Recommend the #1 choice.
    """,
    tools=[generate_and_analyze_names],
)
