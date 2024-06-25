import React from 'react';
import { useTable, useFilters } from 'react-table';

const DataTable = ({ configs, filters, setFilters }) => {
  const data = React.useMemo(() => configs, [configs]);
  const columns = React.useMemo(() => [
    { Header: 'Exchange', accessor: 'exchange' },
    { Header: 'Symbol', accessor: 'symbol' },
    { Header: 'Timeframe', accessor: 'timeframe' },
    { Header: 'First Timestamp', accessor: 'first_timestamp' },
    { Header: 'Last Timestamp', accessor: 'last_timestamp' },
  ], []);

  const {
    getTableProps,
    getTableBodyProps,
    headerGroups,
    rows,
    prepareRow,
    setFilter
  } = useTable({ columns, data }, useFilters);

  const handleFilterChange = (e) => {
    const { name, value } = e.target;
    setFilters((prev) => ({ ...prev, [name]: value }));
    setFilter(name, value);
  };

  return (
    <div>
      <div>
        <label>Filter Exchange</label>
        <input name="exchange" value={filters.exchange} onChange={handleFilterChange} />
        <label>Filter Symbol</label>
        <input name="symbol" value={filters.symbol} onChange={handleFilterChange} />
        <label>Filter Timeframe</label>
        <input name="timeframe" value={filters.timeframe} onChange={handleFilterChange} />
      </div>
      <table {...getTableProps()}>
        <thead>
          {headerGroups.map(headerGroup => (
            <tr {...headerGroup.getHeaderGroupProps()}>
              {headerGroup.headers.map(column => (
                <th {...column.getHeaderProps()}>{column.render('Header')}</th>
              ))}
            </tr>
          ))}
        </thead>
        <tbody {...getTableBodyProps()}>
          {rows.map(row => {
            prepareRow(row);
            return (
              <tr {...row.getRowProps()}>
                {row.cells.map(cell => (
                  <td {...cell.getCellProps()}>{cell.render('Cell')}</td>
                ))}
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
};

export default DataTable;
