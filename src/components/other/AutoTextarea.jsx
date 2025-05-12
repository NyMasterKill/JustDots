import { useRef, useEffect } from 'react';

const AutoResizeTextarea = () => {
    const textareaRef = useRef(null);

    const adjustHeight = () => {
        if (textareaRef.current) {
            textareaRef.current.style.height = 'auto';
            textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
        }
    };

    useEffect(() => {
        adjustHeight();
        // Добавляем обработчик на случай изменения значения извне
        const textarea = textareaRef.current;
        textarea?.addEventListener('input', adjustHeight);
        return () => textarea?.removeEventListener('input', adjustHeight);
    }, []);

    return { textareaRef, adjustHeight };
};

export const AutoTextarea = ({ children }) => {
    const { textareaRef } = AutoResizeTextarea();

    return (
        <textarea
            ref={textareaRef}
            placeholder="Введите текст..."
            value={children}
            className='taskblock-desc'
            rows={1}
            style={{
                resize: 'none',
                overflow: 'hidden',
                minHeight: '50px',
            }}
            disabled
        />
    );
};

export default AutoTextarea;