import pytest

from playlist_logic import (
    DEFAULT_PROFILE,
    normalize_song,
    classify_song,
    build_playlists,
    search_songs,
    lucky_pick,
    prioritize_diverse_songs,
    compute_playlist_stats,
    random_choice_or_none,
)


def test_classify_song_keywords_and_energy():
    profile = dict(DEFAULT_PROFILE)

    s1 = normalize_song({"title": "A", "artist": "X", "genre": "rock", "energy": 6})
    assert classify_song(s1, profile) == "Hype"

    s2 = normalize_song({"title": "B", "artist": "Y", "genre": "lofi", "energy": 2})
    assert classify_song(s2, profile) == "Chill"

    s3 = normalize_song({"title": "C", "artist": "Z", "genre": "pop", "energy": 5})
    assert classify_song(s3, profile) == "Mixed"


def test_build_playlists_and_search():
    profile = dict(DEFAULT_PROFILE)
    songs = [
        {"title": "T1", "artist": "Alpha", "genre": "rock", "energy": 9},
        {"title": "T2", "artist": "Beta", "genre": "lofi", "energy": 1},
        {"title": "T3", "artist": "Gamma", "genre": "pop", "energy": 5},
    ]

    playlists = build_playlists(songs, profile)
    assert "Hype" in playlists and "Chill" in playlists and "Mixed" in playlists

    # search should find artist by substring (case-insensitive)
    hype = playlists["Hype"]
    res = search_songs(hype, "alpha", field="artist")
    assert len(res) == 1


def test_lucky_pick_and_random_choice_none():
    profile = dict(DEFAULT_PROFILE)
    songs = [
        {"title": "T1", "artist": "A", "genre": "rock", "energy": 9},
        {"title": "T2", "artist": "B", "genre": "lofi", "energy": 1},
    ]
    playlists = build_playlists(songs, profile)

    # any should include Mixed as well
    pick = lucky_pick(playlists, mode="any")
    assert pick is None or isinstance(pick, dict)

    history = [playlists["Hype"][0]]
    candidates = prioritize_diverse_songs(playlists["Hype"] + playlists["Chill"], history)
    assert all(song["artist"] != history[0]["artist"] for song in candidates)

    # empty list returns None
    assert random_choice_or_none([]) is None


def test_compute_playlist_stats_counts_and_avg():
    profile = dict(DEFAULT_PROFILE)
    songs = [
        {"title": "T1", "artist": "A", "genre": "rock", "energy": 9},
        {"title": "T2", "artist": "A", "genre": "rock", "energy": 7},
        {"title": "T3", "artist": "B", "genre": "lofi", "energy": 2},
    ]
    playlists = build_playlists(songs, profile)
    stats = compute_playlist_stats(playlists)

    assert stats["total_songs"] == 3
    assert stats["hype_count"] >= 1
    assert stats["chill_count"] >= 1
    assert 0.0 <= stats["hype_ratio"] <= 1.0
    assert stats["avg_energy"] > 0
