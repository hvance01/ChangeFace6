# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

ChangeFace3 is a Streamlit-based video face-swapping tool designed for marketing video personalization. It uses the Replicate API (okaris/roop model) to swap faces in videos.

## Architecture

```
app.py                    # Main Streamlit application entry point
config.py                 # Configuration (API tokens, file limits, model selection)
utils/
├── auth.py              # User authentication (file-based, SHA256 hashed passwords)
├── face_swap.py         # Replicate API integration for face swapping
└── file_handler.py      # File upload/cleanup utilities
```

**Key Flow:**
1. User logs in via `AuthManager` (credentials from `users.txt`)
2. User uploads face image + target video
3. `swap_face_replicate_roop()` calls Replicate API with local file handles
4. Result URL is returned and displayed for download

## Common Commands

```bash
# Run the application
streamlit run app.py

# Full deployment (creates venv, installs deps, starts app)
./start.sh

# Test backend face-swap function directly
python test_backend.py
```

## Configuration

- **API Token**: Set `REPLICATE_API_TOKEN` in `.env` file
- **Users**: Create `users.txt` with format `username:password` per line (see `users.txt.example`)
- **Model**: Change `FACE_SWAP_MODEL` in `config.py` to switch between available models

## Key Implementation Details

- Authentication uses Streamlit session state; passwords are SHA256 hashed
- Uploaded files are saved to `temp/uploads/` with UUID filenames
- Old files are auto-cleaned after 24 hours via `cleanup_old_files()`
- The Replicate API uses file handles directly (not URLs) for `okaris/roop` model
