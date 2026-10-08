import { Component } from 'react';
import styles from './ErrorBoundary.module.css';

class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { error: null };
  }

  static getDerivedStateFromError(error) {
    return { error };
  }

  handleReset = () => {
    this.setState({ error: null });
  };

  render() {
    if (this.state.error) {
      return (
        <section className={styles.errorBoundary} role="alert">
          <p className={styles.eyebrow}>Replay workbench error</p>
          <h1>Unable to render this replay</h1>
          <p>{this.state.error.message}</p>
          <button className={styles.button} type="button" onClick={this.handleReset}>
            Reset view
          </button>
        </section>
      );
    }
    return this.props.children;
  }
}

export default ErrorBoundary;
