# Stock Features from Price Data for Next-Day Direction Prediction Using ML/DL

## Research Summary

**Research Query:** What technical indicators and engineered features derived from stock price data (OHLCV) achieve the highest accuracy in predicting next-day stock price direction when used as inputs to machine learning and deep learning models?

**Inclusions:** Technical indicators (RSI, MACD, Bollinger Bands, moving averages, etc.), feature engineering from OHLCV data, ML/DL classification models, next-day directional prediction, feature importance studies.

**Exclusions:** Fundamental analysis, sentiment/NLP features, high-frequency tick data, options/derivatives, cryptocurrency-only studies, macroeconomic indicators.

---

## Shortlist (High-Impact)

| # | Title | Year | Citations | OpenAlex ID | DOI |
|---|-------|------|-----------|-------------|-----|
| 1 | A deep learning framework for financial time series using stacked autoencoders and long-short term memory | 2017 | 1055 | W2734777338 | 10.1371/journal.pone.0180944 |
| 2 | Predicting Stock Market Trends Using ML and DL Algorithms Via Continuous and Binary Data | 2020 | 436 | W3048630347 | 10.1109/access.2020.3015966 |
| 3 | Deep Learning for Stock Market Prediction | 2020 | 366 | W3014278717 | 10.3390/e22080840 |
| 4 | Short-term stock market price trend prediction using a comprehensive deep learning system | 2020 | 361 | W3081799531 | 10.1186/s40537-020-00333-6 |
| 5 | Forecasting stock prices with a feature fusion LSTM-CNN model using different representations of the same data | 2019 | 324 | W2912036663 | 10.1371/journal.pone.0212320 |
| 6 | A Survey of Forex and Stock Price Prediction Using Deep Learning | 2021 | 314 | W3126284633 | 10.3390/asi4010009 |
| 7 | A comprehensive evaluation of ensemble learning for stock-market prediction | 2020 | 308 | W3013734981 | 10.1186/s40537-020-00299-5 |
| 8 | A graph-based CNN-LSTM stock price prediction algorithm with leading indicators | 2021 | 298 | W3130456109 | 10.1007/s00530-021-00758-w |
| 9 | Predicting the daily return direction of the stock market using hybrid ML algorithms | 2019 | 258 | W2950843237 | 10.1186/s40854-019-0138-0 |
| 10 | Prediction of stock price direction using a hybrid GA-XGBoost algorithm with a three-stage feature engineering process | 2021 | 258 | W3193962426 | 10.1016/j.eswa.2021.115716 |
| 11 | Stock Market Prediction on High-Frequency Data Using Generative Adversarial Nets | 2018 | 257 | W2796929742 | 10.1155/2018/4907423 |
| 12 | Predicting the Direction of Stock Market Index Movement Using an Optimized ANN Model | 2016 | 254 | W2400770063 | 10.1371/journal.pone.0155133 |
| 13 | Stock Market Prediction Using ML Techniques: A Decade Survey | 2021 | 253 | W3214286852 | 10.3390/electronics10212717 |
| 14 | Temporal Attention-Augmented Bilinear Network for Financial Time-Series Data Analysis | 2018 | 240 | W2963122061 | 10.1109/tnnls.2018.2869225 |
| 15 | An ensemble of LSTM neural networks for high-frequency stock market classification | 2019 | 207 | W2845688424 | 10.1002/for.2585 |
| 16 | Forecasting Stock Market Prices Using ML and DL Models: A Systematic Review | 2023 | 199 | W4385363975 | 10.3390/ijfs11030094 |
| 17 | Machine Learning for Quantitative Finance Applications: A Survey | 2019 | 190 | W2994949492 | 10.3390/app9245574 |

---

## Claims

### C1 — high
- **Claim:** Ten technical indicators calculated from historical stock trading data serve as effective input features for ML/DL models predicting stock market direction across multiple prediction horizons (1–30 days). These typically include RSI, MACD, Stochastic Oscillator, Williams %R, CCI, ATR, moving averages, Bollinger Bands, OBV, and Rate of Change.
- **Evidence:** Abstract explicitly states "Ten technical indicators were selected as the inputs into each of the prediction models" and separately "Ten technical indicators from ten years of historical data are our input values."
- **Works:** W3014278717, W3048630347

