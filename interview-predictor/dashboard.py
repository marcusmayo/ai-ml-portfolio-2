"""
Interview Predictor Dashboard
Main Streamlit application for analyzing interview transcripts and recordings
"""

import streamlit as st
import os
import json
from datetime import datetime
from pathlib import Path

# Import utility modules
from utils.asr_processor import ASRProcessor
from utils.nlp_analyzer import NLPAnalyzer
from utils.ensemble_scorer import EnsembleScorer


# Page configuration
st.set_page_config(
    page_title="Interview Predictor",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)


def initialize_session_state():
    """Initialize session state variables"""
    if 'analysis_complete' not in st.session_state:
        st.session_state.analysis_complete = False
    if 'results' not in st.session_state:
        st.session_state.results = None


def save_uploaded_file(uploaded_file, upload_dir="data/uploads"):
    """Save uploaded file to disk"""
    Path(upload_dir).mkdir(parents=True, exist_ok=True)
    file_path = os.path.join(upload_dir, uploaded_file.name)
    
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    return file_path


def load_sample_transcript(sample_name):
    """Load a sample transcript from data/sample/"""
    sample_path = f"data/sample/{sample_name}"
    
    if os.path.exists(sample_path):
        with open(sample_path, 'r') as f:
            return f.read()
    return None


