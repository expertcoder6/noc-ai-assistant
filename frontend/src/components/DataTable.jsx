import React, { useState } from 'react';
import { Table, Eye, EyeOff, Copy, Download, Check } from 'lucide-react';

export const DataTable = ({ data }) => {
  const [expanded, setExpanded] = useState(false);
  const [copied, setCopied] = useState(false);
  
  if (!Array.isArray(data) || data.length === 0) return null;

  const toggle = () => setExpanded((prev) => !prev);
  const columns = Object.keys(data[0]);

  // Copy data to clipboard as TSV (Tab Separated Values)
  const handleCopy = async () => {
    try {
      const headers = columns.join('\t');
      const rows = data.map((row) => columns.map((col) => row[col]).join('\t'));
      const text = [headers, ...rows].join('\n');
      
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy text: ', err);
    }
  };

  // Export data as a raw CSV file
  const handleExport = () => {
    const headers = columns.join(',');
    const rows = data.map((row) => 
      columns.map((col) => {
        const cell = String(row[col]).replace(/"/g, '""');
        return `"${cell}"`;
      }).join(',')
    );
    const csvContent = "data:text/csv;charset=utf-8," + [headers, ...rows].join('\n');
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `telemetry_export_${Date.now()}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="mt-3.5 pt-3.5 border-t border-slate-800/80">
      <div className="flex flex-wrap items-center justify-between gap-3">
        {/* Toggle Telemetry Button */}
        <button
          type="button"
          onClick={toggle}
          className="flex items-center gap-1.5 px-3 py-1.5 bg-slate-950 border border-slate-850 hover:border-slate-800 hover:text-slate-200 text-slate-400 text-xs font-semibold rounded-lg font-mono tracking-wide transition-all shadow-sm select-none cursor-pointer"
        >
          {expanded ? (
            <>
              <EyeOff className="w-3.5 h-3.5" />
              <span>Hide raw telemetry ({data.length} records)</span>
            </>
          ) : (
            <>
              <Table className="w-3.5 h-3.5" />
              <span>Show raw telemetry ({data.length} records)</span>
            </>
          )}
        </button>

        {/* Action Panel (Visible only when expanded) */}
        {expanded && (
          <div className="flex items-center gap-2">
            {/* Copy Clipboard */}
            <button
              type="button"
              onClick={handleCopy}
              className="flex items-center gap-1 px-2.5 py-1.5 bg-slate-900 border border-slate-850 text-slate-400 hover:text-slate-200 hover:border-slate-800 rounded-lg text-[10px] font-mono font-bold transition-all cursor-pointer shadow-sm active:scale-95"
              title="Copy to Clipboard"
            >
              {copied ? (
                <>
                  <Check className="w-3.5 h-3.5 text-emerald-400" />
                  <span className="text-emerald-400">Copied!</span>
                </>
              ) : (
                <>
                  <Copy className="w-3.5 h-3.5" />
                  <span>Copy TSV</span>
                </>
              )}
            </button>

            {/* Export CSV */}
            <button
              type="button"
              onClick={handleExport}
              className="flex items-center gap-1 px-2.5 py-1.5 bg-slate-900 border border-slate-850 text-slate-400 hover:text-slate-200 hover:border-slate-800 rounded-lg text-[10px] font-mono font-bold transition-all cursor-pointer shadow-sm active:scale-95"
              title="Download CSV file"
            >
              <Download className="w-3.5 h-3.5" />
              <span>Export CSV</span>
            </button>
          </div>
        )}
      </div>

      {expanded && (
        <div className="mt-2.5 max-h-56 overflow-auto bg-slate-950 border border-slate-850 rounded-xl shadow-inner scrollbar-thin scrollbar-track-transparent scrollbar-thumb-slate-800">
          <table className="min-w-full text-[10px] font-mono text-slate-300">
            <thead className="bg-slate-900 border-b border-slate-850 text-slate-400 uppercase tracking-wider font-bold sticky top-0">
              <tr>
                {columns.map((col) => (
                  <th key={col} className="px-3 py-2 text-left" scope="col">
                    {col}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-900">
              {data.map((row, idx) => (
                <tr
                  key={idx}
                  className="hover:bg-slate-900/50 transition-colors animate-in fade-in duration-100"
                >
                  {columns.map((col) => {
                    const val = row[col];
                    const isIP = typeof val === 'string' && val.match(/^\d+\.\d+\.\d+\.\d+$/);
                    const isDown = String(val).toLowerCase() === 'down';
                    const isUp = String(val).toLowerCase() === 'up';
                    
                    let cellColor = 'text-slate-300';
                    if (isIP) cellColor = 'text-cyan-400 font-bold';
                    else if (isDown) cellColor = 'text-rose-400 font-bold';
                    else if (isUp) cellColor = 'text-emerald-400 font-bold';
                    
                    return (
                      <td key={col} className={`px-3 py-2 ${cellColor}`}>
                        {String(val)}
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};
