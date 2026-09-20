# Ovi API — Python client

[![Python 3.8+](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/) [![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE) [![Hosted on Synexa](https://img.shields.io/badge/hosted%20on-Synexa-6366f1.svg)](https://synexa.ai/explore/black-forest-labs/flux-3-video?utm_source=github&utm_medium=ugc&utm_campaign=ovi-ai-dev&utm_content=readme-badge&utm_term=tier-a)

Ovi is Character.AI's open model for generating video and audio together in one pass: speech, sound effects and picture come out of the same denoising process, already in sync. This package is a Python client that gives you an Ovi API for the same job, a short clip with synchronised sound from a prompt or a starting image, with `pip install ovi-api` and no GPU of your own.

You get a blocking `run()` that returns when the clip is ready, a submit-and-poll path for queued jobs, webhook delivery for servers that must not block, and a single runtime dependency (`requests`). It is meant for content pipelines, backend services and notebooks that need talking, sounding video as a function call.

> **Try it now:** [https://synexa.ai/explore/black-forest-labs/flux-3-video](https://synexa.ai/explore/black-forest-labs/flux-3-video?utm_source=github&utm_medium=ugc&utm_campaign=ovi-ai-dev&utm_content=readme-top&utm_term=tier-a) — the hosted model behind this client. New accounts get a free trial credit.

## Contents

- [Why this client](#why-this-client)
- [Installation](#installation)
- [Quickstart](#quickstart)
- [Hosted models](#hosted-models)
- [Parameters](#parameters)
- [Advanced usage](#advanced-usage)
- [About Ovi](#about-ovi)
- [Use cases](#use-cases)
- [FAQ](#faq)
- [License](#license)

## Why this client

- **Two backbones need a big card.** Ovi runs an 11B twin-DiT (a video branch and an audio branch fused by cross-attention); the reference implementation is documented for 32 GB GPUs, with CPU offload and FP8 paths to reach 24 GB. The hosted endpoints run on hardware sized for the model.
- **No pipeline assembly.** Self-hosting means the Wan 2.2 VAE and text encoder, the audio VAE, the fusion weights and the right CUDA build. The hosted endpoint takes a prompt and an image and returns an MP4 with sound.
- **No cold start.** Loading both branches and their encoders takes minutes before the first frame; hosted runs start on a warm model.
- **Per-run pricing.** `black-forest-labs/flux-3-video` is $0.17 per run and `bytedance/seedance-2.5` is $0.473 for up to 30 seconds. Nothing sits idle between jobs.

## Installation

```bash
pip install git+https://github.com/ovi-ai-dev/ovi-api.git
```

Then set your API key (create one at [synexa.ai](https://synexa.ai?utm_source=github&utm_medium=ugc&utm_campaign=ovi-ai-dev&utm_content=readme-apikey&utm_term=tier-a)):

```bash
export SYNEXA_API_KEY="sk-..."
```

## Quickstart

```python
import ovi_api

output = ovi_api.run({
    "prompt": "A cinematic shot of a lighthouse at dawn, soft fog, warm light",
    "image_url": "https://example.com/input.png"
})
print(output)   # URL(s) of the generated result
```

Or with an explicit client:

```python
from ovi_api import Client

client = Client(api_key="sk-...")
output = client.run({"prompt": "A cinematic shot of a lighthouse at dawn, soft fog, warm light", "image_url": "https://example.com/input.png"})
```

## Hosted models

| Model | Category | What it does | Price / run |
|---|---|---|---|
| [`black-forest-labs/flux-3-video`](https://synexa.ai/explore/black-forest-labs/flux-3-video?utm_source=github&utm_medium=ugc&utm_campaign=ovi-ai-dev&utm_content=readme-models&utm_term=tier-a) | image-to-video | FLUX 3 animates a single still image into video, with audio, following a prompt that describes how the scene unfolds. | $0.17 |
| [`bytedance/seedance-2.5`](https://synexa.ai/explore/bytedance/seedance-2.5?utm_source=github&utm_medium=ugc&utm_campaign=ovi-ai-dev&utm_content=readme-models&utm_term=tier-a) | text-to-video | Seedance 2.5 generates a single-shot video of up to 30 seconds from a text prompt, with synchronised audio. | $0.473 |

The default model is **`black-forest-labs/flux-3-video`**; pass `model="owner/name"` to `run()` to use another one from the table.

## Parameters

### `black-forest-labs/flux-3-video`

| Field | Type | Required | Default | Range | Description |
|---|---|---|---|---|---|
| `prompt` | string | yes | `The camera drifts slowly to the left as …` | — | The text prompt describing the video you want to generate. |
| `aspect_ratio` | string | no | `auto` | auto, 21:9, 2:1, 16:9, 4:3, 1:1, 3:4, 9:16 | Aspect ratio of the generated video. `auto` lets the model choose. |
| `resolution` | string | no | `720p` | 720p, 1080p | Resolution of the generated video. |
| `duration` | string | no | `auto` | auto, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, … | Duration of the generated video in seconds. `auto` lets the model choose. |
| `generate_audio` | boolean | no | `True` | — | Whether to generate audio for the video. |
| `image_url` | file | yes | — | — | First frame of the video (.jpg/.png/.webp) |

### `bytedance/seedance-2.5`

| Field | Type | Required | Default | Range | Description |
|---|---|---|---|---|---|
| `prompt` | string | yes | `A lone fisherman rows out at dawn across…` | — | The text prompt used to generate the video |
| `resolution` | string | no | `720p` | 480p, 720p, 1080p | Video resolution - 480p for faster generation, 720p for balance, 1080p for high quality. |
| `duration` | string | no | `auto` | auto, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 1… | Duration of the video in seconds. Supports 4 to 30 seconds, or auto to let the model decide based on the prompt. |
| `aspect_ratio` | string | no | `auto` | auto, 21:9, 16:9, 4:3, 1:1, 3:4, 9:16 | The aspect ratio of the generated video. Use 16:9 for landscape, 9:16 for portrait/vertical, 1:1 for square, 21:9 for ultrawide cinematic, or auto to let the model decide. |
| `generate_audio` | boolean | no | `True` | — | Whether to generate synchronized audio for the video, including sound effects, ambient sounds, and lip-synced speech. The cost of video generation is the same regardless of whether audio is generated or not. |
| `bitrate_mode` | string | no | `standard` | standard, high | Output bitrate mode. 'high' requests a higher-quality, larger-file encode from the model; 'standard' uses the default bitrate. |

## Advanced usage

**Submit without blocking, then poll:**

```python
prediction = client.run(input, wait=False)      # returns immediately
prediction = client.wait(prediction, timeout=300)
print(prediction["output"])
```

**Webhook on completion:**

```python
client.run(input, wait=False, webhook="https://your-app.example/hooks/synexa")
```

**Errors:**

```python
from ovi_api import ModelError, PredictionTimeout

try:
    output = client.run(input)
except ModelError as e:
    print("failed:", e, e.prediction and e.prediction.get("id"))
except PredictionTimeout:
    print("still running — poll later")
```

Status values you will see on a prediction: `starting` → `processing` → `succeeded` | `failed`.

## About Ovi

Ovi was released by Character.AI in October 2025 with the paper *Ovi: Twin Backbone Cross-Modal Fusion for Audio-Video Generation*. Its architecture is two diffusion transformers of identical shape: a video branch initialised from the Wan 2.2 5B text-and-image-to-video model and an audio branch of the same design trained from scratch on audio, joined at every block by bidirectional cross-attention with scaled rotary embeddings so timing aligns across modalities. The two branches denoise together, which is why the speech and the lip motion, or the impact and the sound of it, land on the same frame.

The public checkpoint generates 5 second clips at 24 fps in roughly a 720 by 720 pixel area, at 16:9, 9:16 or 1:1, from a text prompt or a text prompt plus a first-frame image. Spoken lines are marked in the prompt with `<S>` and `<E>` tags and ambient or effect audio is described inside `<AUDCAP>` and `<ENDAUDCAP>`, so one prompt carries the script, the scene and the soundscape. The model was trained with an audio-first pretraining stage followed by joint audio-video training on paired data.

Limits are those of a first-generation joint model: five seconds is the hard length, resolution is modest, multi-speaker scenes and long dialogue lines are unreliable, and non-English speech is weaker than English. The weights are open and the repository ships Gradio and CLI scripts rather than a serving stack.

The hosted endpoint used by this client is `black-forest-labs/flux-3-video`, which provides the same capability (a still image plus a prompt produces a video with generated audio); the original Ovi weights are available at https://github.com/character-ai/Ovi if you want to self-host. For text-only prompts and longer clips of up to 30 seconds with lip-synced speech, the client also exposes `bytedance/seedance-2.5`.

**Official project:** https://github.com/character-ai/Ovi

## Use cases

- **Talking product clips** — call `run()` with a packshot as `image_url`, a prompt containing the spoken line and `generate_audio=True` to get a short video with voice and ambience.
- **Sound-designed b-roll** — describe the scene and its sounds in the prompt and let the endpoint produce footsteps, wind or engine noise in sync with the picture.
- **Vertical social videos** — set `aspect_ratio="9:16"` and `resolution="720p"` for reels and shorts from a single key frame.
- **Longer narrated shots** — switch to `bytedance/seedance-2.5` with `duration=20` for a continuous 20 second clip with lip-synced speech.
- **Batch character intros** — submit one job per character image without blocking and collect the videos through a webhook.
- **Silent variants for editing** — set `generate_audio=False` when you will score the clip yourself; pricing is the same either way on Seedance.

## FAQ

**Is there an Ovi API?**

Character.AI publishes Ovi as open weights with Gradio and CLI scripts, not as a hosted API. This package wraps Synexa endpoints that provide the same joint video and audio generation over HTTPS, so you do not need to run the 11B model.

**How much does the Ovi API cost?**

The default endpoint, `black-forest-labs/flux-3-video`, is $0.17 per run. The `bytedance/seedance-2.5` endpoint is $0.473 per run for clips of 4 to 30 seconds, with or without audio. Billing is per completed run.

**Can I run Ovi without a GPU?**

No; the reference implementation needs a 24 to 32 GB GPU even with offloading. With this client the generation happens on the hosted side, so any machine that can make an HTTPS request is enough.

**Does this client work with the original character-ai/Ovi repo or ComfyUI?**

No. It does not load local Ovi checkpoints, does not use the `<S>`/`<AUDCAP>` tag syntax, and does not talk to the ComfyUI Ovi nodes. It is an HTTP client for the hosted endpoints only.

**What input formats does it accept?**

For `black-forest-labs/flux-3-video`, `prompt` and `image_url` (.jpg, .png or .webp) are required, with optional `aspect_ratio`, `resolution`, `duration` and `generate_audio`. For `bytedance/seedance-2.5` only `prompt` is required, with optional `resolution` (480p to 1080p), `duration` (4 to 30 seconds), `aspect_ratio`, `generate_audio` and `bitrate_mode`.

**Is this the official Ovi SDK?**

No. This is an independent client and is not affiliated with Character.AI. The official project is at https://github.com/character-ai/Ovi.

## Related

- [Ovi (official repository)](https://github.com/character-ai/Ovi)
- [Synexa Python client](https://github.com/synexa-ai/synexa-python)
- [black-forest-labs/flux-3-video on Synexa](https://synexa.ai/explore/black-forest-labs/flux-3-video)
- [bytedance/seedance-2.5 on Synexa](https://synexa.ai/explore/bytedance/seedance-2.5)

## License

MIT. This is an independent, community-maintained client and is not affiliated with or endorsed by the authors of Ovi. Model weights and trademarks belong to their respective owners.
