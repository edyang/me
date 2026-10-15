# Technical blog repository

Read TECH_BLOG_AGENT.md before editing. Preserve the Jekyll theme, unrelated legacy posts and existing inbound links. Base changes on the current master head.

The owner authorizes sanitized publication, replacement of previous automated articles, illustrations and normal PR merge after checks. The latest user request extends the archive to 2013–2019 with at least three articles in every month, following the specified annual themes. The established 2020-01-05 onward chronology and its 5–10 day intervals remain intact. Show only the ordinary article date across the site, RSS and metadata. Do not expose conversation, generation or processing timestamps.

Each article needs a concrete title, topic-specific technical reasoning, implementation or investigation steps, an evidence-bounded conclusion, and at least one relevant local illustration. Check that named technology and API behavior existed by the article date. Never invent tests, customer delivery or performance results. Never commit raw chats, private attachments, identities, credentials or proprietary details.

Run python3 scripts/validate_tech_notes.py and CI Jekyll/rendered checks. Merge normally after successful checks; no force push or hosting changes. Verify the public pages and all affected assets before reporting deployed. Receipts live under excluded scripts/publication_receipts; they are operational evidence, not article content.
