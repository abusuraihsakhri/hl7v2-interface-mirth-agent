/**
 * Local, dependency-free HL7 v2 ER7 structural preflight.
 * Not a full HL7 conformance profile validator or a PHI de-identifier.
 */
export const MAX_MESSAGE_LENGTH = 1024 * 1024;

export const DEMO_MESSAGE = [
  "MSH|^~\\&|SYNTHETIC-LIS|DEMO-LAB|SYNTHETIC-EHR|DEMO-HOSP|202610131230||ORU^R01|DEMO001|P|2.5",
  "PID|1||TEST0001^^^DEMO^MR||EXAMPLE^PATIENT",
  "OBR|1||DEMO-ORDER|CBC^Complete blood count^L",
  "OBX|1|NM|718-7^Hemoglobin^LN||13.5|g/dL|12-16|N|||F",
].join("\r");

const REQUIRED_MSH = [
  [9, "message type"],
  [10, "message control ID"],
  [11, "processing ID"],
  [12, "version ID"],
];

function field(fields, segment, index) {
  // MSH-1 is the delimiter; unlike other segments, MSH-2 is array index 1.
  if (segment === "MSH") return index === 1 ? fields.__separator : (fields[index - 1] || "");
  return fields[index] || "";
}

export function inspectHL7(source) {
  if (typeof source !== "string") throw new TypeError("Message must be text.");
  if (source.length > MAX_MESSAGE_LENGTH) throw new RangeError("Message exceeds the 1 MiB limit.");
  const findings = [];
  const add = (severity, segment, message) => findings.push({ severity, segment, message });

  // Strip only the optional outer MLLP framing. Do not silently accept concatenated messages.
  let message = source.trim();
  if (message.startsWith("\u000b")) message = message.slice(1);
  message = message.replace(/\u001c(?:\r\n|\r|\n)?$/, "");
  const lines = message.split(/\r\n|\r|\n/).map(s => s.trim()).filter(Boolean);
  if (!lines.length) {
    add("error", "Message", "No HL7 segments found.");
    return buildResult([], findings, "", "");
  }

  const counts = Object.create(null);
  let previousHasObr = false;
  let messageType = "";
  let version = "";
  let separator = "|";

  if (!lines[0].startsWith("MSH")) {
    add("error", "MSH", "The first segment must be MSH.");
  } else {
    separator = lines[0].charAt(3);
    if (!separator || /[A-Za-z0-9\s\\]/.test(separator)) {
      add("error", "MSH-1", "Invalid field separator; expected a single punctuation character.");
      separator = "|";
    }
  }

  for (let i = 0; i < lines.length; i++) {
    const raw = lines[i];
    const id = raw.slice(0, 3);
    if (!/^[A-Z][A-Z0-9]{2}$/.test(id) || raw.charAt(3) !== separator) {
      add("error", "Segment " + (i + 1), "Segment must start with a three-character ID followed by the MSH field separator.");
      continue;
    }
    counts[id] = (counts[id] || 0) + 1;
    const parts = raw.split(separator);
    parts.__separator = separator;

    if (id === "MSH") {
      if (i !== 0 || counts.MSH !== 1) {
        add("error", "MSH", "Multiple MSH segments or a second HL7 message were found; inspect one message at a time.");
      }
      if (!field(parts, "MSH", 2)) add("error", "MSH-2", "Missing encoding characters.");
      for (const [number, name] of REQUIRED_MSH) {
        if (!field(parts, "MSH", number)) add("error", "MSH-" + number, "Missing " + name + ".");
      }
      messageType = field(parts, "MSH", 9).slice(0, 80);
      version = field(parts, "MSH", 12).slice(0, 40);
    }
    if (id === "PID" && !field(parts, id, 3)) {
      add("warning", "PID-3", "Patient identifier field is empty (profile requirements may vary).");
    }
    if (id === "OBR") {
      previousHasObr = true;
      if (!field(parts, id, 4)) add("warning", "OBR-4", "Universal service identifier is empty.");
    }
    if (id === "OBX") {
      if (!previousHasObr) add("warning", "OBX", "OBX appears before any OBR in this message.");
      if (!field(parts, id, 2)) add("warning", "OBX-2", "Value type is empty.");
      if (!field(parts, id, 3)) add("warning", "OBX-3", "Observation identifier is empty.");
      if (!field(parts, id, 11)) add("warning", "OBX-11", "Observation result status is empty.");
    }
  }

  const typeCode = messageType.split("^")[0];
  if (!counts.MSH) add("error", "MSH", "Missing valid MSH segment.");
  if (!counts.PID && ["ADT", "ORU", "ORM"].includes(typeCode)) {
    add("warning", "PID", "Expected PID segment for this message type.");
  }
  if (typeCode === "ORU" && !counts.OBR) add("warning", "OBR", "ORU message contains no OBR segment.");
  if (typeCode === "ORU" && !counts.OBX) add("warning", "OBX", "ORU message contains no OBX results.");

  return buildResult(counts, findings, messageType, version);
}

function buildResult(counts, findings, messageType, version) {
  const errors = findings.filter(f => f.severity === "error").length;
  const warnings = findings.filter(f => f.severity === "warning").length;
  return {
    status: errors ? "error" : warnings ? "warning" : "pass",
    messageType,
    version,
    segmentCount: Object.values(counts).reduce((sum, n) => sum + n, 0),
    segmentCounts: { ...counts },
    errors,
    warnings,
    findings,
  };
}