def main():
    """Main application function"""
    initialize_session_state()
    
    # Header
    st.title("🎯 Interview Predictor")
    st.markdown("""
    **Analyze interview transcripts and recordings to predict outcomes using ensemble ML techniques.**
    
    Upload an interview recording or transcript, and get instant feedback on interview performance.
    """)
    
    # Sidebar configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Model selection
        st.subheader("ASR Model")
        whisper_model = st.selectbox(
            "Whisper Model Size",
            ["tiny", "base", "small", "medium"],
            index=1,
            help="Larger models are more accurate but slower"
        )
        
        st.markdown("---")
        
        # Sample data option
        st.subheader("📄 Try Sample Data")
        use_sample = st.checkbox("Use sample transcript")
        
        if use_sample:
            sample_choice = st.radio(
                "Select sample:",
                ["Positive Interview", "Negative Interview"]
            )
        
        st.markdown("---")
        
        # About section
        with st.expander("ℹ️ About"):
            st.markdown("""
            **Features:**
            - Speech-to-text transcription
            - Sentiment analysis
            - Toxicity detection
            - Competency assessment
            - Ensemble prediction
            
            **Prediction Categories:**
            - **Likely** (≥70%): Strong signals
            - **Unlikely** (<40%): Weak signals
            - **Inconclusive** (40-70%): Mixed signals
            
            **Disclaimer:** This is a self-coaching tool, not a hiring decision tool.
            """)
    
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("📤 Input")
        
        # Input method selection
        input_method = st.radio(
            "Choose input method:",
            ["Upload Audio File", "Paste Transcript"],
            horizontal=True
        )
        
        transcript_text = None
        audio_file_path = None
        
        if input_method == "Upload Audio File":
            st.info("⚠️ Audio transcription requires significant processing time (1-3 minutes)")
            uploaded_audio = st.file_uploader(
                "Upload interview recording",
                type=["mp3", "wav", "m4a"],
                help="Supported formats: MP3, WAV, M4A"
            )
            
            if uploaded_audio:
                audio_file_path = save_uploaded_file(uploaded_audio)
                st.success(f"✅ File uploaded: {uploaded_audio.name}")
        
        else:  # Paste Transcript
            if use_sample:
                # Load sample
                sample_file = "interview_transcript_positive.txt" if sample_choice == "Positive Interview" else "interview_transcript_negative.txt"
                sample_text = load_sample_transcript(sample_file)
                
                if sample_text:
                    transcript_text = st.text_area(
                        "Interview transcript:",
                        value=sample_text,
                        height=300,
                        help="Edit the sample or paste your own transcript"
                    )
                else:
                    st.error("Sample file not found")
                    transcript_text = st.text_area("Interview transcript:", height=300)
            else:
                transcript_text = st.text_area(
                    "Paste interview transcript:",
                    height=300,
                    placeholder="Paste the full interview conversation here..."
                )
        
        # Analyze button
        analyze_button = st.button("🔍 Analyze Interview", type="primary", use_container_width=True)
    
    with col2:
        st.header("📊 Results")
        
        if analyze_button:
            # Validation
            if not transcript_text and not audio_file_path:
                st.error("❌ Please provide an interview transcript or audio file")
                return
            
            # Processing
            with st.spinner("🤖 Processing interview..."):
                try:
                    # Step 1: Get transcript
                    if audio_file_path:
                        st.info("🎤 Transcribing audio (this may take 1-3 minutes)...")
                        asr = ASRProcessor(model_size=whisper_model)
                        transcription_result = asr.transcribe_audio(audio_file_path)
                        transcript_text = transcription_result["text"]
                        st.success("✅ Transcription complete")
                    
                    # Step 2: NLP Analysis
                    st.info("🧠 Running NLP analysis...")
                    nlp_analyzer = NLPAnalyzer()
                    analysis = nlp_analyzer.analyze_all(transcript_text)
                    st.success("✅ NLP analysis complete")
                    
                    # Step 3: Ensemble Scoring
                    st.info("📊 Calculating ensemble score...")
                    scorer = EnsembleScorer()
                    results = scorer.calculate_ensemble_score(analysis)
                    st.success("✅ Analysis complete!")
                    
                    # Store results
                    st.session_state.results = results
                    st.session_state.analysis_complete = True
                    
                except Exception as e:
                    st.error(f"❌ Error during analysis: {str(e)}")
                    st.exception(e)
                    return
        
        # Display results
        if st.session_state.analysis_complete and st.session_state.results:
            results = st.session_state.results
            
            # Prediction display
            prediction = results["prediction"]
            score = results["score"]
            
            # Color coding
            if prediction == "Likely":
                color = "green"
                emoji = "✅"
            elif prediction == "Unlikely":
                color = "red"
                emoji = "❌"
            else:
                color = "orange"
                emoji = "⚠️"
            
            # Main prediction card
            st.markdown(f"""
            <div style="padding: 20px; border-radius: 10px; background-color: {color}20; border: 2px solid {color};">
                <h2 style="color: {color}; margin: 0;">{emoji} {prediction}</h2>
                <h1 style="color: {color}; margin: 10px 0;">{score}%</h1>
                <p style="margin: 0;">Confidence: {results['confidence']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Component breakdown
            st.subheader("📈 Component Breakdown")
            
            component_scores = results["component_scores"]
            
            for component, score_val in component_scores.items():
                component_name = component.replace("_", " ").title()
                st.metric(
                    label=component_name,
                    value=f"{score_val}%"
                )
                st.progress(score_val / 100)
            
            st.markdown("---")
            
            # Detailed explanation
            with st.expander("📋 Detailed Analysis"):
                st.markdown("**Component Contributions to Final Score:**")
                contributions = results["component_contributions"]
                
                for component, contribution in contributions.items():
                    st.write(f"- **{component.replace('_', ' ').title()}**: {contribution}% of final score")
                
                st.markdown("\n**Score Interpretation:**")
                st.write(f"- Final Score: {score}%")
                st.write(f"- Prediction: {prediction}")
                st.write(f"- Threshold: {'≥70% for Likely, <40% for Unlikely'}")
            
            # Download results
            st.markdown("---")
            
            # Prepare download data
            download_data = {
                "timestamp": datetime.now().isoformat(),
                "prediction": prediction,
                "score": score,
                "confidence": results["confidence"],
                "component_scores": component_scores,
                "component_contributions": contributions
            }
            
            st.download_button(
                label="📥 Download Results (JSON)",
                data=json.dumps(download_data, indent=2),
                file_name=f"interview_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: gray; font-size: 12px;">
        <p>⚠️ <strong>Disclaimer:</strong> This tool is for self-coaching and learning purposes only. 
        Predictions should be treated as guidance, not definitive outcomes. Human judgment remains essential.</p>
        <p>Built with Streamlit • Powered by Hugging Face Transformers</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
