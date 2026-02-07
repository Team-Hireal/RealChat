/**
 * Sound Notification Service
 * Plays audio notifications for various app events
 */

import AudioGenerator from './audioGenerator';

class SoundService {
  constructor() {
    this.audioGenerator = new AudioGenerator();
    this.sounds = {};
    this.useAudioFiles = false; // Set to true if you add audio files
    this.enabled = true;

    // Try to load audio files (optional)
    if (this.useAudioFiles) {
      this.sounds = {
        complete: new Audio('/sounds/complete.mp3'),
        message: new Audio('/sounds/message.mp3'),
        alert: new Audio('/sounds/alert.mp3'),
        success: new Audio('/sounds/success.mp3'),
      };

      // Set default volume
      Object.values(this.sounds).forEach(sound => {
        sound.volume = 0.5;
      });
    }
  }

  /**
   * Play a notification sound
   * @param {string} type - Type of sound (complete, message, alert, success)
   */
  play(type) {
    if (!this.enabled) return;

    if (this.useAudioFiles && this.sounds[type]) {
      // Use audio file if available
      const sound = this.sounds[type];
      sound.currentTime = 0;
      sound.play().catch(err => {
        console.warn('Failed to play sound file, using generator:', err);
        this.playWithGenerator(type);
      });
    } else {
      // Use audio generator
      this.playWithGenerator(type);
    }
  }

  /**
   * Play sound using Web Audio API generator
   */
  playWithGenerator(type) {
    switch (type) {
      case 'complete':
        this.audioGenerator.playComplete();
        break;
      case 'message':
        this.audioGenerator.playMessage();
        break;
      case 'alert':
        this.audioGenerator.playAlert();
        break;
      case 'success':
        this.audioGenerator.playSuccess();
        break;
    }
  }

  /**
   * Play sound when AI completes response
   */
  playComplete() {
    this.play('complete');
  }

  /**
   * Play sound when new message received
   */
  playMessage() {
    this.play('message');
  }

  /**
   * Play sound for alerts/errors
   */
  playAlert() {
    this.play('alert');
  }

  /**
   * Play sound for success actions
   */
  playSuccess() {
    this.play('success');
  }

  /**
   * Enable/disable all sounds
   */
  setEnabled(enabled) {
    this.enabled = enabled;
    this.audioGenerator.setEnabled(enabled);
  }

  /**
   * Set volume for all sounds (0.0 to 1.0)
   */
  setVolume(volume) {
    if (this.useAudioFiles) {
      Object.values(this.sounds).forEach(sound => {
        sound.volume = Math.max(0, Math.min(1, volume));
      });
    }
  }
}

// Create singleton instance
const soundService = new SoundService();

export default soundService;
