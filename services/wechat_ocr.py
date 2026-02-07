#!/usr/bin/env python3
"""
OCR-based message reader for WeChat
Uses macOS Vision framework for fast text extraction
"""
import subprocess
import tempfile
import json
from pathlib import Path
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class WeChatOCR:
    """OCR-based message reader for WeChat"""

    def __init__(self):
        self.last_messages = []
        self.agent_messages = set()  # Track messages sent by agent
        self.recent_agent_responses = []  # Track last 10 agent responses for comparison
        self.last_agent_response_tail = ""  # Track last 3 words of most recent agent response
        self.debug_screenshot_path = '/tmp/wechat_ocr_debug.png'  # Debug screenshot path
        self.previous_raw_text = []  # Store previous OCR text lines for comparison
        self.detected_messages = set()  # Track all previously detected messages
        self.user_messages = set()  # Track user messages that agent is responding to

    def capture_message_area(self, output_path: str) -> bool:
        """
        Capture screenshot of WeChat message area

        Args:
            output_path: Path to save screenshot

        Returns:
            bool: Success status
        """
        try:
            # First, move WeChat window on-screen if needed
            move_script = '''
            tell application "System Events"
                tell process "WeChat"
                    if (count of windows) = 0 then
                        return "no_window"
                    end if

                    set mainWindow to window 1
                    set winPosition to position of mainWindow
                    set y to item 2 of winPosition

                    -- Move window on-screen if it's off-screen (negative Y)
                    if y < 0 then
                        set position of mainWindow to {100, 100}
                        delay 0.2
                    end if
                end tell
            end tell
            '''

            subprocess.run(['osascript', '-e', move_script],
                         capture_output=True, text=True, timeout=5)

            # Get WeChat window bounds
            script = '''
            tell application "System Events"
                tell process "WeChat"
                    if (count of windows) = 0 then
                        return "no_window"
                    end if

                    set mainWindow to window 1
                    set winPosition to position of mainWindow
                    set winSize to size of mainWindow
                    set x to item 1 of winPosition
                    set y to item 2 of winPosition
                    set w to item 1 of winSize
                    set h to item 2 of winSize

                    return (x as string) & "," & (y as string) & "," & (w as string) & "," & (h as string)
                end tell
            end tell
            '''

            result = subprocess.run(['osascript', '-e', script],
                                  capture_output=True, text=True, timeout=5)
            output = result.stdout.strip()

            if output == "no_window":
                logger.error("No WeChat window found")
                return False

            # Parse window bounds
            x, y, w, h = map(int, output.split(','))

            logger.info(f"WeChat window at: x={x}, y={y}, w={w}, h={h}")

            # Adaptive message area calculation based on window size
            # Detect window type: pop-up windows are typically narrower
            is_popup = w < 700  # Pop-up windows are usually < 700px wide

            if is_popup:
                # Pop-up window: no sidebar, just message area
                # Focus on RIGHT HALF to capture user messages (they appear on right side)
                msg_x = x + int(w * 0.5)  # Start from middle of window
                msg_y = y + 60  # Below title bar (smaller for pop-ups)
                msg_w = int(w * 0.45)  # Right half minus margin
                msg_h = h - 140  # Exclude title and input area
                logger.info(f"Detected pop-up window (w={w}), focusing on right half for user messages")
            else:
                # Main window: has sidebar on left
                # Focus on RIGHT HALF of message area to capture user messages
                sidebar_width = int(w * 0.32)  # Sidebar width

                # Title bar height scales with window size
                title_height = max(60, int(h * 0.08))  # 8% of height or 60px minimum

                # Input area at bottom scales with window size
                input_height = max(100, int(h * 0.12))  # 12% of height or 100px minimum

                # Calculate message area width (after sidebar)
                message_area_width = w - sidebar_width - 30

                # Focus on RIGHT HALF of message area (where user messages appear)
                msg_x = x + sidebar_width + int(message_area_width * 0.5)  # Start from middle of message area
                msg_y = y + title_height
                msg_w = int(message_area_width * 0.45)  # Right half minus margin
                msg_h = h - title_height - input_height
                logger.info(f"Detected main window (w={w}), sidebar={sidebar_width}px, focusing on right half for user messages")

            logger.info(f"Message area: x={msg_x}, y={msg_y}, w={msg_w}, h={msg_h}")

            # IMPORTANT: Only capture the BOTTOM 200 pixels of the message area
            # This ensures we only read the newest message, not old messages
            bottom_height = min(200, msg_h)  # Capture bottom 200px or less if window is smaller
            bottom_y = msg_y + msg_h - bottom_height  # Start from bottom

            logger.info(f"Capturing BOTTOM of message area only: y={bottom_y}, h={bottom_height}")

            # Capture screenshot of BOTTOM message area only (newest message)
            cmd = [
                'screencapture',
                '-x',  # No sound
                '-R', f"{msg_x},{bottom_y},{msg_w},{bottom_height}",  # Bottom region only
                output_path
            ]

            result = subprocess.run(cmd, capture_output=True, timeout=10)
            if result.returncode == 0:
                logger.info(f"Screenshot captured: {output_path}")

                # Save a copy for debug preview
                try:
                    import shutil
                    shutil.copy2(output_path, self.debug_screenshot_path)
                    logger.debug(f"Debug screenshot saved: {self.debug_screenshot_path}")
                except Exception as e:
                    logger.warning(f"Failed to save debug screenshot: {e}")

                return True
            else:
                logger.error(f"Screenshot failed: {result.stderr}")
                return False

        except Exception as e:
            logger.error(f"Error capturing screenshot: {e}")
            return False

    def extract_text_vision(self, image_path: str) -> List[str]:
        """
        Extract text from image using macOS Vision framework

        Args:
            image_path: Path to image file

        Returns:
            List of text strings found in image
        """
        try:
            # Use Swift script to call Vision framework
            swift_script = f'''
            import Vision
            import AppKit

            let imageURL = URL(fileURLWithPath: "{image_path}")
            guard let image = NSImage(contentsOf: imageURL),
                  let cgImage = image.cgImage(forProposedRect: nil, context: nil, hints: nil) else {{
                print("ERROR: Could not load image")
                exit(1)
            }}

            let request = VNRecognizeTextRequest()
            request.recognitionLevel = .accurate
            request.usesLanguageCorrection = true

            let handler = VNImageRequestHandler(cgImage: cgImage, options: [:])

            do {{
                try handler.perform([request])

                guard let observations = request.results else {{
                    print("[]")
                    exit(0)
                }}

                var texts: [String] = []
                for observation in observations {{
                    guard let topCandidate = observation.topCandidates(1).first else {{ continue }}
                    texts.append(topCandidate.string)
                }}

                // Output as JSON array
                let jsonData = try JSONSerialization.data(withJSONObject: texts)
                if let jsonString = String(data: jsonData, encoding: .utf8) {{
                    print(jsonString)
                }}

            }} catch {{
                print("ERROR: \\(error)")
                exit(1)
            }}
            '''

            # Write Swift script to temp file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.swift', delete=False) as f:
                f.write(swift_script)
                swift_file = f.name

            try:
                # Run Swift script
                result = subprocess.run(
                    ['swift', swift_file],
                    capture_output=True,
                    text=True,
                    timeout=30
                )

                if result.returncode == 0:
                    # Parse JSON output
                    texts = json.loads(result.stdout.strip())
                    logger.info(f"OCR extracted {len(texts)} text elements")
                    return texts
                else:
                    logger.error(f"Swift OCR failed: {result.stderr}")
                    return []

            finally:
                # Clean up temp file
                Path(swift_file).unlink(missing_ok=True)

        except Exception as e:
            logger.error(f"Error in Vision OCR: {e}")
            return []

    def _filter_ui_elements(self, text: str) -> str:
        """Remove common UI elements from message text"""
        ui_elements = [
            'File Transfer', 'Voice Call', 'Video Call', 'Location',
            'Contact Card', 'Red Packet', 'Mini Program', 'Sticker',
            'Image', 'Video', 'Voice Message'
        ]
        cleaned = text
        for element in ui_elements:
            cleaned = cleaned.replace(element, '')
        return ' '.join(cleaned.split()).strip()

    def _is_valid_message(self, text: str) -> bool:
        """Check if text is a valid message (not timestamp, UI element, etc.)"""
        import re

        # Filter out empty or very short text
        if not text or len(text.strip()) < 3:
            return False

        # Filter out [Agent] messages with ROBUST detection
        # OCR often misreads [Agent] as variations like "ent]", "gent]", "Agent]", etc.
        agent_patterns = [
            r'\[Agent\]',  # Standard [Agent]
            r'\[agent\]',  # Lowercase
            r'ent\]',  # Common OCR error: "ent]"
            r'gent\]',  # Common OCR error: "gent]"
            r'Agent\]',  # Missing opening bracket
            r'\[Agen',  # Partial match
            r'› you today',  # Common fragment from "How can I help you today?"
            r'How can I help you',  # Agent's common phrase
            r'I\'m here to help',  # Agent's common phrase
            r'Nice to meet you',  # Agent's common phrase
            r'Feel free to',  # Agent's common phrase
        ]

        for pattern in agent_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                logger.debug(f"Filtered agent message (pattern: {pattern}): {text[:50]}...")
                return False

        # Filter out timestamps (e.g., "21:30", "01/26", "12:05")
        # Check both standalone timestamps and timestamps within text
        timestamp_patterns = [
            r'\b\d{1,2}:\d{2}\b',  # 21:30, 12:05
            r'\b\d{1,2}/\d{1,2}\b',  # 01/26, 12/05
            r'\b\d{1,2}/\d{1,2}/\d{2,4}\b',  # 01/26/2026
            r'\b/\d{1,2}/\d{1,2}\b',  # /12/05
            r'\b\d{4}-\d{2}-\d{2}\b',  # 2026-01-26
            r'\b\d{1,2}:\d{2}\s*[AP]M\b',  # 11:30 PM, 3:45 AM
        ]

        # If text is ONLY a timestamp, filter it out
        for pattern in timestamp_patterns:
            if re.match(f'^{pattern}$', text.strip()):
                return False

        # If text contains ONLY timestamps and whitespace, filter it out
        text_without_timestamps = text
        for pattern in timestamp_patterns:
            text_without_timestamps = re.sub(pattern, '', text_without_timestamps)

        if not text_without_timestamps.strip():
            return False

        # Filter out common UI text patterns
        ui_patterns = [
            r'^\.{3,}$',  # ...
            r'^[:\s\.]+$',  # : ... etc
            r'^elp\s*\.\.\.$',  # elp ...
            r'^i:\s*\.\.\.$',  # i: ...
        ]

        for pattern in ui_patterns:
            if re.match(pattern, text.strip(), re.IGNORECASE):
                return False

        return True

    def _normalize_text(self, text: str) -> str:
        """Normalize text for comparison"""
        return ' '.join(text.lower().split())

    def _is_agent_response(self, text: str) -> bool:
        """Check if text matches any recent agent responses"""
        # First check: if [Agent] appears anywhere in text, it's an agent message
        if '[Agent]' in text or '[agent]' in text.lower():
            logger.info(f"Text contains [Agent] marker: '{text[:50]}...'")
            return True

        # Remove [Agent] prefix if present
        clean_text = text.replace('[Agent]', '').replace('[agent]', '').strip()
        normalized_text = self._normalize_text(clean_text)

        # Check if message starts with last 3 words of previous agent response
        # This catches cases where OCR picks up the tail of the agent's message
        if self.last_agent_response_tail:
            normalized_tail = self._normalize_text(self.last_agent_response_tail)
            if normalized_text.startswith(normalized_tail):
                logger.info(f"Text starts with agent response tail: '{text[:50]}...' starts with '{self.last_agent_response_tail}'")
                return True

        # Check against recent agent responses
        for agent_response in self.recent_agent_responses:
            normalized_agent = self._normalize_text(agent_response)

            # Check for exact match or if one contains the other
            if (normalized_text == normalized_agent or
                normalized_agent in normalized_text or
                normalized_text in normalized_agent):
                logger.info(f"Text matches recent agent response: '{text[:50]}...' matches '{agent_response[:50]}...'")
                return True

        return False

    def _get_message_signature(self, text: str, num_words: int = 5) -> str:
        """Get first N words of message as signature"""
        words = text.split()[:num_words]
        return ' '.join(words)

    def _extract_last_message_by_timestamp(self, text: str) -> str:
        """
        Extract only the last message by finding the last timestamp and taking text after it

        Args:
            text: Combined OCR text

        Returns:
            Text after the last timestamp, or empty string if no timestamp found
        """
        import re

        # Timestamp patterns
        timestamp_patterns = [
            r'\b\d{1,2}:\d{2}\b',  # 21:30, 12:05, 00:34, 23:57
            r'\b\d{1,2}:\d{2}\s*[AP]M\b',  # 11:30 PM, 3:45 AM
        ]

        # Find all timestamp positions
        last_timestamp_pos = -1
        last_timestamp_end = -1

        for pattern in timestamp_patterns:
            for match in re.finditer(pattern, text):
                if match.start() > last_timestamp_pos:
                    last_timestamp_pos = match.start()
                    last_timestamp_end = match.end()

        # If we found a timestamp, extract text after it
        if last_timestamp_end > 0:
            text_after_timestamp = text[last_timestamp_end:].strip()
            logger.debug(f"Found timestamp at position {last_timestamp_pos}, extracting text after it")
            logger.debug(f"  → Text after timestamp: '{text_after_timestamp[:100]}...'")
            return text_after_timestamp

        # No timestamp found, return original text
        return text

    def _extract_new_text(self, current_lines: List[str], previous_lines: List[str]) -> List[str]:
        """
        Extract ALL new text lines (complete new message)
        Uses the last 3 words of the previous agent message to find the boundary

        Args:
            current_lines: Current OCR text lines
            previous_lines: Previous OCR text lines

        Returns:
            List containing all new text lines
        """
        # If no previous scan, return all current lines
        if not previous_lines:
            if current_lines:
                logger.info(f"First scan: returning all {len(current_lines)} lines")
                return current_lines
            return []

        # Combine current lines into a single text string
        current_text = ' '.join(current_lines)

        # FIRST: Try to extract the last message by timestamp
        # This handles cases where OCR picks up multiple messages
        text_after_timestamp = self._extract_last_message_by_timestamp(current_text)

        if text_after_timestamp and text_after_timestamp != current_text:
            # We found a timestamp and extracted text after it
            # Check if this is different from previous scan
            prev_text = ' '.join(previous_lines)
            prev_after_timestamp = self._extract_last_message_by_timestamp(prev_text)

            if text_after_timestamp != prev_after_timestamp:
                logger.info(f"✅ New message after timestamp: '{text_after_timestamp[:100]}...'")
                return [text_after_timestamp]
            else:
                logger.debug("Text after timestamp unchanged from previous scan")
                return []

        # SECOND: If we have the last 3 words from the previous agent message, use them as a boundary
        if self.last_agent_response_tail:
            # Normalize both texts for comparison
            normalized_current = self._normalize_text(current_text)
            normalized_tail = self._normalize_text(self.last_agent_response_tail)

            logger.debug(f"Looking for agent tail in OCR text...")
            logger.debug(f"  Agent tail: '{self.last_agent_response_tail}'")
            logger.debug(f"  Normalized tail: '{normalized_tail}'")
            logger.debug(f"  Current text (first 200 chars): '{current_text[:200]}'")

            # Try to find the tail in the current text
            # Use fuzzy matching by checking each word of the tail
            tail_words = normalized_tail.split()
            current_words = normalized_current.split()

            # Look for a sequence of words that matches most of the tail words
            best_match_index = -1
            best_match_score = 0

            for i in range(len(current_words) - len(tail_words) + 1):
                # Check how many words match
                matches = 0
                for j, tail_word in enumerate(tail_words):
                    if i + j < len(current_words):
                        # Fuzzy match: check if words are similar (handle OCR errors)
                        current_word = current_words[i + j]
                        if tail_word == current_word or tail_word in current_word or current_word in tail_word:
                            matches += 1

                # Calculate match score
                score = matches / len(tail_words)
                if score > best_match_score:
                    best_match_score = score
                    best_match_index = i + len(tail_words)

            # If we found a good match (>60% of words match), extract text after it
            if best_match_score > 0.6 and best_match_index != -1:
                # Extract words after the boundary
                new_words = current_words[best_match_index:]
                new_text = ' '.join(new_words).strip()

                if new_text:
                    logger.info(f"✅ Found text after agent tail (match score: {best_match_score:.2f})")
                    logger.info(f"  → Extracted: '{new_text[:100]}...'")
                    return [new_text]
                else:
                    logger.debug("No new text after agent tail")
                    return []
            else:
                logger.debug(f"Agent tail not found or match score too low ({best_match_score:.2f})")

        # Fallback: use the old line-by-line comparison
        prev_set = set(previous_lines)
        new_lines = []

        # Find lines that are in current but not in previous
        for line in current_lines:
            if line not in prev_set:
                new_lines.append(line)

        # Return ALL new lines (complete message)
        if new_lines:
            logger.info(f"Found {len(new_lines)} new text lines (fallback method), returning all of them")
            return new_lines

        # If no new lines found, check if the last line changed (edited message)
        if len(current_lines) > 0 and len(previous_lines) > 0:
            if current_lines[-1] != previous_lines[-1]:
                logger.info("Last line changed, treating as new message")
                return [current_lines[-1]]

        logger.debug("No new text detected")
        return []

    def parse_messages(self, text_lines: List[str]) -> List[Dict]:
        """
        Parse OCR text lines into structured messages

        Args:
            text_lines: Raw text lines from OCR

        Returns:
            List of message dictionaries
        """
        import re

        messages = []
        current_message = None

        # Regex to match timestamps: "01:42", "Tuesday 22:33", "Yesterday 14:20", etc.
        timestamp_pattern = re.compile(r'^\d{1,2}:\d{2}$|Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday|Yesterday|Today')

        for line in text_lines:
            line = line.strip()
            if not line:
                continue

            # Check if line is a timestamp
            if timestamp_pattern.search(line):
                # Save previous message if exists
                if current_message:
                    messages.append(current_message)

                # Start new message with timestamp
                current_message = {
                    'timestamp': line,
                    'text': '',
                    'is_agent': False
                }
            elif current_message:
                # Add to current message text
                if current_message['text']:
                    current_message['text'] += ' ' + line
                else:
                    current_message['text'] = line
            else:
                # No timestamp found yet, but we have text
                # Create a message without timestamp
                if not current_message:
                    current_message = {
                        'timestamp': 'Unknown time',
                        'text': line,
                        'is_agent': False
                    }
                else:
                    current_message['text'] += ' ' + line

        # Add last message
        if current_message:
            messages.append(current_message)

        # If we only got one big message with no timestamps, try to split by sentence patterns
        if len(messages) == 1 and len(text_lines) > 5:
            # Try to detect multiple messages by looking for repeated short phrases
            # or complete sentence boundaries
            text = messages[0]['text']

            # Split by common message boundaries (questions followed by statements)
            # This is a heuristic approach
            parts = []
            current_part = []

            for line in text_lines:
                line = line.strip()
                if not line:
                    continue

                # If line is very short (1-3 words) and we have accumulated text,
                # it might be a separate message
                if len(line.split()) <= 3 and current_part:
                    if current_part:
                        parts.append(' '.join(current_part))
                        current_part = []
                    parts.append(line)
                else:
                    current_part.append(line)

            # Add remaining part
            if current_part:
                parts.append(' '.join(current_part))

            # If we successfully split into multiple parts, create separate messages
            if len(parts) > 1:
                messages = []
                for part in parts:
                    if part.strip():
                        messages.append({
                            'timestamp': 'Unknown time',
                            'text': part.strip(),
                            'is_agent': False
                        })

        logger.info(f"Parsed {len(messages)} messages from {len(text_lines)} text lines")
        return messages

    def read_messages(self) -> List[Dict]:
        """
        Read messages from WeChat using OCR

        Returns:
            List of message dictionaries
        """
        try:
            # Capture screenshot
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
                screenshot_path = f.name

            try:
                if not self.capture_message_area(screenshot_path):
                    return []

                # Extract text using Vision OCR
                current_text_lines = self.extract_text_vision(screenshot_path)

                if not current_text_lines:
                    logger.warning("No text extracted from screenshot")
                    return []

                # Log raw OCR output for debugging
                logger.info(f"Raw OCR text ({len(current_text_lines)} lines): {current_text_lines[:10]}")

                # Extract only NEW text lines by comparing with previous scan
                new_text_lines = self._extract_new_text(current_text_lines, self.previous_raw_text)

                # Update previous raw text for next comparison
                self.previous_raw_text = current_text_lines.copy()

                # If no new text, return empty list
                if not new_text_lines:
                    logger.debug("No new text detected in this scan")
                    return []

                # Parse new text lines into messages
                # For new text, we treat it as a single message
                messages = []

                # Combine new lines into a single message
                combined_text = ' '.join(new_text_lines).strip()

                if combined_text:
                    # Validate message first
                    if not self._is_valid_message(combined_text):
                        logger.debug(f"Filtered invalid message: {combined_text[:50]}...")
                        return []

                    # Clean UI elements
                    cleaned_text = self._filter_ui_elements(combined_text)

                    if cleaned_text and self._is_valid_message(cleaned_text):
                        # Filter out [Agent] messages (messages from the AI itself)
                        # Check if [Agent] appears ANYWHERE in the text, not just at start
                        if '[Agent]' in cleaned_text or '[agent]' in cleaned_text.lower():
                            logger.info(f"Filtered [Agent] message: {cleaned_text[:50]}...")
                            return []

                        # Check if text matches any recent agent responses
                        if self._is_agent_response(cleaned_text):
                            logger.info(f"Filtered agent response: {cleaned_text[:50]}...")
                            return []

                        # Check if message was already detected
                        normalized_msg = self._normalize_text(cleaned_text)
                        if normalized_msg in self.detected_messages:
                            logger.debug(f"Filtered previously detected message: {cleaned_text[:50]}...")
                            return []

                        # Check if it matches a user message (to avoid echo)
                        if normalized_msg in self.user_messages:
                            logger.debug(f"Filtered user message echo: {cleaned_text[:50]}...")
                            return []

                        # Check if it's an agent message (additional check)
                        is_agent_msg = False
                        msg_signature = self._get_message_signature(cleaned_text)

                        for agent_msg in self.agent_messages:
                            normalized_agent = self._normalize_text(agent_msg)
                            agent_signature = self._get_message_signature(agent_msg)

                            if (normalized_msg == normalized_agent or
                                normalized_agent in normalized_msg or
                                normalized_msg in normalized_agent or
                                msg_signature == agent_signature):
                                is_agent_msg = True
                                logger.info(f"Filtered agent message: {cleaned_text[:50]}...")
                                break

                        # Only add if it's not an agent message
                        if not is_agent_msg:
                            # Add to detected messages history
                            self.detected_messages.add(normalized_msg)

                            # Keep history size manageable (last 100 messages)
                            if len(self.detected_messages) > 100:
                                # Remove oldest entries (convert to list, remove first half, convert back)
                                msgs_list = list(self.detected_messages)
                                self.detected_messages = set(msgs_list[50:])

                            messages.append({
                                'timestamp': 'Now',
                                'text': cleaned_text,
                                'is_agent': False
                            })
                            logger.info(f"✅ New message detected: {cleaned_text[:100]}")

                return messages

            finally:
                # Clean up screenshot
                Path(screenshot_path).unlink(missing_ok=True)

        except Exception as e:
            logger.error(f"Error reading messages: {e}")
            return []

    def mark_as_agent_message(self, text: str):
        """Mark a message as sent by the agent (to filter it out)"""
        self.agent_messages.add(text)

        # Also add to recent responses list for robust comparison
        # Remove [Agent] prefix for comparison
        clean_text = text.replace('[Agent]', '').replace('[agent]', '').strip()
        self.recent_agent_responses.append(clean_text)

        # Extract last 3 words/tokens for tail matching
        # For English: split by spaces
        # For Chinese/mixed: use last N characters if word count is low
        words = clean_text.split()

        if len(words) >= 3:
            # Use last 3 words
            self.last_agent_response_tail = ' '.join(words[-3:])
        elif len(words) > 0:
            # Use all available words
            self.last_agent_response_tail = clean_text
        else:
            # Fallback: use last 20 characters for Chinese or mixed text
            self.last_agent_response_tail = clean_text[-20:] if len(clean_text) > 20 else clean_text

        # Keep only last 10 responses
        if len(self.recent_agent_responses) > 10:
            self.recent_agent_responses = self.recent_agent_responses[-10:]

        logger.info(f"Marked as agent message: {text[:50]}...")
        logger.info(f"  → Tail for boundary detection: '{self.last_agent_response_tail}'")
        logger.info(f"  → Tracking {len(self.recent_agent_responses)} recent responses")

    def mark_as_user_message(self, text: str):
        """Mark a user message that agent is responding to (to avoid echo)"""
        normalized = self._normalize_text(text)
        self.user_messages.add(normalized)

    def load_initial_context(self) -> bool:
        """
        Load initial context by scanning current messages and marking them as detected.
        This prevents old messages from being processed as "new" when detection starts.

        Returns:
            bool: Success status
        """
        try:
            logger.info("Loading initial context from WeChat...")

            # Capture and extract current text
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
                screenshot_path = f.name

            try:
                if not self.capture_message_area(screenshot_path):
                    logger.warning("Failed to capture initial context")
                    return False

                # Extract text using Vision OCR
                current_text_lines = self.extract_text_vision(screenshot_path)

                if current_text_lines:
                    logger.info(f"Initial context: {len(current_text_lines)} text elements found")

                    # Store as previous scan
                    self.previous_raw_text = current_text_lines.copy()

                    # Mark all current text as detected to avoid processing old messages
                    for line in current_text_lines:
                        if self._is_valid_message(line):
                            cleaned = self._filter_ui_elements(line)
                            if cleaned and self._is_valid_message(cleaned):
                                normalized = self._normalize_text(cleaned)
                                self.detected_messages.add(normalized)

                    logger.info(f"✅ Initial context loaded: {len(self.detected_messages)} messages marked as seen")
                    return True
                else:
                    logger.warning("No text found in initial context")
                    return False

            finally:
                # Clean up screenshot
                Path(screenshot_path).unlink(missing_ok=True)

        except Exception as e:
            logger.error(f"Error loading initial context: {e}")
            return False

    def get_new_messages(self) -> List[Dict]:
        """Get only new messages since last check"""
        current_messages = self.read_messages()

        # Use signature-based deduplication
        last_signatures = {self._get_message_signature(msg['text']) for msg in self.last_messages}
        new_messages = []

        for msg in current_messages:
            msg_signature = self._get_message_signature(msg['text'])
            if msg_signature not in last_signatures:
                new_messages.append(msg)

        self.last_messages = current_messages
        return new_messages
