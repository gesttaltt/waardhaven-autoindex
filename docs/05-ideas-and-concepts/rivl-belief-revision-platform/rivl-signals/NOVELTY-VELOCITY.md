# Novelty & Velocity (N&V) Signal

## Overview
The Novelty & Velocity signal measures the rate of new information generation and its propagation speed across multiple sources and languages. This signal identifies when genuinely new information enters the market and tracks how quickly it spreads, providing early detection of consensus-shifting events before they're fully priced in.

## Mathematical Foundation

### Core Formulas

#### Novelty Score
```
N = (1 - max_similarity) × information_density × source_credibility
```

#### Velocity Score
```
V = Δ(sources) / Δ(time) × language_spread × reach_factor
```

#### Combined N&V Score
```
N&V = α × N + β × V
```
Where α = 0.6, β = 0.4 (tunable based on investment horizon)

### Detailed Calculations

#### 1. Novelty Detection
```python
def calculate_novelty(document, historical_corpus, time_window=7):
    # Semantic embedding of new document
    doc_embedding = embed(document)
    
    # Compare against recent documents
    max_similarity = 0
    for hist_doc in historical_corpus.get_recent(days=time_window):
        similarity = cosine_similarity(doc_embedding, hist_doc.embedding)
        max_similarity = max(max_similarity, similarity)
    
    # Information density (entropy-based)
    info_density = calculate_entropy(document) / max_entropy
    
    # Source credibility weighting
    credibility = SOURCE_CREDIBILITY.get(document.source, 0.5)
    
    novelty = (1 - max_similarity) * info_density * credibility
    return min(1.0, novelty)  # Normalize to [0, 1]
```

#### 2. Velocity Measurement
```python
def calculate_velocity(original_story, time_window=24):
    propagation_events = []
    
    for hours_elapsed in range(1, time_window + 1):
        sources_count = count_sources_reporting(original_story, hours_elapsed)
        languages_count = count_languages(original_story, hours_elapsed)
        total_reach = sum_audience_reach(original_story, hours_elapsed)
        
        propagation_events.append({
            "time": hours_elapsed,
            "sources": sources_count,
            "languages": languages_count,
            "reach": total_reach
        })
    
    # Calculate velocity components
    source_velocity = calculate_derivative(propagation_events, "sources")
    language_spread = len(unique_languages) / len(MONITORED_LANGUAGES)
    reach_factor = log(total_reach) / log(MAX_POSSIBLE_REACH)
    
    velocity = source_velocity * language_spread * reach_factor
    return min(1.0, velocity)  # Normalize to [0, 1]
```

## Input Data Sources

### Primary News Sources
1. **GDELT Project**
   - Global news monitoring
   - 100+ languages
   - Real-time updates

2. **Financial News Feeds**
   - Reuters
   - Bloomberg (via API)
   - Financial Times
   - WSJ

3. **Regional Sources (LatAm Focus)**
   - Valor Econômico (Brazil)
   - El Financiero (Mexico)
   - La Nación (Argentina)
   - América Economía (Regional)

4. **Social Signals**
   - Twitter/X financial community
   - Reddit (r/investing, r/stocks)
   - LinkedIn thought leaders
   - Seeking Alpha

### Data Pipeline
```mermaid
graph LR
    A[News Sources] --> B[Language Detection]
    B --> C[Translation Service]
    C --> D[Deduplication Engine]
    D --> E[Novelty Scorer]
    E --> F[Velocity Tracker]
    F --> G[Signal Generator]
    G --> H[Evidence Linker]
```

## Deduplication Algorithm

### Semantic Deduplication
```python
class DeduplicationEngine:
    def __init__(self, similarity_threshold=0.85):
        self.threshold = similarity_threshold
        self.seen_stories = {}
        
    def is_duplicate(self, story):
        story_embedding = self.embed(story)
        
        for story_id, cached_embedding in self.seen_stories.items():
            similarity = cosine_similarity(story_embedding, cached_embedding)
            if similarity > self.threshold:
                return True, story_id
                
        # Not a duplicate - add to cache
        self.seen_stories[story.id] = story_embedding
        return False, None
```

## Output Specifications

### Signal Structure
```json
{
  "signal_type": "novelty_velocity",
  "ticker": "VALE",
  "novelty_score": 0.81,
  "velocity_score": 0.67,
  "combined_score": 0.75,
  "original_language": "pt-BR",
  "story_summary": "Brazilian mining giant announces unexpected CEO departure",
  "first_detection": {
    "source": "Valor Econômico",
    "timestamp": "2025-01-15T08:15:00Z",
    "url": "https://valor.globo.com/..."
  },
  "propagation": {
    "total_sources": 47,
    "languages": ["pt-BR", "en", "es", "zh"],
    "time_to_english": 35,  # minutes
    "peak_velocity_hour": 3,
    "estimated_reach": 12500000
  },
  "related_documents": [
    {
      "source": "Reuters",
      "timestamp": "2025-01-15T08:50:00Z",
      "similarity": 0.92,
      "language": "en"
    }
  ]
}
```

