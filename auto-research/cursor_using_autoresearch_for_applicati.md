# Using autoresearch for application development
_Exported on 30/03/2026 at 15:53:42 GMT+5:30 from Cursor (2.6.20)_

---

**User**

How to use https://github.com/karpathy/autoresearch for any application I want to build ?

---

**Cursor**

# Using Karpathy's Autoresearch for Your Own Applications

[Autoresearch](https://github.com/karpathy/autoresearch) is not a general-purpose framework you install and plug into any project. It's a **pattern/methodology** for autonomous AI-driven experimentation. Here's how to understand and adapt it:

---

## What Autoresearch Actually Is

It's a setup where:
1. An AI agent (Claude, Codex, etc.) is given a **single file to modify** (`train.py`)
2. A **program file** (`program.md`) gives the agent instructions on what to optimize
3. The agent runs experiments in a loop: **modify code -> train -> evaluate -> keep or discard**
4. The metric is fixed (validation bits-per-byte), and the time budget is fixed (5 minutes per experiment)

The key insight: **you don't write Python — you write the Markdown instructions that guide the AI agent**.

---

## How to Adapt This Pattern to Your Own Application

### Step 1: Define the Structure

Mirror the three-file pattern:

| File | Role | Who Edits |
|------|------|-----------|
| `prepare.py` (or equivalent) | Fixed infrastructure: data loading, evaluation, constants | You (human) |
| `train.py` (or equivalent) | The code the agent iterates on | AI agent |
| `program.md` | Instructions, constraints, and goals for the agent | You (human) |

### Step 2: Define a Clear, Measurable Metric

This is the most critical part. Autoresearch works because it has a single, unambiguous metric (`val_bpb` — lower is better). For your application, you need an equivalent:

| Application Type | Possible Metric |
|-----------------|-----------------|
| Image classifier | Validation accuracy, F1 score |
| Recommender system | NDCG, precision@k |
| Web API | Latency p99, throughput (req/s) |
| Compiler optimization | Binary size, execution time |
| Game AI | Win rate, average score |
| Prompt engineering | LLM judge score, task completion rate |

### Step 3: Create Your `program.md`

This is where you "program the researcher." A minimal template:

```markdown
# Program

## Goal
Improve [YOUR METRIC] on [YOUR TASK].

## Rules
- Only modify `[your_target_file]`
- Each experiment must complete within [TIME BUDGET]
- After each run, compare the metric to the current best
- If improved, keep the change. If not, revert.
- Log every experiment with: what changed, hypothesis, result

## Constraints
- Do not modify `[infrastructure files]`
- Do not install new dependencies
- Keep changes small and incremental (one idea per experiment)

## Context
[Describe what the code does, what the architecture looks like,
 what has been tried before, what areas are promising]

## Current Best
- Metric: [value]
- Achieved by: [description of current best configuration]
```

### Step 4: Set Up the Evaluation Loop

Your infrastructure file needs a function that:
1. Runs the modified code
2. Produces a deterministic, comparable metric
3. Completes within the time budget
4. Returns a clear pass/fail signal

### Step 5: Launch the Agent

Point your AI coding agent (Claude in Cursor, Codex CLI, etc.) at your `program.md`:

```
Hi, have a look at program.md and let's kick off a new experiment! Let's do the setup first.
```

---

## Concrete Example: Adapting for a Different Task

Say you want to optimize a **text classification pipeline**:

```
project/
├── prepare.py      # Downloads dataset, builds vocab, defines eval function
├── classify.py     # Model architecture + training loop (AGENT EDITS THIS)
├── program.md      # Instructions for the agent
```

Your `prepare.py` would have a fixed `evaluate()` function that returns F1 score on a held-out test set. Your `program.md` would tell the agent to maximize F1 by experimenting with architectures, hyperparameters, feature engineering, etc.

---

## Key Principles to Follow

1. **Fixed time budget** — makes every experiment comparable regardless of what the agent changes
2. **Single file to modify** — keeps scope manageable and diffs reviewable
3. **Automated evaluation** — the agent must be able to run and score without human intervention
4. **Keep/discard logic** — revert bad experiments, keep good ones
5. **Logging** — every experiment should be recorded so you can review in the morning

---

## Limitations to Be Aware Of

- **Requires a quantifiable metric** — if you can't score it automatically, this pattern doesn't work
- **Currently single-GPU NVIDIA only** for the default repo (see the notable forks for Mac/AMD/Windows)
- **The agent can get stuck** in local optima, making small changes that don't help
- **Not for arbitrary software engineering** — this is specifically for iterative optimization problems where you can measure quality automatically

---

## Bottom Line

Autoresearch isn't a library you import. It's a **workflow pattern**: give an AI agent a constrained sandbox, a clear metric, and time — then let it iterate autonomously. You can apply this to any domain where you can define "better" as a number and automate the measurement.

---

**User**

Based on price data of gold, usdinr, crude, silver, amd indices like nifty 50, sp500 etc I want to identify patterns, connections between them to forecast next day or next week directional forecast for Nifty 50. Can I use autoresearch to identify the features from price datas, patterns and train neural network (DL) to make predictions?

---

**Cursor**

Yes, you absolutely can adapt the autoresearch pattern for this. It's actually a strong fit because financial forecasting has a **clear, measurable metric** (directional accuracy, Sharpe ratio) and an **infinite space of features/architectures** for the agent to explore. Let me break down exactly how.

---

## Is This a Good Fit for Autoresearch?

| Requirement | Your Problem | Verdict |
|-------------|-------------|---------|
| Quantifiable metric | Directional accuracy, profit factor | Yes |
| Automated evaluation | Backtest on held-out data | Yes |
| Single file to iterate on | Model + feature engineering | Yes |
| Fixed time budget experiments | Train small model in 5 min | Yes |
| Large search space | Features, lags, architectures, ensembles | Yes |

The honest caveat: **financial markets are extremely noisy**, and out-of-sample performance is notoriously hard. But the autoresearch loop is still valuable because it will systematically explore far more ideas than you could manually.

---

## Concrete Architecture

```
nifty-forecast/
├── prepare.py        # Data download, preprocessing, train/val/test split (FIXED)
├── train.py          # Feature engineering + model + training loop (AGENT EDITS)
├── program.md        # Instructions for the AI agent (YOU EDIT)
├── data/             # Price CSVs
│   ├── nifty50.csv
│   ├── sp500.csv
│   ├── gold.csv
│   ├── silver.csv
│   ├── crude.csv
│   └── usdinr.csv
```

---

## Step-by-Step Setup

### 1. `prepare.py` — The Fixed Infrastructure

This file handles data loading and evaluation. The agent never touches it.

```python
import pandas as pd
import numpy as np
from datetime import datetime

# ---- Constants ----
TRAIN_END = "2023-12-31"
VAL_START = "2024-01-01"
VAL_END   = "2024-09-30"
TEST_START = "2024-10-01"

TARGET = "nifty50_direction"  # 1 = up, 0 = down
FORECAST_HORIZON = 1  # 1 = next day, 5 = next week

INSTRUMENTS = ["nifty50", "sp500", "gold", "silver", "crude", "usdinr"]

def load_data():
    """Load and merge all instrument price data on date index."""
    frames = {}
    for inst in INSTRUMENTS:
        df = pd.read_csv(f"data/{inst}.csv", parse_dates=["date"])
        df = df.set_index("date").sort_index()
        df = df.rename(columns={
            "open": f"{inst}_open", "high": f"{inst}_high",
            "low": f"{inst}_low", "close": f"{inst}_close",
            "volume": f"{inst}_volume"
        })
        frames[inst] = df

    merged = pd.concat(frames.values(), axis=1, join="inner")
    merged = merged.dropna()

    # Target: Nifty 50 direction N days ahead
    future_close = merged["nifty50_close"].shift(-FORECAST_HORIZON)
    merged[TARGET] = (future_close > merged["nifty50_close"]).astype(int)
    merged = merged.dropna()

    return merged

def split_data(df):
    train = df[:TRAIN_END]
    val   = df[VAL_START:VAL_END]
    test  = df[TEST_START:]
    return train, val, test

def evaluate(predictions, actuals):
    """
    Returns a dict of metrics. The PRIMARY metric the agent optimizes
    is directional accuracy on validation set.
    """
    correct = (predictions == actuals).sum()
    total = len(actuals)
    accuracy = correct / total

    # Prevent trivial "always predict up" strategies
    up_pct = predictions.mean()
    balance_penalty = 0.0
    if up_pct > 0.85 or up_pct < 0.15:
        balance_penalty = 0.05

    return {
        "directional_accuracy": accuracy - balance_penalty,
        "raw_accuracy": accuracy,
        "up_prediction_pct": up_pct,
        "total_samples": total,
    }
```

### 2. `train.py` — What the Agent Iterates On

This is the starting point. The agent will modify everything here.

```python
import torch
import torch.nn as nn
import numpy as np
import pandas as pd
from prepare import load_data, split_data, evaluate, TARGET, INSTRUMENTS

# ---- Feature Engineering (AGENT: experiment here) ----
def build_features(df):
    """Transform raw OHLCV into model features."""
    features = pd.DataFrame(index=df.index)

    for inst in INSTRUMENTS:
        close = df[f"{inst}_close"]
        # Returns
        features[f"{inst}_ret_1d"] = close.pct_change(1)
        features[f"{inst}_ret_5d"] = close.pct_change(5)
        features[f"{inst}_ret_20d"] = close.pct_change(20)
        # Volatility
        features[f"{inst}_vol_10d"] = close.pct_change().rolling(10).std()
        # Moving average crossover
        features[f"{inst}_ma_ratio"] = close.rolling(5).mean() / close.rolling(20).mean()

    features = features.dropna()
    return features

# ---- Model (AGENT: experiment here) ----
HIDDEN_DIM = 64
NUM_LAYERS = 2
DROPOUT = 0.3
LEARNING_RATE = 1e-3
EPOCHS = 100
BATCH_SIZE = 64
LOOKBACK = 10  # sequence length for temporal models

class DirectionPredictor(nn.Module):
    def __init__(self, input_dim):
        super().__init__()
        self.lstm = nn.LSTM(input_dim, HIDDEN_DIM, NUM_LAYERS,
                           batch_first=True, dropout=DROPOUT)
        self.head = nn.Sequential(
            nn.Linear(HIDDEN_DIM, 32),
            nn.ReLU(),
            nn.Dropout(DROPOUT),
            nn.Linear(32, 1),
            nn.Sigmoid()
        )

    def forward(self, x):
        _, (h, _) = self.lstm(x)
        return self.head(h[-1]).squeeze(-1)

# ---- Training Loop ----
def main():
    df = load_data()
    features = build_features(df)
    df = df.loc[features.index]

    train_df, val_df, _ = split_data(df)
    train_feat, val_feat, _ = split_data(features)

    # Normalize using train stats only (no look-ahead)
    mean = train_feat.mean()
    std = train_feat.std().replace(0, 1)
    train_feat = (train_feat - mean) / std
    val_feat = (val_feat - mean) / std

    input_dim = train_feat.shape[1]
    model = DirectionPredictor(input_dim)
    optimizer = torch.optim.Adam(model.parameters(), lr=LEARNING_RATE)
    criterion = nn.BCELoss()

    # Create sequences
    def make_sequences(feat_df, target_series):
        X, y = [], []
        feat_vals = feat_df.values
        target_vals = target_series.values
        for i in range(LOOKBACK, len(feat_vals)):
            X.append(feat_vals[i-LOOKBACK:i])
            y.append(target_vals[i])
        return torch.tensor(np.array(X), dtype=torch.float32), \
               torch.tensor(np.array(y), dtype=torch.float32)

    X_train, y_train = make_sequences(train_feat, train_df[TARGET])
    X_val, y_val = make_sequences(val_feat, val_df[TARGET])

    best_val_acc = 0.0
    for epoch in range(EPOCHS):
        model.train()
        indices = torch.randperm(len(X_train))
        for start in range(0, len(X_train), BATCH_SIZE):
            idx = indices[start:start+BATCH_SIZE]
            pred = model(X_train[idx])
            loss = criterion(pred, y_train[idx])
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

        # Validate
        model.eval()
        with torch.no_grad():
            val_pred = model(X_val)
            val_pred_binary = (val_pred > 0.5).int().numpy()

        metrics = evaluate(val_pred_binary, y_val.numpy().astype(int))

        if metrics["directional_accuracy"] > best_val_acc:
            best_val_acc = metrics["directional_accuracy"]
            torch.save(model.state_dict(), "best_model.pt")

        if (epoch + 1) % 10 == 0:
            print(f"Epoch {epoch+1}/{EPOCHS} | "
                  f"Loss: {loss.item():.4f} | "
                  f"Val Acc: {metrics['directional_accuracy']:.4f} | "
                  f"Up%: {metrics['up_prediction_pct']:.2f}")

    print(f"\n=== RESULT ===")
    print(f"best_val_directional_accuracy: {best_val_acc:.6f}")

if __name__ == "__main__":
    main()
```

### 3. `program.md` — The Agent's Instructions

This is the most important file. You iterate on this.

```markdown
# Nifty 50 Directional Forecast — Research Program

## Objective
Maximize **directional accuracy** of next-day Nifty 50 movement prediction
on the validation set (2024-01-01 to 2024-09-30).

## Setup
- Run: `python train.py`
- The script prints `best_val_directional_accuracy: X.XXXX` at the end
- **Higher is better.** Baseline is ~0.50 (random).
- Time budget: each training run should complete within 5 minutes.

## What You Can Modify
Only modify `train.py`. Do NOT touch `prepare.py`.

### Feature Engineering Ideas to Explore
- RSI, MACD, Bollinger Bands, ATR for each instrument
- Cross-instrument correlations (gold/USD inverse, crude/INR linkage)
- Lagged features at different horizons (1d, 2d, 3d, 5d, 10d, 20d)
- Volume-price divergence signals
- Day-of-week, month-of-year seasonality
- Regime detection (high vol vs low vol periods)
- Relative strength: Nifty vs SP500, Gold vs Silver
- Yield curve proxies, VIX-like volatility indices
- Inter-market lead-lag: SP500 closes before Nifty opens

### Architecture Ideas to Explore
- LSTM, GRU, Transformer encoder
- 1D CNN + LSTM hybrid
- Attention over lookback window
- Multi-head: separate feature groups processed independently then merged
- Ensemble of small models
- Residual connections, layer norm

### Training Ideas to Explore
- Learning rate schedules (cosine, warmup)
- Label smoothing
- Focal loss for imbalanced directions
- Mixup / data augmentation for time series
- Different optimizers (AdamW, SGD with momentum, Muon)
- Early stopping patience
- Gradient clipping

## Rules
1. Each experiment: change ONE thing. State your hypothesis before running.
2. After each run, record: what changed, hypothesis, result.
3. If val accuracy improves, KEEP the change. If not, REVERT.
4. Never look at test set. Only optimize on validation.
5. Watch for overfitting: if train acc >> val acc, add regularization.
6. Watch for trivial solutions: if up_prediction_pct > 0.85, the model
   is just predicting "up" always. Add class weighting or focal loss.

## Experiment Log
(Agent fills this in as experiments progress)

| # | Hypothesis | Change | Val Acc | Keep? |
|---|-----------|--------|---------|-------|
| 0 | Baseline  | —      | 0.XXXX  | base  |
```

---

## What the Agent Will Explore Autonomously

Once you launch it, the agent will cycle through experiments like:

1. **"Adding RSI and MACD features might capture momentum"** → adds technical indicators → trains → measures → keeps/reverts
2. **"SP500 leads Nifty by 1 day due to timezone"** → adds lagged SP500 returns → trains → measures
3. **"LSTM may not capture long-range patterns, try Transformer"** → swaps architecture → trains → measures
4. **"Gold/USD inverse relationship could signal risk-off moves"** → adds cross-instrument features → trains
5. **"Model is overfitting, add weight decay"** → adjusts regularization → trains

Each loop takes ~5 minutes. Overnight you get ~100 experiments.

---

## Critical Pitfalls to Avoid

### 1. Look-Ahead Bias (the #1 killer in financial ML)
Your `prepare.py` must **never** let future data leak into features:
- Normalize using **only training set statistics**
- Compute rolling indicators using **only past data** at each point
- The target must use **future** prices, but features must use **past** prices

### 2. Non-Stationarity
Markets change regimes. A model trained on 2020-2023 may not work in 2024. Consider:
- Walk-forward validation instead of fixed splits
- Shorter training windows (recent 1-2 years)
- Regime-aware features

### 3. Overfitting to Noise
Financial data has extremely low signal-to-noise. The agent might find patterns that are just noise:
- Keep the model small (underfitting > overfitting here)
- Use strong regularization (dropout, weight decay)
- Watch for train/val accuracy gap

### 4. Transaction Costs
55% directional accuracy sounds great but might not be profitable after costs. Consider adding a profitability-aware metric.

---

## Data Sources

To get the price data, you can use:

| Source | API | Cost |
|--------|-----|------|
| Yahoo Finance | `yfinance` Python package | Free |
| NSE India | `nselib` or `jugaad-data` | Free |
| Alpha Vantage | REST API | Free tier available |
| Quandl/Nasdaq Data Link | REST API | Free tier |

A quick data download script:

```python
import yfinance as yf

tickers = {
    "nifty50": "^NSEI",
    "sp500": "^GSPC",
    "gold": "GC=F",
    "silver": "SI=F",
    "crude": "CL=F",
    "usdinr": "INR=X",
}

for name, symbol in tickers.items():
    df = yf.download(symbol, start="2015-01-01", end="2024-12-31")
    df = df.reset_index()
    df.columns = ["date", "open", "high", "low", "close", "adj_close", "volume"]
    df.to_csv(f"data/{name}.csv", index=False)
    print(f"Saved {name}: {len(df)} rows")
```

---

## Bottom Line

**Yes, autoresearch is a strong fit for this problem.** The pattern of "modify features/model → train → evaluate → keep/revert" maps perfectly to financial forecasting experimentation. The agent will systematically explore far more feature combinations, architectures, and hyperparameters than you could manually — and it'll do it while you sleep.

The hard part isn't the setup — it's **defining the right evaluation metric** and **preventing data leakage**. Get those right in `prepare.py`, and the agent can explore freely in `train.py`.

---

**User**

How can I use it with cursor (not claude or codex)

---

**Cursor**

## Using Autoresearch with Cursor

Cursor works perfectly with autoresearch — in fact, it's one of the most natural fits since Cursor already gives an AI agent full access to your files and terminal.

---

### How It Works in Cursor

The autoresearch loop in Cursor looks like this:

1. You open the project folder in Cursor
2. You tell the Agent to read `program.md`
3. The Agent modifies `train.py`, runs it in the terminal, reads the output, decides whether to keep or revert, and repeats

The agent **stays in a single conversation**, using Cursor's tools to edit files and run commands — exactly what you're doing right now with me.

---

### Setup

#### 1. Create the project structure

```
nifty-forecast/
├── prepare.py        # Fixed infrastructure
├── train.py          # Agent modifies this
├── program.md        # Your instructions to the agent
├── data/             # Price CSVs
```

#### 2. Open the folder in Cursor

Just `File → Open Folder → nifty-forecast/`

#### 3. Start the Agent with this prompt

In Cursor's Agent chat (Cmd+L or the chat panel), send:

```
Read program.md and let's start the autoresearch loop. 
First, run the baseline experiment, then begin iterating. 
For each experiment:
1. State your hypothesis
2. Make ONE change to train.py
3. Run `python train.py` in the terminal
4. Read the output and record the result
5. If val accuracy improved, keep the change. If not, revert train.py.
6. Repeat with the next experiment.

Keep going until I tell you to stop.
```

That's it. The Cursor agent will:
- Use **file editing tools** to modify `train.py`
- Use the **Shell tool** to run `python train.py`
- Read the terminal output to see the metric
- Decide keep/revert based on the result
- Loop automatically

---

### Key Cursor-Specific Tips

#### Use Agent mode, not Ask mode
Agent mode has the ability to edit files and run terminal commands. Ask mode is read-only. Make sure you're in **Agent** mode (the default in the chat panel).

#### Enable "YOLO mode" for autonomous looping
By default, Cursor asks for your approval before running terminal commands. For autoresearch to run autonomously:

1. Go to **Cursor Settings → Features → Terminal**
2. Enable **"Auto-run"** (sometimes called YOLO mode)
3. This lets the agent run `python train.py` without asking each time

Without this, you'll need to click "Allow" for every experiment — which defeats the purpose of overnight autonomy.

#### Keep the conversation going
Cursor's agent stays in one conversation. If it stops after a few experiments (it may think it's "done"), just nudge it:

