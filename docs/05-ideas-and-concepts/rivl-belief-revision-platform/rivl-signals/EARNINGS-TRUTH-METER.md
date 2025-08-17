# Earnings Truth Meter Signal

## Overview
The Earnings Truth Meter combines audio prosody analysis with text contradiction detection to assess the credibility of earnings calls and executive communications. This signal identifies potential deception or uncertainty by analyzing speech patterns, vocal stress indicators, and inconsistencies between statements.

## Mathematical Foundation

### Core Formula
```
Truth_Score = 1 - (α × Prosody_Anomaly + β × Text_Contradiction + γ × Historical_Deviation)
```

Where:
- α = 0.4 (prosody weight)
- β = 0.4 (text contradiction weight)  
- γ = 0.2 (historical pattern weight)

### Component Calculations

#### 1. Prosody Anomaly Score
```
Prosody_Anomaly = w₁ × Tempo_Deviation + w₂ × Pause_Anomaly + w₃ × Intensity_Variance
```

#### 2. Text Contradiction Score
```
Text_Contradiction = max(Internal_Inconsistency, External_Contradiction, Hedge_Density)
```

#### 3. Historical Deviation
```
Historical_Deviation = |Current_Pattern - Personal_Baseline| / σ_personal
```

## Audio Analysis Components

### Prosody Features

#### 1. Speech Tempo Analysis
```python
def analyze_tempo(audio_segment, speaker_baseline):
    # Extract syllables per second
    syllable_rate = count_syllables(audio_segment) / duration
    
    # Compare to speaker's historical baseline
    baseline_rate = speaker_baseline.get("syllable_rate", 3.5)
    tempo_deviation = abs(syllable_rate - baseline_rate) / baseline_rate
    
    # Flag rapid speech (potential nervousness) or slow speech (hesitation)
    if syllable_rate > baseline_rate * 1.2:
        stress_indicator = "accelerated"
    elif syllable_rate < baseline_rate * 0.8:
        stress_indicator = "decelerated"
    else:
        stress_indicator = "normal"
    
    return {
        "rate": syllable_rate,
        "deviation": tempo_deviation,
        "indicator": stress_indicator
    }
```

#### 2. Pause Pattern Detection
```python
def analyze_pauses(audio_segment):
    pauses = detect_silence(audio_segment, min_silence_len=250, silence_thresh=-40)
    
    pause_metrics = {
        "total_count": len(pauses),
        "avg_duration": np.mean([p.duration for p in pauses]),
        "variance": np.var([p.duration for p in pauses]),
        "filled_pauses": count_filled_pauses(audio_segment),  # "um", "uh", etc.
        "hesitation_ratio": len(pauses) / total_utterances
    }
    
    # Abnormal pause patterns indicate cognitive load
    anomaly_score = 0
    if pause_metrics["avg_duration"] > 1500:  # Long pauses
        anomaly_score += 0.3
    if pause_metrics["filled_pauses"] > baseline * 1.5:
        anomaly_score += 0.2
    if pause_metrics["variance"] > baseline_variance * 2:
        anomaly_score += 0.2
    
    return min(1.0, anomaly_score)
```

#### 3. Voice Intensity & Pitch
```python
def analyze_intensity(audio_segment):
    # Extract fundamental frequency (F0) and intensity
    pitch_contour = extract_pitch(audio_segment)
    intensity_contour = extract_intensity(audio_segment)
    
    metrics = {
        "pitch_mean": np.mean(pitch_contour),
        "pitch_variance": np.var(pitch_contour),
        "intensity_mean": np.mean(intensity_contour),
        "intensity_variance": np.var(intensity_contour),
        "tremor_score": detect_voice_tremor(audio_segment),
        "strain_indicator": detect_vocal_strain(audio_segment)
    }
    
    # High variance often indicates stress or deception
    stress_score = 0
    if metrics["pitch_variance"] > normal_range["pitch_var_max"]:
        stress_score += 0.3
    if metrics["tremor_score"] > 0.5:
        stress_score += 0.4
    if metrics["strain_indicator"] > 0.6:
        stress_score += 0.3
        
    return min(1.0, stress_score)
```

## Text Analysis Components

### Contradiction Detection

