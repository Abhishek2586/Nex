import React,{useEffect,useState} from 'react';
import {createRoot} from 'react-dom/client';
import {BrowserRouter,NavLink,useLocation,useNavigate} from 'react-router-dom';
import {ResponsiveContainer,LineChart,Line,XAxis,YAxis,Tooltip,CartesianGrid,BarChart,Bar,ReferenceLine} from 'recharts';
import './style.css';
type Row=Record<string,any>;
async function api(path:string,body?:unknown){const r=await fetch('/api/v1/'+path,body===undefined?{}:{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});if(!r.ok)throw new Error(`${r.status}: ${await r.text()}`);return r.json();}

const SCENARIOS: Record<string, string> = {
  'normal': 'Normal simulated session',
  'gradual_stress': 'Gradual stress-like change',
  'sustained_posture': 'Sustained posture deviation',
  'brief_posture': 'Brief posture deviation',
  'missing_data': 'Missing / low-quality signal',
  'high_motion': 'High-motion interference',
  'repeated_dismissal': 'Repeated prompt dismissal'
};

function App(){
 const [health,H]=useState<Row>({}),[sessions,S]=useState<Row[]>([]),[selected,SEL]=useState(''),[events,E]=useState<Row[]>([]),[prompts,P]=useState<Row[]>([]),[models,M]=useState<Row[]>([]),[activeModel,AM]=useState<Row|null>(null),[runs,R]=useState<Row[]>([]),[jobs,J]=useState<Row[]>([]),[privacy,V]=useState<Row[]>([]),[projections,PROJ]=useState<Row[]>([]),[error,ERR]=useState(''),[scenario,SC]=useState('normal'),[speed,SP]=useState(20),[explanation,X]=useState<Row|null>(null),[explainModel,XM]=useState('neural'),[selectedDataset,SD]=useState('synthetic');
 const [mode, setMode] = useState(()=>localStorage.getItem('nexora-view') || 'research');
 const navigate=useNavigate();
 const routerLocation=useLocation();const pageRaw=decodeURIComponent(routerLocation.pathname.slice(1));const page=pageRaw?pageRaw:mode==='research'?'Overview':'Home';
 
 const refresh=async()=>{try{const [h,s,p,m,am,r,v,proj,dstat]=await Promise.all([api('health'),api('sessions'),api('interventions'),api('models/catalog').catch(()=>[]),api('models/active').catch(()=>null),api('experiments'),api('privacy'),api('privacy/projection'),api('data/status').catch(()=>({wesad: {status: 'NOT RUN'}}))]);h.wesad = dstat.wesad;H(h);S(s);P(p);M(m);AM(am);R(r);V(v);PROJ(proj);if(h.coordinator==='available'){try{J(await api('experiment-jobs'))}catch{J([])}}else J([]);ERR('');if(s.length)SEL(prev=>prev?prev:s[0].id);}catch(e){ERR(String(e));H({status:'disconnected'});}};
 useEffect(()=>{refresh();const timer=setInterval(refresh,2000);return()=>clearInterval(timer)},[selected]);
 useEffect(()=>{E([]);X(null);if(!selected)return;let active=true,cursor=0,socket:WebSocket|undefined,retry:number|undefined;const append=(rows:Row[])=>{if(active&&rows.length){cursor=rows[rows.length-1].sequence;E(old=>{const ids=new Set(old.map(item=>item.event_id));return [...old,...rows.filter(item=>!ids.has(item.event_id))].slice(-1500)})}};const connect=async()=>{try{append(await api(`sessions/${selected}/events?after=${cursor}&limit=1000`));const scheme=window.location.protocol==='https:'?'wss':'ws';socket=new WebSocket(`${scheme}://${window.location.host}/api/v1/sessions/${selected}/stream?after=${cursor}`);socket.onmessage=e=>append([JSON.parse(e.data)]);socket.onclose=()=>{if(active)retry=window.setTimeout(connect,750)};socket.onerror=()=>socket?.close();}catch(e){if(active){ERR(String(e));retry=window.setTimeout(connect,750)}}};connect();return()=>{active=false;if(retry)clearTimeout(retry);socket?.close()}},[selected]);
 
 const researchPages = ['Overview', 'Live session', 'Interventions', 'AI insights', 'Federated & privacy lab', 'Evidence', 'Settings'];
 const userPages = ['Home', 'Guidance', 'History', 'About', 'Settings'];
 const activePages = mode === 'research' ? researchPages : userPages;
 const setAppMode=(next:string)=>{setMode(next);localStorage.setItem('nexora-view',next);navigate(next==='research'?'/Overview':'/Home');};

 const act=async(fn:()=>Promise<unknown>)=>{try{await fn();await refresh()}catch(e){ERR(String(e))}};
 const exportEvidence=()=>{window.location.href='/api/v1/evidence/export';};
 const start=()=>act(async()=>{const s=await api('sessions',{scenario,speed,seed:42});await api(`sessions/${s.id}/start`,{});SEL(s.id)});
 
 const session=sessions.find(s=>s.id===selected);
 const obs=events.filter(e=>e.event_type==='observation').map(e=>{const o={...e.payload,...e.payload.signals}; o.acc_mag_g=(o.acc_x_g!=null&&o.acc_y_g!=null&&o.acc_z_g!=null)?Math.sqrt(o.acc_x_g**2+o.acc_y_g**2+o.acc_z_g**2):null; return o;});
 const latest=obs.at(-1);
 const pred=events.filter(e=>e.event_type==='prediction').at(-1)?.payload;
 const activePrompts=prompts.filter(p=>(p.status==='offered'||p.status==='accepted')&&(p.session_id===selected));
 const fedDisabled = health.coordinator !== 'available' || jobs.some(j => ['queued', 'training'].includes(j.status));
 const fedReason = health.coordinator !== 'available' ? 'Coordinator unavailable' : (jobs.some(j => ['queued', 'training'].includes(j.status)) ? 'Experiment already running' : '');

 const renderChart=(title:string, dataKey:string, unit:string, stroke:string)=>{
   return <div className="card"><div className="cardtitle"><h2>{title}</h2><span>Synthetic · {unit}</span></div><ResponsiveContainer width="100%" height={150}><LineChart data={obs.filter((_,i)=>i%4===0)}><CartesianGrid strokeDasharray="3 3" vertical={false}/><XAxis dataKey="event_time_s" unit="s"/><YAxis/><Tooltip/><Line type="monotone" dataKey={dataKey} stroke={stroke} dot={false} isAnimationActive={false} connectNulls={false}/></LineChart></ResponsiveContainer></div>;
 };

 return <div className="shell"><aside><div className="brand"><b>◈ NEXORA</b><small>{mode === 'research' ? 'RESEARCH CONSOLE' : 'PARTICIPANT APP'}</small></div>
 <div className="mode-toggle" style={{padding: '0 1rem', marginBottom: '1rem'}}>
    <label style={{display: 'flex', alignItems: 'center', gap: '0.5rem', color: '#fff', fontSize: '0.875rem'}}>
      <input aria-label="Research Mode" type="checkbox" checked={mode==='research'} onChange={(e) => setAppMode(e.target.checked ? 'research' : 'user')} />
      Research Mode
    </label>
 </div>
 <nav>{activePages.map((p,i)=><NavLink key={p} to={'/'+p}><span>{['▦','⌁','◎','◇','⬡','▤','⚙'][i % 7]}</span><span>{p}</span></NavLink>)}</nav><div className="asidebottom"><span className="dot"/> Local workspace<small>Software-in-the-loop prototype</small></div></aside><main><header><span>Workspace / <b>{page}</b></span><div className="badges"><span className="badge">Synthetic</span><span className="badge">{health.client_id||'client-a'}</span><span className="badge">Edge {health.status||'Connecting…'}</span><span className="badge">Coordinator {health.coordinator||'unknown'}</span></div></header><section><div className="title"><div><p className="eyebrow">NEXORA / {mode === 'research' ? 'RESEARCH WORKSPACE' : 'PARTICIPANT DASHBOARD'}</p><h1>{page}</h1><p>{mode==='research'?'Inspect signals, model behaviour and traceable software decisions.':'Follow the local simulation and choose whether to use an optional suggestion.'}</p></div><span className="badge">{health.transport||'Connecting…'}</span></div>{error&&<div role="alert" className="error">{error}</div>}
 
 {page==='Overview'&&mode==='research'&&<><div className="card"><h2>Prototype Summary</h2><p><b>NEXORA</b> is a privacy-aware software-in-the-loop research prototype for stress-aware, posture-aware, and context-aware digital interventions.</p><div style={{display:'flex', gap:'10px', marginTop:'10px'}}><span className="badge">Software-in-the-loop</span><span className="badge">Synthetic Data</span></div></div>
 <div className="card controls"><div style={{flexBasis:'100%', marginBottom:'10px'}}><h2>Session Control</h2><p className="muted">Start a simulated session to inject synthetic physiological and biomechanical signals into the processing pipeline.</p></div><label>Scenario<select value={scenario} onChange={e=>SC(e.target.value)}>{Object.entries(SCENARIOS).map(([k,v])=><option key={k} value={k}>{v}</option>)}</select></label><label>Replay speed<select value={speed} onChange={e=>SP(+e.target.value)}>{[1,5,20].map(x=><option key={x} value={x}>{x}×</option>)}</select></label><button onClick={start}>Start synthetic session</button><button className="secondary" disabled={!session||session.status==='stopped'} onClick={()=>act(()=>api(`sessions/${selected}/${session?.status==='running'?'pause':'start'}`,{}))}>{session?.status==='running'?'Pause':'Resume'}</button><button className="secondary" disabled={!session||session.status==='stopped'} onClick={()=>act(()=>api(`sessions/${selected}/stop`,{}))}>Stop</button></div>
 <div className="card"><h2>Architecture Pipeline</h2>
 <div className="pipeline-container">
   <div className="pipeline-node"><div className="node-icon">📥</div><b>Input</b><small>{latest?'Synthetic':'WESAD unavailable'}</small></div>
   <div className="pipeline-node"><div className="node-icon">🔍</div><b>Quality</b><small>{pred?.abstained?'missing/high-motion':'good'}</small></div>
   <div className="pipeline-node"><div className="node-icon">⚙️</div><b>Features</b><small>12 features</small></div>
   <div className="pipeline-node"><div className="node-icon">🧠</div><b>Model</b><small>{activeModel ? activeModel.model_hash?.slice(0,8) : 'None'}</small></div>
   <div className="pipeline-node"><div className="node-icon">⚖️</div><b>Policy</b><small>Threshold {activeModel?.threshold != null ? activeModel.threshold : "Unavailable"}</small></div>
   <div className="pipeline-node"><div className="node-icon">💬</div><b>Intervention</b><small>{activePrompts.length?'Offered':'None'}</small></div>
   <div className="pipeline-node"><div className="node-icon">📈</div><b>Learning</b><small>{events.filter(e=>e.event_type==='feedback').at(-1)?.payload.action || 'None'}</small></div>
 </div>
 </div>
 <div className="twocol">
 <div className="card"><h2>Session Summary</h2><p>Active session ID: <b>{selected || 'None'}</b></p><p>Scenario: {scenario}</p><p className="status">Status: <span className="badge">{session?.status || 'Unknown'}</span></p><p>Active model: {activeModel?.model_hash?.slice(0,8) || 'None'}</p><p>Reviewer next step: Go to <b>Live session</b> to see real-time signals.</p></div>
 <div className="card"><h2>Prototype Limitations & Hardware</h2><p><b>Important:</b> This is a local software simulation. No clinical claims are made.</p><p><b>Future Embodiment:</b> Wrist-worn sensing unit (EDA, Temp, IMU) + optional posture accessory (back clip).</p><p>Current state uses purely synthetic or replayed inputs.</p></div>
 </div>
 </>}
 
  {page==='Live session'&&mode==='research'&&<><div className="info-strip"><span><b>Session:</b> {selected?.slice(0,8)||'None'}</span><span><b>Scenario:</b> {SCENARIOS[scenario]}</span><span><b>Speed:</b> {session?.speed||speed}×</span><span><b>Model:</b> {activeModel?.model_hash?.slice(0,8)||'None'}</span><span><b>Threshold:</b> {activeModel?.threshold||'N/A'}</span><span><b>Policy:</b> {pred?.abstained?'Abstained':'Active'}</span><span><b>Intervention:</b> {activePrompts.length?'Offered':'None'}</span></div>
 <div className="stats">{[['EDA',latest?.eda_us,'µS'],['Skin Temp',latest?.skin_temperature_c,'°C'],['Posture',latest?.posture_angle_deg,'°'],['Movement',latest?.acc_mag_g,'g']].map(([name,value,unit])=><div className="card metric-card" key={name as string}><small>{name}</small><strong>{value==null?'Unavailable':Number(value).toFixed(2)} <em>{value==null?'':unit as string}</em></strong></div>)}</div>
 <div className="twocol">
   {renderChart('Electrodermal activity (EDA)', 'eda_us', 'µS', '#087f83')}
   {renderChart('Posture Angle', 'posture_angle_deg', '°', '#d35400')}
 </div>
 <div className="twocol">
   {renderChart('Skin Temperature', 'skin_temperature_c', '°C', '#c0392b')}
   {renderChart('Acceleration Magnitude (Movement)', 'acc_mag_g', 'g', '#8e44ad')}
 </div>
 <div className="twocol"><div className="card"><h2>Model State & Current Interpretation</h2>
 <div className="model-score-display">{!pred?'Waiting for a complete 30-second window':pred.abstained?`Abstained: ${pred.reason}`:`Stress model score: ${(pred.probabilities[1]*100).toFixed(1)}%`}</div>
 <p className="muted">Scores are uncalibrated model outputs indicating autonomic arousal likelihood. Not a medical diagnosis.</p>
 {activeModel?.model_hash && (activeModel?.reload_state?.hash_mismatch || !['loaded', 'ok', 'ready'].includes(activeModel?.reload_state?.reload_status)) && <div className="alert-box" style={{background:'#f8d7da', color:'#721c24', padding:'0.5rem', marginTop:'0.5rem', borderRadius:'6px'}}>Warning: Reload Issue. Status: {activeModel.reload_state?.reload_status || 'unknown'}. {activeModel.reload_state?.reload_error && `Error: ${activeModel.reload_state.reload_error}`}. {activeModel.reload_state?.hash_mismatch ? `Hash mismatch (loaded: ${activeModel.reload_state?.loaded_model_hash?.slice(0,8) || 'none'} vs registry: ${activeModel.reload_state?.registry_model_hash?.slice(0,8)})` : ''}</div>}
 <div style={{display:'flex', gap:'10px', marginTop:'15px', flexWrap:'wrap'}}>
  <div className="help-box"><b>Predicted vs Abstained:</b> The policy engine skips inference if signal quality is poor (e.g., high motion).</div>
  <div className="help-box"><b>Threshold:</b> The cutoff score ({activeModel?.threshold||'N/A'}) to trigger an intervention consideration.</div>
 </div>
 </div>
 <div className="card"><h2>Recent Predictions</h2><table className="data-table" data-testid="recent-predictions"><thead><tr><th>Time</th><th>Source</th><th>Status</th><th>Score / Reason</th></tr></thead><tbody>{events.filter(e=>e.event_type==='prediction').slice(-5).reverse().map(e=><tr key={e.event_id}><td>{new Date(e.created_at).toLocaleTimeString([],{hour12:false})}</td><td>{e.payload.source}</td><td><span className={`badge ${e.payload.abstained?'badge-abstained':''}`}>{e.payload.abstained?'Abstained':'Predicted'}</span></td><td>{e.payload.abstained?e.payload.reason:<b>{(e.payload.probabilities[1]*100).toFixed(1)}%</b>}</td></tr>)}</tbody></table></div>
 <div className="card" style={{gridColumn:'1 / -1'}}><h2>Recent Decisions & Interventions</h2>
 <div className="timeline-container">{events.filter(e=>e.event_type==='decision').slice(-5).reverse().map(e=><div className="timeline-row" key={e.event_id}><div className="timeline-time">{new Date(e.created_at).toLocaleTimeString([],{hour12:false})}</div><div className="timeline-content"><b>{e.payload.result === 'intervention_triggered' ? 'Triggered Intervention' : 'Suppressed'}</b> <span className="muted">{e.payload.reason_codes.join(', ')}</span></div></div>)}
 {events.filter(e=>e.event_type==='decision').length === 0 && <p className="muted">No decisions logged yet.</p>}</div></div></div></>}
 
 {page==='Home'&&mode==='user'&&<><div className="participant-hero"><span className="eyebrow">Desk-Work Wellbeing Assistant</span><h2>{session?.status==='running'?'Monitoring simulation is active':session?.status==='paused'?'Monitoring simulation is paused':'Ready to start a monitoring simulation'}</h2><p>{pred?.abstained?'Signal quality is insufficient (e.g. high motion).':activePrompts.length?'NEXORA has a small wellness suggestion for you.':'This prototype watches simulated physiological signals and offers gentle posture and stress guidance.'}</p><span className="badge" style={{background: 'rgba(255,255,255,0.2)'}}>Software-in-the-loop Prototype</span></div><div className="stats participant-signals">{[['EDA (Stress)',latest?.eda_us,'available'],['Skin Temperature',latest?.skin_temperature_c,'available'],['Posture Angle',latest?.posture_angle_deg,'available']].map(([name,value,state])=><div className="card" key={String(name)}><small>{name}</small><strong>{value==null?'Unavailable':'Active'}</strong><span>{state==='available'?'Simulated Sensor':'Not supplied by this demo'}</span></div>)}</div><div className="card controls"><button onClick={start}>Start Session</button><button className="secondary" disabled={!session||session.status==='stopped'} onClick={()=>act(()=>api(`sessions/${selected}/${session?.status==='running'?'pause':'start'}`,{}))}>{session?.status==='running'?'Pause':'Resume'}</button><button className="secondary" disabled={!session||session.status==='stopped'} onClick={()=>act(()=>api(`sessions/${selected}/stop`,{}))}>End session</button></div></>}

 {page==='Guidance'&&mode==='user'&&<div className="card guidance"><h2>Current guidance</h2>{!activePrompts.length&&<p className="calm-text">No action is needed right now. Continue your work comfortably.</p>}{activePrompts.map(p=><article key={p.id}><span className="badge">Optional wellness suggestion</span><h3>{p.text}</h3><p>Take a moment to reset. You remain in control of your workflow.</p><div className="intervention-actions">{(p.status==='offered'?['accept','dismiss']:p.status==='accepted'?['complete','cancel']:[]).map(action=><button key={action} className={action==='dismiss'||action==='cancel'?'secondary':''} onClick={()=>act(()=>api(`interventions/${p.id}/feedback`,{feedback_id:crypto.randomUUID(),action}))}>{action==='complete'?'Done':action==='accept'?'Start':action==='dismiss'?'Not now':action}</button>)}</div></article>)}</div>}
 
 {page==='History'&&mode==='user'&&<div className="card"><h2>Session history</h2><p className="muted">Your sessions are retained only in local storage.</p>{!sessions.length&&<p>No sessions yet. Start a session from the Home page.</p>}<div className="history-list">{sessions.map(s=><article key={s.id} className={`history-card ${s.id===selected?'active':''}`} onClick={()=>SEL(s.id)}><div className="history-header"><span className="badge">{SCENARIOS[s.scenario]||s.scenario}</span><span className="badge">{s.status}</span></div><h3>Session {s.id.slice(0,8)}</h3><div className="history-meta"><span>{new Date(s.created_at).toLocaleString()}</span>{s.status==='stopped'&&<span>Duration: {s.started_at&&s.stopped_at?((new Date(s.stopped_at).getTime()-new Date(s.started_at).getTime())/1000).toFixed(0)+'s':'—'}</span>}</div><p className="history-stats">{events.filter(e=>e.session_id===s.id&&e.event_type==='prediction').length} predictions · {events.filter(e=>e.session_id===s.id&&e.event_type==='feedback').length} feedback events</p></article>)}</div></div>}
 
 {page==='About'&&mode==='user'&&<div className="card"><h2>About this prototype</h2><p>NEXORA is a privacy-aware research prototype demonstrating edge-based machine learning for digital wellness interventions.</p><p><b>Prototype Scope:</b></p><ul><li>Local software-only simulation.</li><li>Uses synthetic or replayed data.</li><li>Not a medical device.</li><li>No clinical validation or claims.</li><li>Future hardware embodiment (wrist-worn sensor) is simulated in this build.</li></ul></div>}
 
 {page==='Interventions'&&mode==='research'&&<div className="card"><h2>Prompts & feedback</h2><p className="page-note">Physical hardware outputs are not connected in this software-only prototype. Interventions are delivered to the Participant App.</p>{!prompts.length&&<p>No prompts yet. Start a session and induce stress-like conditions to exercise the policy engine.</p>}
 <div className="intervention-list">
 {prompts.map(p=><article className="intervention-card" key={p.id}><div className="intervention-header"><span className={`badge badge-${p.status}`}>{p.status}</span><span className="muted">{new Date(p.created_at).toLocaleString()}</span></div><h3>{p.text}</h3><div className="intervention-meta"><span><b>Source:</b> {p.source}</span><span><b>Context:</b> Model threshold exceeded, contextual checks passed.</span></div><div className="intervention-actions">{(p.status==='offered'?['accept','dismiss']:p.status==='accepted'?['complete','cancel']:[]).map(action=><button key={action} className={action==='dismiss'||action==='cancel'?'secondary':''} onClick={()=>act(()=>api(`interventions/${p.id}/feedback`,{feedback_id:crypto.randomUUID(),action}))}>{action}</button>)}</div></article>)}
 </div></div>}
 
 {page==='AI insights'&&mode==='research'&&<><div className="card"><h2>Dataset Insights</h2>
  <label style={{marginRight: '10px'}}>Dataset:
    <select value={selectedDataset} onChange={e=>{
      SD(e.target.value);
    }}>
      <option value="synthetic">Synthetic</option>
      {health.wesad && health.wesad.status === 'COMPLETED' && <option value="wesad">WESAD</option>}
    </select>
  </label>
 </div>
 <div className="twocol">
  {models.filter(m => (selectedDataset === 'wesad' ? m.source === 'Recorded dataset' : m.source === 'Synthetic')).map(m=><div className="card" key={m.model_hash}><span className="badge">{m.source} · {m.lifecycle_state||'candidate'}</span><h2>{m.model_id==='baseline'?'Random forest':'Neural network'}</h2><strong className="metric">{(100*(m.validation_score || m.metrics?.balanced_accuracy || 0)).toFixed(1)}%</strong><p>Validation Balanced accuracy</p><p>Test Balanced Acc: {(100*(m.test_balanced_accuracy || m.metrics?.balanced_accuracy || 0)).toFixed(1)}% · Macro-F1: {(m.test_macro_f1 || m.metrics?.macro_f1 || 0).toFixed(3)}</p><p>Architecture: {m.architecture_id || 'Unavailable'}</p><p>Hash: {m.model_hash}</p><p>Dataset Hash: {m.dataset_hash}</p><div><h4>Confusion Matrix</h4><table style={{width:'100%', textAlign:'center'}}><thead><tr><th>Actual \ Pred</th><th>Baseline</th><th>Stress-like</th></tr></thead><tbody><tr><td>Baseline</td><td>{m.metrics?.confusion_matrix?.[0]?.[0]}</td><td>{m.metrics?.confusion_matrix?.[0]?.[1]}</td></tr><tr><td>Stress-like</td><td>{m.metrics?.confusion_matrix?.[1]?.[0]}</td><td>{m.metrics?.confusion_matrix?.[1]?.[1]}</td></tr></tbody></table></div><div className="alert-box" style={{marginTop:'1rem', padding:'1rem', background:'#ffeeba', color:'#856404'}}><strong>{m.source === 'Recorded dataset' ? 'Recorded WESAD research dataset result — offline evaluation only. This model is not currently live in the simulator.' : 'Synthetic simulator result only'}</strong></div></div>)}
 </div><div className="card"><h2>Per-prediction attribution</h2><label>Model (Live session explanation)<select value={explainModel} onChange={e=>{XM(e.target.value);X(null)}}><option value="neural">Neural network</option><option value="baseline">Random forest</option></select></label><button disabled={!pred?.prediction_id} onClick={()=>act(async()=>X(await api(`explanations/${pred.prediction_id}?model=${explainModel}`)))}>Explain latest prediction</button>{explanation&&<><p>{explanation.method} · {explanation.output_space} · class {explanation.class}</p>
 <ResponsiveContainer width="100%" height={300}>
   <BarChart data={explanation.values.map((v:number,i:number)=>({name: explanation.feature_names[i], value: v}))} layout="vertical" margin={{left: 50}}>
     <CartesianGrid strokeDasharray="3 3"/>
     <XAxis type="number"/>
     <YAxis dataKey="name" type="category" width={100}/>
     <Tooltip/>
     <ReferenceLine x={0} stroke="#000" />
     <Bar dataKey="value" fill="#8884d8" />
   </BarChart>
 </ResponsiveContainer>
 <p>Completeness delta: {(explanation.convergence_delta??explanation.completeness_delta).toFixed(7)}</p><p className="muted">Attribution describes model behaviour, not causality or clinical effect.</p></>}</div></>}
 
 {page==='Federated & privacy lab'&&mode==='research'&&<><div className="card explanation-card"><h2>Why Federated Learning?</h2><p>To improve the global stress-inference model without centralizing sensitive physiological data (EDA, Temp), NEXORA learns locally on the edge and aggregates model updates (not raw data). <i>Note: This prototype simulates federated nodes as local processes on the same machine. Secure Aggregation is out of scope for this build.</i></p></div>
 <div className="card controls"><button disabled={fedDisabled} onClick={()=>act(()=>api('experiment-jobs',{mode:'federated',rounds:1,dataset:'synthetic'}))}>Run 1-round FedAvg</button><button disabled={fedDisabled} onClick={()=>act(()=>api('experiment-jobs',{mode:'federated',rounds:3,dataset:'synthetic'}))}>Run 3-round FedAvg</button><button disabled={fedDisabled} onClick={()=>act(()=>api('experiment-jobs',{mode:'federated',rounds:5,dataset:'synthetic'}))}>Run 5-round FedAvg</button><button disabled={fedDisabled} onClick={()=>act(()=>api('experiment-jobs',{mode:'private-federated',rounds:1,dataset:'synthetic'}))}>Run Private FedAvg (DP)</button><span className={`badge ${health.coordinator==='available'?'badge-success':'badge-error'}`}>Coordinator {health.coordinator}</span>{fedDisabled&&<span className="muted" style={{marginLeft:'0.5rem'}}>{fedReason}</span>}</div>
 <div className="card"><h2>Client Topology</h2><p className="muted">Three isolated processes on the same host representing independent edge devices.</p><div className="topology-diagram">{['client-a','client-b','client-c'].map(cid=>{const priv=privacy.find(v=>v.client_id===cid);return(<div className="topology-node" key={cid}><b className="node-title">{cid}</b><small>Port {cid==='client-a'?8080:cid==='client-b'?8082:8083}</small>{priv?<div className="dp-info"><small>ε {priv.epsilon.toFixed(2)}</small><br/><small>{priv.steps} DP steps</small></div>:<div className="dp-info empty">No DP data</div>}</div>)})}</div><div className="topology-arrow">↕ HTTP (loopback)</div><div className="topology-coordinator"><b>Central Coordinator</b><small>Port 8100 · FedAvg aggregation</small></div></div>
 {jobs.length>0&&<div className="card"><h2>Experiment jobs</h2>{jobs.slice(0,5).map(j=><div className="row" key={j.job_id}><span>{j.mode} · {j.rounds} round · {j.status}</span><span>{j.job_id.slice(0,8)} {['queued','training'].includes(j.status)&&<button onClick={()=>act(()=>api(`experiment-jobs/${j.job_id}/cancel`,{}))}>Cancel</button>}</span></div>)}</div>}<div className="stats">{privacy.map(v=><div className="card" key={v.client_id}><small>{v.client_id} · same laptop</small><strong>ε {v.epsilon.toFixed(3)}</strong><span>δ {v.delta} · {v.steps} steps</span><p className="muted">{v.accountant} · {v.randomness_mode.replaceAll('_',' ')}</p></div>)}</div><div className="card"><h2>Measured experiment runs</h2>{!runs.length&&<p>No completed distributed run.</p>}{runs.map(r=><article key={r.run_id}><span className="badge">{r.mode} · {r.source} · {r.status}</span><h3>{r.rounds.length} round{r.rounds.length===1?'':'s'} · val. score {(r.validation_score*100 || 0).toFixed(1)}%</h3><p>Run {r.run_id}</p><p>Candidate Hash: {r.model_hash}</p>
 <button onClick={()=>act(()=>api(`models/${r.run_id}/activate`,{round:r.rounds.length}))}>Activate Candidate</button><button className="secondary" style={{marginLeft:'0.5rem'}} onClick={()=>act(()=>api(`models/rollback`,{}))}>Rollback to Previous</button>
 {r.rounds.map((round:Row)=><div className="row" key={round.round}><span>Round {round.round}: {round.clients.map((c:Row)=>`${c.client_id} ${c.records} records`).join(' · ')}</span><b>Base: {round.base_hash?.slice(0,8)}... Update: {round.model_hash?.slice(0,8)}...</b></div>)}</article>)}</div></>}
 
 {page==='Evidence'&&mode==='research'&&<div className="card"><h2>Evidence package</h2>
  {health.wesad && health.wesad.status === 'COMPLETED' ? (
    <div style={{background:'var(--surface)',borderRadius:'0.5rem',padding:'1rem',marginBottom:'1rem'}}>
      <p><strong>WESAD offline evaluation:</strong> COMPLETED</p>
      <p><strong>Imported subjects:</strong> {health.wesad.subject_count}</p>
      <p><strong>Train / Val / Test split counts:</strong> {health.wesad.splits.train?.length} / {health.wesad.splits.validation?.length} / {health.wesad.splits.test?.length}</p>
      <p><strong>Dataset SHA256:</strong> {health.wesad.dataset_hash}</p>
      <p><strong>Baseline model hash:</strong> {models.find(m => m.model_id === 'baseline' && m.source === 'Recorded dataset')?.model_hash?.slice(0,8) || 'N/A'}</p>
      <p><strong>Neural model hash:</strong> {models.find(m => m.model_id === 'neural' && m.source === 'Recorded dataset')?.model_hash?.slice(0,8) || 'N/A'}</p>
      <p><strong>Measured test metrics (Baseline):</strong> Balanced Acc: {((models.find(m => m.model_id === 'baseline' && m.source === 'Recorded dataset')?.test_balanced_accuracy || 0) * 100).toFixed(1)}% · Macro-F1: {(models.find(m => m.model_id === 'baseline' && m.source === 'Recorded dataset')?.test_macro_f1 || 0).toFixed(3)}</p>
      <p><strong>Measured test metrics (Neural):</strong> Balanced Acc: {((models.find(m => m.model_id === 'neural' && m.source === 'Recorded dataset')?.test_balanced_accuracy || 0) * 100).toFixed(1)}% · Macro-F1: {(models.find(m => m.model_id === 'neural' && m.source === 'Recorded dataset')?.test_macro_f1 || 0).toFixed(3)}</p>
      <p><strong>Federated run status:</strong> {health.wesad.federated_status}</p>
      <p><strong>Private federated run status:</strong> {health.wesad.private_federated_status}</p>
    </div>
  ) : (
    <div style={{background:'var(--surface)',borderRadius:'0.5rem',padding:'1rem',marginBottom:'1rem'}}>
      <p><strong>WESAD offline evaluation:</strong> NOT RUN</p>
    </div>
  )}
 <div style={{background:'var(--surface)',borderRadius:'0.5rem',padding:'1rem',marginBottom:'1rem'}}><p><strong>Active model:</strong> {activeModel?activeModel.model_hash?.slice(0,8)||'None':'No active model'}</p><p><strong>Architecture:</strong> {activeModel?.architecture_id||'Unavailable'}</p><p><strong>Threshold:</strong> {activeModel?.threshold!=null?activeModel.threshold:'Unavailable'}</p><p><strong>Lifecycle:</strong> {activeModel?.lifecycle_state||'Unavailable'}</p><p><strong>Source:</strong> Synthetic dataset (seeded, artificial)</p><p><strong>Verification:</strong> Hash-indexed; see export-manifest.json inside ZIP</p></div><button onClick={exportEvidence} id="download-evidence-zip">Download ZIP Evidence</button></div>}
 
 {page==='Settings'&&<><div className="card"><h2>Settings</h2><p className="muted">These settings apply to this browser session only.</p><label style={{display:'block',marginBottom:'1rem'}}>Replay speed (applies to next session start)<select value={speed} onChange={e=>SP(+e.target.value)}><option value={1}>1× (slow)</option><option value={5}>5× (medium)</option><option value={20}>20× (fast)</option></select></label><label style={{display:'flex',alignItems:'center',gap:'0.5rem',marginBottom:'1rem'}}><input type="checkbox" id="reduced-motion" onChange={e=>{if(e.target.checked){document.body.classList.add('reduce-motion')}else{document.body.classList.remove('reduce-motion')}}} aria-label="Reduce animations"/><span>Reduce animations (accessibility)</span></label><div className="muted" style={{fontSize:'0.8rem',marginTop:'1rem'}}><p>Active model hash: {activeModel?.model_hash?.slice(0,8)||'None'}</p><p>Threshold: {activeModel?.threshold!=null?activeModel.threshold:'Unavailable'}</p><p>Architecture: {activeModel?.architecture_id||'Unavailable'}</p></div></div></>}
 </section><footer>Research prototype · Recorded/simulated inputs · No live health measurements.</footer></main></div>
}
createRoot(document.getElementById('root')!).render(<BrowserRouter><App/></BrowserRouter>);
