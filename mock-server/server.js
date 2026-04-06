const express = require('express');
const cors = require('cors');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = 3001;

app.use(cors());
app.use(express.json());

// Load static data
let actionRuns = [];
let playbookRuns = [];
let soarDailyStats = [];
let soarActionSummary = [];
let playbooks = [];
let incidents = [];

try {
  actionRuns = JSON.parse(fs.readFileSync(path.join(__dirname, 'mock-data/action_runs.json')));
  playbookRuns = JSON.parse(fs.readFileSync(path.join(__dirname, 'mock-data/playbook_runs.json')));
  soarDailyStats = JSON.parse(fs.readFileSync(path.join(__dirname, 'mock-data/soar_daily_stats.json')));
  soarActionSummary = JSON.parse(fs.readFileSync(path.join(__dirname, 'mock-data/soar_action_summary.json')));
  playbooks = JSON.parse(fs.readFileSync(path.join(__dirname, 'mock-data/playbooks.json')));
  incidents = JSON.parse(fs.readFileSync(path.join(__dirname, 'mock-data/incidents.json')));
  console.log(`Loaded ${actionRuns.length} action runs, ${playbookRuns.length} playbook runs, ${playbooks.length} playbooks, ${incidents.length} incidents`);
} catch (error) {
  console.error('Error loading mock data:', error);
  process.exit(1);
}

// Build playbook lookup by ID
const playbookById = {};
playbooks.forEach(p => { playbookById[p.id] = p; });

// Helper function to parse ISO date string or epoch milliseconds
function parseDate(dateStr) {
  // Handle epoch milliseconds (what Grafana ${__from} / ${__to} produce)
  if (/^\d{13}$/.test(String(dateStr))) {
    return new Date(parseInt(dateStr, 10));
  }
  // Handle epoch seconds
  if (/^\d{10}$/.test(String(dateStr))) {
    return new Date(parseInt(dateStr, 10) * 1000);
  }
  return new Date(dateStr);
}

// Helper function to filter data by time range
function filterByTimeRange(data, startTime, endTime, timeField = 'create_time') {
  if (!startTime || !endTime) {
    return data;
  }
  
  const start = parseDate(startTime);
  const end = parseDate(endTime);
  
  return data.filter(item => {
    const itemTime = parseDate(item[timeField]);
    return itemTime >= start && itemTime <= end;
  });
}

// Helper function to aggregate daily stats by time range
function aggregateDailyStats(data, startTime, endTime) {
  if (!startTime || !endTime) {
    return data;
  }
  
  const start = parseDate(startTime);
  const end = parseDate(endTime);
  
  return data.filter(item => {
    const itemTime = parseDate(item.date);
    return itemTime >= start && itemTime <= end;
  });
}


// DEBUG: echo back query params so we can inspect what Infinity sends
app.get('/debug/params', (req, res) => {
  console.log('DEBUG params:', JSON.stringify(req.query));
  res.json({ received_params: req.query });
});
// SOAR API Endpoints (mimicking real SOAR REST API)

// GET /rest/action_run - Time-aware action runs
app.get('/rest/action_run', (req, res) => {
  const { start_time, end_time, limit = 1000, order = '-create_time' } = req.query;
  
  let filtered = filterByTimeRange(actionRuns, start_time, end_time, 'create_time');
  
  // Sort by create_time (descending by default)
  if (order === '-create_time') {
    filtered.sort((a, b) => new Date(b.create_time) - new Date(a.create_time));
  } else if (order === 'create_time') {
    filtered.sort((a, b) => new Date(a.create_time) - new Date(b.create_time));
  }
  
  // Apply limit
  filtered = filtered.slice(0, parseInt(limit));
  
  res.json({
    count: filtered.length,
    results: filtered
  });
});

