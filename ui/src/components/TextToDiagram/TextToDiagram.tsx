import React, { useState } from 'react';
import { getDiagramCode } from '../../mocks/textToDiagramMock';
import DiagramViewer from './DiagramViewer';

const TextToDiagram: React.FC = () => {
    const [description, setDescription] = useState('');
    const [diagramCode, setDiagramCode] = useState('');

    const handleDescriptionChange = (event: React.ChangeEvent<HTMLTextAreaElement>) => {
        setDescription(event.target.value);
    };

    const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
        event.preventDefault();
        const code = await getDiagramCode(description);
        setDiagramCode(code);
    };

    return (
        <div className="container">
            <h2>Text to Diagram</h2>
            <form onSubmit={handleSubmit} className="input-form">
                <textarea
                    value={description}
                    onChange={handleDescriptionChange}
                    placeholder="Enter your text description here"
                    rows={5}
                    required
                />
                <div className="button-container">
                    <button type="submit" className="generate-btn">Generate</button>
                </div>
            </form>
            {diagramCode && (
                <div className="result-box">
                    <h3>Generated Diagram:</h3>
                    <DiagramViewer diagramCode={diagramCode} />
                </div>
            )}
        </div>
    );
};

export default TextToDiagram;