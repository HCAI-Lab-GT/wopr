import { Search } from 'lucide-react';
import { forwardRef } from 'react';
import styles from './SearchBox.module.css';

function SearchBox({ query, onQueryChange, totalMatches, resultPosition }, ref) {
  function handleChange(event) {
    onQueryChange(event.target.value);
  }

  return (
    <div className={styles.search}>
      <Search className={styles.icon} size={14} />
      <input
        aria-label="Search events"
        className={styles.input}
        onChange={handleChange}
        placeholder="Search events by type, player, card (/)"
        ref={ref}
        type="search"
        value={query}
      />
      {query ? (
        <span className={styles.count}>
          {totalMatches === 0 ? 'no matches' : `${resultPosition} / ${totalMatches}`}
        </span>
      ) : null}
    </div>
  );
}

export default forwardRef(SearchBox);
