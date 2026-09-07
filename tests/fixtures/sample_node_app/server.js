const express = require('express');
const app = express();

app.get('/api/users', (req, res) => {
  res.json([{ id: 1, name: 'Alice' }]);
});

app.post('/api/users', (req, res) => {
  res.status(201).json({ success: true });
});

/**
 * Calculates sum with tax applied.
 * @param amount Base price
 * @param rate Tax rate decimal
 */
export function calculateTax(amount, rate) {
  return amount * (1 + rate);
}
