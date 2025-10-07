Overview
========


What is this project?
---------------------
A short, plain-English explanation of the problem this library solves and who it’s for.
For example: “Survey Builder lets you describe surveys as Python objects, convert to/from
XML, and validate common constraints.”

Key features
------------
- Typed models for questions, logic/routing, and structural elements
- XML parsing and serialization helpers
- Small utilities for XML editing and formatting
- Optional helpers for external APIs (e.g., Forsta)

Typical workflow
----------------
1. Parse existing survey XML into Python models (or start from scratch)
2. Build/modify questions and sections
3. Validate invariants (required options, unique IDs, etc.)
4. Serialize back to XML (or integrate with an external API)


First look
----------
Give a 4–8 line snippet showing the *shape* of common use, e.g. creating a question,
adding options, exporting to XML. Keep it runnable and minimal.

Next steps
----------
- :doc:`architecture`
- :doc:`modules_classes/index`
