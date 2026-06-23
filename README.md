# AI-Powered Prospecting Pipeline
**Automated YouTube creator discovery and outreach — Python + Claude + Google Sheets**

---

## What this does

End-to-end automation pipeline that identifies, qualifies, and generates personalized
outreach messages for YouTube creators — at scale, with minimal human input.

Built to solve a specific problem: finding niche creators who match a precise profile
across thousands of channels, without manual review.

---

## How it works

**Stage 1 — Discovery**
Queries the YouTube Data API v3 by keyword and niche to pull candidate channels.

**Stage 2 — Multi-layer filtering**
Each channel is evaluated against defined criteria:
- Activity level (recent upload frequency)
- Audience size (subscriber range)
- Content format (long-form, documentary-style, narrative)
- Niche alignment

Channels that don't meet all criteria are automatically blacklisted.

**Stage 3 — AI fit analysis**
Qualifying channels are passed to Claude (Anthropic API) for deep fit evaluation.
Claude assesses alignment between the creator's content style and the target profile.

**Stage 4 — Personalized outreach generation**
For high-fit channels, Claude generates a personalized outreach message in a
defined voice — referencing specific content from the channel to ensure authenticity.

**Stage 5 — Export & tracking**
All results — qualified channels, fit scores, outreach messages, and blacklisted
prospects — are exported to a live Google Sheets dashboard via the Sheets API.

---

## Results

- 10,000+ channels processed
- 54 high-fit matches identified
- Personalized outreach messages generated for each match
- Zero manual channel review required

---

## Stack

- Python
- YouTube Data API v3
- Anthropic API (Claude)
- Google Sheets API
- gspread
- pandas

---

## Structure
prospecting-pipeline/

├── main.py               # Main pipeline runner

├── youtube_search.py     # Channel discovery and filtering

├── claude_analysis.py    # AI fit evaluation and message generation

├── sheets_export.py      # Google Sheets integration

├── config.py             # API keys and filter parameters

└── README.md

---

*Built by Nahuel Ramon — AI Content & Operations Strategist*
*linkedin.com/in/nahuelramon*
