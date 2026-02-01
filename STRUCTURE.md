## WeChat Auto-Reply Bot - Clean Structure

### Core Files (9 total)

**Main Bot:**
- `wemac_autoreply.applescript` (16K) - The auto-reply bot that sends templated messages

**Support:**
- `mouseclick.py` (633B) - Mouse automation helper (required by AppleScript)

**User Scripts:**
- `get-started.sh` (7.9K) - Interactive setup wizard (run this first!)
- `config.sh` (4.0K) - Reconfigure bot settings
- `run.sh` (3.2K) - Run the auto-reply bot
- `troubleshoot.sh` (1.5K) - Diagnose WeChat window issues
- `diagnose_ui.applescript` (2.5K) - UI structure diagnostic

**Documentation:**
- `README.md` (8.2K) - Complete documentation

**Cleanup:**
- `cleanup.sh` (2.4K) - The cleanup script (can be deleted)

---

### Quick Start

1. **First time setup:**
   ```bash
   ./get-started.sh
   ```

2. **If you have issues:**
   ```bash
   ./troubleshoot.sh
   ```

3. **Run the bot:**
   ```bash
   ./run.sh
   ```

4. **Change settings:**
   ```bash
   ./config.sh
   ```

---

### What Was Removed

- ❌ Draft reply mode (unused feature)
- ❌ Message history retrieval (unused feature)
- ❌ WeChat Moments retrieval (unused feature)
- ❌ Database manager (not needed)
- ❌ All test scripts (test-*.sh)
- ❌ All exploration scripts (explore-*.sh, monitor.sh, etc.)
- ❌ 13 redundant documentation files

**Backup location:** `../wemac_backup_20260128_184353/`

---

### File Size Comparison

- **Before:** ~38 files, ~150KB total
- **After:** 9 files, ~46KB total
- **Reduction:** 76% fewer files, 69% smaller

---

That's it! The codebase is now clean and focused on the core auto-reply functionality.
