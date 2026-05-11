import { useState } from 'react';
import axios from 'axios';

const API_URL = 'http://localhost:5000/api';

function ComponentForm({ onAssessmentCreated }) {
  const [componentName, setComponentName] = useState('');
  const [useInteractive, setUseInteractive] = useState(true);
  const [suggestion, setSuggestion] = useState(null);
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState(null);

  // Manual mode fields
  const [level, setLevel] = useState('');
  const [description, setDescription] = useState('');
  const [assets, setAssets] = useState(['']);
  const [interfaces, setInterfaces] = useState(['']);
  const [priorityDrivers, setPriorityDrivers] = useState(['']);

  const handleGetSuggestions = async () => {
    if (!componentName.trim()) {
      setError('Please enter a component name');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await axios.post(`${API_URL}/suggest`, {
        component_name: componentName,
      });
      setSuggestion(response.data);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to get suggestions');
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateAssessment = async () => {
    setGenerating(true);
    setError(null);

    try {
      const payload = {
        component_name: componentName,
      };

      if (useInteractive && suggestion) {
        payload.level = suggestion.level;
        payload.description = suggestion.description;
        payload.assets = suggestion.assets;
        payload.interfaces = suggestion.interfaces;
        payload.priority_drivers = suggestion.priority_drivers;
      } else if (!useInteractive) {
        payload.level = level;
        payload.description = description;
        payload.assets = assets.filter(a => a.trim());
        payload.interfaces = interfaces.filter(i => i.trim());
        payload.priority_drivers = priorityDrivers.filter(p => p.trim());
      }

      await axios.post(`${API_URL}/assess`, payload);
      onAssessmentCreated();
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to generate assessment');
      setGenerating(false);
    }
  };

  const addField = (setter, current) => {
    setter([...current, '']);
  };

  const updateField = (setter, current, index, value) => {
    const updated = [...current];
    updated[index] = value;
    setter(updated);
  };

  return (
    <div className="component-form">
      <h2>Create New Assessment</h2>

      <div className="form-group">
        <label>Component Name *</label>
        <input
          type="text"
          value={componentName}
          onChange={(e) => setComponentName(e.target.value)}
          placeholder="e.g., gate oxide, bond pad, crypto engine"
          disabled={generating}
        />
      </div>

      <div className="form-group">
        <label>
          <input
            type="checkbox"
            checked={useInteractive}
            onChange={(e) => setUseInteractive(e.target.checked)}
            disabled={generating}
          />
          Use AI-suggested metadata (recommended)
        </label>
      </div>

      {useInteractive ? (
        <div className="interactive-mode">
          {!suggestion ? (
            <button 
              onClick={handleGetSuggestions}
              disabled={loading || !componentName.trim()}
              className="btn-primary"
            >
              {loading ? '🔍 Analyzing...' : '🔍 Get Suggestions'}
            </button>
          ) : (
            <div className="suggestion-box">
              <h3>AI Suggestions</h3>
              
              <div className="suggestion-item">
                <strong>Hardware Level:</strong>
                <p>{suggestion.level.replace(/_/g, ' ')}</p>
              </div>

              <div className="suggestion-item">
                <strong>Description:</strong>
                <p>{suggestion.description}</p>
              </div>

              <div className="suggestion-item">
                <strong>Protected Assets:</strong>
                <ul>
                  {suggestion.assets.map((asset, i) => (
                    <li key={i}>{asset}</li>
                  ))}
                </ul>
              </div>

              <div className="suggestion-item">
                <strong>Interfaces:</strong>
                <ul>
                  {suggestion.interfaces.map((iface, i) => (
                    <li key={i}>{iface}</li>
                  ))}
                </ul>
              </div>

              <div className="suggestion-item">
                <strong>Priority Drivers:</strong>
                <ul>
                  {suggestion.priority_drivers.map((driver, i) => (
                    <li key={i}>{driver}</li>
                  ))}
                </ul>
              </div>

              <div className="suggestion-item">
                <strong>Rationale:</strong>
                <p>{suggestion.rationale}</p>
              </div>

              <div className="button-group">
                <button 
                  onClick={handleGenerateAssessment}
                  disabled={generating}
                  className="btn-success"
                >
                  {generating ? '⚙️ Generating...' : '✅ Generate Assessment'}
                </button>
                <button 
                  onClick={() => setSuggestion(null)}
                  disabled={generating}
                  className="btn-secondary"
                >
                  Try Again
                </button>
              </div>
            </div>
          )}
        </div>
      ) : (
        <div className="manual-mode">
          <div className="form-group">
            <label>Hardware Level *</label>
            <select value={level} onChange={(e) => setLevel(e.target.value)}>
              <option value="">Select level...</option>
              <option value="architecture_rtl_gates">Architecture / RTL / Gates</option>
              <option value="transistors">Transistors</option>
              <option value="terminals_channel_body">Source, Drain, Gate, Channel, Body</option>
              <option value="doped_regions_wells_junctions">Doped Regions / Wells / Junctions</option>
              <option value="oxides_dielectrics_isolation">Oxides, Dielectrics, Isolation</option>
              <option value="contacts_vias_interconnects">Contacts, Vias, Interconnects</option>
              <option value="passivation_protective_layers">Passivation and Protective Layers</option>
              <option value="die_package_substrate_pins">Die, Package, Substrate, Pins</option>
              <option value="wafer_process_chemistry">Wafer Material, Process, Chemistry</option>
            </select>
          </div>

          <div className="form-group">
            <label>Description</label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows="3"
            />
          </div>

          <div className="form-group">
            <label>Protected Assets</label>
            {assets.map((asset, i) => (
              <input
                key={i}
                type="text"
                value={asset}
                onChange={(e) => updateField(setAssets, assets, i, e.target.value)}
                placeholder="e.g., cryptographic keys"
              />
            ))}
            <button onClick={() => addField(setAssets, assets)} className="btn-small">
              + Add Asset
            </button>
          </div>

          <div className="form-group">
            <label>Interfaces</label>
            {interfaces.map((iface, i) => (
              <input
                key={i}
                type="text"
                value={iface}
                onChange={(e) => updateField(setInterfaces, interfaces, i, e.target.value)}
                placeholder="e.g., metal layer contact"
              />
            ))}
            <button onClick={() => addField(setInterfaces, interfaces)} className="btn-small">
              + Add Interface
            </button>
          </div>

          <div className="form-group">
            <label>Priority Drivers</label>
            {priorityDrivers.map((driver, i) => (
              <input
                key={i}
                type="text"
                value={driver}
                onChange={(e) => updateField(setPriorityDrivers, priorityDrivers, i, e.target.value)}
                placeholder="e.g., no field update path"
              />
            ))}
            <button onClick={() => addField(setPriorityDrivers, priorityDrivers)} className="btn-small">
              + Add Driver
            </button>
          </div>

          <button 
            onClick={handleGenerateAssessment}
            disabled={generating || !componentName.trim() || !level}
            className="btn-primary"
          >
            {generating ? '⚙️ Generating...' : '🚀 Generate Assessment'}
          </button>
        </div>
      )}

      {error && <div className="error-message">❌ {error}</div>}
      {generating && (
        <div className="info-message">
          ⚙️ Generating threat assessment... This may take 30-60 seconds.
        </div>
      )}
    </div>
  );
}

export default ComponentForm;