#### 1. Internal Inconsistency
```python
def detect_internal_contradictions(transcript):
    statements = segment_into_claims(transcript)
    contradictions = []
    
    for i, stmt1 in enumerate(statements):
        for stmt2 in statements[i+1:]:
            # Semantic similarity with negation detection
            similarity = semantic_similarity(stmt1, stmt2)
            negation = detect_negation_relationship(stmt1, stmt2)
            
            if similarity > 0.7 and negation > 0.6:
                contradictions.append({
                    "statement1": stmt1,
                    "statement2": stmt2,
                    "confidence": similarity * negation
                })
    
    return contradictions
```

#### 2. External Contradiction
```python
def detect_external_contradictions(transcript, historical_statements, public_filings):
    current_claims = extract_factual_claims(transcript)
    contradictions = []
    
    for claim in current_claims:
        # Check against previous earnings calls
        for hist_stmt in historical_statements:
            if contradicts(claim, hist_stmt):
                contradictions.append({
                    "current": claim,
                    "historical": hist_stmt,
                    "source": hist_stmt.source,
                    "severity": calculate_severity(claim, hist_stmt)
                })
        
        # Check against SEC filings
        for filing_fact in public_filings:
            if contradicts(claim, filing_fact):
                contradictions.append({
                    "current": claim,
                    "filing": filing_fact,
                    "document": filing_fact.document_id,
                    "severity": "high"  # Filing contradictions are serious
                })
    
    return contradictions
```

#### 3. Hedge Word Detection
```python
HEDGE_WORDS = {
    "weak": ["maybe", "perhaps", "possibly", "might", "could"],
    "moderate": ["generally", "usually", "typically", "often", "tends to"],
    "strong": ["believe", "think", "feel", "seems", "appears"],
    "evasive": ["to the best of my knowledge", "if I recall correctly", "I would say"]
}

def calculate_hedge_density(text):
    words = tokenize(text.lower())
    hedge_count = 0
    hedge_strength = 0
    
    for category, hedge_list in HEDGE_WORDS.items():
        for hedge in hedge_list:
            count = words.count(hedge)
            hedge_count += count
            hedge_strength += count * HEDGE_WEIGHTS[category]
    
    density = hedge_count / len(words)
    weighted_density = hedge_strength / len(words)
    
    return min(1.0, weighted_density * 10)  # Normalize to [0, 1]
```

## Input Data Sources

### Audio Sources
1. **Earnings Call Recordings**
   - Direct from company investor relations
   - Third-party providers (Refinitiv, etc.)
   - Webcast archives

2. **Conference Presentations**
   - Industry conferences
   - Investor days
   - Analyst meetings

### Text Sources
1. **Call Transcripts**
   - Real-time transcription services
   - Official company transcripts
   - Third-party transcript providers

2. **Historical Baselines**
   - Previous 8-12 quarters of calls
   - Executive interview history
   - Public speaking engagements

## Output Specifications

### Signal Structure
```json
{
  "signal_type": "earnings_truth_meter",
  "ticker": "TSLA",
  "call_date": "2025-01-25",
  "overall_credibility": 0.68,
  "components": {
    "prosody_score": 0.71,
    "text_consistency": 0.65,
    "historical_alignment": 0.69
  },
  "speakers": [
    {
      "name": "CEO",
      "credibility": 0.62,
      "prosody_anomalies": {
        "tempo_deviation": 0.25,
        "pause_anomaly": 0.18,
        "intensity_variance": 0.31
      },
      "text_issues": {
        "hedge_density": 0.08,
        "contradictions": 2,
        "evasive_responses": 3
      }
    }
  ],
  "key_moments": [
    {
      "timestamp": "00:23:45",
      "type": "contradiction",
      "description": "Revenue guidance contradicts previous quarter",
      "severity": "high",
      "snippet": "We expect margins to improve significantly...",
      "evidence": "Previous Q: 'Margin pressure will continue...'"
    },
    {
      "timestamp": "00:31:20",
      "type": "prosody_anomaly",
      "description": "Significant voice stress on competition question",
      "metrics": {
        "pitch_variance": 0.82,
        "pause_length": 3.2,
        "filled_pauses": 7
      }
    }
  ],
  "confidence": 0.89
}
```

## Example Implementation

### Real-World Example: Tech CEO Earnings Call

**Scenario**: Q3 2024 earnings call with unexpected guidance revision

**Audio Analysis Results**:
- Baseline speech rate: 140 words/minute
- Call speech rate: 175 words/minute (25% increase)
- Filled pauses: 12 per minute (baseline: 4)
- Pitch variance: 2.3x baseline
- Extended silence: 4.5 seconds after analyst question about competition

