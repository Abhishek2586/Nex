export const researchPages = ['Overview', 'System & Embodiment', 'Live session', 'Interventions', 'AI insights', 'Federated & privacy lab', 'Evidence', 'Settings'];
export const userPages = ['Home', 'Guidance', 'History', 'About', 'Settings'];
export const SCENARIOS: Record<string, string> = {
  'normal': 'Normal simulated session',
  'gradual_stress': 'Gradual stress-like change',
  'sustained_posture': 'Sustained posture deviation',
  'brief_posture': 'Brief posture deviation',
  'missing_data': 'Missing / low-quality signal',
  'high_motion': 'High-motion interference',
  'repeated_dismissal': 'Repeated prompt dismissal'
};