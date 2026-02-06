from aivideogen.generator.avgl_engine import convert_avgl_json_to_text

mock_json = {
    "title": "Test Group Project",
    "blocks": [
        {
            "title": "Intro Block",
            "scenes": [
                {"title": "Scene 1", "text": "Hello world", "assets": [{"id": "img1.png"}]}
            ],
            "groups": [
                {
                    "title": "My Super Group",
                    "scenes": [
                        {"title": "G-Scene 1", "text": "Inside group", "assets": [{"id": "g1.png"}]},
                        {"title": "G-Scene 2", "text": "Still inside", "assets": [{"id": "g2.png"}]}
                    ]
                }
            ]
        }
    ]
}

text_out = convert_avgl_json_to_text(mock_json)
print(text_out)

if "### GROUP: My Super Group ###" in text_out and "Inside group" in text_out:
    print("\n✅ SUCCESS: Groups are visible in text!")
else:
    print("\n❌ FAILURE: Groups missing.")
