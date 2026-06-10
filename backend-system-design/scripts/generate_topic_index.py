"""Generate a Markdown topic index for the documentation."""

from pathlib import Path

root = Path(__file__).resolve().parent.parent
topics_dir = root / "docs" / "topics"
output = root / "docs" / "topic-index.md"

topic_titles = {
    "01-apis": "01 APIs",
    "02-api-gateways": "02 API Gateways",
    "03-jwts": "03 JWTs",
    "04-webhooks": "04 Webhooks",
    "05-rest-vs-graphql": "05 REST vs GraphQL",
    "06-long-polling-vs-websockets": "06 Long Polling vs WebSockets",
    "07-rate-limiting": "07 Rate Limiting",
    "08-idempotency": "08 Idempotency",
    "09-load-balancing": "09 Load Balancing",
    "10-proxy-vs-reverse-proxy": "10 Proxy vs Reverse Proxy",
    "11-scalability": "11 Scalability",
    "12-caching": "12 Caching",
    "13-cache-eviction": "13 Cache Eviction",
    "14-cdn": "14 CDN",
    "15-sql-vs-nosql": "15 SQL vs NoSQL",
    "16-acid-transactions": "16 ACID Transactions",
    "17-indexes": "17 Indexes",
    "18-sharding": "18 Sharding",
    "19-change-data-capture": "19 Change Data Capture",
    "20-availability": "20 Availability",
    "21-single-point-of-failure": "21 Single Point of Failure",
    "22-cap-theorem": "22 CAP Theorem",
    "23-consistent-hashing": "23 Consistent Hashing",
    "24-message-queues": "24 Message Queues",
    "25-stateful-vs-stateless": "25 Stateful vs Stateless",
    "26-concurrency-vs-parallelism": "26 Concurrency vs Parallelism",
    "27-batch-vs-stream-processing": "27 Batch vs Stream Processing",
    "28-bloom-filters": "28 Bloom Filters",
    "29-geohashing": "29 Geohashing",
}

page_order = [
    ("concept.md", "Concept"),
    ("foundation.md", "Foundation"),
    ("lab.md", "Lab"),
    ("math-foundation.md", "Math Foundation"),
    ("quiz.md", "Quiz"),
]

lines = ["# Topic Index", ""]
for topic_path in sorted(topics_dir.iterdir()):
    if not topic_path.is_dir():
        continue
    lines.append(f"## {topic_titles.get(topic_path.name, topic_path.name)}")
    for file_name, label in page_order:
        page = topic_path / file_name
        if not page.exists():
            continue
        rel = page.relative_to(root / "docs").as_posix()
        lines.append(f"- [{label}]({rel})")
    lines.append("")

lines.extend(
    [
        "## Navigation",
        "",
        "- Home: [System Engineering Tutorials](index.md)",
        "- Learning Path: [Full roadmap](learning-path.md)",
        "- Start Topic: [APIs](topics/01-apis/concept.md)",
        "- End Topic: [Geohashing](topics/29-geohashing/concept.md)",
    ]
)

output.write_text("\n".join(lines), encoding="utf-8")
print(f"Wrote topic index to {output}")