## Language Arbitrage

### Cross-Language Detection
```python
LANGUAGE_PRIORITIES = {
    "pt-BR": 1.2,  # Portuguese (Brazil) - high value for LatAm
    "es": 1.15,     # Spanish - regional priority
    "zh": 1.1,      # Chinese - early Asian indicators
    "en": 1.0,      # English - baseline
    "fr": 0.95,     # French
    "de": 0.95,     # German
}

def calculate_language_advantage(original_lang, time_to_english):
    priority = LANGUAGE_PRIORITIES.get(original_lang, 1.0)
    # Bonus for non-English origination with delayed translation
    if original_lang != "en" and time_to_english > 30:
        return priority * (1 + log(time_to_english) / 10)
    return priority
```

## Example Implementation

### Real-World Example: Brazilian Dam Safety News

**Timeline**:
- **T+0 min**: Local Brazilian outlet reports dam inspection concerns at VALE facility
- **T+15 min**: Story picked up by 3 regional Portuguese outlets
- **T+45 min**: First Spanish translation appears in Chilean media
- **T+90 min**: Reuters Brazil publishes English version
- **T+120 min**: Story reaches mainstream financial media

**Signal Calculation**:
1. **Novelty**: 0.91 (completely new information, no prior reports)
2. **Velocity**: 0.73 (rapid spread, multiple languages)
3. **Language advantage**: 1.35 (90-minute advantage from Portuguese)
4. **Combined N&V**: 0.91 × 0.6 + 0.73 × 0.4 = **0.84** (Strong signal)

## Information Density Measurement

### Entropy Calculation
```python
def calculate_entropy(text):
    # Tokenize and calculate term frequencies
    tokens = tokenize(text)
    freq_dist = FreqDist(tokens)
    
    # Calculate Shannon entropy
    entropy = 0
    total = len(tokens)
    for token, count in freq_dist.items():
        probability = count / total
        if probability > 0:
            entropy -= probability * log2(probability)
    
    # Normalize by theoretical maximum
    max_entropy = log2(len(freq_dist))
    return entropy / max_entropy if max_entropy > 0 else 0
```

## Limitations and Caveats

### Known Limitations
1. **Echo Chamber Effects**: Same story can appear novel due to rephrasing
2. **Translation Quality**: Machine translation may miss nuances
3. **Source Reliability**: Not all sources are equally credible
4. **Time Zone Bias**: Some markets naturally report earlier

### Mitigation Strategies
- Multi-model ensemble for similarity detection
- Human-in-the-loop for critical translations
- Dynamic source credibility scoring
- Time zone normalization for fair comparison

## Performance Metrics

### Quality Metrics
- **Deduplication Accuracy**: >95% for same-story detection
- **Translation Fidelity**: >90% semantic preservation
- **False Novelty Rate**: <5% (stories marked novel but aren't)

### Operational Metrics
- **Detection Latency**: <30 seconds from publication
- **Processing Throughput**: 10,000 articles/minute
- **Language Coverage**: 15 languages at launch

## Configuration

### Environment Variables
```yaml
GDELT_API_KEY: ${GDELT_API_KEY}
TRANSLATION_SERVICE: "deepl"  # or "google", "azure"
EMBEDDING_MODEL: "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
DEDUP_THRESHOLD: 0.85
NOVELTY_WINDOW_DAYS: 7
VELOCITY_WINDOW_HOURS: 24
```

### Source Credibility Weights
```python
SOURCE_CREDIBILITY = {
    # Tier 1 - Highest credibility
    "reuters": 1.0,
    "bloomberg": 1.0,
    "wsj": 0.95,
    "ft": 0.95,
    
    # Tier 2 - Regional leaders
    "valor_economico": 0.85,
    "el_financiero": 0.85,
    "nikkei": 0.85,
    
    # Tier 3 - Aggregators
    "seeking_alpha": 0.7,
    "marketwatch": 0.7,
    
    # Tier 4 - Social
    "twitter_verified": 0.6,
    "reddit": 0.5,
}
```

## Integration Points

### Downstream Consumers
- **Surprise Index**: Primary velocity input
- **Consensus Gap**: Information flow measurement
- **Alert System**: Real-time notifications

### Upstream Dependencies
- **Translation Service**: Multi-language support
- **Embedding Service**: Semantic similarity
- **Entity Resolution**: Company/ticker mapping

## TODO Items
- `TODO(data-team, 2025-01-20)`: Implement GDELT streaming API
- `TODO(ml-team, 2025-01-23)`: Train custom news similarity model
- `TODO(platform, 2025-01-26)`: Add Kafka for real-time processing
- `TODO(product, 2025-01-29)`: Define alerting thresholds by sector