"use client";

/**
 * Arcade Sound Effects using Web Audio API
 * No external files needed - pure synthetics
 */

class AudioManager {
  private audioContext: AudioContext | null = null;
  private masterGain: GainNode | null = null;

  constructor() {
    // Lazy init - only create when first sound plays
  }

  private ensureContext() {
    if (!this.audioContext) {
      this.audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
      this.masterGain = this.audioContext.createGain();
      this.masterGain.connect(this.audioContext.destination);
      this.masterGain.gain.value = 0.3; // 30% volume to not blast user
    }
  }

  /**
   * Post published - satisfying whoosh
   */
  playPostWhoosh() {
    this.ensureContext();
    if (!this.audioContext || !this.masterGain) return;

    const ctx = this.audioContext;
    const now = ctx.currentTime;

    // Descending frequency sweep (whoosh)
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();

    osc.type = "sine";
    osc.frequency.setValueAtTime(800, now);
    osc.frequency.exponentialRampToValueAtTime(200, now + 0.3);

    gain.gain.setValueAtTime(0.3, now);
    gain.gain.exponentialRampToValueAtTime(0.01, now + 0.3);

    osc.connect(gain);
    gain.connect(this.masterGain!);

    osc.start(now);
    osc.stop(now + 0.3);
  }

  /**
   * Stat update - sharp ding
   */
  playStatDing() {
    this.ensureContext();
    if (!this.audioContext || !this.masterGain) return;

    const ctx = this.audioContext;
    const now = ctx.currentTime;

    // Bell-like ding (higher frequency)
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();

    osc.type = "sine";
    osc.frequency.setValueAtTime(1200, now);

    gain.gain.setValueAtTime(0.2, now);
    gain.gain.exponentialRampToValueAtTime(0.01, now + 0.2);

    osc.connect(gain);
    gain.connect(this.masterGain!);

    osc.start(now);
    osc.stop(now + 0.2);

    // Add harmonics for richness
    const osc2 = ctx.createOscillator();
    const gain2 = ctx.createGain();

    osc2.type = "sine";
    osc2.frequency.setValueAtTime(1800, now);

    gain2.gain.setValueAtTime(0.1, now);
    gain2.gain.exponentialRampToValueAtTime(0.01, now + 0.15);

    osc2.connect(gain2);
    gain2.connect(this.masterGain!);

    osc2.start(now);
    osc2.stop(now + 0.15);
  }

  /**
   * Dogpile / Hater Winter - jarring glitch
   */
  playGlitch() {
    this.ensureContext();
    if (!this.audioContext || !this.masterGain) return;

    const ctx = this.audioContext;
    const now = ctx.currentTime;

    // Harsh, descending glitch (white noise + tone)
    const noise = ctx.createBufferSource();
    const buffer = ctx.createBuffer(1, ctx.sampleRate * 0.1, ctx.sampleRate);
    const data = buffer.getChannelData(0);
    for (let i = 0; i < buffer.length; i++) {
      data[i] = Math.random() * 2 - 1;
    }
    noise.buffer = buffer;

    const gainNoise = ctx.createGain();
    gainNoise.gain.setValueAtTime(0.4, now);
    gainNoise.gain.exponentialRampToValueAtTime(0.01, now + 0.15);

    noise.connect(gainNoise);
    gainNoise.connect(this.masterGain!);

    noise.start(now);

    // Also add a descending sine tone for the glitch
    const osc = ctx.createOscillator();
    const gainOsc = ctx.createGain();

    osc.type = "sawtooth";
    osc.frequency.setValueAtTime(600, now);
    osc.frequency.exponentialRampToValueAtTime(100, now + 0.1);

    gainOsc.gain.setValueAtTime(0.2, now);
    gainOsc.gain.exponentialRampToValueAtTime(0.01, now + 0.1);

    osc.connect(gainOsc);
    gainOsc.connect(this.masterGain!);

    osc.start(now);
    osc.stop(now + 0.1);
  }

  /**
   * Propaganda purchase / Money spent - cash register cha-ching
   */
  playChaChing() {
    this.ensureContext();
    if (!this.audioContext || !this.masterGain) return;

    const ctx = this.audioContext;
    const now = ctx.currentTime;

    // Ascending arpeggio (do-mi-sol) like a cash register
    const frequencies = [523.25, 659.25, 783.99]; // C5, E5, G5
    let time = now;

    frequencies.forEach((freq, idx) => {
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();

      osc.type = "sine";
      osc.frequency.setValueAtTime(freq, time);

      const duration = 0.1;
      gain.gain.setValueAtTime(0.2, time);
      gain.gain.exponentialRampToValueAtTime(0.01, time + duration);

      osc.connect(gain);
      gain.connect(this.masterGain!);

      osc.start(time);
      osc.stop(time + duration);

      time += 0.08; // Slight overlap between notes
    });

    // Final "ching" - high sine wave decay
    const ching = ctx.createOscillator();
    const chingGain = ctx.createGain();

    ching.type = "sine";
    ching.frequency.setValueAtTime(1047.0, now + 0.25); // C6

    chingGain.gain.setValueAtTime(0.3, now + 0.25);
    chingGain.gain.exponentialRampToValueAtTime(0.01, now + 0.5);

    ching.connect(chingGain);
    chingGain.connect(this.masterGain!);

    ching.start(now + 0.25);
    ching.stop(now + 0.5);
  }

  /**
   * Deplatforming / Game Over - ominous descending tone
   */
  playGameOver() {
    this.ensureContext();
    if (!this.audioContext || !this.masterGain) return;

    const ctx = this.audioContext;
    const now = ctx.currentTime;

    // Deep, descending gamelan-like sound
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();

    osc.type = "sine";
    osc.frequency.setValueAtTime(400, now);
    osc.frequency.exponentialRampToValueAtTime(50, now + 1);

    gain.gain.setValueAtTime(0.4, now);
    gain.gain.exponentialRampToValueAtTime(0.01, now + 1);

    osc.connect(gain);
    gain.connect(this.masterGain!);

    osc.start(now);
    osc.stop(now + 1);
  }

  /**
   * Mute/unmute all audio
   */
  setMasterVolume(volume: number) {
    this.ensureContext();
    if (this.masterGain) {
      this.masterGain.gain.value = Math.max(0, Math.min(1, volume));
    }
  }
}

// Singleton instance
const audioManager = new AudioManager();

export function useAudio() {
  return {
    postWhoosh: () => audioManager.playPostWhoosh(),
    statDing: () => audioManager.playStatDing(),
    glitch: () => audioManager.playGlitch(),
    chaChing: () => audioManager.playChaChing(),
    gameOver: () => audioManager.playGameOver(),
    setVolume: (v: number) => audioManager.setMasterVolume(v),
  };
}