```
Keep going. Run the next experiment.
```

Or be more specific:

```
Good progress. Now try adding RSI features and see if that helps.
```

#### Use Cursor Rules for persistent instructions
Instead of repeating yourself, create a `.cursor/rules/autoresearch.mdc` file:

```markdown
---
description: Autoresearch loop for Nifty 50 forecasting
globs: ["train.py"]
---

When editing train.py, follow the autoresearch protocol:
- Read program.md for full instructions
- Make ONE change per experiment
- Run `python train.py` after each change
- Keep changes that improve val_directional_accuracy
- Revert changes that don't improve the metric
- Log every experiment in the experiment log section of program.md
```

This way, every time the agent touches `train.py`, it automatically gets these instructions.

---

### What a Typical Session Looks Like

```
You:    Read program.md and start experimenting.

Agent:  Reading program.md... I see the goal is to maximize directional
        accuracy for Nifty 50 prediction. Let me run the baseline first.
        
        [runs python train.py]
        
        Baseline result: val_directional_accuracy = 0.5123
        
        Experiment 1: I'll add RSI-14 for all instruments as features.
        Hypothesis: RSI captures overbought/oversold momentum.
        
        [edits train.py → adds RSI features]
        [runs python train.py]
        
        Result: 0.5287 — improved! Keeping this change.
        
        Experiment 2: I'll add MACD crossover signals.
        Hypothesis: MACD captures trend changes.
        
        [edits train.py → adds MACD]
        [runs python train.py]
        
        Result: 0.5195 — worse than 0.5287. Reverting.
        
        Experiment 3: I'll try a GRU instead of LSTM.
        ...
```

