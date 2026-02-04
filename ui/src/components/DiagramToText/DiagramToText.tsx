import React, { useState } from 'react';
import ScreenshotUpload from './ScreenshotUpload';
import { mockDiagramToText } from '../../mocks/diagramToTextMock';

const DiagramToText: React.FC = () => {
    const [description, setDescription] = useState<string | null>(null);

    const handleScreenshotUpload = async (file: File) => {
        const result = await mockDiagramToText(file);
        setDescription(result);
    };

    return (
        <div className="container">
            <h2>Diagram to Text</h2>
            <ScreenshotUpload onUpload={handleScreenshotUpload} />
            {description && (
                <div className="result-box">
                    <h3>Text Description:</h3>
                    <p>{description}</p>
                </div>
            )}
        </div>
    );
};

export default DiagramToText;