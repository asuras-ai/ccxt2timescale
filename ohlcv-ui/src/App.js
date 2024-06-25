import React, { useState, useEffect } from 'react';
import axios from 'axios';
import DataTable from './DataTable';
import ConfigForm from './ConfigForm';

const App = () => {
  const [configs, setConfigs] = useState([]);
  const [filters, setFilters] = useState({ exchange: '', symbol: '', timeframe: '' });

  useEffect(() => {
    fetchConfigs();
  }, []);

  const fetchConfigs = async () => {
    const response = await axios.get('/api/configs');
    setConfigs(response.data);
  };

  const addConfig = async (newConfig) => {
    await axios.post('/api/configs', newConfig);
    fetchConfigs();
  };

  return (
    <div className="container">
      <h1>OHLCV Configurations</h1>
      <ConfigForm addConfig={addConfig} />
      <DataTable configs={configs} filters={filters} setFilters={setFilters} />
    </div>
  );
};

export default App;
