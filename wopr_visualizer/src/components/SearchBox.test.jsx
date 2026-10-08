import { fireEvent, render, screen } from '@testing-library/react';
import { createRef } from 'react';
import { describe, expect, it, vi } from 'vitest';
import SearchBox from './SearchBox.jsx';

describe('SearchBox', () => {
  it('forwards the ref to the input', () => {
    const ref = createRef();
    render(<SearchBox onQueryChange={() => {}} query="" ref={ref} />);

    expect(ref.current.tagName).toBe('INPUT');
  });

  it('emits query changes', () => {
    const onQueryChange = vi.fn();
    render(<SearchBox onQueryChange={onQueryChange} query="" />);

    fireEvent.change(screen.getByLabelText('Search events'), { target: { value: 'launch' } });
    expect(onQueryChange).toHaveBeenLastCalledWith('launch');
  });

  it('shows the match position while a query is active', () => {
    render(<SearchBox onQueryChange={() => {}} query="war" resultPosition={2} totalMatches={5} />);

    expect(screen.getByText('2 / 5')).toBeInTheDocument();
  });

  it('shows no-matches text when total is zero with a query', () => {
    render(<SearchBox onQueryChange={() => {}} query="zzz" resultPosition={0} totalMatches={0} />);

    expect(screen.getByText('no matches')).toBeInTheDocument();
  });

  it('hides the count when query is empty', () => {
    render(<SearchBox onQueryChange={() => {}} query="" resultPosition={0} totalMatches={0} />);

    expect(screen.queryByText(/no matches/)).not.toBeInTheDocument();
  });
});
