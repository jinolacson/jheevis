#!/bin/bash
# Quick start script for Jheevis MLX

echo "╔════════════════════════════════════════╗"
echo "║    JHEEVIS MLX - Installation Check   ║"
echo "╚════════════════════════════════════════╝"
echo ""

# Check if running on Apple Silicon
echo "1. Checking Python architecture..."
ARCH=$(python -c "import platform; print(platform.processor())")
if [ "$ARCH" = "arm" ]; then
    echo "   ✅ Native ARM Python detected"
else
    echo "   ❌ ERROR: Not using native ARM Python (found: $ARCH)"
    echo "   Please install native Python or create ARM conda environment"
    echo "   Run: CONDA_SUBDIR=osx-arm64 conda create -n jheevis python=3.11"
    exit 1
fi
echo ""

# Check Python version
echo "2. Checking Python version..."
PYTHON_VERSION=$(python --version)
echo "   $PYTHON_VERSION"
echo ""

# Install dependencies
echo "3. Installing dependencies..."
echo "   This may take 10-15 minutes (downloading ~4GB)..."
pip install -r requirements.txt -q
if [ $? -eq 0 ]; then
    echo "   ✅ Dependencies installed"
else
    echo "   ❌ Installation failed. Check internet connection."
    exit 1
fi
echo ""

# Check microphone access
echo "4. Checking microphone access..."
python -c "import sounddevice as sd; sd.query_devices()" > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "   ✅ Audio devices detected"
else
    echo "   ⚠️  Warning: Audio device check failed"
fi
echo ""

# Test imports
echo "5. Testing MLX imports..."
python -c "import mlx.core as mx; import mlx_whisper; from mlx_lm import load" > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "   ✅ MLX modules working"
else
    echo "   ❌ MLX import failed. Reinstall dependencies."
    exit 1
fi
echo ""

echo "╔════════════════════════════════════════╗"
echo "║         Installation Complete!         ║"
echo "╚════════════════════════════════════════╝"
echo ""
echo "To start Jheevis:"
echo "   python main.py"
echo ""
echo "First run will download models (~4GB)"
echo "Say 'Hey Jheevis' to activate!"
echo ""
