import { fireEvent, render, screen } from '@testing-library/react';
import { describe, expect, it, vi } from 'vitest';
import RunList from './RunList.jsx';
import sampleSummary from '../data/batch_summary.json';
import seed101Replay from '../data/seed-101.replay.json';

function filesMap() {
  return new Map(
    sampleSummary.results.map((result) => [
      result.replay_path,
      { name: result.replay_path, text: () => Promise.resolve(JSON.stringify(sampleReplayForSeed(result.seed))) },
    ]),
  );
}

function sampleReplayForSeed(seed) {
  return { ...seed101Replay, seed };
}

describe('RunList', () => {
  it('renders a row per result', () => {
    render(<RunList summary={sampleSummary} dirFiles={new Map()} onSelectRun={() => {}} />);
    sampleSummary.results.forEach((result) => {
      expect(screen.getByText(result.replay_path)).toBeInTheDocument();
    });
  });

  it('marks rows disabled when dirFiles is empty', () => {
    render(<RunList summary={sampleSummary} dirFiles={new Map()} onSelectRun={() => {}} />);
    const firstRow = screen.getByText(sampleSummary.results[0].replay_path).closest('tr');
    expect(firstRow).toHaveAttribute('aria-disabled', 'true');
  });

  it('invokes onSelectRun with the row when clicked and resolvable', () => {
    const onSelectRun = vi.fn();
    render(<RunList summary={sampleSummary} dirFiles={filesMap()} onSelectRun={onSelectRun} />);
    fireEvent.click(screen.getByText(sampleSummary.results[0].replay_path).closest('tr'));
    expect(onSelectRun).toHaveBeenCalledTimes(1);
    expect(onSelectRun.mock.calls[0][0]).toMatchObject({
      seed: sampleSummary.results[0].seed,
      replayPath: sampleSummary.results[0].replay_path,
    });
  });
});