// GET /rest/playbook_run - Time-aware playbook runs
app.get('/rest/playbook_run', (req, res) => {
  const { start_time, end_time, limit = 1000, order = '-start_time' } = req.query;
  
  // If start_time or end_time look like unsubstituted Grafana vars, return all data
  const looksUnsubstituted = (p) => !p || p.includes('${__') || p === '';
  if (looksUnsubstituted(start_time) || looksUnsubstituted(end_time)) {
    filtered = playbookRuns;
    console.log('[/rest/playbook_run/stats] Unsubstituted vars (start="'+start_time+'"), returning all '+playbookRuns.length+' runs');
  } else {
    filtered = filterByTimeRange(playbookRuns, start_time, end_time, 'start_time');
    console.log('[/rest/playbook_run/stats] start='+start_time+' end='+end_time+' -> '+filtered.length+' runs');
  }
  
  // Sort by start_time (descending by default)
  if (order === '-start_time') {
    filtered.sort((a, b) => new Date(b.start_time) - new Date(a.start_time));
  } else if (order === 'start_time') {
    filtered.sort((a, b) => new Date(a.start_time) - new Date(b.start_time));
  }
  
  // Apply limit
  filtered = filtered.slice(0, parseInt(limit));
  
  res.json({
    count: filtered.length,
    results: filtered
  });
});

// GET /rest/action_run/stats - Aggregated action run statistics
app.get('/rest/action_run/stats', (req, res) => {
  const { start_time, end_time, group_by = 'day' } = req.query;
  
  let filtered = aggregateDailyStats(soarDailyStats, start_time, end_time);
  
  res.json({
    count: filtered.length,
    results: filtered
  });
});

// GET /rest/action_run/summary - Action summary (not time-dependent)
app.get('/rest/action_run/summary', (req, res) => {
  res.json({
    count: soarActionSummary.length,
    results: soarActionSummary
  });
});

// Legacy endpoints for backwards compatibility
app.get('/soar_daily_stats.json', (req, res) => {
  const { start_time, end_time } = req.query;
  const filtered = aggregateDailyStats(soarDailyStats, start_time, end_time);
  res.json(filtered);
});

app.get('/action_runs.json', (req, res) => {
  const { start_time, end_time, limit = 1000 } = req.query;
  let filtered = filterByTimeRange(actionRuns, start_time, end_time, 'create_time');
  filtered = filtered.slice(0, parseInt(limit));
  res.json(filtered);
});

app.get('/action_runs_recent.json', (req, res) => {
  const { start_time, end_time, limit = 100 } = req.query;
  let filtered = filterByTimeRange(actionRuns, start_time, end_time, 'create_time');
  filtered.sort((a, b) => new Date(b.create_time) - new Date(a.create_time));
  filtered = filtered.slice(0, parseInt(limit));
  res.json(filtered);
});

app.get('/playbook_runs.json', (req, res) => {
  const { start_time, end_time, limit = 1000 } = req.query;
  // If start_time or end_time look like unsubstituted Grafana vars, return all data
  const looksUnsubstituted = (p) => !p || p.includes('${__') || p === '';
  if (looksUnsubstituted(start_time) || looksUnsubstituted(end_time)) {
    filtered = playbookRuns;
    console.log('[/rest/playbook_run/stats] Unsubstituted vars (start="'+start_time+'"), returning all '+playbookRuns.length+' runs');
  } else {
    filtered = filterByTimeRange(playbookRuns, start_time, end_time, 'start_time');
    console.log('[/rest/playbook_run/stats] start='+start_time+' end='+end_time+' -> '+filtered.length+' runs');
  }
  filtered = filtered.slice(0, parseInt(limit));
  res.json(filtered);
});


