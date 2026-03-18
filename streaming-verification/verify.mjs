#!/usr/bin/env node

import { program } from "commander";
import { createReadStream, statSync } from "fs";
import { resolve } from "path";
import WebSocket from "ws";

program
  .requiredOption("--target <target>", "Target: local or upstream")
  .requiredOption("--audio <path>", "Path to audio file")
  .option("--model <model>", "Model name", "default")
  .option("--port <port>", "Local WS port (local target)", "3001")
  .option("--host <host>", "Local host (local target)", "localhost")
  .option("--token <token>", "Bearer token (upstream target)")
  .option("--region <region>", "Region (upstream target)")
  .option("--owner <owner>", "Owner (upstream target)")
  .option("--space <space>", "Space (upstream target)")
  .option("--synthesis-sources", "Enable synthesis sources", false)
  .option("--audio-format <format>", "Audio format hint")
  .parse();

const opts = program.opts();

if (opts.target !== "local" && opts.target !== "upstream") {
  console.error("Error: --target must be 'local' or 'upstream'");
  process.exit(1);
}

const audioPath = resolve(opts.audio);
try {
  statSync(audioPath);
} catch {
  console.error(`Error: audio file not found: ${audioPath}`);
  process.exit(1);
}

function resolveUpstreamConfig() {
  const token = opts.token || process.env.HIYA_API_TOKEN;
  const region = opts.region || process.env.HIYA_REGION;
  const owner = opts.owner || process.env.HIYA_OWNER;
  const space = opts.space || process.env.HIYA_SPACE;

  if (!token) {
    console.error(
      "Error: --token or HIYA_API_TOKEN env var required for upstream target"
    );
    process.exit(1);
  }
  if (!region) {
    console.error(
      "Error: --region or HIYA_REGION env var required for upstream target"
    );
    process.exit(1);
  }
  if (!owner || !space) {
    console.error(
      "Error: --owner and --space (or HIYA_OWNER and HIYA_SPACE env vars) required for upstream target"
    );
    process.exit(1);
  }

  return { token, region, owner, space };
}

function buildUrl() {
  if (opts.target === "local") {
    return `ws://${opts.host}:${opts.port}/v1/verify/authenticity`;
  }

  const { region, owner, space } = resolveUpstreamConfig();
  return `wss://api.hiya.com/audiointel/${region}/v1/spaces/${owner}/${space}/verify/authenticity`;
}

function buildHeaders() {
  if (opts.target === "local") return {};

  const { token } = resolveUpstreamConfig();
  return {
    Authorization: `Bearer ${token}`,
    "User-Agent": "streaming-verification-example/1.0",
  };
}

function buildInitMessage() {
  const init = {
    model: opts.model,
    config: {
      synthesisSources: opts.synthesisSources,
    },
  };
  if (opts.audioFormat) {
    init.audioFormat = opts.audioFormat;
  }
  return JSON.stringify(init);
}

const CHUNK_SIZE = 16 * 1024;

function streamAudio(ws) {
  return new Promise((resolve, reject) => {
    const stream = createReadStream(audioPath, { highWaterMark: CHUNK_SIZE });

    stream.on("data", (chunk) => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.send(chunk);
      }
    });

    stream.on("end", () => resolve());
    stream.on("error", (err) => reject(err));
  });
}

function formatScores(scores) {
  if (!scores) return "n/a";
  const parts = [];
  if (scores.synthesis != null) parts.push(`synthesis=${scores.synthesis}`);
  if (scores.replay != null) parts.push(`replay=${scores.replay}`);
  if (scores.synthesisSources) {
    const sources = Object.entries(scores.synthesisSources)
      .filter(([, v]) => v != null)
      .map(([k, v]) => `${k}=${v}`)
      .join(", ");
    if (sources) parts.push(`sources={${sources}}`);
  }
  return parts.join(", ") || "n/a";
}

function ms(hrtime) {
  return (Number(hrtime) / 1e6).toFixed(1);
}

