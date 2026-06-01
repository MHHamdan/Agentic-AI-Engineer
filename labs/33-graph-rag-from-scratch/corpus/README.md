# Lab 33 corpus — a fictional AI-research ecosystem

This is an **entirely fictional** entity-rich corpus built for the Graph RAG lab
(and reused by Labs 34 and 35). No real people, organizations, or papers are
referenced; any resemblance is coincidental.

Six documents describe a small research ecosystem with dense cross-document
structure — people, labs, projects, publications, collaborations, and funding —
chosen so that:

- **Entities recur across documents** (e.g. Aanya Rao appears in researchers, labs,
  projects, publications, collaborations), so graph construction has something to
  merge.
- **Relationships are explicit** (leads, works-at, previously-at, collaborated-with,
  advises, funds, authored, builds-on, partners-with), so entity-relationship
  extraction has clear targets.
- **Global themes exist** (the Helix-Meridian collaboration cluster, the role of
  Beacon Foundation funding, the Northgate training lineage), so global "what are
  the main themes" questions have real answers that no single chunk contains.
- **Specific facts exist** (who leads each lab, who funds what), so specific-lookup
  queries work for flat retrieval.
- **Multi-hop paths exist** (e.g. "who did the leader of the Helix Lab previously
  collaborate with, and on what?"), so multi-hop questions are answerable.

This structure is why Graph RAG can outperform flat retrieval here in a way it
cannot on the Lab 06 concept corpus: the answers to global and multi-hop questions
live in the *relationships between* documents, not inside any one chunk.
