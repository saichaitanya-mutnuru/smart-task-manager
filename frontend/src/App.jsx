import { useState, useEffect } from 'react';
import axios from 'axios';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';

// Base URL configuration for Axios
const API_BASE = 'https://smart-task-manager-bjzv.onrender.com';

function App() {
  const [tasks, setTasks] = useState([]);
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [priority, setPriority] = useState('Medium');
  const [deadline, setDeadline] = useState('');
  const [loading, setLoading] = useState(false);
  const [breakdownLoadingId, setBreakdownLoadingId] = useState(null);
  const [taskSubTasks, setTaskSubTasks] = useState({});

  // FIXED: Patched production endpoint mapping
  const fetchTasks = async () => {
    try {
      const response = await axios.get(`${API_BASE}/tasks`);
      setTasks(response.data);
    } catch (error) {
      console.error("Error fetching tasks:", error);
    }
  };

  useEffect(() => {
    const loadData = async () => {
      await fetchTasks();
    };
    loadData();
  }, []);

  // FIXED: Patched production endpoint mapping
  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!title.trim()) return;
    try {
      await axios.post(`${API_BASE}/tasks`, {
        title,
        description,
        priority,
        deadline: deadline ? new Date(deadline).toISOString() : null
      });
      setTitle('');
      setDescription('');
      setPriority('Medium');
      setDeadline('');
      fetchTasks();
    } catch (error) {
      console.error("Error creating task:", error);
    }
  };

  // FIXED: Patched production endpoint mapping
  const handleOptimize = async () => {
    setLoading(true);
    try {
      await axios.post(`${API_BASE}/tasks/optimize`);
      await fetchTasks();
    } catch (error) {
      console.error("Error optimizing tasks:", error);
    } finally {
      setLoading(false);
    }
  };

  // FIXED: Patched production endpoint mapping
  const handleComplete = async (id) => {
    try {
      await axios.put(`${API_BASE}/tasks/${id}/complete`);
      fetchTasks();
    } catch (error) {
      console.error("Error completing task:", error);
    }
  };

  // FIXED: Patched production endpoint mapping
  const handleDelete = async (id) => {
    if (!window.confirm("Are you sure you want to delete this task?")) return;
    try {
      await axios.delete(`${API_BASE}/tasks/${id}`);
      fetchTasks();
    } catch (error) {
      console.error("Error deleting task:", error);
    }
  };

  // FIXED: Patched production endpoint mapping
  const handleBreakdown = async (id) => {
    setBreakdownLoadingId(id);
    try {
      const response = await axios.post(`${API_BASE}/tasks/${id}/breakdown`);
      setTaskSubTasks(prev => ({ ...prev, [id]: response.data.sub_tasks }));
    } catch (error) {
      console.error("Error creating task breakdown:", error);
    } finally {
      setBreakdownLoadingId(null);
    }
  };

  const getChartData = () => {
    const priorities = ['Low', 'Medium', 'High'];
    return priorities.map(p => ({
      priority: p,
      Completed: tasks.filter(t => t.priority === p && t.status === 'Completed').length,
      Pending: tasks.filter(t => t.priority === p && t.status === 'Pending').length,
    }));
  };

  const totalTasks = tasks.length;
  const completedTasks = tasks.filter(t => t.status === 'Completed').length;
  const productivityScore = totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0;

  return (
    <div style={{ maxWidth: '1100px', margin: '40px auto', padding: '0 20px', fontFamily: '"Inter", system-ui, sans-serif', color: '#1e293b' }}>
      
      {/* Header Area */}
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '32px', borderBottom: '1px solid #e2e8f0', paddingBottom: '20px' }}>
        <div>
          <h1 style={{ margin: 0, fontSize: '28px', fontWeight: '800', letterSpacing: '-0.5px' }}>Smart Task Manager</h1>
          <p style={{ margin: '4px 0 0 0', color: '#64748b', fontSize: '14px' }}>AI-Powered Workflow Optimization</p>
        </div>
        <button onClick={handleOptimize} disabled={loading} style={{ background: '#0ea5e9', color: 'white', padding: '10px 18px', border: 'none', borderRadius: '8px', cursor: 'pointer', fontWeight: '6px', fontSize: '14px', transition: 'all 0.2s', boxShadow: '0 2px 4px rgba(14, 165, 233, 0.2)' }}>
          {loading ? 'AI Sorting...' : '⚡ AI Prioritize Queue'}
        </button>
      </header>
      
      {/* Analytics Dashboard Grid Banner */}
      <div style={{ display: 'grid', gridTemplateColumns: '1.2fr 2fr', gap: '24px', background: '#f8fafc', padding: '24px', borderRadius: '16px', marginBottom: '32px', border: '1px solid #e2e8f0', alignItems: 'center' }}>
        <div>
          <h3 style={{ margin: '0 0 8px 0', fontSize: '18px', fontWeight: '700' }}>Productivity Metrics</h3>
          <div style={{ display: 'flex', alignItems: 'baseline', gap: '8px', marginBottom: '4px' }}>
            <span style={{ fontSize: '36px', fontWeight: '800', color: '#0f172a' }}>{productivityScore}%</span>
            <span style={{ color: '#64748b', fontSize: '14px', fontWeight: '500' }}>efficiency score</span>
          </div>
          <p style={{ color: '#64748b', fontSize: '14px', margin: 0 }}>{completedTasks} of {totalTasks} tasks completed successfully</p>
        </div>
        <div style={{ width: '100%', height: 130 }}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={getChartData()} margin={{ top: 0, right: 0, left: -25, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
              <XAxis dataKey="priority" axisLine={false} tickLine={false} style={{ fontSize: 12, fill: '#64748b' }} />
              <YAxis allowDecimals={false} axisLine={false} tickLine={false} style={{ fontSize: 12, fill: '#64748b' }} />
              <Tooltip cursor={{ fill: '#f1f5f9' }} />
              <Bar dataKey="Completed" fill="#10b981" stackId="a" radius={[0, 0, 4, 4]} />
              <Bar dataKey="Pending" fill="#3b82f6" stackId="a" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Main Workspace Split Layout */}
      <div style={{ display: 'grid', gridTemplateColumns: '320px 1fr', gap: '40px', alignItems: 'start' }}>
        
        {/* Creation Form Frame */}
        <div style={{ background: '#ffffff', border: '1px solid #e2e8f0', padding: '24px', borderRadius: '16px', boxShadow: '0 1px 3px rgba(0,0,0,0.02)' }}>
          <h3 style={{ margin: '0 0 16px 0', fontSize: '18px', fontWeight: '700' }}>Create Task</h3>
          <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <div>
              <input type="text" placeholder="Task Title" value={title} onChange={(e) => setTitle(e.target.value)} required style={{ width: '100%', padding: '10px 12px', borderRadius: '8px', border: '1px solid #cbd5e1', boxSizing: 'border-box', fontSize: '14px' }} />
            </div>
            <div>
              <textarea placeholder="Task Description" value={description} onChange={(e) => setDescription(e.target.value)} style={{ width: '100%', padding: '10px 12px', height: '70px', borderRadius: '8px', border: '1px solid #cbd5e1', boxSizing: 'border-box', fontSize: '14px', resize: 'none' }} />
            </div>
            <div>
              <label style={{ fontSize: '13px', fontWeight: '6px', color: '#475569', display: 'block', marginBottom: '6px' }}>Priority Level</label>
              <select value={priority} onChange={(e) => setPriority(e.target.value)} style={{ width: '100%', padding: '10px 12px', borderRadius: '8px', border: '1px solid #cbd5e1', fontSize: '14px', background: '#fff' }}>
                <option value="Low">Low</option>
                <option value="Medium">Medium</option>
                <option value="High">High</option>
              </select>
            </div>
            <div>
              <label style={{ fontSize: '13px', fontWeight: '6px', color: '#475569', display: 'block', marginBottom: '6px' }}>Due Date</label>
              <input type="datetime-local" value={deadline} onChange={(e) => setDeadline(e.target.value)} style={{ width: '100%', padding: '10px 12px', borderRadius: '8px', border: '1px solid #cbd5e1', fontSize: '14px', boxSizing: 'border-box' }} />
            </div>
            <button type="submit" style={{ background: '#0f172a', color: 'white', padding: '12px', border: 'none', borderRadius: '8px', cursor: 'pointer', fontWeight: '6px', fontSize: '14px', marginTop: '4px' }}>Add Target</button>
          </form>
        </div>

        {/* Tasks Stream Column */}
        <div>
          <h3 style={{ margin: '0 0 20px 0', fontSize: '18px', fontWeight: '700' }}>Execution Queue</h3>
          
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            {tasks.length === 0 ? (
              <p style={{ color: '#64748b', fontSize: '14px', textAlign: 'center', padding: '40px 0' }}>Your workflow dashboard is empty.</p>
            ) : tasks.map((task) => (
              <div key={task.id} style={{ border: '1px solid #e2e8f0', padding: '20px', borderRadius: '16px', background: '#fff', transition: 'all 0.2s', opacity: task.status === 'Completed' ? 0.55 : 1, boxShadow: '0 1px 2px rgba(0,0,0,0.01)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '16px' }}>
                  <div style={{ flex: 1 }}>
                    <h4 style={{ margin: 0, textDecoration: task.status === 'Completed' ? 'line-through' : 'none', fontSize: '16px', fontWeight: '6px', display: 'flex', alignItems: 'center', gap: '8px', color: task.status === 'Completed' ? '#64748b' : '#0f172a' }}>
                      {task.ai_order > 0 && task.status === 'Pending' && <span style={{ background: '#f1f5f9', padding: '2px 8px', borderRadius: '6px', fontSize: '11px', color: '#475569', fontWeight: '700' }}>Rank {task.ai_order}</span>}
                      {task.title}
                    </h4>
                    <p style={{ margin: '8px 0', fontSize: '14px', color: '#475569', lineHeight: '1.5' }}>{task.description}</p>
                    {task.deadline && (
                      <div style={{ display: 'flex', alignItems: 'center', gap: '4px', color: '#94a3b8', fontSize: '12px' }}>
                        <span>⏱️ Due: {new Date(task.deadline).toLocaleString([], { dateStyle: 'short', timeStyle: 'short' })}</span>
                      </div>
                    )}
                  </div>
                  
                  <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '12px' }}>
                    <span style={{ fontSize: '11px', fontWeight: '700', padding: '4px 10px', borderRadius: '6px', textTransform: 'uppercase', tracking: '0.5px', background: task.priority === 'High' ? '#fee2e2' : task.priority === 'Medium' ? '#fef3c7' : '#f1f5f9', color: task.priority === 'High' ? '#991b1b' : task.priority === 'Medium' ? '#92400e' : '#475569' }}>
                      {task.priority}
                    </span>
                    <button onClick={() => handleDelete(task.id)} style={{ background: 'none', border: 'none', color: '#94a3b8', cursor: 'pointer', fontSize: '14px', padding: '4px', borderRadius: '4px', transition: 'color 0.2s' }} title="Delete Task" onMouseOver={(e) => e.target.style.color = '#ef4444'} onMouseOut={(e) => e.target.style.color = '#94a3b8'}>
                      🗑️
                    </button>
                  </div>
                </div>

                {taskSubTasks[task.id] && (
                  <div style={{ marginTop: '16px', padding: '14px', background: '#f8fafc', borderRadius: '12px', border: '1px solid #e2e8f0' }}>
                    <h5 style={{ margin: '0 0 8px 0', fontSize: '12px', color: '#0369a1', fontWeight: '700', textTransform: 'uppercase', letterSpacing: '0.5px' }}>AI Recommended Checklist</h5>
                    <ul style={{ margin: 0, paddingLeft: '20px', fontSize: '13px', color: '#334155', display: 'flex', flexDirection: 'column', gap: '6px' }}>
                      {taskSubTasks[task.id].map((sub, i) => <li key={i}>{sub}</li>)}
                    </ul>
                  </div>
                )}

                {task.status === 'Pending' && (
                  <div style={{ marginTop: '16px', display: 'flex', justifyContent: 'flex-end', gap: '12px', borderTop: '1px solid #f1f5f9', paddingTop: '12px' }}>
                    <button onClick={() => handleBreakdown(task.id)} disabled={breakdownLoadingId === task.id} style={{ background: '#fff', border: '1px solid #cbd5e1', padding: '6px 12px', borderRadius: '6px', cursor: 'pointer', fontSize: '13px', color: '#475569', fontWeight: '500' }}>
                      {breakdownLoadingId === task.id ? 'Analyzing...' : '🔍 AI Breakdown'}
                    </button>
                    <button onClick={() => handleComplete(task.id)} style={{ background: '#f1f5f9', border: '1px solid #cbd5e1', padding: '6px 12px', borderRadius: '6px', cursor: 'pointer', fontSize: '13px', fontWeight: '6px', color: '#1e293b' }}>Mark Complete</button>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

      </div>
    </div>
  );
}

export default App;