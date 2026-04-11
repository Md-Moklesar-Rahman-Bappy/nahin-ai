"""Bengali command patterns and mappings."""

BENGALI_COMMANDS = {
    "greetings": [
        "হ্যালো", "হাই", "নাহিন", "ওহে", "শুভ সকাল", "শুভ দুপুর", "শুভ সন্ধ্যা",
        "hello", "hi", "hey", "good morning", "good afternoon", "good evening"
    ],
    "farewell": [
        "বিদায়", "যাচ্ছি", "চলে যাচ্ছি", "ঘুমাতে যাচ্ছি", "থামো",
        "bye", "goodbye", "see you", "tata", "stop"
    ],
    "affirmation": [
        "হ্যাঁ", "ঠিক আছে", "জি", "এবার থামো", "ধন্যবাদ",
        "yes", "okay", "ok", "sure", "thanks", "thank you"
    ],
    "negation": [
        "না", "আর না", "থামো", "বন্ধ করো",
        "no", "nope", "stop", "cancel", "never mind"
    ],
    "system": {
        "volume_up": ["ভলিউম বাড়াও", "volume বাড়াও", "আওয়াজ বাড়াও", "বেশি করো"],
        "volume_down": ["ভলিউম কমাও", "volume কমাও", "আওয়াজ কমাও", "কম করো"],
        "volume_mute": ["নোইস করো", "mute করো", "চুপ করাও"],
        "brightness_up": ["ব্রাইটনেস বাড়াও", "brightness বাড়াও", "আলো বাড়াও"],
        "brightness_down": ["ব্রাইটনেস কমাও", "brightness কমাও", "আলো কমাও"],
        "shutdown": ["পিসি বন্ধ করো", "shutdown করো", "বন্ধ করো দয়া করে"],
        "restart": ["restart করো", "রিস্টার্ট করো", "আবার চালু করো"],
        "lock": ["lock করো", "লক করো", "বন্ধ করে রাখো"],
        "sleep": ["ঘুম দাও", "sleep করো", "বিশ্রাম নাও"],
        "screenshot": ["স্ক্রিনশট নাও", "screenshot নাও", "ছবি তুলো"]
    },
    "apps": {
        "open_chrome": ["chrome খোলো", "chrom খোলো", "ব্রাউজার খোলো"],
        "open_notepad": ["notepad খোলো", "নোটপ্যাড খোলো", "লেখার জায়গা খোলো"],
        "open_vscode": ["vscode খোলো", "vs code খোলো", "coding খোলো"],
        "open_explorer": ["explorer খোলো", "file manager খোলো"],
        "open_terminal": ["terminal খোলো", "cmd খোলো", "command খোলো"],
        "open_calculator": ["calculator খোলো", "গণনা করো", "যোগ করো"],
        "close": ["বন্ধ করো", "exit করো", "চলে যাও"]
    },
    "files": {
        "create_folder": ["folder তৈরি করো", "ফোল্ডার বানাও", "নতুন folder"],
        "open_downloads": ["downloads খোলো", "ডাউনলোড খোলো"],
        "open_documents": ["documents খোলো", "ডকুমেন্টস খোলো"],
        "open_desktop": ["desktop খোলো", "ডেস্কটপ খোলো"],
        "find_file": ["ফাইল খুঁজো", "search করো file", "কোথাও আছে"]
    },
    "search": {
        "web_search": ["খুঁজে দেখো", "search করো", "google করো", "বলো তো"],
        "youtube_search": ["youtube এ খুঁজো", "video খোলো"],
        "wiki_search": ["wiki তে খুঁজো", "wikipedia এ দেখো"]
    }
}


def is_bengali_text(text: str) -> bool:
    bengali_chars = sum(1 for c in text if '\u0980' <= c <= '\u09FF')
    return bengali_chars > len(text) * 0.3


def extract_query(text: str, prefixes: list) -> str:
    for prefix in prefixes:
        if prefix.lower() in text.lower():
            query = text.lower().replace(prefix.lower(), "").strip()
            return query
    return text.strip()
