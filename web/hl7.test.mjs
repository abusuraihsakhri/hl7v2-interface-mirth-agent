import test from "node:test";
import assert from "node:assert/strict";
import { DEMO_MESSAGE, inspectHL7, MAX_MESSAGE_LENGTH } from "./hl7.mjs";

test("synthetic ORU message passes implemented checks", () => {
  const result = inspectHL7(DEMO_MESSAGE);
  assert.equal(result.status, "pass");
  assert.equal(result.segmentCount, 4);
  assert.equal(result.messageType, "ORU^R01");
  assert.equal(result.version, "2.5");
  assert.deepEqual(result.segmentCounts, { MSH: 1, PID: 1, OBR: 1, OBX: 1 });
});

test("supports MLLP and LF line endings", () => {
  const result = inspectHL7("\u000b" + DEMO_MESSAGE.replaceAll("\r", "\n") + "\u001c\r");
  assert.equal(result.status, "pass");
});

test("empty input is not a successful validation", () => {
  const result = inspectHL7(" ");
  assert.equal(result.status, "error");
  assert.ok(result.errors > 0);
});

test("requires MSH first and reports missing MSH", () => {
  const result = inspectHL7("PID|1||TEST");
  assert.equal(result.status, "error");
  assert.ok(result.findings.some(f => f.segment === "MSH"));
});

test("detects missing MSH-10 and MSH-12", () => {
  const result = inspectHL7("MSH|^~\\&|S|F|R|T|20260101||ORU^R01|||");
  assert.equal(result.status, "error");
  assert.ok(result.findings.some(f => f.segment === "MSH-10"));
  assert.ok(result.findings.some(f => f.segment === "MSH-12"));
});

test("detects unframed concatenated messages", () => {
  const result = inspectHL7(DEMO_MESSAGE + "\r" + DEMO_MESSAGE);
  assert.equal(result.status, "error");
  assert.ok(result.findings.some(f => f.message.includes("Multiple MSH")));
});

test("OBX without OBR produces a warning", () => {
  const result = inspectHL7(DEMO_MESSAGE.split("\r").filter(s => !s.startsWith("OBR")).join("\r"));
  assert.equal(result.status, "warning");
  assert.ok(result.findings.some(f => f.segment === "OBX"));
});

test("does not require OBR or OBX for ADT", () => {
  const adt = DEMO_MESSAGE.split("\r").slice(0, 2).join("\r").replace("ORU^R01", "ADT^A01");
  assert.equal(inspectHL7(adt).status, "pass");
});

test("rejects oversize text and non-string input", () => {
  assert.throws(() => inspectHL7("x".repeat(MAX_MESSAGE_LENGTH + 1)), RangeError);
  assert.throws(() => inspectHL7(null), TypeError);
});

test("unknown Z segments are not rejected as malformed", () => {
  const result = inspectHL7(DEMO_MESSAGE + "\rZBX|custom|value");
  assert.equal(result.status, "pass");
});
