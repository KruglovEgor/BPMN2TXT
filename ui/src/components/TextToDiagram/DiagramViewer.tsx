import React, { useEffect, useRef, useState } from 'react';
import mermaid from 'mermaid';

interface DiagramViewerProps {
    diagramCode: string;
}

const DiagramViewer: React.FC<DiagramViewerProps> = ({ diagramCode }) => {
    const diagramRef = useRef<HTMLDivElement>(null);
    const [svg, setSvg] = useState<string>('');
    const [showCode, setShowCode] = useState<boolean>(false);

    useEffect(() => {
        const renderDiagram = async () => {
            if (diagramCode) {
                try {
                    mermaid.initialize({ 
                        startOnLoad: false, 
                        theme: 'default',
                        securityLevel: 'loose'
                    });
                    
                    const { svg: renderedSvg } = await mermaid.render('diagram-' + Date.now(), diagramCode);
                    setSvg(renderedSvg);
                } catch (error) {
                    console.error('Diagram rendering error:', error);
                    setSvg('');
                }
            }
        };
        
        renderDiagram();
    }, [diagramCode]);

    return (
        <div>
            <div className="diagram-controls">
                <button type="button" onClick={() => setShowCode(!showCode)}>
                    {showCode ? 'Hide Code' : 'Show Code'}
                </button>
            </div>
            
            {showCode && (
                <div className="diagram-code">
                    <h4>Diagram Code:</h4>
                    <pre>{diagramCode}</pre>
                </div>
            )}
            
            <div className="diagram-display" ref={diagramRef} dangerouslySetInnerHTML={{ __html: svg }} />
        </div>
    );
};

export default DiagramViewer;