import { DiagramToTextResponse, TextToDiagramResponse } from '../types';

const API_BASE = process.env.REACT_APP_API_BASE || 'http://localhost:7000';

export const diagramToText = async (image: File): Promise<DiagramToTextResponse> => {
    const formData = new FormData();
    formData.append('image', image);

    const response = await fetch(`${API_BASE}/api/v1/diagram-to-text`, {
        method: 'POST',
        body: formData
    });

    if (!response.ok) {
        throw new Error(`Request failed: ${response.status}`);
    }

    return response.json();
};

export const textToDiagram = async (description: string): Promise<TextToDiagramResponse> => {
    const response = await fetch(`${API_BASE}/api/v1/text-to-diagram`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ description })
    });

    if (!response.ok) {
        throw new Error(`Request failed: ${response.status}`);
    }

    return response.json();
};