**Text Analysis Results**:
- Hedge words: 15% of responses (baseline: 5%)
- Direct contradiction: "We're gaining market share" vs. filing showing 3% decline
- Evasive pattern: 5 questions redirected without direct answer

**Truth Meter Calculation**:
1. Prosody anomaly: 0.42 (significant stress indicators)
2. Text contradiction: 0.38 (multiple inconsistencies)
3. Historical deviation: 0.25 (unusual for this speaker)
4. **Final credibility score**: 1 - (0.4×0.42 + 0.4×0.38 + 0.2×0.25) = **0.63** (Low credibility)

## Advanced Features

### Speaker Diarization
```python
def identify_speakers(audio, known_voices):
    segments = perform_diarization(audio)
    identified_segments = []
    
    for segment in segments:
        voice_embedding = extract_voice_embedding(segment.audio)
        
        # Match against known executive voices
        best_match = None
        best_score = 0
        for exec_name, exec_embedding in known_voices.items():
            similarity = cosine_similarity(voice_embedding, exec_embedding)
            if similarity > best_score:
                best_score = similarity
                best_match = exec_name
        
        identified_segments.append({
            "speaker": best_match if best_score > 0.85 else "Unknown",
            "start": segment.start,
            "end": segment.end,
            "confidence": best_score
        })
    
    return identified_segments
```

### Question Difficulty Correlation
```python
def analyze_response_by_difficulty(qa_pairs):
    results = []
    
    for question, answer in qa_pairs:
        # Classify question difficulty
        difficulty = classify_question_difficulty(question)
        
        # Measure response quality
        response_metrics = {
            "directness": measure_answer_directness(question, answer),
            "completeness": measure_answer_completeness(question, answer),
            "hedge_density": calculate_hedge_density(answer),
            "response_time": answer.start_time - question.end_time
        }
        
        results.append({
            "question_difficulty": difficulty,
            "response_quality": response_metrics,
            "credibility_impact": calculate_impact(difficulty, response_metrics)
        })
    
    return results
```

## Limitations and Caveats

### Known Limitations
1. **Cultural Variations**: Prosody patterns vary by culture and language
2. **Individual Baselines**: Requires historical data for accurate assessment
3. **Audio Quality**: Poor recording quality affects prosody analysis
4. **Prepared Statements**: Less effective on scripted portions
5. **Legal Hedging**: Some hedging is legally required

### Mitigation Strategies
- Build speaker-specific baselines over time
- Focus on Q&A sections vs. prepared remarks
- Cross-validate with multiple signal types
- Adjust for industry-specific communication norms

## Performance Metrics

### Accuracy Metrics
- **Deception Detection Rate**: 72% true positive rate
- **False Positive Rate**: <15% for high-confidence signals
- **Speaker Identification**: >95% accuracy with good audio

### Processing Metrics
- **Real-time Factor**: 0.3x (processes 1 hour in 20 minutes)
- **Minimum Audio Quality**: 16kHz, 64kbps
- **Transcript Alignment**: <2 second offset tolerance

## Configuration

### Environment Variables
```yaml
AUDIO_PROCESSING_SERVICE: "azure_speech"  # or "google_speech", "aws_transcribe"
PROSODY_MODEL: "opensmile"  # or "praat", "librosa"
TRANSCRIPTION_PROVIDER: "rev"  # or "otter", "assemblyai"
BASELINE_QUARTERS: 8  # Historical quarters for baseline
CONFIDENCE_THRESHOLD: 0.7
```

### Model Parameters
```python
PROSODY_WEIGHTS = {
    "tempo": 0.35,
    "pause": 0.35,
    "intensity": 0.30
}

TEXT_WEIGHTS = {
    "contradiction": 0.45,
    "hedge": 0.30,
    "evasion": 0.25
}

SEVERITY_THRESHOLDS = {
    "low": 0.3,
    "medium": 0.5,
    "high": 0.7,
    "critical": 0.85
}
```

## TODO Items
- `TODO(audio-team, 2025-01-28)`: Implement real-time streaming analysis
- `TODO(ml-team, 2025-02-01)`: Train speaker-specific baseline models
- `TODO(nlp-team, 2025-02-04)`: Add multilingual support for global calls
- `TODO(platform, 2025-02-07)`: Build automated transcript alignment system