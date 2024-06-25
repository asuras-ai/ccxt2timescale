import React, { useState } from 'react';

const ConfigForm = ({ addConfig }) => {
  const [exchange, setExchange] = useState('');
  const [symbol, setSymbol] = useState('');
  const [timeframe, setTimeframe] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    addConfig({ exchange, symbol, timeframe });
    setExchange('');
    setSymbol('');
    setTimeframe('');
  };

  return (
    <form onSubmit={handleSubmit}>
      <div>
        <label>Exchange</label>
        <input type="text" value={exchange} onChange={(e) => setExchange(e.target.value)} required />
      </div>
      <div>
        <label>Symbol</label>
        <input type="text" value={symbol} onChange={(e) => setSymbol(e.target.value)} required />
      </div>
      <div>
        <label>Timeframe</label>
        <input type="text" value={timeframe} onChange={(e) => setTimeframe(e.target.value)} required />
      </div>
      <button type="submit">Add Config</button>
    </form>
  );
};

export default ConfigForm;
