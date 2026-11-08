import assert from "node:assert/strict";
import { test } from "node:test";
import { findEntry } from "../src/changelog.js";

const changelog = `# Changelog

## [1.2.0] - 2026-11-01
- Add low-stock report

## 1.1.10
- Fix search

See version 9.9.9 for details.
`;

test("finds a bracketed version", () => {
  assert.equal(findEntry(changelog, "1.2.0"), "## [1.2.0] - 2026-11-01");
});

test("accepts a leading v", () => {
  assert.equal(findEntry(changelog, "v1.2.0"), "## [1.2.0] - 2026-11-01");
});

test("does not match a prefix of another version", () => {
  assert.equal(findEntry(changelog, "1.1.1"), null);
});

test("ignores versions outside headings", () => {
  assert.equal(findEntry(changelog, "9.9.9"), null);
});
