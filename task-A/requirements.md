# Task A requirements and evaluation decisions

Source: Vertex Labs Intern Take-Home Assessment.pdf, Section A, page 3. The assessment permits AI assistance and asks for disclosure and raw chat exports or share links.

## Required submission

- A system message and user template containing `{article}`.
- Funding-news extraction into the exact specified JSON structure.
- Three runs of each of the three supplied snippets.
- Three runs of one original stress input: twelve raw outputs for the selected prompt.
- Model name and failure/consistency/ambiguity notes of at most 150 words.
- An AI log of at most 80 words and actual raw chat export or share link.

## Additional work requested by Yash

Five system prompts of different lengths, ten additional tests, code checks for validity and separate correctness checks, Markdown results, temperature zero, instructions in system messages, invalid-output handling guidance, production classifier/LLM-validator discussion, and a maintained Git repository. Tasks B and C are reserved folders; the current requested implementation is Task A.

## Output contract

Root object: only `companies`, an array. Every company object contains exactly:

- `name`: string.
- `hq_country`: string or null.
- `sector`: string or null.
- `round`: one of `Pre-seed`, `Seed`, `Series A`, `Series B`, `Series C+`, `Unknown`.
- `amount_usd`: number or null.
- `lead_investors`: array of strings.
- `evidence`: a short quotation from the article supporting the round and amount where stated.

Never invent values. Missing facts are null or Unknown; an absent lead investor list is empty. Non-USD sums become null unless the article supplies a USD figure. Non-funding articles produce `{"companies": []}`.

## Decisions to freeze before testing

The examples imply geographic knowledge is allowed: Jakarta maps to Indonesia, Bengaluru and Pune to India. Use unambiguous city-to-country mappings, without guessing ambiguous places. Treat bare `$` as USD in this English-language assessment, and state this ambiguity in the submission. Normalize Series D and later to Series C+. Do not infer a stage or exact amount from 'fresh funding' or 'mid-eight figures'. Do not turn participating investors into lead investors. Exclude hypothetical future raises, acquisitions, and historical background funding when an article is not announcing that funding round. Evidence must be copied from the input, without invented wording.

## Current status

Assessment extracted successfully. Live API testing awaits restoration of the OpenAI Platform connection, which returned 'requires reauthentication'. No prompts have been run and no evaluation results are claimed.
