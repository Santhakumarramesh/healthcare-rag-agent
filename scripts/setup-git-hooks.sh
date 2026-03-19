#!/bin/bash
# Setup git hooks for API key protection

echo "🔧 Setting up git hooks for security..."

# Create pre-commit hook
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash

echo "🔍 Checking for API keys before commit..."

# Check staged changes for API keys
if git diff --cached | grep -E "(sk-proj-[A-Za-z0-9_-]{20,}|sk-svcacct-[A-Za-z0-9_-]{20,}|rnd_[A-Za-z0-9]{20,}|tvly-[A-Za-z0-9]{20,}|nvapi-[A-Za-z0-9]{20,})"; then
    echo ""
    echo "❌ ERROR: API key detected in staged changes!"
    echo ""
    echo "🔒 Security Issue:"
    echo "   You are trying to commit actual API keys to git."
    echo ""
    echo "✅ How to fix:"
    echo "   1. Remove the API key from your code"
    echo "   2. Use environment variables instead: os.getenv('OPENAI_API_KEY')"
    echo "   3. Add your key to .env (which is gitignored)"
    echo "   4. On Render, add it in Dashboard → Environment"
    echo ""
    exit 1
fi

# Check for .env files
if git diff --cached --name-only | grep -E "^\.env$|\.env\.local$"; then
    echo ""
    echo "❌ ERROR: .env file in staged changes!"
    echo ""
    echo "🔒 Security Issue:"
    echo "   You are trying to commit a .env file which may contain secrets."
    echo ""
    echo "✅ How to fix:"
    echo "   1. git reset HEAD .env"
    echo "   2. Verify .env is in .gitignore"
    echo "   3. Only commit .env.example with placeholders"
    echo ""
    exit 1
fi

echo "✅ No API keys detected - safe to commit"
exit 0
EOF

# Make it executable
chmod +x .git/hooks/pre-commit

echo "✅ Git hooks installed successfully!"
echo ""
echo "📋 What was installed:"
echo "   • Pre-commit hook: Checks for API keys before every commit"
echo "   • Blocks commits containing: sk-proj-, sk-svcacct-, rnd_, tvly-, nvapi-"
echo "   • Prevents .env files from being committed"
echo ""
echo "🔒 Your repository is now protected!"