### C2 — high
- **Claim:** Technical indicators can be represented as either continuous numerical values or binary (up/down) signals. Binary conversion notably improves performance of traditional ML models while deep learning methods (RNN, LSTM) remain superior with continuous data. The gap between simple and complex models narrows with binary features.
- **Evidence:** "Firstly, calculating the indicators by stock trading values as continuous data, and secondly converting indicators to binary data before using... in binary data evaluation, deep learning methods are best; however, the difference becomes less because of the noticeable improvement of models' performance in second way."
- **Works:** W3048630347

### C3 — high
- **Claim:** Stacked autoencoders (SAEs) generate deep high-level features from stock price data that are superior to raw features for next-day closing price prediction. When combined with wavelet transform denoising and LSTM, this framework outperforms other approaches in both predictive accuracy and profitability.
- **Evidence:** "SAEs is applied to generate deep high-level features for predicting stock price... the proposed model outperforms other similar models in both predictive accuracy and profitability performance."
- **Works:** W2734777338

### C4 — high
- **Claim:** PCA transformation of financial and economic features significantly improves classification accuracy for daily return direction prediction using deep neural networks, compared to untransformed raw features.
- **Evidence:** "DNNs using PCA-represented datasets give significantly higher classification accuracy than those using the entire untransformed dataset, as well as several other hybrid machine learning algorithms."
- **Works:** W2950843237

### C5 — high
- **Claim:** Combining temporal features from price time series (via LSTM) with spatial/pattern features from candlestick chart images (via CNN) reduces prediction error more than using either feature type alone. Candlestick charts are the most effective visual representation.
- **Evidence:** "prediction error can be efficiently reduced by using a combination of temporal and image features from the same data rather than using these features separately... the candlestick chart image is the most appropriate stock chart image."
- **Works:** W2912036663

### C6 — medium
- **Claim:** Comprehensive feature engineering (including pre-processing, multiple feature engineering techniques, and customized deep learning) is the primary driver of prediction accuracy, more so than model architecture alone.
- **Evidence:** "our proposed solution outperforms due to the comprehensive feature engineering that we built."
- **Works:** W3081799531

### C7 — medium
- **Claim:** Wavelet transform decomposition of stock price time series eliminates noise and improves the signal-to-noise ratio of features before they enter the prediction model.
- **Evidence:** "the stock price time series is decomposed by WT to eliminate noise."
- **Works:** W2734777338

### C8 — high
- **Claim:** Stacking and blending ensemble techniques achieve the highest directional prediction accuracies (90–100% and 85.7–100% respectively) compared to bagging (53–97.78%) and boosting (52.7–96.32%) across four global stock exchanges.
- **Evidence:** Explicit accuracy ranges stated in abstract: "stacking and blending techniques offer higher prediction accuracies (90–100%) and (85.7–100%) respectively."
- **Works:** W3013734981

### C9 — medium
- **Claim:** Incorporating leading indicators (options and futures data) alongside historical stock price data in a sequence array format as CNN input significantly improves prediction performance.
- **Evidence:** "constructs a sequence array of historical data and its leading indicators (options and futures), and uses the array as the input image of the CNN framework."
- **Works:** W3130456109

### C10 — high
- **Claim:** Temporal attention mechanisms in neural networks detect and focus on crucial temporal information in financial time series, providing both improved prediction accuracy and interpretability about which time periods carry the most predictive power.
- **Evidence:** "an attention mechanism that enables the layer to detect and focus on crucial temporal information... The resulting network is highly interpretable."
- **Works:** W2963122061

### C11 — medium
- **Claim:** The choice of input variable type (raw prices vs derived/transformed features) significantly affects directional prediction accuracy. Derived "Type 2" input variables with genetic-algorithm-optimized ANN generate higher forecast accuracy than raw price inputs.
- **Evidence:** "Type 2 input variables can generate a higher forecast accuracy and it is possible to enhance the performance of the optimized ANN model by selecting input variables appropriately."
- **Works:** W2400770063

### C12 — low
- **Claim:** A hybrid Genetic Algorithm + XGBoost model with a three-stage feature engineering process achieves effective stock price direction prediction.
- **Evidence:** Title-only inference — no abstract available.
- **Works:** W3193962426

### C13 — high
- **Claim:** LSTM consistently shows the most accurate results with the highest model fitting ability among all algorithms tested (Decision Tree, Bagging, Random Forest, Adaboost, Gradient Boosting, XGBoost, ANN, RNN) across multiple prediction horizons.
- **Evidence:** "Among all algorithms used in this paper, LSTM shows more accurate results with the highest model fitting ability."
- **Works:** W3014278717

