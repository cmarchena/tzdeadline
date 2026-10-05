# Requirements Document

## Introduction

`tzdeadline` is a command-line tool and MCP server that converts a user-supplied date-time string
from one IANA timezone to another, then displays the converted timestamp alongside a human-readable
countdown (or elapsed time) to that moment. All timezone handling is performed offline using the
Python 3.11+ standard-library module `zoneinfo`. The same conversion logic is also exposed as a
single MCP tool named `convert_time` so that AI assistants and other MCP clients can invoke it
programmatically.

---

## Glossary

- **CLI**: The `tzdeadline` command-line interface invoked directly by a user in a terminal.
- **Converter**: The internal component responsible for parsing date-time strings and applying
  timezone conversions using `zoneinfo`.
- **MCP_Server**: The Model Context Protocol server that exposes `tzdeadline` functionality to
  MCP-compatible clients.
- **IANA_Timezone**: A timezone identifier drawn from the IANA Time Zone Database (e.g.,
  `America/New_York`, `Europe/Berlin`, `UTC`).
- **Deadline**: The target moment in time supplied by the user, expressed as a date-time string.
- **Countdown**: The human-readable duration between the current wall-clock time and the Deadline
  (e.g., "in 3 days, 4 hours, 12 minutes" or "2 hours ago").

---

## Requirements

### Requirement 1: Timezone Conversion

**User Story:** As a developer, I want to convert a date-time from one timezone to another, so that
I can quickly determine what a deadline looks like in my local timezone.

#### Acceptance Criteria

1. WHEN the CLI is invoked with a date-time string, a source IANA_Timezone, and a target
   IANA_Timezone, THE Converter SHALL parse the date-time string and return a timezone-aware
   datetime object expressed in the target IANA_Timezone.
2. THE Converter SHALL perform all timezone conversions using only the Python 3.11+ `zoneinfo`
   standard-library module, making no network calls.
3. IF the source or target IANA_Timezone identifier is not recognised by `zoneinfo`, THEN THE CLI
   SHALL print a descriptive error message to stderr and exit with a non-zero status code.

---

### Requirement 2: Deadline Countdown Output

**User Story:** As a developer, I want to see how long until (or since) a deadline, so that I can
gauge urgency at a glance.

#### Acceptance Criteria

1. WHEN a successful timezone conversion is performed, THE CLI SHALL print the converted date-time
   in ISO 8601 format to stdout.
2. WHEN a successful timezone conversion is performed, THE CLI SHALL print a Countdown string to
   stdout that expresses the duration between the current system time and the converted Deadline in
   days, hours, and minutes.
3. WHEN the Deadline is in the past, THE CLI SHALL prefix the Countdown string with a label that
   clearly indicates the moment has already passed (e.g., "2 hours ago").

---

### Requirement 3: Input Parsing

**User Story:** As a developer, I want to supply the deadline in common date-time formats, so that I
do not need to pre-format my input.

#### Acceptance Criteria

1. WHEN a date-time string is provided, THE Converter SHALL accept input in ISO 8601 format
   (e.g., `2025-12-31T23:59:00` and `2025-12-31 23:59:00`).
2. IF the date-time string cannot be parsed into a valid datetime object, THEN THE CLI SHALL print a
   descriptive error message to stderr and exit with a non-zero status code.

---

### Requirement 4: MCP Tool Exposure

**User Story:** As an AI assistant user, I want `tzdeadline` to be available as an MCP tool, so
that I can invoke timezone conversion from within an MCP-compatible client without leaving my
workflow.

#### Acceptance Criteria

1. THE MCP_Server SHALL expose exactly one tool named `convert_time` that accepts a date-time
   string, a source IANA_Timezone, and a target IANA_Timezone as parameters.
2. WHEN `convert_time` is invoked with valid parameters, THE MCP_Server SHALL return the converted
   date-time in ISO 8601 format and the Countdown string as its response.
3. IF `convert_time` is invoked with an unrecognised IANA_Timezone or an unparseable date-time
   string, THEN THE MCP_Server SHALL return a structured error response describing the problem
   rather than raising an unhandled exception.

---

### Requirement 5: Round-Trip Correctness

**User Story:** As a developer, I want confidence that converting a time from timezone A to timezone
B and back again yields the original value, so that I can trust the tool's output.

#### Acceptance Criteria

1. FOR ALL valid date-time strings and pairs of IANA_Timezones A and B, converting from A to B and
   then from B to A SHALL produce a datetime that is equivalent to the original input datetime
   (round-trip property).
