import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from classes.Tts import TTS  # noqa: E402
from omnivoice_refs import (  # noqa: E402
    OMNIVOICE_REF_DIR,
    create_default_reference_voices,
    list_reference_voices,
    resolve_omnivoice_reference_voice,
)


def _cmd_create_defaults(_args) -> int:
    tts = TTS(voice="Jasper", language="auto")
    model = tts._get_omnivoice_model()
    registry = create_default_reference_voices(model, OMNIVOICE_REF_DIR)
    print(f"Created {len(registry['voices'])} OmniVoice reference voice(s) in {OMNIVOICE_REF_DIR}")
    for voice in registry["voices"]:
        print(f"- {voice['id']}: {voice['ref_audio']}")
    return 0


def _cmd_list(_args) -> int:
    voices = list_reference_voices()
    if not voices:
        print("No OmniVoice reference voices found. Run: uv run python scripts\\omnivoice_refs.py create-defaults")
        return 0
    for voice in voices:
        print(f"{voice.get('id')} | {voice.get('language')} | {voice.get('ref_audio')}")
    return 0


def _cmd_test(args) -> int:
    ref = resolve_omnivoice_reference_voice(args.voice_id)
    if not ref:
        print(f"Reference voice not found or missing WAV: {args.voice_id}")
        return 1

    tts = TTS(voice=args.voice_id, language=str(ref.get("language") or "auto"))
    output = str(OMNIVOICE_REF_DIR / f"test_{args.voice_id}.wav")
    tts.synthesize(args.text, output)
    print(f"Wrote test audio: {output}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Create and test OmniVoice reference voices.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    create_parser = subparsers.add_parser("create-defaults", help="Create 3 synthetic reference voices.")
    create_parser.set_defaults(func=_cmd_create_defaults)

    list_parser = subparsers.add_parser("list", help="List registered reference voices.")
    list_parser.set_defaults(func=_cmd_list)

    test_parser = subparsers.add_parser("test", help="Generate a short sample with a reference voice.")
    test_parser.add_argument("voice_id")
    test_parser.add_argument(
        "--text",
        default="Day la doan test giong doc on dinh cho OmniVoice.",
        help="Text to synthesize.",
    )
    test_parser.set_defaults(func=_cmd_test)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
