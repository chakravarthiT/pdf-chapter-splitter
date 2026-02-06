# GitHub Codespaces Setup Guide 🚀

## What is GitHub Codespaces?

GitHub Codespaces is a cloud-hosted development environment that runs in your browser. It allows you to:
- ✅ Develop directly in the cloud without local setup
- ✅ Collaborate seamlessly with teammates
- ✅ Access consistent environment across any device
- ✅ Keep your local machine clean (no local dependencies)
- ✅ Use VS Code features in your browser

**Key Benefit**: Your local environment stays untouched. This is a completely separate cloud instance!

## How to Use GitHub Codespaces

### Step 1: Push to GitHub
First, ensure your project is pushed to GitHub:
```bash
git add .
git commit -m "Add GitHub Codespaces configuration"
git push origin main
```

### Step 2: Create a Codespace
1. Go to your GitHub repository
2. Click the **Code** button (green button)
3. Select the **Codespaces** tab
4. Click **Create codespace on main** (or your branch)

### Step 3: Automatic Setup
The Codespace will:
1. ✅ Clone your repository
2. ✅ Build the dev container using `.devcontainer/devcontainer.json`
3. ✅ Run `uv sync` automatically (via `postCreateCommand`)
4. ✅ Install VS Code extensions
5. ✅ Open a fully configured development environment in your browser

### Step 4: Start Developing
Once the Codespace loads (~3-5 minutes for first setup):
```bash
# The environment is ready! Just run:
uv run streamlit run app.py
```

The Streamlit app will be accessible at `http://localhost:8501` (auto-forwarded).

## What the Configuration Does

### `.devcontainer/devcontainer.json`
- **Image**: Uses Python 3.11 container
- **Features**: Git, GitHub CLI pre-installed
- **postCreateCommand**: Automatically runs `uv sync` after container creation
- **VS Code Extensions**: Python, Pylance, Ruff, Black, GitHub theme
- **Port Forwarding**: Port 8501 (Streamlit) is automatically exposed

### `.devcontainer/Dockerfile` (Optional)
Custom Docker image for more control. Includes:
- System dependencies (git, curl, build tools)
- `uv` package manager installation

## Local vs. Cloud Development

| Aspect | Local Environment | GitHub Codespaces |
|--------|------------------|-------------------|
| **Setup** | Manual installation needed | Automatic (Docker-based) |
| **Device** | Only on your machine | Any device with browser |
| **Collaboration** | Share screen/code manually | Easy sharing via URL |
| **Resources** | Uses local disk/RAM | Cloud resources (GitHub provided) |
| **Cost** | Free (uses your hardware) | Free tier (60 hours/month for personal use) |
| **Internet** | Works offline | Requires internet connection |

## Common Codespace Commands

### From GitHub Web UI:
- **Pause**: Stops the Codespace (saves compute time)
- **Delete**: Removes the Codespace
- **Rebuild**: Rebuilds the container (useful if config changes)

### From Terminal (inside Codespace):
```bash
# View running services
ps aux

# Check available ports
netstat -tlnp

# Install additional packages
uv pip install <package-name>

# Update dependencies
uv sync

# Run Streamlit app
uv run streamlit run app.py
```

## Accessing Your Codespace

After creation, you can:
1. **Open in Browser**: Visit `github.com/` → Your Repo → Code → Codespaces
2. **Open in VS Code Desktop**: Click "Open in Visual Studio Code" in the browser
3. **Access via SSH**: Click "..." → Connect to SSH

## Environment Variables

For sensitive data (API keys, etc.):

### In Codespaces:
1. Go to GitHub Settings → Codespaces → Secrets and variables
2. Add your secrets (e.g., `GOOGLE_API_KEY`)
3. Secrets are automatically injected into your Codespace

### Local `.env` file:
Your local project's `.env` file is **not** uploaded to Codespaces. You need to:
1. Add secrets via GitHub Codespaces settings, OR
2. Create a new `.env` file in the Codespace manually, OR
3. Use GitHub Secrets and load them in your Codespace

## Tips & Best Practices

✅ **DO:**
- Commit your `.devcontainer` folder to GitHub
- Use GitHub Secrets for sensitive data
- Test config changes in a new Codespace before deleting old ones
- Keep your local environment as a backup

❌ **DON'T:**
- Modify `.devcontainer` config without testing
- Store secrets in environment files
- Delete Codespace before confirming it works
- Use Codespaces for always-on processes (use Azure Container Instances or similar)

## Troubleshooting

### Codespace takes too long to create:
- First creation takes longer (5-10 mins)
- Subsequent creations are faster (use Docker layer caching)

### Dependencies not installing:
- Check `uv sync` output in logs
- Verify `pyproject.toml` and `requirements.txt` are correct
- Rebuild the Codespace from the GitHub UI

### Streamlit port not forwarding:
- Port 8501 should auto-forward
- If not, manually add port in VS Code: Ports panel → Add Port → 8501

### Out of storage space:
- Codespaces have 32GB storage
- Clean up cache: `uv cache clean`
- Delete old builds/artifacts

## Next Steps

1. ✅ Push `.devcontainer/` folder to GitHub
2. ✅ Create a Codespace from GitHub UI
3. ✅ Test the Streamlit app in the cloud
4. ✅ Try accessing from different devices
5. ✅ Pause when not in use to save compute hours
6. ✅ Keep your local environment as backup

## Resources

- [GitHub Codespaces Documentation](https://docs.github.com/en/codespaces)
- [Dev Container Specification](https://containers.dev/)
- [Streamlit in Codespaces](https://docs.streamlit.io/deploy/tutorials/deploy-streamlit-using-codespaces)
- [Python in Dev Containers](https://containers.dev/features)

---

**Remember**: Your local environment is untouched! Codespaces is just another way to develop. You can use both simultaneously! 🎉