---

### Cursor vs Claude/Codex for Autoresearch

| Aspect | Cursor Agent | Claude Code CLI | Codex CLI |
|--------|-------------|----------------|-----------|
| File editing | Built-in tools | Built-in tools | Built-in tools |
| Terminal execution | Built-in Shell | Built-in Bash | Built-in Shell |
| Autonomous mode | YOLO mode toggle | `--dangerously-skip-permissions` | Sandbox mode |
| Visual feedback | See edits in real-time in IDE | Terminal only | Terminal only |
| Manual intervention | Easy — just type in chat | Easy — just type | Easy — just type |
| Long overnight runs | May need nudging | Runs until done | Runs until done |

Cursor's main **advantage** is that you see every file edit live in the editor with diffs. Its main **limitation** for autoresearch is that long conversations can hit context window limits — after 50+ experiments, you may need to start a new chat and say "read program.md, continue from experiment 51."

---

### One Practical Tip

Add this to the bottom of your `program.md` to help the agent track state across experiments:

```markdown
## Current Best
- Metric: 0.5123 (baseline)
- Configuration: LSTM, 64 hidden, 10-day lookback, basic returns + vol + MA features

## Experiment Log
| # | Hypothesis | Change | Val Acc | Keep? |
|---|-----------|--------|---------|-------|
| 0 | Baseline  | —      | 0.5123  | base  |
```

