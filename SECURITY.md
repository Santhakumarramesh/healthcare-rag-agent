# Security Guidelines

## 🔒 API Key Protection

### ⚠️ CRITICAL: Never Commit API Keys

**API keys should NEVER be committed to git.** This includes:
- OpenAI API keys (`sk-proj-...`, `sk-svcacct-...`)
- Render API keys (`rnd_...`)
- Tavily API keys (`tvly-...`)
- NVIDIA API keys (`nvapi-...`)
- Pinecone API keys
- Any other credentials

---

## ✅ Safe Practices

### 1. Use Environment Variables

**Local Development:**
```bash
# Copy the example file
cp .env.example .env

# Edit .env with your actual keys (this file is gitignored)
nano .env

# Add your keys:
OPENAI_API_KEY=sk-proj-your-actual-key-here
```

**Production (Render):**
1. Go to Render Dashboard → Your Service → Environment
2. Add environment variables there
3. Never put keys in code or config files

---

### 2. Check Before Committing

**Always run this before `git push`:**
```bash
# Check for exposed keys
git diff | grep -E "(sk-proj-|sk-svcacct-|rnd_|tvly-|nvapi-)"

# If anything shows up, DO NOT COMMIT
```

---

### 3. Files That Are Safe to Commit

✅ `.env.example` - Contains only placeholders
✅ `.env.local.example` - Contains only placeholders
✅ Code files that read from `os.getenv()`
✅ `config.py` that uses environment variables

---

### 4. Files That Should NEVER Be Committed

❌ `.env` - Contains actual keys
❌ `.env.local` - Contains actual keys
❌ Any file with `sk-proj-`, `rnd_`, etc. in it
❌ `credentials.json`
❌ `secrets.py`

---

## 🚨 If You Accidentally Commit a Key

### Immediate Steps:

1. **Revoke the key immediately**
   - OpenAI: https://platform.openai.com/api-keys
   - Render: https://dashboard.render.com/account/api-keys
   - Generate a new key

2. **Remove from git history**
   ```bash
   # Use git-filter-repo (recommended)
   pip install git-filter-repo
   git filter-repo --path .env --invert-paths
   
   # Or use BFG Repo-Cleaner
   java -jar bfg.jar --delete-files .env
   ```

3. **Force push** (⚠️ only if you're the only contributor)
   ```bash
   git push origin main --force
   ```

4. **Update the key everywhere**
   - Local `.env` file
   - Render environment variables
   - Any other deployment platforms

---

## 🔍 Automated Key Detection

### Pre-commit Hook (Recommended)

Create `.git/hooks/pre-commit`:
```bash
#!/bin/bash

# Check for API keys before commit
if git diff --cached | grep -E "(sk-proj-[A-Za-z0-9_-]{20,}|sk-svcacct-[A-Za-z0-9_-]{20,}|rnd_[A-Za-z0-9]{20,}|tvly-[A-Za-z0-9]{20,}|nvapi-[A-Za-z0-9]{20,})"; then
    echo "❌ ERROR: API key detected in staged changes!"
    echo "Remove the key and use environment variables instead."
    exit 1
fi

echo "✅ No API keys detected"
exit 0
```

Make it executable:
```bash
chmod +x .git/hooks/pre-commit
```

---

## 📋 Security Checklist

Before every commit:
- [ ] Run `git diff` and check for keys
- [ ] Verify `.env` is in `.gitignore`
- [ ] Confirm actual keys are only in environment variables
- [ ] Check that code uses `os.getenv()` not hardcoded strings
- [ ] Review changes one more time

Before pushing to GitHub:
- [ ] Run `git log -p | grep -E "sk-|rnd_|tvly-"` to check history
- [ ] Verify no `.env` files are tracked
- [ ] Confirm all keys are in Render dashboard, not code

---

## 🛡️ Current Protection Status

### ✅ What's Protected:
- `.env` is in `.gitignore`
- `.env.local` is in `.gitignore`
- All code uses `os.getenv()` for keys
- `.env.example` contains only placeholders
- No keys found in git history (verified)

### ⚠️ What You Need to Do:
1. Never commit `.env` files
2. Always use Render dashboard for production keys
3. Revoke and regenerate any key that gets exposed
4. Run security checks before pushing

---

## 📚 Additional Resources

- [GitHub Secret Scanning](https://docs.github.com/en/code-security/secret-scanning)
- [OWASP API Security](https://owasp.org/www-project-api-security/)
- [12-Factor App Config](https://12factor.net/config)

---

## 🆘 Need Help?

If you've exposed a key:
1. **Don't panic**
2. **Revoke it immediately**
3. **Generate a new one**
4. **Clean git history** (see above)
5. **Update all deployments**

**Remember**: It's better to be paranoid about keys than to have them exposed!