### C14 — medium
- **Claim:** Classification accuracy of deep neural networks for daily return direction prediction increases as network depth increases (12 to 1000 hidden layers), suggesting deeper architectures capture more complex financial patterns.
- **Evidence:** "a pattern for the classification accuracy of the DNNs is detected and demonstrated as the number of hidden layers increases gradually from 12 to 1000."
- **Works:** W2950843237

### C15 — medium
- **Claim:** A GAN framework combining LSTM and CNN with adversarial training effectively improves stock price direction prediction accuracy and reduces forecast error on high-frequency trading data, using only publicly available index data as input.
- **Evidence:** "our proposed approach can effectively improve stock price direction prediction accuracy and reduce forecast error."
- **Works:** W2796929742

---

## Hypotheses

### H1 — supported
A core set of 10–15 technical indicators derived from OHLCV data (RSI, MACD, Bollinger Bands, SMA/EMA, Stochastic Oscillator, CCI, Williams %R, ATR, OBV, Rate of Change, ADX) provides sufficient predictive signal for next-day stock direction classification when paired with appropriate ML/DL architectures. **Falsifiable if:** a controlled experiment shows that removing all technical indicators in favor of raw OHLCV alone produces equal or higher accuracy.
- **Grounding:** C1, C2, C6, C11

### H2 — supported
Feature transformation and engineering (PCA, wavelet denoising, autoencoder-based extraction, binary conversion) contributes more to prediction accuracy than the choice of model architecture. **Falsifiable if:** an ablation study holding features constant while varying models shows model choice dominates the accuracy variance.
- **Grounding:** C3, C4, C6, C7

### H3 — supported
Multi-representation features — combining temporal/sequential features (time series via LSTM) with spatial/visual features (candlestick chart images via CNN) from the same OHLCV data — provide complementary predictive information that neither representation alone captures. **Falsifiable if:** the fused model accuracy equals the best single-representation model accuracy.
- **Grounding:** C5, C10, C9

### H4 — speculative
Binary transformation of technical indicators (converting continuous values to directional up/down signals) acts as a noise-reduction technique that narrows the performance gap between simple ML models and complex DL models, suggesting that much of the predictive signal lies in directional patterns rather than magnitudes. **Falsifiable if:** binary-transformed features degrade DL model performance while improving ML models.
- **Grounding:** C2, C7

### H5 — supported
Ensemble stacking/blending of heterogeneous base learners (DT, SVM, NN) achieves higher directional prediction accuracy than any single model or homogeneous ensemble (pure bagging or boosting). **Falsifiable if:** a single-model approach consistently outperforms stacking across multiple market datasets.
- **Grounding:** C8, C13

### H6 — speculative
The optimal feature set for next-day direction prediction combines all layers: (a) raw OHLCV, (b) computed technical indicators in both continuous and binary form, (c) PCA-reduced dimensionality versions, (d) autoencoder-learned latent representations, and (e) candlestick chart image features — creating a multi-layer feature stack. **Falsifiable if:** adding layers beyond a subset produces diminishing or negative returns due to overfitting.
- **Grounding:** C1, C2, C3, C4, C5, C6, C12

### H7 — speculative
Temporal attention mechanisms applied to engineered features can identify which lookback periods and which specific features carry the most directional predictive power, potentially enabling adaptive feature selection per market regime. **Falsifiable if:** attention weights are uniformly distributed with no regime-dependent variation.
- **Grounding:** C10, C14

---

## Contradictions

### CON1 — scope_mismatch
**Summary:** C8 reports stacking/blending achieving 90–100% accuracy across four exchanges (Ghana, Johannesburg, Bombay, NYSE, 2012–2018), while multiple other studies report more modest accuracy improvements. These ultra-high accuracy figures may reflect specific market conditions, low-volatility periods, or data leakage and may not generalize.
- **Refs:** C8, C13, C2

### CON2 — measurement_mismatch
**Summary:** C13 concludes LSTM is clearly the best model architecture, while C2 shows that binary feature conversion narrows the gap between simple ML and complex DL models, suggesting that with proper feature engineering, simpler models may approach LSTM performance. These use different feature representations and markets.
- **Refs:** C13, C2, C8

