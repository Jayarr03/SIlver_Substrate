import { useState, useEffect } from 'react';
import axios from 'axios';

const API_URL = 'http://localhost:5000/api';

function AssessmentDetail({ filename, onBack, showBackButton = true }) {
  const [assessment, setAssessment] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('threats'); // 'threats', 'requirements', 'actions'

  useEffect(() => {
    loadAssessment();
  }, [filename]);

  const loadAssessment = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await axios.get(`${API_URL}/assessments/${filename}`);
      setAssessment(response.data);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to load assessment');
    } finally {
      setLoading(false);
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority?.toLowerCase()) {
      case 'critical': return '#dc2626';
      case 'high': return '#ea580c';
      case 'medium': return '#eab308';
      case 'low': return '#16a34a';
      default: return '#6b7280';
    }
  };

  if (loading) {
    return <div className="loading">Loading assessment...</div>;
  }

  if (error) {
    return (
      <div>
        {showBackButton && onBack && (
          <button onClick={onBack} className="btn-back">← Back</button>
        )}
        <div className="error-message">❌ {error}</div>
      </div>
    );
  }

  if (!assessment) {
    return null;
  }

  return (
    <div className="assessment-detail">
      {showBackButton && onBack && (
        <button onClick={onBack} className="btn-back">← Back to Library</button>
      )}
      
      <div className="detail-header">
        <h1>{assessment.component_name}</h1>
        <span className="level-badge large">
          {assessment.level.replace(/_/g, ' ')}
        </span>
      </div>

      <div className="detail-summary">
        <h3>Summary</h3>
        <p>{assessment.summary}</p>
      </div>

      <div className="detail-assumptions">
        <h3>Deployment Assumptions</h3>
        <p>{assessment.deployment_assumptions}</p>
      </div>

      <div className="detail-prioritization">
        <h3>Prioritization Summary</h3>
        <p>{assessment.prioritization_summary}</p>
      </div>

      <div className="tabs">
        <button 
          className={activeTab === 'threats' ? 'active' : ''}
          onClick={() => setActiveTab('threats')}
        >
          🚨 Threats ({assessment.threats?.length || 0})
        </button>
        <button 
          className={activeTab === 'requirements' ? 'active' : ''}
          onClick={() => setActiveTab('requirements')}
        >
          ✅ Requirements ({assessment.security_requirements?.length || 0})
        </button>
        <button 
          className={activeTab === 'actions' ? 'active' : ''}
          onClick={() => setActiveTab('actions')}
        >
          📋 Actions ({assessment.prioritized_actions?.length || 0})
        </button>
      </div>

      <div className="tab-content">
        {activeTab === 'threats' && (
          <div className="threats-list">
            {assessment.threats?.map((threat, index) => (
              <div key={index} className="threat-card">
                <div className="threat-header">
                  <h4>{threat.title}</h4>
                  <span 
                    className="priority-badge"
                    style={{ backgroundColor: getPriorityColor(threat.priority) }}
                  >
                    {threat.priority} ({threat.priority_score})
                  </span>
                </div>
                <p className="description">{threat.description}</p>
                
                {/* Attack Overview Highlight */}
                <div className="attack-overview">
                  <div className="attack-overview-item">
                    <div className="attack-icon">🎯</div>
                    <div className="attack-content">
                      <strong>Attack Surface</strong>
                      <p>{threat.attack_surface}</p>
                    </div>
                  </div>
                  
                  <div className="attack-overview-item">
                    <div className="attack-icon">⚔️</div>
                    <div className="attack-content">
                      <strong>Attack Scenario</strong>
                      <p>{threat.scenario}</p>
                    </div>
                  </div>
                  
                  <div className="attack-overview-item impact">
                    <div className="attack-icon">💥</div>
                    <div className="attack-content">
                      <strong>Potential Impact</strong>
                      <p>{threat.potential_impact}</p>
                    </div>
                  </div>
                  
                  <div className="attack-overview-item outcome">
                    <div className="attack-icon">⚠️</div>
                    <div className="attack-content">
                      <strong>Deployment Outcome</strong>
                      <p>{threat.deployment_consequence}</p>
                    </div>
                  </div>
                </div>

                {/* Additional Details */}
                <div className="threat-details-section">
                  <div className="threat-section">
                    <strong>SDLC Phase:</strong>
                    <p>{threat.sdlc_phase} - {threat.sdlc_phase_description}</p>
                  </div>

                  {threat.preconditions?.length > 0 && (
                    <div className="threat-section">
                      <strong>Attack Preconditions:</strong>
                      <ul>
                        {threat.preconditions.map((pre, i) => (
                          <li key={i}>{pre}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  <div className="threat-section">
                    <strong>Priority Rationale:</strong>
                    <p>{threat.priority_rationale}</p>
                  </div>

                  <div className="threat-section">
                    <strong>Confidence Level:</strong>
                    <span className="confidence-badge">{threat.confidence}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {activeTab === 'requirements' && (
          <div className="requirements-list">
            {assessment.security_requirements?.map((req, index) => (
              <div key={index} className="requirement-card">
                <div className="requirement-header">
                  <h4>{req.title}</h4>
                  <span 
                    className="priority-badge"
                    style={{ backgroundColor: getPriorityColor(req.priority) }}
                  >
                    {req.priority} ({req.priority_score})
                  </span>
                </div>
                <p className="description">{req.description}</p>
                
                <div className="requirement-section">
                  <strong>SDLC Phase:</strong>
                  <p>{req.sdlc_phase}</p>
                </div>

                <div className="requirement-section">
                  <strong>Requirement:</strong>
                  <p>{req.requirement}</p>
                </div>

                {req.mitigates?.length > 0 && (
                  <div className="requirement-section">
                    <strong>Mitigates Threats:</strong>
                    <ul>
                      {req.mitigates.map((threat, i) => (
                        <li key={i}>{threat}</li>
                      ))}
                    </ul>
                  </div>
                )}

                <div className="requirement-section">
                  <strong>Verification Method:</strong>
                  <p>{req.verification_method}</p>
                </div>

                <div className="requirement-section">
                  <strong>Owner:</strong>
                  <p>{req.owner}</p>
                </div>

                <div className="requirement-section">
                  <strong>Design Robustness:</strong>
                  <p>{req.design_robustness}</p>
                </div>

                <div className="requirement-section">
                  <strong>Priority Rationale:</strong>
                  <p>{req.priority_rationale}</p>
                </div>
              </div>
            ))}
          </div>
        )}

        {activeTab === 'actions' && (
          <div className="actions-list">
            {assessment.prioritized_actions?.map((action) => (
              <div key={action.rank} className="action-card">
                <div className="action-header">
                  <span className="action-rank">#{action.rank}</span>
                  <h4>{action.title}</h4>
                  <span 
                    className="priority-badge"
                    style={{ backgroundColor: getPriorityColor(action.priority) }}
                  >
                    {action.priority} ({action.priority_score})
                  </span>
                </div>
                
                <div className="action-type">{action.action_type}</div>
                
                <div className="action-section">
                  <strong>Rationale:</strong>
                  <p>{action.rationale}</p>
                </div>

                <div className="action-section">
                  <strong>Next Step:</strong>
                  <p>{action.next_step}</p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {assessment.open_questions?.length > 0 && (
        <div className="open-questions">
          <h3>Open Questions</h3>
          <ul>
            {assessment.open_questions.map((question, i) => (
              <li key={i}>{question}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

export default AssessmentDetail;