Tell the agent to **update this table after each experiment**. That way, even if you start a new conversation, the agent can read `program.md` and know exactly where things stand.

---

**User**

How are different ways we can use autoresearch ? Can it also be used for research or new project ideas or it is only for training the model ?
Suppose I want to do some research on thermodynamics for specific purpose, will it perform the research ?

---

**Cursor**

Great question. Let me be very precise about what autoresearch **is and isn't**, and then cover the broader landscape of how AI agents can do research.

---

## What Autoresearch Actually Does

Autoresearch has **one specific loop**:

```
modify code → run code → measure output → keep or revert → repeat
```

That's it. It's an **automated code experimentation loop**. It doesn't "think," "read papers," or "reason about physics." It edits a file, runs it, checks a number, and decides if the number got better.

---

## Can It Do Thermodynamics Research?

**Not directly, no.** Here's why:

| What autoresearch does | What thermodynamics research requires |
|------------------------|--------------------------------------|
| Edits code | Reads papers, textbooks, derives equations |
| Runs code, gets a number | Designs experiments (physical or computational) |
| Optimizes that number | Formulates hypotheses from theory |
| Repeats blindly | Reasons about why results occur |

Autoresearch has **no understanding of physics**. It's a blind optimizer that modifies code to improve a metric.

### But... there's a version that COULD work

