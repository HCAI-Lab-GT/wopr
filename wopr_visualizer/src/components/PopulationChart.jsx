import { populationSeries, seriesBounds } from '../replay/populationSeries.js';
import styles from './PopulationChart.module.css';

const LINE_COLORS = [
  'var(--chart-line-0)',
  'var(--chart-line-1)',
  'var(--chart-line-2)',
  'var(--chart-line-3)',
  'var(--chart-line-4)',
  'var(--chart-line-5)',
];
const VIEW_WIDTH = 640;
const VIEW_HEIGHT = 220;
const PAD_LEFT = 36;
const PAD_BOTTOM = 24;
const PAD_TOP = 12;
const PAD_RIGHT = 12;

function PopulationChart({ frames, onSelectTurn, selectedTurn }) {
  const ids = Object.keys(frames[0]?.afterState?.players ?? {}).sort();
  const { turns, series } = populationSeries(frames, ids);
  const { min, max } = seriesBounds(series);
  const plotWidth = VIEW_WIDTH - PAD_LEFT - PAD_RIGHT;
  const plotHeight = VIEW_HEIGHT - PAD_TOP - PAD_BOTTOM;
  const xStep = turns.length > 1 ? plotWidth / (turns.length - 1) : 0;

  return (
    <div className={styles.chartPanel}>
      <header className={styles.sectionHeader}>
        <div>
          <p className={styles.eyebrow}>Population over turns</p>
          <h2>Per-player population by turn</h2>
        </div>
        <ul className={styles.legend}>
          {ids.map((id, index) => (
            <li key={id} className={styles.legendItem}>
              <span className={styles.swatch} style={{ background: colorFor(index) }} />
              {id.replace('_', ' ')}
            </li>
          ))}
        </ul>
      </header>
      <svg
        aria-label="Population chart"
        className={styles.svg}
        role="img"
        viewBox={`0 0 ${VIEW_WIDTH} ${VIEW_HEIGHT}`}
      >
        {renderGrid({ plotWidth, plotHeight, turns, min, max })}
        {ids.map((id, index) => (
          <polyline
            className={styles.line}
            fill="none"
            key={id}
            points={pointsFor(series[id], turns.length, xStep, plotHeight, min, max)}
            stroke={colorFor(index)}
            strokeWidth={2}
          />
        ))}
        {ids.map((id, index) =>
          series[id].map((value, pointIndex) => {
            const turn = turns[pointIndex];
            const isActive = turn === selectedTurn;
            return (
              <circle
                className={styles.point}
                cx={xFor(pointIndex, xStep)}
                cy={yFor(value, plotHeight, min, max)}
                fill={colorFor(index)}
                key={`${id}-${pointIndex}`}
                onClick={() => onSelectTurn?.(turn)}
                r={isActive ? 4 : 2.5}
              />
            );
          }),
        )}
      </svg>
    </div>
  );
}

function renderGrid({ plotWidth, plotHeight, turns, min, max }) {
  const lines = [];
  const steps = 4;
  for (let i = 0; i <= steps; i += 1) {
    const y = PAD_TOP + (plotHeight / steps) * i;
    const value = Math.round(max - ((max - min) / steps) * i);
    lines.push(
      <g key={`grid-${i}`}>
        <line
          className={styles.gridLine}
          x1={PAD_LEFT}
          x2={PAD_LEFT + plotWidth}
          y1={y}
          y2={y}
        />
        <text className={styles.axisLabel} x={PAD_LEFT - 6} y={y + 3} textAnchor="end">
          {value}
        </text>
      </g>,
    );
  }
  const xLabels = turns.length > 8 ? turns.filter((_, i) => i % Math.ceil(turns.length / 8) === 0) : turns;
  xLabels.forEach((turn) => {
    const pointIndex = turns.indexOf(turn);
    lines.push(
      <text
        className={styles.axisLabel}
        key={`x-${turn}`}
        x={xFor(pointIndex, plotWidth / Math.max(turns.length - 1, 1))}
        y={VIEW_HEIGHT - 6}
        textAnchor="middle"
      >
        {turn}
      </text>,
    );
  });
  return lines;
}

function pointsFor(values, count, xStep, plotHeight, min, max) {
  return values
    .map((value, index) => `${xFor(index, xStep)},${yFor(value, plotHeight, min, max)}`)
    .join(' ');
}

function xFor(index, xStep) {
  return PAD_LEFT + index * xStep;
}

function yFor(value, plotHeight, min, max) {
  const range = max - min || 1;
  return PAD_TOP + plotHeight - ((value - min) / range) * plotHeight;
}

function colorFor(index) {
  return LINE_COLORS[index % LINE_COLORS.length];
}

export default PopulationChart;
