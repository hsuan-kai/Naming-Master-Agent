# namer_agent/knowledge_base.py
class NamingKnowledgeBase:
    def __init__(self):
        self.surname_map = {
            # Western Surnames
            "smith": "史 (Shǐ)", "miller": "米 (Mǐ)", "johnson": "江 (Jiāng)",
            "williams": "韋 (Wéi)", "brown": "包 (Bāo)", "jones": "鍾 (Zhōng)",
            "davis": "戴 (Dài)", "wilson": "魏 (Wèi)", "moore": "莫 (Mò)",
            "taylor": "泰 (Tài)", "anderson": "安 (Ān)", "thomas": "唐 (Táng)",
            "jackson": "傑 (Jié)", "white": "白 (Bái)", "tayal": "戴 (Dài)",
            # Judges & VIPs
            "cruz": "古 (Gǔ)", "plomecka": "普 (Pǔ)", "lukasz": "盧 (Lú)",
            "kamilky": "康 (Kāng)", "arias": "艾 (Ài)", "ohsomoi": "歐 (Ōu)",
            "sala": "沙 (Shā)", "clark": "柯 (Kē)", "fardel": "方 (Fāng)",
            # Heritage Surnames
            "wu": "吳 (Wú)", "wang": "王 (Wáng)", "chang": "張 (Zhāng)",
            "chen": "陳 (Chén)", "lin": "林 (Lín)", "lee": "李 (Lǐ)",
            "li": "李 (Lǐ)", "liu": "劉 (Liú)", "huang": "黃 (Huáng)",
            "yang": "楊 (Yáng)", "tsai": "蔡 (Cài)"
        }
        
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
        
        self.lucky_numbers = [1, 3, 5, 6, 7, 8, 11, 13, 15, 16, 17, 18, 21, 23, 24, 25, 29, 31, 32, 33, 35, 37, 39, 41, 45, 47, 48, 52, 61, 63, 65, 67, 68, 81]

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

# Singleton instance
kb = NamingKnowledgeBase()
