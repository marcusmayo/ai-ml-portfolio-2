# Known Issues and Limitations

## Sentiment Analysis in Interview Context

### Issue Description
The sentiment analysis component uses RoBERTa-based word-level sentiment detection, which may produce unexpected results in interview contexts.

### Technical Details
- **Model:** cardiffnlp/twitter-roberta-base-sentiment-latest
- **Behavior:** Analyzes sentiment of individual words/phrases
- **Scale:** Returns 0-100% positive/negative/neutral scores

### Why This Occurs
Interview conversations often involve:
- Discussing past challenges, failures, or weaknesses (negative words)
- Describing problem-solving scenarios (negative context, positive resolution)
- Professional framing of difficult situations

**Example:**
```
Transcript: "They went through corporate downsizing, so I pivoted into AI engineering"
Detected Sentiment: 0% positive, 99.96% negative
Actual Context: Professional, confident discussion of career transition
```

The model correctly identifies "downsizing" as negative, but cannot detect that the speaker is:
- Calmly describing past events (not currently distressed)
- Demonstrating adaptability and resilience
- Speaking with professional confidence

### Impact
- **Short interviews (60 sec):** May show accurate sentiment if uniformly positive content
- **Long interviews (20+ min):** Average sentiment often 40-60% due to mixed content discussion
- **Interviews discussing challenges:** Will show lower sentiment despite strong performance

### Current Workaround
The overall interview score uses an ensemble approach where sentiment is only 25% of the total:
- Sentiment: 25%
- Toxicity: 25% (inverted)
- Competency: 30%
- Keywords: 20%

This prevents sentiment from dominating the final score.

### Future Improvements (Planned)
Consider replacing or supplementing sentiment with interview-specific metrics:
1. **Confidence Level:** Vocal tone analysis, hesitation detection
2. **Communication Clarity:** Articulation, structure, coherence scoring
3. **Professionalism:** Appropriate language and demeanor assessment
4. **Answer Relevance:** How well responses match questions

### Validation
The sentiment calculation is working as designed - it correctly computes average sentiment across segments. The limitation is in the applicability of word-level sentiment to interview analysis, not in the implementation.

**Test Results:**
- Short positive interview: 100% sentiment ✓
- Mixed content interview: 53% sentiment ✓ (accurately reflects word-level sentiment)
- Calculation verified with debug logging ✓

---
**Last Updated:** 2025-01-03
**Status:** Documented, will address in future iteration
