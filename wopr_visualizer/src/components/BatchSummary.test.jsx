import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import BatchSummary from './BatchSummary.jsx';
import sampleSummary from '../data/batch_summary.json';

describe('BatchSummary', () => {
  it('renders run and player counts from the fixture', () => {
    render(<BatchSummary summary={sampleSummary} />);
    expect(screen.getByText(/3 runs, 4 players/)).toBeInTheDocument();
    expect(screen.getByText('table')).toBeInTheDocument();
  });

  it('renders an agent outcomes row per agent', () => {
    render(<BatchSummary summary={sampleSummary} />);
    expect(screen.getAllByText('heuristic').length).toBeGreaterThan(0);
    expect(screen.getAllByText('random').length).toBeGreaterThan(0);
    expect(screen.getAllByText('decision_heuristic').length).toBeGreaterThan(0);
  });

  it('shows no-provider-data messaging when provider fields absent', () => {
    render(<BatchSummary summary={sampleSummary} />);
    expect(screen.getByText('No provider data')).toBeInTheDocument();
  });

  it('renders winner and termination counts', () => {
    render(<BatchSummary summary={sampleSummary} />);
    expect(screen.getByText('Winners')).toBeInTheDocument();
    expect(screen.getByText('Termination reasons')).toBeInTheDocument();
  });
});