If your thermodynamics problem can be expressed as **"write code, run simulation, check metric"**, then yes, autoresearch applies. Examples:

| Thermodynamics Problem | Autoresearch-able? | Why |
|------------------------|-------------------|-----|
| "Derive the Clausius inequality" | No | Requires mathematical reasoning, not code optimization |
| "Find the optimal heat exchanger fin geometry via CFD simulation" | **Yes** | Code modifies geometry params → runs simulation → measures heat transfer efficiency |
| "What's the best material combination for a thermoelectric generator?" | **Yes** | Code sweeps material properties → runs model → measures ZT figure of merit |
| "Explain why entropy increases in irreversible processes" | No | Conceptual understanding, not optimization |
| "Optimize a Rankine cycle's turbine inlet conditions for max efficiency" | **Yes** | Code modifies T, P → runs thermodynamic model → measures efficiency |

**The rule: if you can reduce it to code → number → better/worse, autoresearch works.**

---

## The 4 Different Ways to Use Autoresearch

### 1. ML Model Training (The Original Use Case)
What Karpathy built it for. The agent experiments with architectures, hyperparameters, and training techniques to minimize a loss metric.

**Examples:**
- LLM training optimization (the original)
- Your Nifty 50 forecasting project
- Image classification accuracy
- Speech recognition word error rate

