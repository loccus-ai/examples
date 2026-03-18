# Streaming Audio Authenticity Verification Example

This example performs a real-time streaming audio authenticity verification over WebSocket. It supports two targets:

- **local**: Connect to a [self-hosted](https://developer.hiya.com/docs/guides/audio-intel/self-hosted/introduction#how-it-works) instance running locally.
- **upstream**: Connect to the Hiya Audio Intelligence API.

The script streams audio in chunks, prints per-chunk results as they arrive, and displays a final verification result with a latency summary.

# Prerequisites

1. You need [Node.js](https://nodejs.org/) (v18 or later) installed.
2. Install the dependencies:

   ```sh
   npm install
   ```

3. For the **upstream** target, you need a Hiya account. [You can register here](https://developer.hiya.com/console/audiointel/signup).

# Usage

## Local target (self-hosted)

```sh
node verify.mjs --target local --audio path/to/audio.wav
```

By default this connects to `ws://localhost:3001`. You can override the host and port:

```sh
node verify.mjs --target local --audio path/to/audio.wav --host 192.168.1.10 --port 8080
```

## Upstream target (Hiya API)

Set your credentials via environment variables:

```sh
export HIYA_API_TOKEN="<YOUR_TOKEN>"
export HIYA_REGION="<REGION>"
export HIYA_OWNER="<OWNER>"
export HIYA_SPACE="<SPACE>"
```

Then run:

```sh
node verify.mjs --target upstream --audio path/to/audio.wav
```

Alternatively, pass credentials directly as CLI flags:

```sh
node verify.mjs --target upstream --audio path/to/audio.wav \
  --token <YOUR_TOKEN> --region <REGION> --owner <OWNER> --space <SPACE>
```

## Additional options

| Flag | Description | Default |
|---|---|---|
| `--model <model>` | Model name to use for verification | `phone` |
| `--synthesis-sources` | Enable synthesis source scores | `false` |
| `--audio-format <format>` | Audio format hint (e.g., `wav`, `flac`) | auto-detected |

# Output

The script prints:

1. **Chunk results** as they stream in, showing time ranges, labels, and scores.
2. **Verification result** with overall model, duration, voice duration, chunk count, and scores.
3. **Latency summary** including connection time, upload time, time to first chunk, chunk intervals, and total E2E time.

The script exits with code `0` (PASS) if a verification response is received, or `1` (FAIL) otherwise.
