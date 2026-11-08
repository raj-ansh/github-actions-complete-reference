import { readFile } from "node:fs/promises";
import * as core from "@actions/core";
import { findEntry } from "./changelog.js";

async function run() {
  const version = core.getInput("version", { required: true });
  const file = core.getInput("file") || "CHANGELOG.md";
  const text = await readFile(file, "utf8");
  const heading = findEntry(text, version);
  if (heading === null) {
    core.setFailed(`${file} has no entry for version ${version}`);
    return;
  }
  core.info(`Found: ${heading}`);
  core.setOutput("heading", heading);
}

run().catch((error) => core.setFailed(error.message));
