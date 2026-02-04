import React, { useState } from 'react';

const TaskSelector: React.FC<{ onTaskChange: (task: 'diagramToText' | 'textToDiagram') => void }> = ({ onTaskChange }) => {
    const [selectedTask, setSelectedTask] = useState<string>('diagramToText');

    const handleTaskChange = (task: 'diagramToText' | 'textToDiagram') => {
        setSelectedTask(task);
        onTaskChange(task);
    };

    return (
        <div className="task-selector">
            <button onClick={() => handleTaskChange('diagramToText')} className={selectedTask === 'diagramToText' ? 'active' : ''}>
                Diagram to Text
            </button>
            <button onClick={() => handleTaskChange('textToDiagram')} className={selectedTask === 'textToDiagram' ? 'active' : ''}>
                Text to Diagram
            </button>
        </div>
    );
};

export default TaskSelector;