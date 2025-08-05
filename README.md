# Market Signal Synthesizer 

A clean, automated workflow for product and competitive intelligence:
scraping market signals (Reddit + news), clustering themes via topic modeling,
and optionally interpreting those with a local LLM (GPT4All).

---

##  Why This Project Exists

- **Stay ahead of chatter** about competitors like Grip Security, Wiz, AppOmni, and Valence Security.
- **Aggregate public sentiment** across Reddit threads and reputable news articles.
- **Uncover emerging themes** with minimal effort using unsupervised clustering.
- **Deliver clarity** with one-sentence interpretations powered by GPT4All.

---

##  Quick Start

### Prerequisites

- Python 3.9+  
- Git  
- (Optional) GPT4All model file: `orca-mini-3b-gguf2-q4_0.gguf`

### Installation

```bash
git clone https://github.com/psych25/market_signal_tracker.git
cd market_signal_tracker
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