// GET /rest/playbook_run/stats - Computed stats from time-filtered playbook runs
// Returns Infinity backend-parser compatible format: {columns: [...], rows: [...]}
app.get('/rest/playbook_run/stats', (req, res) => {
  const { start_time, end_time } = req.query;
  
  // If start_time or end_time look like unsubstituted Grafana vars, return all data
  const looksUnsubstituted = (p) => !p || p.includes('${__') || p === '';
  if (looksUnsubstituted(start_time) || looksUnsubstituted(end_time)) {
    filtered = playbookRuns;
    console.log('[/rest/playbook_run/stats] Unsubstituted vars (start="'+start_time+'"), returning all '+playbookRuns.length+' runs');
  } else {
    filtered = filterByTimeRange(playbookRuns, start_time, end_time, 'start_time');
    console.log('[/rest/playbook_run/stats] start='+start_time+' end='+end_time+' -> '+filtered.length+' runs');
  }
  
  const total = filtered.length;
  const failed = filtered.filter(r => r.status === 'failed').length;
  const success = total - failed;
  const successRate = total > 0 ? success / total : 0;
  
  // Compute avg duration from runs that have both times
  const runsWithDuration = filtered.filter(r => r.start_time && r.update_time);
  const avgDuration = runsWithDuration.length > 0
    ? runsWithDuration.reduce((sum, r) => {
        return sum + (new Date(r.update_time) - new Date(r.start_time)) / 1000;
      }, 0) / runsWithDuration.length
    : 0;
  
  console.log(`[/rest/playbook_run/stats] start=${start_time} end=${end_time} -> ${filtered.length} runs`);

  // Check Accept header or format param — return flat JSON array by default for Infinity compatibility
  const format = req.query.format;
  if (format === 'columns') {
    // Legacy columns+rows format
    res.json({
      columns: [
        { text: "total_runs", type: "number" },
        { text: "successful_runs", type: "number" },
        { text: "failed_runs", type: "number" },
        { text: "success_rate", type: "number" },
        { text: "avg_duration_seconds", type: "number" }
      ],
      rows: [[
        total,
        success,
        failed,
        parseFloat(successRate.toFixed(4)),
        parseFloat(avgDuration.toFixed(2))
      ]]
    });
  } else {
    // Flat JSON array — easy for Infinity backend parser to extract via selectors
    res.json([{
      total_runs: total,
      successful_runs: success,
      failed_runs: failed,
      success_rate: parseFloat(successRate.toFixed(4)),
      avg_duration_seconds: parseFloat(avgDuration.toFixed(2))
    }]);
  }
});

// GET /rest/playbook_run/per_playbook - Time-filtered per-playbook aggregation
// Returns one row per playbook with success/failed counts and avg duration
app.get('/rest/playbook_run/per_playbook', (req, res) => {
  const { start_time, end_time } = req.query;

  const looksUnsubstituted = (p) => !p || p.includes('${__') || p === '';
  let filtered;
  if (looksUnsubstituted(start_time) || looksUnsubstituted(end_time)) {
    filtered = playbookRuns;
    console.log(`[/rest/playbook_run/per_playbook] Unsubstituted vars, returning all ${playbookRuns.length} runs`);
  } else {
    filtered = filterByTimeRange(playbookRuns, start_time, end_time, 'start_time');
    console.log(`[/rest/playbook_run/per_playbook] start=${start_time} end=${end_time} -> ${filtered.length} runs`);
  }

  // Group by playbook ID
  const groups = {};
  filtered.forEach(run => {
    const pid = run.playbook;
    if (!groups[pid]) {
      groups[pid] = { success: 0, failed: 0, totalDuration: 0, durationCount: 0 };
    }
    if (run.status === 'failed') {
      groups[pid].failed++;
    } else {
      groups[pid].success++;
    }
    if (run.start_time && run.update_time) {
      groups[pid].totalDuration += (new Date(run.update_time) - new Date(run.start_time)) / 1000;
      groups[pid].durationCount++;
    }
  });

  // Build result array with playbook metadata
  const result = Object.keys(groups).map(pid => {
    const g = groups[pid];
    const pb = playbookById[parseInt(pid)] || {};
    return {
      id: parseInt(pid),
      name: pb.name || `Playbook ${pid}`,
      category: pb.category || 'Unknown',
      active: pb.active !== undefined ? pb.active : true,
      playbook_run_count: g.success + g.failed,
      successful_run_count: g.success,
      failed_run_count: g.failed,
      avg_duration_seconds: g.durationCount > 0 ? parseFloat((g.totalDuration / g.durationCount).toFixed(2)) : 0,
      success_rate: (g.success + g.failed) > 0 ? parseFloat((g.success / (g.success + g.failed)).toFixed(4)) : 0
    };
  });

  // Sort by total runs descending
  result.sort((a, b) => b.playbook_run_count - a.playbook_run_count);

  console.log(`[/rest/playbook_run/per_playbook] Returning ${result.length} playbook aggregates`);
  res.json(result);
});

