# WeChat Desktop Chat Scanning Limitations

## Current Status

After extensive investigation, we've discovered that **WeChat's desktop accessibility API has severe limitations**:

### What We Found:

1. **UI Structure Identified:**
   - Chat list is at: `window 1 → UI element 1 → UI element 9 → UI element 1 → UI element 7`
   - Contains 55+ UI elements (AXStaticText)
   - However, these elements don't expose their text content via standard accessibility properties

2. **What We're Getting Instead:**
   - Message content from the currently open chat
   - Timestamps and message types
   - Not actual chat names

3. **Accessibility API Limitations:**
   - `name` property: missing value
   - `value` property: missing value
   - `description` property: empty
   - `entire contents`: doesn't reveal text
   - WeChat doesn't expose chat names through standard accessibility attributes

### Why This Happens:

WeChat's macOS app uses custom UI rendering that doesn't properly integrate with macOS accessibility APIs. This is likely intentional for security/privacy reasons, or simply poor accessibility implementation.

### Solutions:

#### ✅ **Recommended: Use WeChat Web Mode**

WeChat Web provides a proper DOM structure that can be reliably automated:

1. Switch to "WeChat Web" mode in the web interface
2. Scan QR code to log in
3. Full access to chat names and messages
4. More reliable automation

#### ⚠️ **Alternative: OCR-based Scanning**

We have a `scan_chats_ocr.py` script that uses:
- Screenshot capture
- OCR (Optical Character Recognition)
- Can extract visible chat names from screenshots
- Requires WeChat window to be visible and positioned correctly

#### ❌ **Desktop Accessibility API**

Not recommended due to severe limitations discovered above.

## Current Implementation

The `scan_chats.applescript` currently returns whatever text it can extract from the UI, which is often message content rather than chat names. This is a limitation of WeChat's implementation, not our code.

## Next Steps

1. **For Production Use:** Implement WeChat Web automation
2. **For Testing:** Use OCR-based approach with `scan_chats_ocr.py`
3. **Manual Entry:** Users can manually type chat names (most reliable for desktop mode)
