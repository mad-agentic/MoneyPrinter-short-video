from src.subtitles.script_srt import build_script_srt, split_script_captions


def test_split_preserves_vietnamese_words_and_diacritics():
    chunks = split_script_captions(
        "Trong crypto, một cú click sai có thể mất toàn bộ tiền. Đừng nhập seed phrase vào link lạ.",
        max_chars=52,
    )
    assert chunks == [
        "Trong crypto, một cú click sai có thể mất toàn bộ tiền.",
        "Đừng nhập seed phrase vào link lạ.",
    ]


def test_split_long_sentence_by_words():
    text = "Một câu rất dài không có dấu chấm cần được chia thành nhiều dòng ngắn để subtitle dễ đọc trên video dọc"
    chunks = split_script_captions(text, max_chars=42)
    assert all(len(chunk) <= 42 for chunk in chunks)
    assert " ".join(chunks) == text


def test_build_script_srt_uses_full_audio_duration():
    srt = build_script_srt("Câu một ngắn. Câu hai dài hơn một chút.", duration_seconds=6.0, max_chars=52)
    assert "1\n00:00:00,000 -->" in srt
    assert "2\n" in srt
    assert "00:00:06,000" in srt
    assert "Câu một ngắn." in srt
    assert "Câu hai dài hơn một chút." in srt


def test_build_script_srt_returns_empty_for_blank_text():
    assert build_script_srt("   ", duration_seconds=10.0) == ""
