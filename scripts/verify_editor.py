import os
import sys

sys.path.append(os.getcwd())

from backend.integrations.jianying_api.draft_editor import DraftEditor


def test_draft_editor():
    """
    Verify DraftEditor logic with mock data
    """
    print("Testing DraftEditor...")

    # Mock draft content
    mock_content = {
        "tracks": [
            {
                "id": "video_track_1",
                "type": "video",
                "segments": [
                    {
                        "id": "segment_1",
                        "material_id": "mat_1",
                        "target_timerange": {"start": 0, "duration": 5000000},
                        "source_timerange": {"start": 0, "duration": 5000000}
                    }
                ]
            }
        ],
        "materials": {
            "videos": [{"id": "mat_1", "path": "/path/to/video.mp4"}],
            "audios": []
        }
    }

    editor = DraftEditor(mock_content)

    # Test Adding Music
    print("\n[1] Testing Add Music...")
    editor.add_audio("/path/to/music.mp3", start_time=0, duration=5000000)

    # check if audio track created
    has_audio = False
    for track in editor.content["tracks"]:
        if track["type"] == "audio":
            has_audio = True
            print("  -> Audio track created.")
            # check segment
            if len(track["segments"]) > 0:
                print(f"  -> Segment created with material_id: {track['segments'][0]['material_id']}")

    if not has_audio:
        print("  -> FAILED: No audio track found.")

    # Test Deduplication
    print("\n[2] Testing Deduplication...")
    editor.deduplicate({"speed": True, "mirror": True, "crop": True})

    # check video segment properties
    video_segment = editor.content["tracks"][0]["segments"][0]

    print(f"  -> Speed factor: {video_segment.get('speed')}")
    if video_segment.get("speed") != 1.0:
        print("  -> Speed changed successfully.")
    else:
        print("  -> WARNING: Speed might not have changed (random factor).")

    clip = video_segment.get("clip", {})
    print(f"  -> Flip Horizontal: {clip.get('flip', {}).get('horizontal')}")
    print(f"  -> Scale X: {clip.get('scale', {}).get('x')}")

    print("\nDraftEditor Logic Verification Completed.")


if __name__ == "__main__":
    test_draft_editor()
