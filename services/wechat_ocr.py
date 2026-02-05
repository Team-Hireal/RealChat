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
                # Leave small margins on all sides
                msg_x = x + 10  # Small left margin
                msg_y = y + 60  # Below title bar (smaller for pop-ups)
                msg_w = w - 20  # Full width minus margins
                msg_h = h - 140  # Exclude title and input area
                logger.info(f"Detected pop-up window (w={w})")
            else:
                # Main window: has sidebar on left
                # Sidebar is approximately 30-35% of width, but adapt to actual size
                sidebar_width = int(w * 0.32)  # Slightly adjusted

                # Title bar height scales with window size
                title_height = max(60, int(h * 0.08))  # 8% of height or 60px minimum

                # Input area at bottom scales with window size
                input_height = max(100, int(h * 0.12))  # 12% of height or 100px minimum

                msg_x = x + sidebar_width + 10  # After sidebar plus small margin
                msg_y = y + title_height
                msg_w = w - sidebar_width - 30  # Remaining width minus margins
                msg_h = h - title_height - input_height
                logger.info(f"Detected main window (w={w}), sidebar={sidebar_width}px")

            logger.info(f"Message area: x={msg_x}, y={msg_y}, w={msg_w}, h={msg_h}")

            # Capture screenshot of message area only
            cmd = [
                'screencapture',
                '-x',  # No sound
                '-R', f"{msg_x},{msg_y},{msg_w},{msg_h}",  # Region
                output_path
            ]

            result = subprocess.run(cmd, capture_output=True, timeout=10)
            if result.returncode == 0:
                logger.info(f"Screenshot captured: {output_path}")
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

        # Add last message
        if current_message:
            messages.append(current_message)

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
                text_lines = self.extract_text_vision(screenshot_path)

                if not text_lines:
                    logger.warning("No text extracted from screenshot")
                    return []

                # Parse into messages
                messages = self.parse_messages(text_lines)

                # Filter out agent's own messages
                new_messages = []
                for msg in messages:
                    msg_text = msg['text']
                    if msg_text not in self.agent_messages:
                        new_messages.append(msg)

                logger.info(f"Read {len(new_messages)} new messages")
                return new_messages

            finally:
                # Clean up screenshot
                Path(screenshot_path).unlink(missing_ok=True)

        except Exception as e:
            logger.error(f"Error reading messages: {e}")
            return []

    def mark_as_agent_message(self, text: str):
        """Mark a message as sent by the agent (to filter it out)"""
        self.agent_messages.add(text)

    def get_new_messages(self) -> List[Dict]:
        """
        Get only new messages since last check

        Returns:
            List of new message dictionaries
        """
        current_messages = self.read_messages()

        # Find messages not in last_messages
        last_texts = {msg['text'] for msg in self.last_messages}
        new_messages = [msg for msg in current_messages if msg['text'] not in last_texts]

        # Update last_messages
        self.last_messages = current_messages

        return new_messages
