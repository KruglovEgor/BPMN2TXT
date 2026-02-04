export const formatDescription = (description: string): string => {
    return description.trim();
};

export const validateScreenshot = (file: File | null): boolean => {
    if (!file) return false;
    const validTypes = ['image/png', 'image/jpeg', 'image/jpg'];
    return validTypes.includes(file.type);
};