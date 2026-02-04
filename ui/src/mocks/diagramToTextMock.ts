export const mockDiagramToText = (screenshot: File): Promise<string> => {
    return new Promise((resolve) => {
        setTimeout(() => {
            resolve("This is a mock description of the diagram.");
        }, 1000);
    });
};

export default mockDiagramToText;