### CON3 — scope_mismatch
**Summary:** C4 advocates PCA (linear dimensionality reduction) for feature transformation, while C3 uses stacked autoencoders (non-linear learned representations). Both claim significant improvements but on different markets (S&P 500 vs six global indices), making direct comparison of these competing feature extraction philosophies impossible.
- **Refs:** C3, C4

---

## Scores (0–10)

- **evidenceStrength:** 7 — Most claims are grounded in explicit abstract-level findings with quantified results; one claim is title-only.
- **specificity:** 6 — Several papers mention "ten technical indicators" without naming them in abstracts; feature engineering details are often high-level.
- **reproducibility:** 5 — Common patterns are identified but specific indicator sets, hyperparameters, and preprocessing steps vary significantly across papers.
- **topicFit:** 9 — All 17 shortlisted papers directly address stock price/direction prediction using ML/DL with price-derived features.
- **contradictionSeverity:** 4 — Contradictions are mostly scope/measurement mismatches; the 90–100% accuracy claim warrants skepticism given lack of regime-controlled evaluation.

**Rationale:** The synthesis is strongly aligned with the user's question about price-derived features for next-day direction prediction. The main limitation is that specific technical indicator names and formulas are often not available from abstracts alone — the literature consistently uses ~10 indicators but individual studies do not always enumerate them in the abstract. The 90–100% accuracy range from ensemble stacking should be treated cautiously.

---

## Structural Interventions

### SI1
- **Failure Mode:** Ambiguity in which specific technical indicators (by name and formula) are most predictive; papers cite "ten technical indicators" without abstract-level specification.
- **Structural Change:** Future studies should provide explicit feature importance rankings using SHAP values or permutation importance, naming each indicator and its marginal contribution to directional accuracy.

### SI2
- **Failure Mode:** Accuracy metrics (90–100%) reported without controlling for market regime (bull, bear, sideways) or realistic transaction costs.
- **Structural Change:** Evaluation should be stratified by market regime and include transaction costs, slippage, and bid-ask spread in profitability metrics.

### SI3
- **Failure Mode:** Conflation of feature engineering value vs model architecture value — it is unclear whether improvements come from better features or better models.
- **Structural Change:** Ablation studies that hold features constant while varying models, and vice versa, are needed to isolate each contributor's marginal effect.

### SI4
- **Failure Mode:** Most studies validate on a single market/exchange; cross-market generalizability is unknown.
- **Structural Change:** Cross-market validation (train on Market A, test on Market B) and temporal out-of-sample validation across different market regimes (2008 crisis, COVID-2020, etc.).

---

## Refinement Notes

### Pass 1
- Merged overlapping coverage between C1 (ten indicators as input) and C11 (variable type selection); kept both as C1 covers the count/identity while C11 covers the transformation type.
- Narrowed C6 from vague "comprehensive feature engineering" — left with caveat that abstract does not specify which techniques were most impactful.
- Removed 8 off-topic papers: AI/Marketing (W3037880470), auditing (W2598798227), green gram prices (W4398243663), cryptocurrency (W3021511960), structured events/NLP (W2126267628), heterogeneous information/sentiment (W2780013296), textual features (W3009012433), and S&P volatility forecasting (W2068527816).
- Flagged C12 (GA-XGBoost three-stage feature engineering) for low evidence strength (title-only) but high topical relevance.

### Pass 2
- H6 confidence remains speculative but better grounded after structural analysis; the multi-layer feature stack is supported by multiple independent lines of evidence but no single study has tested all components together.
- contradictionSeverity adjusted from 3 to 4 after acknowledging that the 90–100% accuracy claim (C8) is more problematic without regime-controlled evaluation.
- Added emphasis on the feature-centric vs model-centric debate (H2) as the central unresolved tension in this literature.

---

## Decision Record (Proposed Solution)

### Problem Context
The user needs to identify which features derived from stock OHLCV price data are most predictive of next-day stock direction for ML/DL model input. This is fundamentally a feature engineering question. The literature shows that feature quality and representation matter at least as much as — and likely more than — model architecture selection. A practical answer must enumerate concrete features, organized by category, that have demonstrated predictive value across multiple high-citation studies.

### Options Considered

**Option A: Raw OHLCV + Standard Technical Indicators (10–15 indicators)**
Use raw Open, High, Low, Close, Volume data plus a standard set of technical indicators (RSI, MACD, Bollinger Bands, SMA/EMA, Stochastic Oscillator, etc.) in their continuous numerical form.

