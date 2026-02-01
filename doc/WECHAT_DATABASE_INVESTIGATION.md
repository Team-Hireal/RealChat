# WeChat Database Access Investigation

## Summary

We successfully located WeChat's local databases but discovered they are **encrypted with SQLCipher**. This document explains what we found and provides recommendations.

## What We Discovered

### 1. Database Location ✅

WeChat stores its data in:
```
~/Library/Containers/com.tencent.xinWeChat/Data/Documents/xwechat_files/wxid_XXXXX_HASH/
```

### 2. Database Files Found ✅

We found 16 encrypted databases:

**Contact & Chat Information:**
- `contact/contact.db` (10.2 MB) - Contact list and chat information
- `session/session.db` (610 KB) - Chat sessions

**Messages:**
- `message/message_0.db` (54.8 MB) - Chat messages
- `message/biz_message_0.db` (24 MB) - Business messages
- `message/media_0.db` (10.9 MB) - Media files

**Other:**
- `favorite/favorite.db` - Favorites
- `sns/sns.db` - Moments/Timeline
- `emoticon/emoticon.db` - Stickers
- And 8 more databases

### 3. Encryption Status 🔒

**All 16 databases are encrypted with SQLCipher**

- Standard SQLite tools cannot read them
- The encryption key is derived from system/device information
- WeChat uses proprietary key derivation algorithm

## Why Desktop Accessibility API Failed

The accessibility API limitation we encountered earlier is actually a **secondary issue**. The **primary challenge** is:

1. **UI Rendering**: WeChat's chat list UI elements don't expose text through accessibility APIs
2. **Database Encryption**: Even if we bypass the UI, the databases are encrypted
3. **Proprietary Protection**: WeChat intentionally protects user data with encryption

## Decryption Challenges

### What's Needed to Decrypt

1. **Encryption Key**: Derived from:
   - WeChat user ID (wxid)
   - Device hardware UUID
   - MAC address
   - Possibly other factors (IMEI, device serial, etc.)

2. **Key Derivation Algorithm**:
   - Proprietary to WeChat
   - Changes between versions
   - Not publicly documented

3. **SQLCipher Library**:
   - Requires compilation with specific settings
   - Compatibility issues with newer Python versions

### Our Attempt

We created scripts that:
- ✅ Located all WeChat databases
- ✅ Identified encryption status
- ✅ Extracted system information (wxid, MAC, UUID)
- ✅ Attempted key derivation using common methods
- ❌ Could not decrypt (expected - proprietary algorithm)

## Existing Solutions

### Open Source Projects

There are some projects that claim to decrypt WeChat databases:

1. **WeChatMsg** (GitHub)
   - Chinese project for WeChat message export
   - May work with specific WeChat versions
   - Requires reverse engineering updates for new versions

2. **WeChatDecrypt** (GitHub)
   - Focuses on Android WeChat
   - macOS support limited

3. **Commercial Tools**
   - Various paid tools claim to export WeChat data
   - Use with caution (privacy/security concerns)

### Risks & Considerations

⚠️ **Important Warnings:**

1. **Terms of Service**: Decrypting WeChat databases may violate WeChat's ToS
2. **Privacy**: User chat data is encrypted for privacy protection
3. **Security**: Third-party tools may contain malware
4. **Legality**: Check local laws regarding data decryption
5. **Stability**: Decryption methods break with WeChat updates

## Recommended Solutions

### Option 1: WeChat Web Mode (RECOMMENDED) ✅

**Status**: Already implemented and working

**Advantages:**
- ✅ No encryption to bypass
- ✅ Official WeChat interface
- ✅ Reliable and stable
- ✅ No ToS violations
- ✅ Works across versions

**How to Use:**
See `WECHAT_WEB_QUICKSTART.md`

### Option 2: WeChat Official Export

**WeChat has a built-in chat export feature:**

1. Open WeChat desktop
2. Select a chat
3. Click "..." menu
4. Choose "Export Chat History"
5. Save as text or file

**Advantages:**
- Official feature
- No encryption issues
- User-authorized

**Limitations:**
- Manual process
- One chat at a time
- Limited automation

### Option 3: Manual Chat Name Entry

**Simple and straightforward:**

1. User types chat name in configuration
2. Bot monitors that specific chat
3. No scanning needed

**Advantages:**
- No technical barriers
- User knows their chat names
- Simple implementation

### Option 4: Research Current Decryption Methods

**If you really need database access:**

1. Search GitHub for recent WeChat decryption projects
2. Check if they support your WeChat version
3. Test in a safe environment
4. Be aware of risks

**Example search terms:**
- "WeChat database decrypt macOS"
- "WeChat SQLCipher key extraction"
- "微信数据库解密 Mac"

## Technical Details

### System Information Extracted

```
WeChat User ID: wxid_hjbp4usufo1j12
MAC Address: 8A:C7:D8:81:7E:FA
Hardware UUID: 3F88D3E5-D86A-5D8C-ABEC-7E4D285662F9
Hostname: tests-MacBook-Pro.local
```

### Key Derivation Attempts

We tried three common methods:
1. MD5(wxid + MAC address)
2. HMAC-SHA256(wxid, hardware UUID)
3. SHA256(wxid + UUID + MAC)

None worked (expected - WeChat uses proprietary algorithm).

### Database Schema (If Decrypted)

Based on research, the `contact.db` likely contains:

**Tables:**
- `Contact` - Contact information
- `ContactHeadImage` - Profile pictures
- `ContactLabel` - Contact tags
- `Session` - Chat sessions

**Useful Queries (if decrypted):**
```sql
-- List all contacts
SELECT userName, nickName, remark FROM Contact;

-- List recent chats
SELECT * FROM Session ORDER BY lastMessageTime DESC;
```

## Scripts Created

1. **`explore_wechat_db.py`** - Lists and analyzes all WeChat databases
2. **`decrypt_wechat_db.py`** - Attempts decryption with derived keys

**Usage:**
```bash
python3 explore_wechat_db.py    # List databases
python3 decrypt_wechat_db.py    # Attempt decryption
```

## Conclusion

### What We Learned

1. ✅ WeChat databases exist and are accessible (file-level)
2. 🔒 All databases are encrypted with SQLCipher
3. ❌ Decryption requires proprietary key derivation algorithm
4. ⚠️ Decryption attempts may violate ToS and have security risks

### Best Path Forward

**Use WeChat Web Mode** - It's:
- Already implemented
- Fully functional
- Officially supported
- No encryption barriers
- Reliable and maintainable

### If You Need Database Access

1. Research current WeChat decryption projects
2. Check compatibility with your WeChat version
3. Test in isolated environment
4. Consider privacy/security implications
5. Have a backup plan (WeChat Web)

## Resources

- **WeChat Web Quickstart**: `WECHAT_WEB_QUICKSTART.md`
- **Integration Status**: `WECHAT_INTEGRATION_FINAL.md`
- **Database Explorer**: `explore_wechat_db.py`
- **Decryption Attempt**: `decrypt_wechat_db.py`

---

**Last Updated**: 2026-01-30
**Status**: Investigation Complete - Encryption Confirmed
**Recommendation**: Use WeChat Web Mode
