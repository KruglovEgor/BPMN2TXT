import React, { useState } from 'react';
import { textToDiagram } from '../../api/gateway';
import DiagramViewer from './DiagramViewer';

const TextToDiagram: React.FC = () => {
    const [description, setDescription] = useState('');
    const [diagramCode, setDiagramCode] = useState('');
    const [error, setError] = useState<string | null>(null);

    const handleDescriptionChange = (event: React.ChangeEvent<HTMLTextAreaElement>) => {
        setDescription(event.target.value);
    };

    const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
        event.preventDefault();
        setError(null);
        setDiagramCode('');
        try {
            const result = await textToDiagram(description);
            setDiagramCode(result.diagramCode);
        } catch (err) {
            setError('Failed to generate diagram.');
        }
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
            {error && (
                <div className="result-box">
                    <h3>Error:</h3>
                    <p>{error}</p>
                </div>
            )}
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