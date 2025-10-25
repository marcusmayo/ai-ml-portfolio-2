# Dependency Resolution History

## Working Configuration (FINAL)
```
torch==2.8.0+cu128
numpy==2.0.2
transformers==4.57.1
whisperx (latest from pip)
scipy (latest)
fastapi==0.115.0
```

## Critical Issues Encountered

### 1. PyTorch Version Conflicts
**Problem**: Tried torch 2.4.1, 2.5.1, 2.9.0 - all had issues
- torch 2.4.1: CVE-2025-32434 security check blocked model loading
- torch 2.5.1: triton compatibility issues  
- torch 2.9.0: torchaudio version mismatch

**Solution**: torch==2.8.0+cu128 with matching torchaudio/torchvision

### 2. NumPy 2.0 Breaking Changes
**Problem**: NumPy 2.0 removed `np.NaN` (now `np.nan`)
- pyannote.audio uses `np.NaN`
- Initial attempts used numpy 1.26.4

**Solution**: numpy>=2.0.2,<2.1.0 (WhisperX requirement, pyannote adapted)

### 3. Transformers/Tokenizers Version Hell
**Problem**: 
- transformers 4.30.2 incompatible with torch 2.8.0
- transformers 4.57.1 requires newer tokenizers
- tokenizers 0.13.3 had Rust build failures

**Solution**: transformers>=4.48.0 with binary wheels only

### 4. Scipy Non-Existent Version
**Problem**: requirements.txt had scipy==1.16.2 (doesn't exist!)

**Solution**: Use scipy (latest) - currently 1.14.1

### 5. WhisperX Strict Requirements
**Problem**: WhisperX 3.7.4 requires:
- torch>=2.8.0
- torchaudio==2.8.0 (exact)
- numpy>=2.0.2,<2.1.0

**Solution**: Install WhisperX and let it manage its own dependencies

### 6. TorchVision Operator Missing
**Problem**: `RuntimeError: operator torchvision::nms does not exist`
- Mismatch between torch 2.8.0+cu128 and torchvision 0.19.1+cu121

**Solution**: torchvision==0.23.0+cu128 (matches torch CUDA version)

## Installation Order (CRITICAL)
1. PyTorch FIRST (with CUDA index)
2. NumPy
3. Transformers
4. WhisperX (manages its own deps)
5. ML libraries (scipy, pandas, sklearn)
6. Audio libraries
7. Google API
8. Web framework

## DO NOT
- ❌ Mix CUDA versions (cu121 vs cu128)
- ❌ Use numpy <2.0 with WhisperX
- ❌ Use transformers <4.48.0
- ❌ Install torch without --index-url
- ❌ Pin scipy to non-existent versions
- ❌ Use pip without venv activated

## Verified On
- Date: October 25, 2025
- GPU: Tesla T4
- CUDA: 12.8
- Python: 3.12.3
- OS: Ubuntu 24.04
