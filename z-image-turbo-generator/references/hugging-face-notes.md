# Hugging Face Notes

Use this reference only when debugging or when the user asks how the skill works.

## Current integration assumptions

- Authentication uses a user-supplied Hugging Face API key.
- The API key should be a fine-grained token with permission to make calls to Inference Providers.
- Provider is `fal-ai`.
- Model is `Tongyi-MAI/Z-Image-Turbo`.
- The bundled script uses `huggingface_hub.InferenceClient(...).text_to_image(...)`.

## Defaults for this skill

- Width: 1024
- Height: 1024
- Inference steps: 9
- Guidance scale: 0.0

## Common fixes

### Authentication or permission failure

Tell the user to verify:

1. The token is valid.
2. The token has permission to make calls to Inference Providers.
3. Their Hugging Face account has available usage or billing.

### Missing dependency

Run:

```bash
pip install -r scripts/requirements.txt
```
