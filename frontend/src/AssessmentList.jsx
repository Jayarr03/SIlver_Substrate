import { useState, useEffect } from 'react';
import axios from 'axios';
import AssessmentDetail from './AssessmentDetail';

const API_URL = 'http://localhost:5000/api';

function AssessmentList({ refreshKey }) {
  const [assessments, setAssessments] = useState([]);
  const [selectedAssessment, setSelectedAssessment] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadAssessments();
  }, [refreshKey]);

  const loadAssessments = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await axios.get(`${API_URL}/assessments`);
      setAssessments(response.data.assessments);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to load assessments');
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (timestamp) => {
    return new Date(timestamp * 1000).toLocaleString();
  };

  if (loading) {
    return <div className="loading">Loading assessments...</div>;
  }

  if (error) {
    return <div className="error-message">❌ {error}</div>;
  }

  if (assessments.length === 0) {
    return (
      <div className="empty-state">
        <h2>No Assessments Yet</h2>
        <p>Create your first hardware threat assessment to get started.</p>
      </div>
    );
  }

  return (
    <div className="library-split-view">
      {/* Left Panel - Component List */}
      <div className="library-sidebar">
        <div className="sidebar-header">
          <h2>Components</h2>
          <span className="list-count">{assessments.length}</span>
        </div>
        
        <div className="component-list">
          {assessments.map((assessment) => (
            <div 
              key={assessment.filename}
              className={`component-list-item ${selectedAssessment === assessment.filename ? 'active' : ''}`}
              onClick={() => setSelectedAssessment(assessment.filename)}
            >
              <div className="component-list-header">
                <h3>{assessment.component_name}</h3>
                <span className="mini-badge">{assessment.threat_count}</span>
              </div>
              <div className="component-list-meta">
                <span className="mini-level-badge">
                  {assessment.level.replace(/_/g, ' ')}
                </span>
                <span className="mini-date">{formatDate(assessment.created)}</span>
              </div>
              {assessment.top_threat && (
                <div className="mini-threat-preview">
                  🎯 {assessment.top_threat.title}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Right Panel - Detail View */}
      <div className="library-detail-panel">
        {selectedAssessment ? (
          <AssessmentDetail 
            filename={selectedAssessment}
            showBackButton={false}
          />
        ) : (
          <div className="detail-placeholder">
            <div className="placeholder-content">
              <h2>👈 Select a component</h2>
              <p>Choose a component from the list to view its threat assessment details.</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default AssessmentList;
