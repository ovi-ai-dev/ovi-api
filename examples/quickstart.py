        """Minimal Ovi example: create one prediction and print the output URL(s)."""
        import ovi_api

        output = ovi_api.run({
    "prompt": "A cinematic shot of a lighthouse at dawn, soft fog, warm light",
    "image_url": "https://example.com/input.png"
})
        print(output)
