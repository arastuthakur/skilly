#!/usr/bin/env node

/**
 * Node.js cross-platform runner for Skilly.
 * Enables zero-setup execution via `npx skilly <project>` or `npm install -g skilly`.
 * Automatically detects python3 / python and executes the core analyzer.
 */

const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

const rootDir = path.resolve(__dirname, '..');
const scriptPath = path.join(rootDir, 'skilly.py');

// Find suitable python executable
function findPython() {
  const pythonBins = process.platform === 'win32'
    ? ['python.exe', 'python3.exe', 'py.exe', 'python']
    : ['python3', 'python'];

  for (const bin of pythonBins) {
    try {
      const res = require('child_process').spawnSync(bin, ['--version'], { stdio: 'pipe' });
      if (res.status === 0) {
        return bin;
      }
    } catch (e) {
      // ignore and try next
    }
  }
  return null;
}

const pythonBin = findPython();
if (!pythonBin) {
  console.error('\x1b[31m[Error]\x1b[0m Python 3 was not found in your system PATH.');
  console.error('Please install Python 3.8+ to run Skilly: https://www.python.org/downloads/');
  process.exit(1);
}

const args = [scriptPath, ...process.argv.slice(2)];
const env = Object.assign({}, process.env, {
  PYTHONPATH: `${rootDir}${path.delimiter}${process.env.PYTHONPATH || ''}`
});

const child = spawn(pythonBin, args, {
  stdio: 'inherit',
  env: env
});

child.on('close', (code) => {
  process.exit(code || 0);
});

child.on('error', (err) => {
  console.error('\x1b[31mFailed to start Skilly:\x1b[0m', err.message);
  process.exit(1);
});