### 2. Simulation Parameter Optimization
Any domain where you have a simulator and want to find optimal parameters.

**Examples:**
- CFD simulations (fluid dynamics, heat transfer)
- Finite element analysis (structural engineering)
- Circuit simulation (electronics design)
- Chemical process simulation (reaction yields)

```
program.md: "Optimize heat exchanger design for maximum thermal efficiency"
prepare.py: Runs OpenFOAM/COMSOL simulation, returns efficiency metric
train.py:   Agent modifies geometry, materials, flow rates
```

### 3. Algorithm/Code Optimization
Making code faster, more memory-efficient, or more accurate.

**Examples:**
- Optimizing a sorting algorithm's performance
- Compiler flag tuning
- Database query optimization
- Game AI strategy refinement

```
program.md: "Minimize execution time of this graph algorithm on benchmark"
prepare.py: Runs benchmark, measures wall-clock time
train.py:   Agent modifies the algorithm implementation
```

### 4. Prompt Engineering / LLM Pipeline Optimization
Surprisingly good fit — the agent optimizes prompts, RAG configs, or LLM pipelines.

**Examples:**
- Optimizing system prompts for accuracy on a benchmark
- Tuning RAG chunk sizes, retrieval strategies
- Finding the best few-shot examples for a task

```
program.md: "Maximize accuracy on this Q&A benchmark"
prepare.py: Sends prompts to LLM API, scores responses
train.py:   Agent modifies prompt templates, chunking strategy, etc.
```

