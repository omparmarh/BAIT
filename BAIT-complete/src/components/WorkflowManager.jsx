import React, { useState, useEffect } from 'react';
import './WorkflowManager.css';

/**
 * BAIT PRO ULTIMATE - Workflow Manager Component
 * - Create workflows from natural language
 * - List and manage all workflows
 * - Execute workflows manually
 * - Enable/disable workflows
 */

const WorkflowManager = () => {
    const [workflows, setWorkflows] = useState([]);
    const [newWorkflowText, setNewWorkflowText] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [showExamples, setShowExamples] = useState(true);

    const examples = [
        "Every day at 9:00 am, open Chrome and go to Gmail.com",
        "Every 30 minutes, check calendar",
        "When I say 'work mode', close Spotify and open VS Code",
        "Every morning at 8am, play my favorite playlist"
    ];

    useEffect(() => {
        loadWorkflows();
    }, []);

    const loadWorkflows = async () => {
        setIsLoading(true);
        try {
            const response = await fetch('/api/ultimate/workflow/list');
            if (response.ok) {
                const data = await response.json();
                setWorkflows(data.workflows || []);
            }
        } catch (error) {
            console.error('Failed to load workflows:', error);
        } finally {
            setIsLoading(false);
        }
    };

    const createWorkflow = async () => {
        if (!newWorkflowText.trim()) return;

        setIsLoading(true);
        try {
            const response = await fetch('/api/ultimate/workflow/create', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ description: newWorkflowText })
            });

            if (response.ok) {
                setNewWorkflowText('');
                loadWorkflows();
            }
        } catch (error) {
            console.error('Failed to create workflow:', error);
        } finally {
            setIsLoading(false);
        }
    };

    const executeWorkflow = async (workflowId) => {
        try {
            const response = await fetch('/api/ultimate/workflow/execute', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ workflow_id: workflowId })
            });

            if (response.ok) {
                console.log('Workflow executed successfully');
            }
        } catch (error) {
            console.error('Failed to execute workflow:', error);
        }
    };

    const deleteWorkflow = async (workflowId) => {
        try {
            const response = await fetch(`/api/ultimate/workflow/${workflowId}`, {
                method: 'DELETE'
            });

            if (response.ok) {
                loadWorkflows();
            }
        } catch (error) {
            console.error('Failed to delete workflow:', error);
        }
    };

    const getTriggerIcon = (trigger) => {
        const typeIcons = {
            'time': '⏰',
            'interval': '🔄',
            'voice': '🎤',
            'app_event': '📱',
            'system': '⚙️',
            'manual': '👆'
        };
        return typeIcons[trigger.type] || '📌';
    };

    const getTriggerText = (trigger) => {
        if (trigger.type === 'time') {
            return `Daily at ${trigger.hour}:${trigger.minute.toString().padStart(2, '0')}`;
        }
        if (trigger.type === 'interval') {
            return `Every ${trigger.value} ${trigger.unit}(s)`;
        }
        if (trigger.type === 'voice') {
            return `Voice: "${trigger.command}"`;
        }
        if (trigger.type === 'manual') {
            return 'Manual execution';
        }
        return 'Custom trigger';
    };

    return (
        <div className="workflow-manager">
            <div className="workflow-header">
                <h3>⚡ Workflow Automation</h3>
                <div className="workflow-count">{workflows.length} workflows</div>
            </div>

            {/* Create Workflow */}
            <div className="workflow-create">
                <h4>Create New Workflow</h4>
                <textarea
                    placeholder="Describe your workflow in natural language..."
                    value={newWorkflowText}
                    onChange={(e) => setNewWorkflowText(e.target.value)}
                    className="workflow-input"
                    rows={3}
                />
                <button
                    onClick={createWorkflow}
                    disabled={!newWorkflowText.trim() || isLoading}
                    className="create-button"
                >
                    ✨ Create Workflow
                </button>

                {/* Examples */}
                {showExamples && (
                    <div className="workflow-examples">
                        <div className="examples-header">
                            <span>Examples:</span>
                            <button onClick={() => setShowExamples(false)} className="hide-button">
                                ×
                            </button>
                        </div>
                        {examples.map((example, index) => (
                            <div
                                key={index}
                                className="example-item"
                                onClick={() => setNewWorkflowText(example)}
                            >
                                {example}
                            </div>
                        ))}
                    </div>
                )}
            </div>

            {/* Workflow List */}
            <div className="workflow-list">
                <h4>Your Workflows</h4>
                {isLoading ? (
                    <div className="loading">Loading workflows...</div>
                ) : workflows.length === 0 ? (
                    <div className="no-workflows">
                        <p>No workflows yet. Create one above!</p>
                    </div>
                ) : (
                    workflows.map((workflow) => (
                        <div key={workflow.id} className="workflow-card">
                            <div className="workflow-info">
                                <h5 className="workflow-name">{workflow.name}</h5>

                                {/* Triggers */}
                                <div className="workflow-triggers">
                                    {workflow.triggers?.map((trigger, idx) => (
                                        <div key={idx} className="trigger-badge">
                                            {getTriggerIcon(trigger)} {getTriggerText(trigger)}
                                        </div>
                                    ))}
                                </div>

                                {/* Actions */}
                                <div className="workflow-actions-list">
                                    {workflow.actions?.map((action, idx) => (
                                        <div key={idx} className="action-item">
                                            → {action.type}: {JSON.stringify(action).substring(0, 50)}...
                                        </div>
                                    ))}
                                </div>

                                <div className="workflow-meta">
                                    <span className={`status ${workflow.enabled ? 'enabled' : 'disabled'}`}>
                                        {workflow.enabled ? '● Enabled' : '○ Disabled'}
                                    </span>
                                    <span className="created-date">
                                        {new Date(workflow.created_at).toLocaleDateString()}
                                    </span>
                                </div>
                            </div>

                            <div className="workflow-controls">
                                <button
                                    onClick={() => executeWorkflow(workflow.id)}
                                    className="execute-btn"
                                    title="Execute now"
                                >
                                    ▶️
                                </button>
                                <button
                                    onClick={() => deleteWorkflow(workflow.id)}
                                    className="delete-btn"
                                    title="Delete"
                                >
                                    🗑️
                                </button>
                            </div>
                        </div>
                    ))
                )}
            </div>
        </div>
    );
};

export default WorkflowManager;
