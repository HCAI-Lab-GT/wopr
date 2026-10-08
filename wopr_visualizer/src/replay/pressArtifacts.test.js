import { describe, expect, it } from 'vitest';
import {
  normalizePressArtifacts,
  parsePressArtifactJson,
} from './pressArtifacts.js';

const replay = {
  mode: 'table',
  seed: 81,
  agent: 'decision_heuristic',
  players: 4,
  turns: 2,
};

describe('parsePressArtifactJson', () => {
  it('validates schema_version, press_mode, and replay reference', () => {
    const payload = {
      schema_version: 1,
      press_mode: 'press_light',
      replay,
      messages: [],
    };
    expect(parsePressArtifactJson(JSON.stringify(payload), replay)).toEqual(payload);
  });

  it('rejects mismatched replay reference', () => {
    const payload = {
      schema_version: 1,
      press_mode: 'press_light',
      replay: { ...replay, seed: 999 },
      messages: [],
    };
    expect(() => parsePressArtifactJson(JSON.stringify(payload), replay)).toThrow();
  });

  it('rejects unknown press_mode', () => {
    const payload = {
      schema_version: 1,
      press_mode: 'bogus',
      replay,
      messages: [],
    };
    expect(() => parsePressArtifactJson(JSON.stringify(payload), replay)).toThrow();
  });
});

describe('normalizePressArtifacts', () => {
  it('returns no-press source for absent artifacts', () => {
    expect(normalizePressArtifacts(null)).toEqual({ messages: [], source: 'none' });
  });

  it('normalizes messages into conversation shape', () => {
    const normalized = normalizePressArtifacts({
      messages: [
        {
          message_id: 'press:2:player_0:1',
          turn: 2,
          speaker: 'player_0',
          audience: 'public',
          visibility: 'public',
          text: 'Hold fire.',
        },
      ],
    });

    expect(normalized.source).toBe('press');
    expect(normalized.messages).toEqual([
      {
        id: 'press:2:player_0:1',
        turn: 2,
        speaker: 'player_0',
        speakerLabel: 'Player 0',
        audience: 'public',
        audienceLabel: 'Public',
        text: 'Hold fire.',
        visibility: 'public',
        recipient: null,
        recipientLabel: 'Unknown',
        commitment: null,
      },
    ]);
  });

  it('normalizes private whispers with recipient and commitment', () => {
    const normalized = normalizePressArtifacts({
      messages: [
        {
          message_id: 'press:3:player_1:1',
          turn: 3,
          speaker: 'player_1',
          audience: 'player_0',
          visibility: 'private',
          recipient: 'player_0',
          text: 'Stand down.',
          commitment: { kind: 'stand_down', target_round: 4 },
        },
      ],
    });

    expect(normalized.messages[0]).toEqual({
      id: 'press:3:player_1:1',
      turn: 3,
      speaker: 'player_1',
      speakerLabel: 'Player 1',
      audience: 'player_0',
      audienceLabel: 'Player 0',
      text: 'Stand down.',
      visibility: 'private',
      recipient: 'player_0',
      recipientLabel: 'Player 0',
      commitment: { kind: 'stand_down', target_round: 4 },
    });
  });
});
