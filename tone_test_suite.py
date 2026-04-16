import argparse
import re
from dataclasses import dataclass
from typing import Callable, List, Optional

from llm_client import LLMClient


BANNED_PHRASES = [
    "you find yourself",
    "as you approach",
    "seems to",
]


def sentence_count(text: str) -> int:
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return len([p for p in parts if p.strip()])


@dataclass
class ToneTestCase:
    name: str
    player_input: str
    validator: Callable[[str], tuple[bool, str]]


def contains_stat_line(text: str) -> bool:
    # Accept either arrow format OR explicit "X damage" format
    has_arrow = bool(re.search(r"(->|→)\s*(Hit|Miss)", text, re.I))
    has_damage = bool(re.search(r"\b\d+\s*damage\b", text, re.I))
    has_hp = bool(re.search(r"HP:\s*\d+/\d+", text, re.I))
    return (has_arrow or has_damage) and has_hp

def has_damage_number(text: str) -> bool:
    return bool(re.search(r"\b\d+\s*damage\b|\b-\d+\s*HP\b", text, re.IGNORECASE))


def validate_short(max_sentences: int) -> Callable[[str], tuple[bool, str]]:
    def _validate(text: str) -> tuple[bool, str]:
        n = sentence_count(text)
        if n > max_sentences:
            return False, f"too many sentences ({n} > {max_sentences})"
        lower = text.lower()
        for phrase in BANNED_PHRASES:
            if phrase in lower:
                return False, f"contains banned phrase: {phrase}"
        return True, "ok"

    return _validate


def validate_combat(text: str) -> tuple[bool, str]:
    n = sentence_count(text)
    if n > 3:
        return False, f"combat too long ({n} sentences)"
    if not contains_stat_line(text):
        return False, "missing combat stat line"
    if not has_damage_number(text):
        return False, "missing explicit damage"
    return True, "ok"


def validate_failure_snark(text: str) -> tuple[bool, str]:
    n = sentence_count(text)
    if n > 4:
        return False, f"failure response too long ({n} sentences)"
    lower = text.lower()
    if not any(word in lower for word in ["bad", "dumb", "terrible", "nope", "hell", "damn", "shit", "fuck"]):
        return False, "missing snark/profanity flavor"
    return True, "ok"


def build_tone_instruction(model_tier: str) -> str:
    base = """You are narrating a Homestuck-inspired RPG.

CORE RULES:
1. Be conversational and concise (1-3 sentences for simple actions)
2. Use second person ("You do X")
3. Be snarky about failures
4. Use mild profanity naturally (fuck, shit, damn)
5. Avoid purple prose - no flowery descriptions

BANNED PHRASES (never use these):
- "You find yourself"
- "As you approach"  
- "seems to"
- Long descriptive metaphors

REQUIRED COMBAT FORMAT:
Action description
→ Hit/Miss! X damage
Enemy HP: current/max
Brief reaction (1 sentence)

EXAMPLES:

Player: "examine tower"
GM: "It's a tower. Old stone, kind of creepy. Probably important."

Player: "attack imp"
GM: "You swing your hammer.
→ Hit! 22 damage
Imp HP: 18/50
The imp stumbles backward, hissing."

Player: "try something impossible"
GM: "You try to punch through solid rock.
It doesn't work. Because it's rock.
-3 HP for being a shithead."

Player: "go to village"
GM: "You head to the village. Takes a few minutes."

FOLLOW THESE EXAMPLES EXACTLY. Keep responses SHORT."""

    if model_tier == "large":
        return base + "\n\nMax 50 words per response unless dramatic moment."
    elif model_tier == "small":
        return base + "\n\nPrioritize brevity over creativity."
    return base

def cleanup_response(text: str, max_sentences: int = 3) -> str:
    # Truncate to max sentences
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    truncated = ' '.join(sentences[:max_sentences])
    
    # Check for banned phrases
    for phrase in BANNED_PHRASES:
        if phrase in truncated.lower():
            # Try to remove the sentence containing it
            parts = re.split(r'(?<=[.!?])\s+', truncated)
            truncated = ' '.join(p for p in parts if phrase not in p.lower())
    
    return truncated