---

## What Autoresearch CANNOT Do

| Task | Why Not |
|------|---------|
| Literature review | It can't read papers or browse the web |
| Theoretical derivation | It can't do math reasoning — it just edits code |
| Experimental design (physical) | It can't operate lab equipment |
| Creative ideation | It doesn't "think" — it hill-climbs a metric |
| Open-ended exploration | It needs a fixed metric to optimize |
| Qualitative research | No metric = no autoresearch |

---

## What You Actually Want for General Research

If your goal is "AI agent that does research" in the broader sense (reads papers, synthesizes ideas, proposes hypotheses), you need **different tools**:

| Tool | What It Does | Good For |
|------|-------------|----------|
| **Autoresearch** | Blind code optimization loop | Improving a metric through code changes |
| **Deep Research** (Gemini, ChatGPT, Perplexity) | Reads web, synthesizes info, writes reports | Literature review, market research, surveying a field |
| **Cursor Agent** (what you're using now) | Reads code/files, edits, runs commands, reasons | Building software, debugging, coding tasks |
| **Notebook LM / Claude Projects** | Analyzes uploaded documents | Understanding papers, extracting insights |
| **OpenAI Codex / Claude Code** | Autonomous coding agent | Multi-step software engineering tasks |

### For Your Thermodynamics Research

The right approach depends on what you mean by "research":

**"I want to understand thermodynamic concepts and derive insights"**
→ Use **Deep Research** (ChatGPT, Gemini, Perplexity) — they read papers, reason about theory, and synthesize knowledge.

**"I want to optimize a thermodynamic system via simulation"**
→ Use **Autoresearch** — set up the simulation in code, define the metric, let the agent iterate.

**"I want to build a thermodynamics simulation tool"**
→ Use **Cursor Agent** — it helps you write and debug code interactively.

**"I want to survey the field, find gaps, and propose new research directions"**
→ Use **Deep Research + your own judgment** — AI can survey, but research taste is still human.

---

## The Honest Summary

```
Autoresearch = automated code hill-climbing

It answers: "What code change makes this number better?"
It does NOT answer: "What should we research?" or "Why does this happen?"
```

It's a **power tool for a specific job** — optimizing anything expressible as `code → metric`. It's not a general-purpose research assistant. For broader research, combine it with other AI tools: use Deep Research for understanding, Cursor for building, and Autoresearch for optimizing.

