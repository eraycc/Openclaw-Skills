---
name: z-image-turbo-generator
description: generate images with tongyi-mai/z-image-turbo through hugging face inference providers using a user-supplied hugging face api key. use when the user wants chatgpt to create an image from a prompt with this fixed model, especially when they mention z-image-turbo, hugging face api key, hf token, negative prompt, seed, image size, or want image-only output. ask for the hugging face api key only if it is missing from the current conversation, then run the bundled script and return only the generated image unless the user explicitly asks for settings or debugging details.
metadata:
  {
    "openclaw":
      { "emoji": "🎨", "requires": { "env": ["HF_TOKEN"] }, "primaryEnv": "HF_TOKEN" },
  }
---

# Z Image Turbo Generator

Generate a single image with `Tongyi-MAI/Z-Image-Turbo` through Hugging Face Inference Providers.

### Important
Always save the generated image to `/root/.openclaw/workspace/` (not `/tmp`) to ensure it can be sent via the Telegram channel. Use a unique filename or overwrite a fixed one as needed.

## Workflow

1. Confirm the user wants image generation with this fixed model.
2. Check whether the user has already provided a Hugging Face API key in the current conversation.
   - If the key is missing, ask for it.
   - Never echo the full key back to the user.
   - Treat the key as sensitive and do not copy it into the final response.
3. Extract the image request from the user's message.
   - Required: prompt
   - Optional: negative prompt, width, height, seed
4. Use these defaults unless the user asks otherwise:
   - `model=Tongyi-MAI/Z-Image-Turbo`
   - `provider=wavespeed`
   - `width=1024`
   - `height=1024`
   - `num_inference_steps=9`
   - `guidance_scale=0.0`
5. Run `scripts/generate_image.py`.
6. Return only the generated image file unless the user explicitly asks for the parameters or for debugging help.

## Command

Install dependencies if needed:

```bash
pip install -r scripts/requirements.txt
```

Generate the image:

```bash
HF_TOKEN='<user token>' python scripts/generate_image.py \
  --prompt 'A cinematic panda astronaut on the moon' \
  --output /root/.openclaw/workspace/zimage.png
```

Optional arguments:

```bash
--negative-prompt 'blurry, low quality'
--width 1024
--height 1024
--seed 42
--num-inference-steps 9
--guidance-scale 0.0
```

## Parameter Rules

- Keep the model fixed to `Tongyi-MAI/Z-Image-Turbo` unless the user explicitly asks to change the skill.
- For this turbo model, prefer `guidance_scale=0.0` and `num_inference_steps=9` by default.
- If the user gives only one dimension, keep the other at the default.
- If the user gives no seed, omit the seed argument.
- Pass the negative prompt only when the user supplies one.

## Failure Handling

- If the script reports a missing token, ask the user for a Hugging Face API key.
- If the request fails with an authentication or permission error, tell the user to verify that the token is a fine-grained Hugging Face token with permission to make calls to Inference Providers.
- If the request fails because of provider availability or credits, briefly explain the failure and ask the user to retry or check their Hugging Face billing and usage.
- Keep failure messages short and actionable.

## Output

Default output is image-only.

Do not add a prose summary before or after the image unless the user asks for details.