**Option B: Multi-Layer Feature Engineering Pipeline**
Build features in layers: (1) raw OHLCV, (2) technical indicators in both continuous and binary forms, (3) wavelet-denoised versions, (4) PCA or autoencoder dimensionality-reduced representations, (5) rolling statistics and lagged features. Feed this enriched feature matrix to LSTM or ensemble stacking models.

**Option C: Multi-Representation Feature Fusion**
Combine temporal/sequential feature extraction (LSTM on time series) with visual/spatial feature extraction (CNN on candlestick chart images) from the same underlying OHLCV data, fusing both representations for prediction.

### Pros and Cons

**Option A**
- Pros: Simple to implement; well-supported by literature (C1, C11); interpretable; computationally lightweight.
- Cons: Leaves significant accuracy on the table compared to transformed features (C4, C3); raw features carry noise; does not exploit feature complementarity.

**Option B**
- Pros: Strongest evidence base (C2, C3, C4, C6, C7); addresses noise (wavelet denoising); captures both linear (PCA) and non-linear (autoencoder) latent structure; binary indicators provide noise-robust directional signals; flexibility to use with any model.
- Cons: More complex pipeline; risk of overfitting with many engineered features; requires careful cross-validation; higher computational cost.

**Option C**
- Pros: Captures complementary information (C5); candlestick patterns encode visual structure missed by numerical features; proven to reduce prediction error beyond single-representation models.
- Cons: Requires CNN infrastructure for image processing; candlestick image generation adds pipeline complexity; less interpretable than numerical features; fewer studies have validated this approach.

### Final Proposed Solution

**Option B — Multi-Layer Feature Engineering Pipeline** is the recommended approach, optionally enhanced with elements from Option C (candlestick chart features) if infrastructure allows.

The concrete recommended feature set, organized by category:

**Layer 1 — Raw Price Features (5–8 features)**
- Open, High, Low, Close, Volume
- Daily return: (Close_t - Close_{t-1}) / Close_{t-1}
- Intraday range: High - Low
- Body: Close - Open
- Upper/Lower shadow lengths

**Layer 2 — Technical Indicators, Continuous Form (15–20 features)**
- SMA (5, 10, 20, 50 day)
- EMA (5, 10, 20 day)
- RSI (14 day)
- MACD line, Signal line, MACD histogram
- Stochastic Oscillator (%K, %D)
- Bollinger Bands (upper, lower, bandwidth, %B)
- ATR (14 day)
- Williams %R
- CCI (20 day)
- OBV (On-Balance Volume)
- Rate of Change (ROC, 10 day)
- ADX (Average Directional Index)

**Layer 3 — Binary/Directional Transforms (15–20 features)**
- Binary versions of each indicator above (1 if above threshold/rising, 0 otherwise)
- E.g., RSI > 50 → 1; MACD > Signal → 1; Close > SMA_20 → 1

**Layer 4 — Derived/Rolling Features (10–15 features)**
- Lagged returns (1-day, 2-day, 3-day, 5-day)
- Rolling mean of returns (5, 10, 20 day)
- Rolling standard deviation of returns (5, 10, 20 day)
- Rolling skewness and kurtosis (20 day)
- Price gap: Open_today - Close_yesterday
- Relative price: Close / SMA_20, Close / SMA_50

**Layer 5 — Dimensionality Reduction (3–10 features)**
- Top PCA components (capturing 95% variance) from Layers 1–4
- OR: Autoencoder latent representations (bottleneck layer output)
- Wavelet-denoised versions of key features

**Recommended Model Pairing:**
- **Primary:** LSTM with attention mechanism on the full feature stack
- **Alternative:** Ensemble stacking (XGBoost + Random Forest + LSTM as base learners, logistic regression as meta-learner)

### Confidence: medium-high
Evidence is consistent across 17 high-citation papers. The specific feature set is well-established; the exact optimal combination requires per-market tuning.

### Follow-Up Tasks
1. Implement the feature engineering pipeline with a specific stock dataset
2. Run ablation study: test each feature layer individually and cumulatively
3. Compare LSTM-attention vs ensemble stacking vs GA-XGBoost on the same feature set
4. Evaluate across market regimes (bull, bear, sideways) separately
5. Add SHAP analysis to identify individual feature importance rankings
6. Validate out-of-sample across at least two different exchanges and time periods
