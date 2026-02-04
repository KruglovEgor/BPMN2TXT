import React, { useState } from 'react';
import Header from './components/common/Header';
import TaskSelector from './components/common/TaskSelector';
import DiagramToText from './components/DiagramToText/DiagramToText';
import TextToDiagram from './components/TextToDiagram/TextToDiagram';

const App: React.FC = () => {
    const [selectedTask, setSelectedTask] = useState<'diagramToText' | 'textToDiagram'>('diagramToText');

    const handleTaskChange = (task: 'diagramToText' | 'textToDiagram') => {
        setSelectedTask(task);
    };

    return (
        <div className="App">
            <Header />
            <TaskSelector onTaskChange={handleTaskChange} />
            {selectedTask === 'diagramToText' ? <DiagramToText /> : <TextToDiagram />}
        </div>
    );
};

export default App;