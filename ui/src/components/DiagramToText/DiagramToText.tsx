import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import ScreenshotUpload from './ScreenshotUpload';
import { diagramToText } from '../../api/gateway';

const DiagramToText: React.FC = () => {
    const [description, setDescription] = useState<string | null>(null);
    const [error, setError] = useState<string | null>(null);

    const handleScreenshotUpload = async (file: File) => {
        setError(null);
        setDescription(null);
        try {
            const result = await diagramToText(file);
            setDescription(result.description);
        } catch (err) {
            setError('Failed to convert diagram.');
        }
    };

    return (
        <div className="container">
            <h2>Diagram to Text</h2>
            <ScreenshotUpload onUpload={handleScreenshotUpload} />
            {error && (
                <div className="result-box">
                    <h3>Error:</h3>
                    <p>{error}</p>
                </div>
            )}
            {description && (
                <div className="result-box">
                    <h3>Text Description:</h3>
                    <div className="markdown-content">
                        <ReactMarkdown remarkPlugins={[remarkGfm]}>
                            {description}
                        </ReactMarkdown>
                    </div>
                </div>
            )}
        </div>
    );
};

export default DiagramToText;