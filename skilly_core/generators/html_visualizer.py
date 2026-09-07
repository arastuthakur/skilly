"""
Interactive HTML Knowledge Graph Visualizer for Skilly.
Features force-directed physics, particle streams on edges, cluster convex hulls,
1-hop/2-hop neighborhood isolation, PageRank heatmap view, live minimap radar,
sound synthesis, and high-res PNG snapshot export.
100% self-contained and offline-capable.
"""

import json
from skilly_core.models import ProjectAnalysisResult


class HTMLVisualizer:
    """Renders a visual knowledge graph visualization."""

    def generate(self, result: ProjectAnalysisResult) -> str:
        nodes_data = [n.to_dict() for n in result.nodes]
        edges_data = [e.to_dict() for e in result.edges]
        clusters_data = result.clusters
        summary_data = result.summary.to_dict()

        payload = {
            "summary": summary_data,
            "nodes": nodes_data,
            "edges": edges_data,
            "clusters": clusters_data,
        }
        json_payload = json.dumps(payload)

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{result.summary.name} - Knowledge Graph</title>
  <style>
    :root {{
      --bg: #070a13;
      --panel-bg: rgba(13, 19, 36, 0.88);
      --panel-border: rgba(255, 255, 255, 0.12);
      --text: #f8fafc;
      --text-muted: #94a3b8;
      --accent: #38bdf8;
      --accent-glow: rgba(56, 189, 248, 0.35);
      --node-file: #38bdf8;
      --node-class: #a855f7;
      --node-fn: #10b981;
      --node-ep: #f43f5e;
      --node-cli: #f59e0b;
      --node-model: #6366f1;
      --node-dep: #64748b;
      --node-cfg: #ec4899;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
      background: var(--bg);
      color: var(--text);
      overflow: hidden;
      width: 100vw;
      height: 100vh;
      user-select: none;
    }}
    #canvas-container {{
      width: 100%;
      height: 100%;
      position: absolute;
      top: 0;
      left: 0;
    }}
    canvas {{
      width: 100%;
      height: 100%;
      display: block;
      cursor: grab;
    }}
    canvas:active {{ cursor: grabbing; }}

    /* Top HUD */
    .hud-top {{
      position: absolute;
      top: 18px;
      left: 18px;
      right: 18px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      pointer-events: none;
      z-index: 10;
    }}
    .hud-card {{
      background: var(--panel-bg);
      backdrop-filter: blur(14px);
      border: 1px solid var(--panel-border);
      border-radius: 12px;
      padding: 10px 18px;
      pointer-events: auto;
      box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }}
    .project-title {{
      font-size: 1.15rem;
      font-weight: 700;
      color: #fff;
      display: flex;
      align-items: center;
      gap: 10px;
    }}
    .badge {{
      font-size: 0.72rem;
      padding: 2px 8px;
      border-radius: 9999px;
      background: rgba(56, 189, 248, 0.15);
      color: var(--accent);
      border: 1px solid rgba(56, 189, 248, 0.35);
      text-transform: uppercase;
      font-weight: 600;
    }}
    .stats-row {{
      font-size: 0.8rem;
      color: var(--text-muted);
      margin-top: 4px;
      display: flex;
      gap: 12px;
    }}

    /* Controls Bar */
    .controls-wrapper {{
      display: flex;
      gap: 8px;
      align-items: center;
      pointer-events: auto;
    }}
    .search-box {{
      position: relative;
    }}
    .search-input {{
      background: rgba(15, 23, 42, 0.95);
      border: 1px solid var(--panel-border);
      color: #fff;
      padding: 8px 14px 8px 34px;
      border-radius: 8px;
      font-size: 0.85rem;
      outline: none;
      width: 220px;
      transition: all 0.2s ease;
    }}
    .search-input:focus {{
      border-color: var(--accent);
      box-shadow: 0 0 14px var(--accent-glow);
      width: 260px;
    }}
    .search-icon {{
      position: absolute;
      left: 10px;
      top: 50%;
      transform: translateY(-50%);
      color: var(--text-muted);
      font-size: 0.85rem;
    }}
    .btn {{
      background: rgba(30, 41, 59, 0.85);
      border: 1px solid var(--panel-border);
      color: #f1f5f9;
      padding: 8px 12px;
      border-radius: 8px;
      font-size: 0.82rem;
      font-weight: 500;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 6px;
      transition: all 0.15s ease;
    }}
    .btn:hover {{
      background: rgba(51, 65, 85, 0.95);
      border-color: var(--accent);
    }}
    .btn.active {{
      background: rgba(56, 189, 248, 0.2);
      border-color: var(--accent);
      color: var(--accent);
    }}

    /* Bottom Filters */
    .hud-bottom-left {{
      position: absolute;
      bottom: 18px;
      left: 18px;
      pointer-events: auto;
      z-index: 10;
    }}
    .filter-chips {{
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      max-width: 520px;
    }}
    .chip {{
      font-size: 0.72rem;
      padding: 4px 9px;
      border-radius: 6px;
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 6px;
      background: rgba(15, 23, 42, 0.85);
      border: 1px solid var(--panel-border);
      color: var(--text-muted);
      transition: all 0.15s ease;
    }}
    .chip.active {{
      color: #fff;
      border-color: rgba(255,255,255,0.3);
      background: rgba(30, 41, 59, 0.95);
    }}
    .chip-dot {{
      width: 8px;
      height: 8px;
      border-radius: 50%;
    }}

    /* Minimap Radar */
    .minimap-card {{
      position: absolute;
      bottom: 18px;
      right: 18px;
      width: 160px;
      height: 120px;
      background: var(--panel-bg);
      backdrop-filter: blur(14px);
      border: 1px solid var(--panel-border);
      border-radius: 10px;
      overflow: hidden;
      z-index: 10;
      box-shadow: 0 10px 25px rgba(0,0,0,0.5);
    }}
    #minimapCanvas {{
      width: 100%;
      height: 100%;
      display: block;
    }}

    /* Sidebar Inspector */
    .sidebar {{
      position: absolute;
      top: 80px;
      right: 18px;
      width: 370px;
      max-height: calc(100vh - 120px);
      background: var(--panel-bg);
      backdrop-filter: blur(18px);
      border: 1px solid var(--panel-border);
      border-radius: 12px;
      padding: 20px;
      overflow-y: auto;
      z-index: 10;
      transform: translateX(410px);
      transition: transform 0.3s cubic-bezier(0.16, 1, 0.3, 1);
      box-shadow: -12px 20px 40px rgba(0,0,0,0.6);
    }}
    .sidebar.open {{ transform: translateX(0); }}
    .sidebar-close {{
      position: absolute;
      top: 14px;
      right: 14px;
      background: none;
      border: none;
      color: var(--text-muted);
      font-size: 1.2rem;
      cursor: pointer;
    }}
    .node-header {{ margin-bottom: 14px; }}
    .node-type-badge {{
      display: inline-block;
      font-size: 0.68rem;
      text-transform: uppercase;
      font-weight: 700;
      padding: 2px 8px;
      border-radius: 4px;
      margin-bottom: 6px;
    }}
    .node-title {{
      font-size: 1.2rem;
      font-weight: 700;
      color: #fff;
      word-break: break-all;
    }}
    .node-path {{
      font-size: 0.75rem;
      color: var(--text-muted);
      margin-top: 4px;
      font-family: monospace;
    }}
    .focus-btn {{
      margin-top: 10px;
      width: 100%;
      padding: 8px;
      border-radius: 6px;
      background: rgba(56, 189, 248, 0.15);
      border: 1px solid rgba(56, 189, 248, 0.4);
      color: var(--accent);
      cursor: pointer;
      font-weight: 600;
      font-size: 0.78rem;
      transition: all 0.15s;
    }}
    .focus-btn:hover {{
      background: rgba(56, 189, 248, 0.25);
    }}
    .metric-grid {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 8px;
      margin: 14px 0 12px 0;
    }}
    .metric-card {{
      background: rgba(255,255,255,0.03);
      border: 1px solid rgba(255,255,255,0.06);
      padding: 8px;
      border-radius: 6px;
      text-align: center;
    }}
    .metric-value {{
      font-size: 1.1rem;
      font-weight: 700;
      color: var(--accent);
    }}
    .metric-label {{
      font-size: 0.68rem;
      color: var(--text-muted);
    }}
    .section-title {{
      font-size: 0.72rem;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: var(--text-muted);
      margin: 16px 0 8px 0;
      font-weight: 600;
    }}
    .code-box {{
      background: #04060d;
      border: 1px solid rgba(255,255,255,0.08);
      border-radius: 6px;
      padding: 10px;
      font-family: monospace;
      font-size: 0.75rem;
      color: #cbd5e1;
      white-space: pre-wrap;
      max-height: 140px;
      overflow-y: auto;
    }}
    .link-list {{
      list-style: none;
      display: flex;
      flex-direction: column;
      gap: 5px;
    }}
    .link-item {{
      font-size: 0.78rem;
      padding: 6px 10px;
      border-radius: 6px;
      background: rgba(255,255,255,0.03);
      cursor: pointer;
      display: flex;
      justify-content: space-between;
      transition: background 0.15s;
    }}
    .link-item:hover {{
      background: rgba(56, 189, 248, 0.18);
      color: #fff;
    }}
    .dev-signature {{
      margin-top: 24px;
      padding-top: 14px;
      border-top: 1px solid rgba(255, 255, 255, 0.08);
      font-size: 0.74rem;
      color: var(--text-muted);
      display: flex;
      flex-direction: column;
      gap: 6px;
    }}
    .dev-links {{
      display: flex;
      gap: 12px;
    }}
    .dev-link {{
      color: var(--accent);
      text-decoration: none;
      font-weight: 500;
      transition: color 0.15s;
    }}
    .dev-link:hover {{
      text-decoration: underline;
      color: #fff;
    }}
    .hud-author-badge {{
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 0.75rem;
      color: var(--text-muted);
      background: rgba(13, 19, 36, 0.88);
      border: 1px solid var(--panel-border);
      border-radius: 8px;
      padding: 7px 14px;
      pointer-events: auto;
      backdrop-filter: blur(14px);
    }}
    .hud-author-badge a {{
      color: var(--accent);
      text-decoration: none;
      font-weight: 600;
    }}
    .hud-author-badge a:hover {{
      text-decoration: underline;
    }}
  </style>
