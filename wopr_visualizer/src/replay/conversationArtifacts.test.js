import { describe, expect, it } from 'vitest';
import { normalizeConversationArtifacts } from './conversationArtifacts.js';

describe('normalizeConversationArtifacts', () => {
  it('returns an explicit no-press source for absent artifacts', () => {
    expect(normalizeConversationArtifacts(null)).toEqual({ messages: [], source: 'none' });
  });

  it('normalizes public and private press records without inferring motives', () => {
    const normalized = normalizeConversationArtifacts({
      press: [
        { turn: 2, speaker: 'player_0', audience: 'public', text: 'Hold fire.', visibility: 'public' },
        { turn: 2, speaker: 'player_1', audience: 'player_0', text: 'I will intercept.', visibility: 'private' },
      ],
    });

    expect(normalized.source).toBe('press');
    expect(normalized.messages).toEqual([
      {
        id: 'press-0',
        turn: 2,
        speaker: 'player_0',
        speakerLabel: 'Player 0',
        audience: 'public',
        audienceLabel: 'Public',
        text: 'Hold fire.',
        visibility: 'public',
      },
      {
        id: 'press-1',
        turn: 2,
        speaker: 'player_1',
        speakerLabel: 'Player 1',
        audience: 'player_0',
        audienceLabel: 'Player 0',
        text: 'I will intercept.',
        visibility: 'private',
      },
    ]);
  });
});