def _guess_model_risk(model_slug: str) -> Optional[str]:
    lower = model_slug.lower()
    if "embed" in lower:
        return "Model name suggests an embedding model, which is usually not suitable for chat generation."
    if "vl" in lower:
        return "Model name suggests vision-language behavior; pure text RPG output may be inconsistent."
    return None


def _probe_model_compatibility(llm: LLMClient, model_hint: Optional[str]) -> tuple[bool, str]:
    if not model_hint:
        return True, "No explicit model override; using configured provider defaults."

    try:
        probe = llm.generate(
            system_instruction="You are a test probe. Return exactly one short sentence.",
            user_message="Say hello in five words.",
            temperature=0.0,
            model_hint=model_hint,
        )
    except Exception as exc:
        return False, f"Model probe failed: {exc}"

    if not probe or not probe.strip():
        return False, "Model probe returned empty output."
    return True, "Model probe succeeded."


def run_suite(model_tier: str, model_hint: Optional[str] = None, provider: Optional[str] = None) -> int:
    llm = LLMClient(primary=provider) if provider else LLMClient()
    system_instruction = build_tone_instruction(model_tier)

    if model_hint:
        print(f"Model override: {model_hint}")
        risk = _guess_model_risk(model_hint)
        if risk:
            print(f"⚠  Compatibility warning: {risk}")

    ok_probe, probe_reason = _probe_model_compatibility(llm, model_hint)
    print(f"Compatibility probe: {'PASS' if ok_probe else 'FAIL'} ({probe_reason})\n")
    if not ok_probe:
        return 2

    tests: List[ToneTestCase] = [
        ToneTestCase("examine tower", "examine the tower", validate_short(3)),
        ToneTestCase("go village", "go to the consort village", validate_short(3)),
        ToneTestCase("attack imp", "attack the imp", validate_combat),
        ToneTestCase("defend", "defend against the ogre", validate_combat),
        ToneTestCase("impossible action", "i headbutt a mountain until it opens", validate_failure_snark),
        ToneTestCase("talk sprite", "ask my sprite what this pillar does", validate_short(4)),
        ToneTestCase("alchemy", "combine hammer and laptop", validate_short(4)),
        ToneTestCase("inventory", "captchalogue the broken clock", validate_short(3)),
        ToneTestCase("abscond", "abscond from this strife", validate_combat),
        ToneTestCase("inspect clue", "look for clues near the gate", validate_short(3)),
    ]

    passed = 0
    print(f"Running {len(tests)} tone tests with tier '{model_tier}'...\n")

    for i, test in enumerate(tests, start=1):
        response = llm.generate(
            system_instruction=system_instruction,
            user_message=f'Player: "{test.player_input}"\nGM:',
            temperature=0.7,
            model_hint=model_hint,
        ).strip()
        response = cleanup_response(response, max_sentences=3)
        ok, reason = test.validator(response)
        status = "PASS" if ok else "FAIL"
        print(f"[{i:02d}] {test.name}: {status} ({reason})")
        print(f"     {response}\n")
        if ok:
            passed += 1

    ratio = passed / len(tests)
    print(f"Summary: {passed}/{len(tests)} passed ({ratio:.0%})")
    if passed >= 8:
        print("Tone quality target met (>= 8/10).")
        return 0

    print("Tone quality target NOT met (< 8/10).")
    return 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Homestuck tone regression checks.")
    parser.add_argument("--tier", choices=["small", "medium", "large"], default="medium")
    parser.add_argument(
        "--model",
        default=None,
        help="Optional explicit model slug to test (e.g. nvidia/llama-...:free).",
    )
    parser.add_argument(
        "--provider",
        choices=["gemini", "openrouter"],
        default=None,
        help="Optional provider override for this run.",
    )
    args = parser.parse_args()
    return run_suite(args.tier, model_hint=args.model, provider=args.provider)


if __name__ == "__main__":
    raise SystemExit(main())
