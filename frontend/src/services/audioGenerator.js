/**
 * Web Audio API Sound Generator
 * Generates notification sounds programmatically when audio files are not available
 */

class AudioGenerator {
  constructor() {
    this.audioContext = null;
    this.enabled = true;
  }

  /**
   * Initialize audio context (must be called after user interaction)
   */
  init() {
    if (!this.audioContext) {
      this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
    }
  }

  /**
   * Play a tone with specified frequency and duration
   */
  playTone(frequency, duration, type = 'sine') {
    if (!this.enabled) return;

    try {
      this.init();

      const oscillator = this.audioContext.createOscillator();
      const gainNode = this.audioContext.createGain();

      oscillator.connect(gainNode);
      gainNode.connect(this.audioContext.destination);

      oscillator.frequency.value = frequency;
      oscillator.type = type;

      // Envelope for smooth sound
      gainNode.gain.setValueAtTime(0, this.audioContext.currentTime);
      gainNode.gain.linearRampToValueAtTime(0.3, this.audioContext.currentTime + 0.01);
      gainNode.gain.exponentialRampToValueAtTime(0.01, this.audioContext.currentTime + duration);

      oscillator.start(this.audioContext.currentTime);
      oscillator.stop(this.audioContext.currentTime + duration);
    } catch (err) {
      console.warn('Failed to play tone:', err);
    }
  }

  /**
   * Play completion sound (ascending notes)
   */
  playComplete() {
    this.playTone(523.25, 0.1); // C5
    setTimeout(() => this.playTone(659.25, 0.1), 100); // E5
    setTimeout(() => this.playTone(783.99, 0.15), 200); // G5
  }

  /**
   * Play message notification (two quick beeps)
   */
  playMessage() {
    this.playTone(800, 0.08);
    setTimeout(() => this.playTone(1000, 0.08), 100);
  }

  /**
   * Play alert sound (lower, urgent tone)
   */
  playAlert() {
    this.playTone(400, 0.15);
    setTimeout(() => this.playTone(350, 0.15), 150);
  }

  /**
   * Play success sound (single pleasant tone)
   */
  playSuccess() {
    this.playTone(880, 0.12); // A5
  }

  /**
   * Enable/disable sounds
   */
  setEnabled(enabled) {
    this.enabled = enabled;
  }
}

export default AudioGenerator;
