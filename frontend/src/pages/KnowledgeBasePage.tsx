/**
 * Page 4: Interactive Knowledge Graph Visualizer & Entity Explorer.
 */
import React, { useState, useEffect } from 'react';
import { Network, RefreshCw, Search, Sparkles, Filter } from 'lucide-react';
import { api } from '../api/endpoints';
import { useAuth } from '../context/AuthContext';

export const KnowledgeBasePage: React.FC = () => {
  const { activeWorkspace } = useAuth();
  const [graphData, setGraphData] = useState<{ nodes: any[]; edges: any[] }>({ nodes: [], edges: [] });
  const [isLoading, setIsLoading] = useState(true);
  const [selectedNode, setSelectedNode] = useState<any | null>(null);
  const [filterType, setFilterType] = useState('all');
  const [isExtracting, setIsExtracting] = useState(false);

  const fetchGraph = async () => {
    setIsLoading(true);
    try {
      const data = await api.getGraph(60);
      setGraphData(data);
      if (data.nodes.length > 0) {
        setSelectedNode(data.nodes[0]);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleExtractAll = async () => {
    setIsExtracting(true);
    try {
      await api.extractAllEntities();
      await fetchGraph();
    } catch (err: any) {
      alert(`Extraction error: ${err.message}`);
    } finally {
      setIsExtracting(false);
    }
  };

  useEffect(() => {
    fetchGraph();
  }, [activeWorkspace?.id]);

  const filteredNodes = graphData.nodes.filter((n) => filterType === 'all' || n.type === filterType);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Enterprise Knowledge Graph</h1>
          <p className="text-sm text-slate-400">Explore extracted organizational entities, requirements, and cross-document relationships.</p>
        </div>
        <div className="flex items-center gap-2">
          <select
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
            className="px-3 py-2 rounded-lg bg-slate-900 border border-slate-800 text-xs text-slate-300"
          >
            <option value="all">All Entity Types</option>
            <option value="Requirement">Requirements</option>
            <option value="Organization">Organizations</option>
            <option value="Product">Products</option>
            <option value="Metric">Metrics</option>
          </select>
          <button
            onClick={handleExtractAll}
            disabled={isExtracting}
            className="px-3 py-2 rounded-lg bg-blue-600 hover:bg-blue-500 font-semibold text-white text-xs flex items-center gap-1.5 shadow-md disabled:opacity-50 transition-all"
            title="Extract entities from all uploaded documents"
          >
            <Sparkles className={`w-3.5 h-3.5 ${isExtracting ? 'animate-spin' : ''}`} />
            {isExtracting ? 'Extracting...' : 'Extract Entities'}
          </button>
          <button
            onClick={fetchGraph}
            className="p-2 rounded-lg bg-slate-900 hover:bg-slate-800 border border-slate-800 text-slate-300 hover:text-white transition-colors"
            title="Refresh Knowledge Graph"
          >
            <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* Main Canvas & Inspector Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Interactive Graph Canvas */}
        <div className="lg:col-span-2 h-[560px] rounded-2xl bg-slate-900/90 border border-slate-800 p-6 relative flex flex-col justify-between overflow-hidden shadow-xl">
          <div className="flex items-center justify-between z-10">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider">
              {filteredNodes.length} Entities • {graphData.edges.length} Relationships
            </span>
            <span className="text-[10px] text-blue-400 font-medium px-2 py-0.5 rounded bg-blue-500/10 border border-blue-500/20">
              Interactive Force Graph
            </span>
          </div>

          {/* SVG Diagram Representation */}
          <div className="relative flex-1 flex items-center justify-center">
            {filteredNodes.length === 0 ? (
              <p className="text-xs text-slate-500">No entities extracted yet. Upload documents to populate the knowledge graph.</p>
            ) : (
              <svg className="w-full h-full">
                {/* Render Edges */}
                {graphData.edges.slice(0, 30).map((edge, idx) => {
                  const sIdx = graphData.nodes.findIndex((n) => n.id === edge.source);
                  const tIdx = graphData.nodes.findIndex((n) => n.id === edge.target);
                  if (sIdx === -1 || tIdx === -1) return null;

                  const x1 = 100 + (sIdx % 6) * 90;
                  const y1 = 80 + Math.floor(sIdx / 6) * 80;
                  const x2 = 100 + (tIdx % 6) * 90;
                  const y2 = 80 + Math.floor(tIdx / 6) * 80;

                  return (
                    <line
                      key={edge.id || idx}
                      x1={x1}
                      y1={y1}
                      x2={x2}
                      y2={y2}
                      stroke="#334155"
                      strokeWidth="1.5"
                      strokeDasharray="3 3"
                    />
                  );
                })}

                {/* Render Nodes */}
                {filteredNodes.map((node, i) => {
                  const cx = 100 + (i % 6) * 90;
                  const cy = 80 + Math.floor(i / 6) * 80;
                  const isSelected = selectedNode?.id === node.id;

                  return (
                    <g
                      key={node.id}
                      onClick={() => setSelectedNode(node)}
                      className="cursor-pointer transition-transform hover:scale-110"
                    >
                      <circle
                        cx={cx}
                        cy={cy}
                        r={isSelected ? 18 : 14}
                        fill={node.type === 'Requirement' ? '#3b82f6' : '#8b5cf6'}
                        className="transition-all shadow-md"
                        stroke={isSelected ? '#ffffff' : '#1e293b'}
                        strokeWidth={isSelected ? 3 : 1}
                      />
                      <text
                        x={cx}
                        y={cy + 26}
                        textAnchor="middle"
                        fill="#94a3b8"
                        fontSize="9"
                        fontWeight="600"
                        className="select-none"
                      >
                        {node.name.length > 12 ? node.name.slice(0, 10) + '..' : node.name}
                      </text>
                    </g>
                  );
                })}
              </svg>
            )}
          </div>
        </div>

        {/* Entity Inspector Panel */}
        <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 space-y-4">
          <h2 className="text-sm font-bold text-white uppercase tracking-wider border-b border-slate-800 pb-2">
            Entity Inspector
          </h2>

          {selectedNode ? (
            <div className="space-y-4 text-xs">
              <div>
                <span className="text-slate-400 font-medium">Entity Name</span>
                <p className="text-sm font-bold text-white mt-0.5">{selectedNode.name}</p>
              </div>

              <div>
                <span className="text-slate-400 font-medium">Category</span>
                <p className="text-blue-400 font-semibold mt-0.5">{selectedNode.type}</p>
              </div>

              <div>
                <span className="text-slate-400 font-medium">Confidence Score</span>
                <p className="text-emerald-400 font-semibold mt-0.5">{Math.round((selectedNode.confidence || 0.95) * 100)}%</p>
              </div>

              <div>
                <span className="text-slate-400 font-medium">Evidence Context</span>
                <p className="text-slate-300 mt-1 p-3 rounded-lg bg-slate-950/80 border border-slate-800 leading-relaxed">
                  {selectedNode.description || 'Extracted through automated entity parsing.'}
                </p>
              </div>
            </div>
          ) : (
            <p className="text-xs text-slate-500 py-8 text-center">Click a node on the graph to inspect entity attributes.</p>
          )}
        </div>
      </div>
    </div>
  );
};