async function run() {
  const url = buildUrl();
  const headers = buildHeaders();

  console.log(`Target:  ${opts.target}`);
  console.log(`URL:     ${url}`);
  console.log(`Audio:   ${audioPath}`);
  console.log(`Model:   ${opts.model}`);
  console.log();

  const timing = {
    start: process.hrtime.bigint(),
    connected: null,
    initSent: null,
    audioSent: null,
    closeSent: null,
    firstChunk: null,
    lastChunk: null,
    verification: null,
    closed: null,
    chunkTimestamps: [],
  };

  const ws = new WebSocket(url, { headers });

  let gotVerification = false;

  ws.on("open", async () => {
    timing.connected = process.hrtime.bigint();
    console.log(`Connected. (${ms(timing.connected - timing.start)}ms)`);

    console.log("Sending init...");
    ws.send(buildInitMessage());
    timing.initSent = process.hrtime.bigint();

    console.log("Streaming audio...");
    await streamAudio(ws);
    timing.audioSent = process.hrtime.bigint();
    console.log(`Audio sent. (${ms(timing.audioSent - timing.initSent)}ms)`);

    console.log("Sending close...");
    ws.send(JSON.stringify({ type: "close" }));
    timing.closeSent = process.hrtime.bigint();
  });

  ws.on("message", (data) => {
    const now = process.hrtime.bigint();
    const msg = JSON.parse(data.toString());

    if (msg.type === "chunk") {
      if (!timing.firstChunk) timing.firstChunk = now;
      timing.lastChunk = now;
      timing.chunkTimestamps.push(now);

      const c = msg.chunk;
      const elapsed = ms(now - timing.start);
      console.log(
        `  [chunk] ${c.startTime} -> ${c.endTime}  label=${c.label}  ${formatScores(c.scores)}  (${elapsed}ms)`
      );
    } else if (msg.type === "verification") {
      timing.verification = now;
      gotVerification = true;
      const v = msg.verification;
      console.log();
      console.log("=== Verification Result ===");
      console.log(`  Model:          ${v.model}`);
      console.log(`  Duration:       ${v.duration}`);
      console.log(`  Voice Duration: ${v.voiceDuration}`);
      console.log(`  Chunks:         ${v.chunks}`);
      console.log(`  Scores:         ${formatScores(v.scores)}`);
    } else if (msg.type === "error") {
      console.error(`  [error] ${msg.message}`);
    } else {
      console.log(`  [unknown] ${JSON.stringify(msg)}`);
    }
  });

  ws.on("error", (err) => {
    console.error(`WebSocket error: ${err.message}`);
  });

  ws.on("close", (code, reason) => {
    timing.closed = process.hrtime.bigint();
    console.log();
    console.log(`Connection closed (code=${code}, reason=${reason || ""})`);

    // latency summary
    console.log();
    console.log("=== Latency Summary ===");

    const row = (label, value) =>
      console.log(`  ${label.padEnd(28)} ${value}`);

    row("Connection time:", `${ms(timing.connected - timing.start)}ms`);
    row(
      "Audio upload time:",
      timing.audioSent
        ? `${ms(timing.audioSent - timing.initSent)}ms`
        : "n/a"
    );

    if (timing.firstChunk) {
      row(
        "Time to first chunk:",
        `${ms(timing.firstChunk - timing.start)}ms`
      );
      row(
        "  (from init sent):",
        `${ms(timing.firstChunk - timing.initSent)}ms`
      );
    }

    if (timing.chunkTimestamps.length > 1) {
      const intervals = [];
      for (let i = 1; i < timing.chunkTimestamps.length; i++) {
        intervals.push(
          Number(timing.chunkTimestamps[i] - timing.chunkTimestamps[i - 1]) /
            1e6
        );
      }
      const avg = intervals.reduce((a, b) => a + b, 0) / intervals.length;
      const min = Math.min(...intervals);
      const max = Math.max(...intervals);
      row("Chunk intervals:", `avg=${avg.toFixed(1)}ms  min=${min.toFixed(1)}ms  max=${max.toFixed(1)}ms`);
    }

    if (timing.verification && timing.lastChunk) {
      row(
        "Last chunk -> verification:",
        `${ms(timing.verification - timing.lastChunk)}ms`
      );
    }

    if (timing.verification) {
      row("Total E2E time:", `${ms(timing.verification - timing.start)}ms`);
    }

    row(
      "Total wall time:",
      `${ms(timing.closed - timing.start)}ms`
    );

    row("Chunks received:", `${timing.chunkTimestamps.length}`);

    console.log();
    if (gotVerification) {
      console.log("PASS");
      process.exit(0);
    } else {
      console.log("FAIL: no verification response received");
      process.exit(1);
    }
  });
}

run().catch((err) => {
  console.error(`Fatal: ${err.message}`);
  process.exit(1);
});
