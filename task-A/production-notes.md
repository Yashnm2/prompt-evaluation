# Production classification and safety

Source check: 6 November 2026. These are design recommendations, not Task A benchmark results.

For a production system, I would evaluate a dedicated classifier such as TypeSafe AI's Jev for bounded decisions, or OpenAI's moderation model for harmful-content classification. The aim would be lower cost, stronger task accuracy and more useful uncertainty signals than asking a general-purpose LLM to generate labels. Those improvements need measurement on representative inputs.

Task A is structured extraction, so neither a funding/not-funding classifier nor a moderation classifier alone replaces it. A classifier could filter non-funding articles or review individual claims, followed by an extractor for names, amounts and evidence. Check recall carefully: filtering out an actual funding article would prevent extraction altogether.

TypeSafe describes its models as producing typed decisions with confidence estimates and markets cost and latency advantages. These are vendor claims; evaluate accuracy, calibration and cost for this workload. Sources: [TypeSafe AI](https://typesafe.ai/) and [official documentation](https://docs.typesafe.ai/introduction).

OpenAI's moderation endpoint is free and returns predefined harm-category flags and scores. It is not an arbitrary-label classifier. Use its scores as policy signals, with review thresholds validated on representative data and reassessed after model updates. Source: [OpenAI moderation documentation](https://developers.openai.com/api/docs/guides/moderation).

Use a review band for uncertain decisions. A low harm score alone does not establish certainty that an input is safe. Measure false negatives, false positives, calibration and review coverage before automating actions.

An additional LLM can validate the extracted facts against the source and safety policy. Run deterministic checks first, use a separate trusted system prompt, and treat both article and proposed output as untrusted data. Check whether every recipient has a real announced round, each amount belongs to that round, each lead is explicitly identified, and each quote supports the extracted fields. Validate the reviewer's verdict too. Escalate disagreement or uncertainty instead of automatically accepting either model. This may improve safety but adds cost and latency and can share the extractor's mistakes. Test its actual benefit. No LLM validator or classifier comparison has been run in this repository.
