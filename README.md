# 🐉 Project Overview - Naming Master

> **Capstone Project for the Google AI Agents Intensive**
> 
> *Track: Freestyle Agents | Built with Google ADK & Gemini 2.5 Flash-Lite*

This project contains the core logic for **Naming Master**, a hybrid multi-agent system designed to help non-native speakers find authentic, meaningful, and culturally safe Chinese names.

### Problem Statement

Finding a Chinese name is notoriously difficult for non-native speakers. With over **6.1 billion possible combinations**, a direct translation often results in names that sound awkward, have negative homophones (e.g., sounding like "death" or "pig"), are vulgar and boring, or lack cultural significance. 

To find a _good_ name, one must balance five conflicting dimensions:

- **🔊 Phonetics:** Does it sound like the original English name?
    
- **📖 Meaning:** Do the characters convey elegance, strength, or virtue?
    
- **🛡️ Cultural Safety:** Is it free of embarrassing homophones or slang?
    
- **🧮 Onomastics (Numerology):** Does the stroke count align with traditional "Sancai" luck algorithms?
    
- **🌏 Authenticity:** Does it sound like a real name from a Chinese-speaking region?
    

This complexity  of balancing **Phonetics** (sound), **Meaning** (semantics), and **Onomastics** (numerology/luck) creates a significant hurdle—not just for foreigners, but also for native speakers.


### Solution Statement

**Naming Master** acts as a "Lead Cultural Consultant" agent. Instead of relying on a single LLM prompt, it orchestrates a sophisticated pipeline that combines **Generative AI** (for linguistic nuance and creativity) with a deterministic **Knowledge Engine** (for accurate stroke counting and surname mapping). This hybrid approach ensures that every generated name is not only phonetically accurate but also mathematically "lucky" according to traditional Sancai numerology, thereby solving the "hallucination problem" common in pure LLM solutions.

### Value Statement

Naming Master transforms a process that usually requires a human consultant into an instant, reliable service. By automating the "Safety Audit" (homophone check) and "Luck Calculation" (stroke math), users save hours of research and are prevented from lifelong embarrassment by choosing a culturally inappropriate name.

---

### Architecture

Core to Naming Master is a **Stateless Root Agent** pattern that ensures reliability across multi-turn conversations. It does not just "chat"; it executes a rigorous **Atomic Workflow** for every request.

<img width="2268" height="598" alt="Untitled diagram-2025-11-26-124505" src="https://github.com/user-attachments/assets/6b78b23c-e268-4879-a1a5-8720c2370fc0" />

The system is powered by a unique **Atomic Tool** (`generate_and_analyze_names`) that encapsulates the entire naming pipeline into a single transaction, preventing agent memory loss or timeouts.

**1. The Knowledge Engine (The Brain)**
A deterministic Python class that grounds the agent in facts. It contains:
* **Surname Map:** A database mapping Western surnames (e.g., "Smith" → "Shi") and internet handles to authentic Chinese surnames.
* **Stroke Database:** A hard-coded dictionary of Kangxi stroke counts to ensure 100% mathematical accuracy for numerology, solving the issue where LLMs often "guess" stroke counts incorrectly.

**2. The Generator Pipeline (The Creative)**
Uses `gemini-2.5-flash-lite` to phonetically transliterate the user's First Name while strictly adhering to the surname provided by the Knowledge Engine. It optimizes for elegance and standard length (2-3 characters).

**3. The Safety Audit (The Validator)**
Every generated name immediately passes through a dual-check system:
* **Math Check:** Calculates the "Luck Score" based on the stroke count database.
* **Linguistic Check:** An LLM audit to scan for negative homophones or slang associations.

---

### Key Features & Concepts

In this submission, I demonstrate the following advanced ADK concepts:

* ✅ **Custom Tools (Atomic Tooling):** I developed a unified tool that integrates Python logic (Math/Database) with Generative AI. This "Hybrid Tool" pattern solves the reliability issues of sequential agent chains.
* ✅ **Context Engineering:** The system prompt implements a "Stateless Processing" architecture, forcing the agent to clear its context window logic for every new request to prevent hallucinations from previous users.
* ✅ **Sessions & Memory:** The agent intelligently manages multi-turn slots (e.g., if a user provides a Name in Turn 1 and Gender in Turn 2, the agent retains state until the tool can be executed).

---

### Installation & Usage

This project was built against Python 3.10+.

**1. Install Dependencies**
```bash
pip install google-adk google-generativeai
```
**2. Set API Key**
```bash
export GOOGLE_API_KEY="your_api_key_here"
```

**3. Run the Agent (ADK Web UI). To launch the interactive chat interface:**
```bash
# Run from the root directory
adk web namer_agent
```

---

### 💡 Example Interaction

**User:** "My name is Mary Smith, Female."

**Agent Process:**
> 1.  **Surname Map:** Detected "Smith" → Mapped to Authentic Surname **'Shi' (史)**
> 2.  **Strategy Engine:**
>     * *Phonetic:* Transliterating "Mary" → **'Mei-Li' (梅莉)**
>     * *Semantic:* Extracting meaning "Mary" (Sea/Bitter) → **'Hai Yue' (海悅 - Ocean Joy)**
> 3.  **Safety Audit:** Scanning for negative homophones... **Passed (Safe)**
> 4.  **Numerology:** Calculating Sancai Stroke Luck... **95 (Auspicious)**
> 5.  **Synthesis:** Ranking top 5 candidates...

**Final Output:**

| Rank | Name | Meaning | Safety | Luck Score |
| :--- | :--- | :--- | :--- | :--- |
| 🥇 | **史梅莉** (Shǐ Méi Lì) | **史**: History, Chronicle (Surname)<br>**梅**: Plum Blossom, resilience<br>**莉**: Jasmine, elegance | ✅ Safe: No negative homophones found. | **95** (Auspicious) |
| 🥈 | **史瑪莉** (Shǐ Mǎ Lì) | **史**: History, Chronicle<br>**瑪**: Agate, precious stone<br>**莉**: Jasmine | ✅ Safe: Standard transliteration. | **95** (Auspicious) |
| 🥉 | **史海悅** (Shǐ Hǎi Yuè) | **史**: History<br>**海**: Ocean (Related to 'Mary')<br>**悅**: Joy, delight | ✅ Safe: Positive meaning. | **88** (Balanced) |
| 4 | **史雅麗** (Shǐ Yǎ Lì) | **史**: History<br>**雅**: Elegant, refined<br>**麗**: Beautiful | ✅ Safe: Very common and positive. | **78** (Good) |
| 5 | **史馬麗** (Shǐ Mǎ Lì) | **史**: History<br>**馬**: Horse<br>**麗**: Beautiful | ⚠️ Note: 'Ma' (Horse) is safe, but can be associated with slang in rare contexts. | **74** (Average) |

---
Citation
Addison Howard, Brenda Flynn, Eric Schmidt, Kanchana Patlolla, Kinjal Parekh, María Cruz, Naz Bayrak, Polong Lin, and Ray Harvey. Agents Intensive - Capstone Project. https://kaggle.com/competitions/agents-intensive-capstone-project, 2025. Kaggle.
