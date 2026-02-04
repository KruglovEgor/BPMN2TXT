export const getDiagramCode = (description: string): Promise<string> => {
    return new Promise((resolve) => {
        // Simulating a delay for the mock API response
        setTimeout(() => {
            // Mock diagram code based on the description
            const mockDiagramCode = `
                graph TD;
                A[${description}] --> B[Next Step];
                B --> C[Final Step];
            `;
            resolve(mockDiagramCode);
        }, 1000);
    });
};

export default getDiagramCode;