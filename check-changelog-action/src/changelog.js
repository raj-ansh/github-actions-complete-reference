/** Return the first Markdown heading that names a version, or null. */
export function findEntry(text, version) {
  const wanted = version.replace(/^v/, "");
  for (const line of text.split(/\r?\n/)) {
    if (!/^#{1,6}\s/.test(line)) {
      continue;
    }
    const tokens = line.match(/\d+\.\d+\.\d+[\w.-]*/g) ?? [];
    if (tokens.includes(wanted)) {
      return line.trim();
    }
  }
  return null;
}
