import batchSummary from './batch_summary.json';
import replay101 from './seed-101.replay.json';
import traces101 from './seed-101.replay.traces.json';
import replay102 from './seed-102.replay.json';
import traces102 from './seed-102.replay.traces.json';
import replay103 from './seed-103.replay.json';
import traces103 from './seed-103.replay.traces.json';

function makeFile(name, content) {
  return new File([JSON.stringify(content)], name, { type: 'application/json' });
}

const files = [
  ['summary.json', makeFile('summary.json', batchSummary)],
  ['seed-101.replay.json', makeFile('seed-101.replay.json', replay101)],
  ['seed-101.replay.traces.json', makeFile('seed-101.replay.traces.json', traces101)],
  ['seed-102.replay.json', makeFile('seed-102.replay.json', replay102)],
  ['seed-102.replay.traces.json', makeFile('seed-102.replay.traces.json', traces102)],
  ['seed-103.replay.json', makeFile('seed-103.replay.json', replay103)],
  ['seed-103.replay.traces.json', makeFile('seed-103.replay.traces.json', traces103)],
];

export { files };