// GET /rest/playbook_run/by_category - Time-filtered per-category aggregation
app.get('/rest/playbook_run/by_category', (req, res) => {
  const { start_time, end_time } = req.query;

  const looksUnsubstituted = (p) => !p || p.includes('${__') || p === '';
  let filtered;
  if (looksUnsubstituted(start_time) || looksUnsubstituted(end_time)) {
    filtered = playbookRuns;
    console.log(`[/rest/playbook_run/by_category] Unsubstituted vars, returning all ${playbookRuns.length} runs`);
  } else {
    filtered = filterByTimeRange(playbookRuns, start_time, end_time, 'start_time');
    console.log(`[/rest/playbook_run/by_category] start=${start_time} end=${end_time} -> ${filtered.length} runs`);
  }

  // Group by category
  const categories = {};
  filtered.forEach(run => {
    const pb = playbookById[run.playbook];
    const cat = pb ? pb.category : 'Unknown';
    categories[cat] = (categories[cat] || 0) + 1;
  });

  const result = Object.entries(categories).map(([category, count]) => ({
    category,
    playbook_run_count: count
  }));

  result.sort((a, b) => b.playbook_run_count - a.playbook_run_count);

  console.log(`[/rest/playbook_run/by_category] Returning ${result.length} categories`);
  res.json(result);
});

// ========== Incident Endpoints ==========

// Helper to time-filter incidents by _time field
function filterIncidents(startTime, endTime) {
  const looksUnsubstituted = (p) => !p || p.includes('${__') || p === '';
  if (looksUnsubstituted(startTime) || looksUnsubstituted(endTime)) {
    return incidents;
  }
  return filterByTimeRange(incidents, startTime, endTime, '_time');
}

// GET /incidents - Time-filtered incident list
app.get('/incidents', (req, res) => {
  const { start_time, end_time } = req.query;
  const filtered = filterIncidents(start_time, end_time);
  console.log(`[/incidents] start=${start_time} end=${end_time} -> ${filtered.length} incidents`);
  res.json(filtered);
});

// GET /incidents/by_category - Group by security_domain
app.get('/incidents/by_category', (req, res) => {
  const { start_time, end_time } = req.query;
  const filtered = filterIncidents(start_time, end_time);
  const counts = {};
  filtered.forEach(i => { counts[i.security_domain] = (counts[i.security_domain] || 0) + 1; });
  const result = Object.entries(counts).map(([category, count]) => ({ category, count }));
  result.sort((a, b) => b.count - a.count);
  res.json(result);
});

// GET /incidents/by_severity - Group by severity
app.get('/incidents/by_severity', (req, res) => {
  const { start_time, end_time } = req.query;
  const filtered = filterIncidents(start_time, end_time);
  const counts = {};
  filtered.forEach(i => { counts[i.severity] = (counts[i.severity] || 0) + 1; });
  const result = Object.entries(counts).map(([severity, count]) => ({ severity, count }));
  res.json(result);
});

// GET /incidents/by_owner - Group by owner
app.get('/incidents/by_owner', (req, res) => {
  const { start_time, end_time } = req.query;
  const filtered = filterIncidents(start_time, end_time);
  const counts = {};
  filtered.forEach(i => { counts[i.owner] = (counts[i.owner] || 0) + 1; });
  const result = Object.entries(counts).map(([analyst, count]) => ({ analyst, count }));
  result.sort((a, b) => b.count - a.count);
  res.json(result);
});

// GET /incidents/by_source - Group by mitre_attack_tactic
app.get('/incidents/by_source', (req, res) => {
  const { start_time, end_time } = req.query;
  const filtered = filterIncidents(start_time, end_time);
  const counts = {};
  filtered.forEach(i => { counts[i.mitre_attack_tactic] = (counts[i.mitre_attack_tactic] || 0) + 1; });
  const result = Object.entries(counts).map(([tactic, count]) => ({ tactic, count }));
  result.sort((a, b) => b.count - a.count);
  res.json(result);
});

// GET /incidents/by_status - Group by status_label
app.get('/incidents/by_status', (req, res) => {
  const { start_time, end_time } = req.query;
  const filtered = filterIncidents(start_time, end_time);
  const counts = {};
  filtered.forEach(i => { counts[i.status_label] = (counts[i.status_label] || 0) + 1; });
  const result = Object.entries(counts).map(([status, count]) => ({ status, count }));
  res.json(result);
});

// Static endpoints (unchanged)
app.get('/soar_action_summary.json', (req, res) => {
  res.json(soarActionSummary);
});

// Serve other static files
app.use(express.static(path.join(__dirname, 'mock-data')));

app.listen(PORT, () => {
  console.log(`🚀 Time-aware SOAR Mock Server running on port ${PORT}`);
  console.log(`📊 Loaded ${actionRuns.length} action runs spanning ${actionRuns.length > 0 ? 
    `${actionRuns[actionRuns.length-1].create_time} to ${actionRuns[0].create_time}` : 'no data'}`);
});