</head>
<body>

  <div id="canvas-container">
    <canvas id="graphCanvas"></canvas>
  </div>

  <!-- Top HUD -->
  <div class="hud-top">
    <div class="hud-card">
      <div class="project-title">
        <span>{result.summary.name}</span>
        <span class="badge">Knowledge Graph</span>
      </div>
      <div class="stats-row">
        <span><strong>{result.summary.total_nodes}</strong> Entities</span>
        <span>•</span>
        <span><strong>{result.summary.total_edges}</strong> Relations</span>
        <span>•</span>
        <span><strong>{len(result.clusters)}</strong> Clusters</span>
        <span>•</span>
        <span><strong>{len(result.summary.languages)}</strong> Languages</span>
      </div>
    </div>

    <div class="controls-wrapper">
      <div class="search-box">
        <span class="search-icon">🔍</span>
        <input type="text" id="searchInput" class="search-input" placeholder="Search any symbol, route, model...">
      </div>
      <button class="btn" id="toggleParticlesBtn">Stream Particles</button>
      <button class="btn" id="toggleHeatmapBtn">Centrality Heatmap</button>
      <button class="btn" id="toggleHullsBtn">Cluster Hulls</button>
      <button class="btn" id="resetCamBtn">Reset</button>
      <button class="btn" id="exportPngBtn">Export PNG</button>
      <button class="btn" id="soundBtn">Audio: Off</button>
      <div class="hud-author-badge">
        <span>By <a href="https://arastuthakur.com.np/" target="_blank">Arastu Thakur</a></span>
        <span>•</span>
        <a href="https://github.com/arastuthakur" target="_blank">GitHub</a>
        <span>•</span>
        <a href="https://www.linkedin.com/in/arastuthakur/" target="_blank">LinkedIn</a>
      </div>
    </div>
  </div>

  <!-- Bottom Filters -->
  <div class="hud-bottom-left">
    <div class="hud-card filter-chips" id="filterContainer"></div>
  </div>

  <!-- Minimap Radar -->
  <div class="minimap-card">
    <canvas id="minimapCanvas"></canvas>
  </div>

  <!-- Sidebar Inspector -->
  <div class="sidebar" id="sidebar">
    <button class="sidebar-close" id="sidebarClose">✕</button>
    <div class="node-header">
      <span class="node-type-badge" id="sideTypeBadge">Function</span>
      <h2 class="node-title" id="sideTitle">Symbol Name</h2>
      <div class="node-path" id="sidePath">src/core/example.py:42</div>
      <button class="focus-btn" id="focusIsoBtn">Focus Neighborhood Sub-Graph</button>
    </div>

    <div class="metric-grid">
      <div class="metric-card">
        <div class="metric-value" id="sidePageRank">0.042</div>
        <div class="metric-label">Centrality (PageRank)</div>
      </div>
      <div class="metric-card">
        <div class="metric-value" id="sideDegree">8</div>
        <div class="metric-label">Total Connections</div>
      </div>
    </div>

    <div class="section-title">Description / Signature</div>
    <div class="code-box" id="sideDesc">Detailed content</div>

    <div class="section-title">Inbound Dependencies (<span id="inboundCount">0</span>)</div>
    <ul class="link-list" id="inboundList"></ul>

    <div class="section-title">Outbound References (<span id="outboundCount">0</span>)</div>
    <ul class="link-list" id="outboundList"></ul>

    <div class="dev-signature">
      <div>Engineered by <strong>Arastu Thakur</strong></div>
      <div class="dev-links">
        <a class="dev-link" href="https://arastuthakur.com.np/" target="_blank">🌐 Website</a>
        <a class="dev-link" href="https://github.com/arastuthakur" target="_blank">💻 GitHub</a>
        <a class="dev-link" href="https://www.linkedin.com/in/arastuthakur/" target="_blank">💼 LinkedIn</a>
      </div>
    </div>
  </div>

  <script>
    const DATA = {json_payload};

    const TYPE_COLORS = {{
      file: '#38bdf8',
      module: '#0ea5e9',
      class: '#a855f7',
      function: '#10b981',
      endpoint: '#f43f5e',
      cli: '#f59e0b',
      data_model: '#6366f1',
      dependency: '#64748b',
      config: '#ec4899'
    }};

    const activeFilters = new Set(Object.keys(TYPE_COLORS));
    let selectedNode = null;
    let hoveredNode = null;
    let isolatedNeighborhood = null; // Set of node IDs or null

    let showParticles = true;
    let showHeatmap = false;
    let showHulls = true;
    let soundEnabled = false;

    // Web Audio Synthesizer
    let audioCtx = null;
    function playTone(freq, duration = 0.06) {{
      if (!soundEnabled) return;
      try {{
        if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
        const osc = audioCtx.createOscillator();
        const gain = audioCtx.createGain();
        osc.type = 'sine';
        osc.frequency.setValueAtTime(freq, audioCtx.currentTime);
        gain.gain.setValueAtTime(0.04, audioCtx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.0001, audioCtx.currentTime + duration);
        osc.connect(gain);
        gain.connect(audioCtx.destination);
        osc.start();
        osc.stop(audioCtx.currentTime + duration);
      }} catch (e) {{}}
    }}

    // Setup Canvas
    const canvas = document.getElementById('graphCanvas');
    const ctx = canvas.getContext('2d');
    const miniCanvas = document.getElementById('minimapCanvas');
    const miniCtx = miniCanvas.getContext('2d');

    let width = (canvas.width = window.innerWidth);
    let height = (canvas.height = window.innerHeight);
    miniCanvas.width = 160;
    miniCanvas.height = 120;

    let camera = {{ x: width / 2, y: height / 2, zoom: 1 }};
    let isDragging = false;
    let dragStart = {{ x: 0, y: 0 }};
    let draggedNode = null;

    window.addEventListener('resize', () => {{
      width = canvas.width = window.innerWidth;
      height = canvas.height = window.innerHeight;
    }});

    // Initialize Simulation Nodes
    const nodeMap = new Map();
    const nodes = DATA.nodes.map((n, i) => {{
      const angle = (i / Math.max(1, DATA.nodes.length)) * Math.PI * 2;
      const radius = 220 + Math.random() * 350;
      const nodeObj = {{
        ...n,
        x: Math.cos(angle) * radius,
        y: Math.sin(angle) * radius,
        vx: 0,
        vy: 0,
        radius: Math.max(7, Math.min(26, 7 + (n.importance_score || 0) * 140 + (n.in_degree + n.out_degree) * 1.6))
      }};
      nodeMap.set(n.id, nodeObj);
      return nodeObj;
    }});

    // Initialize Edges & Particles
    const edges = DATA.edges.map(e => ({{
      ...e,
      sourceNode: nodeMap.get(e.source),
      targetNode: nodeMap.get(e.target),
      particleT: Math.random() // Particle offset 0..1
    }})).filter(e => e.sourceNode && e.targetNode);

    // Build Connectivity Index
    const inboundMap = new Map();
    const outboundMap = new Map();
    edges.forEach(e => {{
      if (!outboundMap.has(e.source)) outboundMap.set(e.source, []);
      if (!inboundMap.has(e.target)) inboundMap.set(e.target, []);
      outboundMap.get(e.source).push(e);
      inboundMap.get(e.target).push(e);
    }});

    // Cluster node map for Hulls
    const clusterNodes = new Map();
    nodes.forEach(n => {{
      const c = n.cluster || 'Core';
      if (!clusterNodes.has(c)) clusterNodes.set(c, []);
      clusterNodes.get(c).push(n);
    }});

    // Color Helpers
    function getHeatmapColor(score) {{
      // score: 0..~0.1 -> Blue to Yellow to Red
      const t = Math.min(1, score * 15);
      if (t < 0.5) {{
        const r = Math.floor(t * 2 * 255);
        const g = Math.floor(t * 2 * 230);
        return `rgb(${{r}}, ${{g}}, 255)`;
      }} else {{
        const g = Math.floor((1 - (t - 0.5) * 2) * 230);
        return `rgb(255, ${{g}}, 50)`;
      }}
    }}

    // Filter Chips
    const filterContainer = document.getElementById('filterContainer');
    Object.keys(TYPE_COLORS).forEach(type => {{
      const count = nodes.filter(n => n.type === type).length;
      if (count === 0) return;
      const chip = document.createElement('div');
      chip.className = 'chip active';
      chip.innerHTML = `<span class="chip-dot" style="background: ${{TYPE_COLORS[type]}}"></span>${{type.toUpperCase()}} (${{count}})`;
      chip.onclick = () => {{
        if (activeFilters.has(type)) {{
          activeFilters.delete(type);
          chip.classList.remove('active');
        }} else {{
          activeFilters.add(type);
          chip.classList.add('active');
        }}
        playTone(550, 0.04);
      }};
      filterContainer.appendChild(chip);
    }});

    // Simulation Physics
    function simulate() {{
      const visibleNodes = nodes.filter(n => activeFilters.has(n.type));

      // 1. Repulsion
      for (let i = 0; i < visibleNodes.length; i++) {{
        const a = visibleNodes[i];
        for (let j = i + 1; j < visibleNodes.length; j++) {{
          const b = visibleNodes[j];
          const dx = b.x - a.x;
          const dy = b.y - a.y;
          const distSq = dx * dx + dy * dy || 1;
          const dist = Math.sqrt(distSq);
          if (dist < 340) {{
            const force = (340 - dist) / (dist * 22);
            const fx = dx * force;
            const fy = dy * force;
            a.vx -= fx;
            a.vy -= fy;
            b.vx += fx;
            b.vy += fy;
          }}
        }}
      }}

      // 2. Spring Attraction
      edges.forEach(e => {{
        if (!activeFilters.has(e.sourceNode.type) || !activeFilters.has(e.targetNode.type)) return;
        const a = e.sourceNode;
        const b = e.targetNode;
        const dx = b.x - a.x;
        const dy = b.y - a.y;
        const dist = Math.sqrt(dx * dx + dy * dy) || 1;
        const targetDist = 95;
        const force = (dist - targetDist) * 0.018;
        const fx = (dx / dist) * force;
        const fy = (dy / dist) * force;
        a.vx += fx;
        a.vy += fy;
        b.vx -= fx;
        b.vy -= fy;
      }});

      // 3. Center gravity & damping
      visibleNodes.forEach(n => {{
        if (n === draggedNode) return;
        n.vx -= n.x * 0.0018;
        n.vy -= n.y * 0.0018;
        n.vx *= 0.87;
        n.vy *= 0.87;
        n.x += n.vx;
        n.y += n.vy;
      }});

      // Advance particles
      if (showParticles) {{
        edges.forEach(e => {{
          e.particleT = (e.particleT + 0.015) % 1;
        }});
      }}
    }}

    // Draw Main Loop
    function draw() {{
      simulate();

      ctx.clearRect(0, 0, width, height);

      ctx.save();
      ctx.translate(camera.x, camera.y);
      ctx.scale(camera.zoom, camera.zoom);

      // 1. Draw Cluster Hulls (Convex Bubbles)
      if (showHulls && !isolatedNeighborhood) {{
        clusterNodes.forEach((cNodes, cName) => {{
          const activeCNodes = cNodes.filter(n => activeFilters.has(n.type));
          if (activeCNodes.length < 2) return;
          // Approximate center and radius
          let cx = 0, cy = 0;
          activeCNodes.forEach(n => {{ cx += n.x; cy += n.y; }});
          cx /= activeCNodes.length;
          cy /= activeCNodes.length;
          let maxR = 0;
          activeCNodes.forEach(n => {{
            const d = Math.hypot(n.x - cx, n.y - cy);
            if (d > maxR) maxR = d;
          }});
          maxR += 50;

          ctx.beginPath();
          ctx.arc(cx, cy, maxR, 0, Math.PI * 2);
          ctx.fillStyle = 'rgba(56, 189, 248, 0.025)';
          ctx.fill();
          ctx.strokeStyle = 'rgba(56, 189, 248, 0.08)';
          ctx.lineWidth = 1.5;
          ctx.setLineDash([6, 6]);
          ctx.stroke();
          ctx.setLineDash([]);

          ctx.fillStyle = 'rgba(148, 163, 184, 0.4)';
          ctx.font = '10px sans-serif';
          ctx.textAlign = 'center';
          ctx.fillText(cName, cx, cy - maxR + 14);
        }});
      }}

      // 2. Draw Edges
      edges.forEach(e => {{
        if (!activeFilters.has(e.sourceNode.type) || !activeFilters.has(e.targetNode.type)) return;

        const isDimmed = isolatedNeighborhood && (!isolatedNeighborhood.has(e.source) || !isolatedNeighborhood.has(e.target));
        const isHighlighted = selectedNode && (e.sourceNode === selectedNode || e.targetNode === selectedNode);

        ctx.beginPath();
        ctx.moveTo(e.sourceNode.x, e.sourceNode.y);
        ctx.lineTo(e.targetNode.x, e.targetNode.y);

        if (isDimmed) {{
          ctx.strokeStyle = 'rgba(255, 255, 255, 0.02)';
          ctx.lineWidth = 0.6;
        }} else if (isHighlighted) {{
          ctx.strokeStyle = '#38bdf8';
          ctx.lineWidth = 2.4;
        }} else {{
          ctx.strokeStyle = 'rgba(255, 255, 255, 0.09)';
          ctx.lineWidth = 1;
        }}
        ctx.stroke();

        // Animated Flow Particle
        if (showParticles && !isDimmed && (isHighlighted || camera.zoom > 0.45)) {{
          const px = e.sourceNode.x + (e.targetNode.x - e.sourceNode.x) * e.particleT;
          const py = e.sourceNode.y + (e.targetNode.y - e.sourceNode.y) * e.particleT;
          ctx.beginPath();
          ctx.arc(px, py, 2.5, 0, Math.PI * 2);
          ctx.fillStyle = isHighlighted ? '#38bdf8' : 'rgba(56, 189, 248, 0.7)';
          ctx.fill();
        }}
      }});

      // 3. Draw Nodes
      nodes.forEach(n => {{
        if (!activeFilters.has(n.type)) return;

        const isDimmed = isolatedNeighborhood && !isolatedNeighborhood.has(n.id);
        const isSelected = n === selectedNode;
        const isHovered = n === hoveredNode;

        const baseColor = showHeatmap ? getHeatmapColor(n.importance_score) : (TYPE_COLORS[n.type] || '#ffffff');

        // Outer Glow
        if ((isSelected || isHovered) && !isDimmed) {{
          ctx.beginPath();
          ctx.arc(n.x, n.y, n.radius + 8, 0, Math.PI * 2);
          ctx.fillStyle = isSelected ? 'rgba(56, 189, 248, 0.45)' : 'rgba(255, 255, 255, 0.22)';
          ctx.fill();
        }}

        // Node Circle
        ctx.beginPath();
        ctx.arc(n.x, n.y, n.radius, 0, Math.PI * 2);
        ctx.fillStyle = isDimmed ? 'rgba(100, 116, 139, 0.2)' : baseColor;
        ctx.fill();
        ctx.strokeStyle = isSelected ? '#ffffff' : (isDimmed ? 'transparent' : 'rgba(0, 0, 0, 0.5)');
        ctx.lineWidth = isSelected ? 2.5 : 1;
        ctx.stroke();

        // Label
        if (!isDimmed && (camera.zoom > 0.65 || n.importance_score > 0.03 || isSelected || isHovered)) {{
          ctx.fillStyle = isSelected ? '#ffffff' : '#cbd5e1';
          ctx.font = `${{isSelected ? 'bold ' : ''}}11px sans-serif`;
          ctx.textAlign = 'center';
          ctx.fillText(n.label, n.x, n.y + n.radius + 14);
        }}
      }});

      ctx.restore();

      // Render Minimap
      drawMinimap();

      requestAnimationFrame(draw);
    }}

    // Minimap Radar Rendering
    function drawMinimap() {{
      miniCtx.clearRect(0, 0, 160, 120);
      let minX = -800, maxX = 800, minY = -600, maxY = 600;

      const scaleX = 160 / (maxX - minX);
      const scaleY = 120 / (maxY - minY);

      // Draw mini dots
      nodes.forEach(n => {{
        if (!activeFilters.has(n.type)) return;
        const mx = (n.x - minX) * scaleX;
        const my = (n.y - minY) * scaleY;
        miniCtx.beginPath();
        miniCtx.arc(mx, my, 1.6, 0, Math.PI * 2);
        miniCtx.fillStyle = TYPE_COLORS[n.type] || '#38bdf8';
        miniCtx.fill();
      }});

      // Draw camera viewport box
      const camLeft = ((-camera.x / camera.zoom) - minX) * scaleX;
      const camTop = ((-camera.y / camera.zoom) - minY) * scaleY;
      const camW = (width / camera.zoom) * scaleX;
      const camH = (height / camera.zoom) * scaleY;

      miniCtx.strokeStyle = 'rgba(56, 189, 248, 0.8)';
      miniCtx.lineWidth = 1.2;
      miniCtx.strokeRect(camLeft, camTop, camW, camH);
    }}

    requestAnimationFrame(draw);

    // Coordinate Transformation Helpers
    function toWorld(screenX, screenY) {{
      return {{
        x: (screenX - camera.x) / camera.zoom,
        y: (screenY - camera.y) / camera.zoom
      }};
    }}

    function findNodeAt(worldX, worldY) {{
      for (let i = nodes.length - 1; i >= 0; i--) {{
        const n = nodes[i];
        if (!activeFilters.has(n.type)) continue;
        const dx = n.x - worldX;
        const dy = n.y - worldY;
        if (dx * dx + dy * dy <= (n.radius + 5) * (n.radius + 5)) {{
          return n;
        }}
      }}
      return null;
    }}

    // Canvas Mouse Events
    canvas.addEventListener('mousedown', e => {{
      const w = toWorld(e.clientX, e.clientY);
      const hit = findNodeAt(w.x, w.y);
      if (hit) {{
        draggedNode = hit;
        selectNode(hit);
        playTone(680, 0.08);
      }} else {{
        isDragging = true;
        dragStart = {{ x: e.clientX - camera.x, y: e.clientY - camera.y }};
      }}
    }});

    window.addEventListener('mousemove', e => {{
      const w = toWorld(e.clientX, e.clientY);
      const oldHover = hoveredNode;
      hoveredNode = findNodeAt(w.x, w.y);
      if (hoveredNode && hoveredNode !== oldHover) {{
        playTone(420, 0.02);
      }}

      if (draggedNode) {{
        draggedNode.x = w.x;
        draggedNode.y = w.y;
        draggedNode.vx = 0;
        draggedNode.vy = 0;
      }} else if (isDragging) {{
        camera.x = e.clientX - dragStart.x;
        camera.y = e.clientY - dragStart.y;
      }}
    }});

    window.addEventListener('mouseup', () => {{
      isDragging = false;
      draggedNode = null;
    }});

    canvas.addEventListener('wheel', e => {{
      e.preventDefault();
      const zoomFactor = e.deltaY < 0 ? 1.12 : 0.89;
      const newZoom = Math.max(0.15, Math.min(3.8, camera.zoom * zoomFactor));
      const mouseWorld = toWorld(e.clientX, e.clientY);
      camera.x = e.clientX - mouseWorld.x * newZoom;
      camera.y = e.clientY - mouseWorld.y * newZoom;
      camera.zoom = newZoom;
    }}, {{ passive: false }});

    // Inspector Sidebar Controller
    function selectNode(n) {{
      selectedNode = n;
      const sidebar = document.getElementById('sidebar');
      sidebar.classList.add('open');

      document.getElementById('sideTypeBadge').textContent = n.type.toUpperCase();
      document.getElementById('sideTypeBadge').style.background = TYPE_COLORS[n.type] || '#38bdf8';
      document.getElementById('sideTypeBadge').style.color = '#000';
      document.getElementById('sideTitle').textContent = n.label;
      document.getElementById('sidePath').textContent = (n.file_path || 'External') + (n.line ? `:${{n.line}}` : '');
      document.getElementById('sidePageRank').textContent = n.importance_score;
      document.getElementById('sideDegree').textContent = n.in_degree + n.out_degree;
      document.getElementById('sideDesc').textContent = n.description || n.metadata?.signature || 'No docstring or signature available.';

      const focusBtn = document.getElementById('focusIsoBtn');
      focusBtn.textContent = (isolatedNeighborhood && isolatedNeighborhood.has(n.id)) ? "Exit Sub-Graph Focus" : "Focus Neighborhood Sub-Graph";

      // Inbound List
      const inbound = inboundMap.get(n.id) || [];
      document.getElementById('inboundCount').textContent = inbound.length;
      const inList = document.getElementById('inboundList');
      inList.innerHTML = '';
      inbound.slice(0, 15).forEach(e => {{
        const li = document.createElement('li');
        li.className = 'link-item';
        li.innerHTML = `<span>${{e.sourceNode.label}}</span><small style="color:var(--text-muted)">${{e.type}}</small>`;
        li.onclick = () => selectNode(e.sourceNode);
        inList.appendChild(li);
      }});

      // Outbound List
      const outbound = outboundMap.get(n.id) || [];
      document.getElementById('outboundCount').textContent = outbound.length;
      const outList = document.getElementById('outboundList');
      outList.innerHTML = '';
      outbound.slice(0, 15).forEach(e => {{
        const li = document.createElement('li');
        li.className = 'link-item';
        li.innerHTML = `<span>${{e.targetNode.label}}</span><small style="color:var(--text-muted)">${{e.type}}</small>`;
        li.onclick = () => selectNode(e.targetNode);
        outList.appendChild(li);
      }});
    }}

    document.getElementById('sidebarClose').onclick = () => {{
      document.getElementById('sidebar').classList.remove('open');
      selectedNode = null;
      isolatedNeighborhood = null;
    }};

    // Neighborhood Isolation Button
    document.getElementById('focusIsoBtn').onclick = () => {{
      if (isolatedNeighborhood) {{
        isolatedNeighborhood = null;
        document.getElementById('focusIsoBtn').textContent = "Focus Neighborhood Sub-Graph";
      }} else if (selectedNode) {{
        const isoSet = new Set([selectedNode.id]);
        const inb = inboundMap.get(selectedNode.id) || [];
        const outb = outboundMap.get(selectedNode.id) || [];
        inb.forEach(e => isoSet.add(e.source));
        outb.forEach(e => isoSet.add(e.target));
        isolatedNeighborhood = isoSet;
        document.getElementById('focusIsoBtn').textContent = "Exit Sub-Graph Focus";
      }}
      playTone(720, 0.08);
    }};

    // Search Autocomplete
    const searchInput = document.getElementById('searchInput');
    searchInput.addEventListener('input', e => {{
      const query = e.target.value.toLowerCase().trim();
      if (!query) return;
      const found = nodes.find(n => n.label.toLowerCase().includes(query) || (n.description && n.description.toLowerCase().includes(query)));
      if (found) {{
        camera.x = width / 2 - found.x * camera.zoom;
        camera.y = height / 2 - found.y * camera.zoom;
        selectNode(found);
      }}
    }});

    // Controls
    document.getElementById('resetCamBtn').onclick = () => {{
      camera = {{ x: width / 2, y: height / 2, zoom: 1 }};
      isolatedNeighborhood = null;
      selectedNode = null;
      playTone(500, 0.05);
    }};

    const toggleParticlesBtn = document.getElementById('toggleParticlesBtn');
    toggleParticlesBtn.onclick = () => {{
      showParticles = !showParticles;
      toggleParticlesBtn.classList.toggle('active', showParticles);
      playTone(600, 0.05);
    }};
    toggleParticlesBtn.classList.add('active');

    const toggleHeatmapBtn = document.getElementById('toggleHeatmapBtn');
    toggleHeatmapBtn.onclick = () => {{
      showHeatmap = !showHeatmap;
      toggleHeatmapBtn.classList.toggle('active', showHeatmap);
      playTone(640, 0.05);
    }};

    const toggleHullsBtn = document.getElementById('toggleHullsBtn');
    toggleHullsBtn.onclick = () => {{
      showHulls = !showHulls;
      toggleHullsBtn.classList.toggle('active', showHulls);
      playTone(580, 0.05);
    }};
    toggleHullsBtn.classList.add('active');

    const soundBtn = document.getElementById('soundBtn');
    soundBtn.onclick = () => {{
      soundEnabled = !soundEnabled;
      soundBtn.textContent = soundEnabled ? 'Audio: On' : 'Audio: Off';
      soundBtn.classList.toggle('active', soundEnabled);
      if (soundEnabled) playTone(880, 0.1);
    }};

    // Export PNG
    document.getElementById('exportPngBtn').onclick = () => {{
      const link = document.createElement('a');
      link.download = `${{DATA.summary.name || 'project'}}_knowledge_graph.png`;
      link.href = canvas.toDataURL('image/png');
      link.click();
      playTone(900, 0.1);
    }};
  </script>
</body>
</html>
"""
        return html
