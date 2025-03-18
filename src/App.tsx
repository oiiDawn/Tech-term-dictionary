import React, { useEffect, useState } from 'react';

const App: React.FC = () => {
    const [elements, setElements] = useState<Array<{ tag: string; id: string; className: string }> | null>(null);

    useEffect(() => {
        chrome.storage.local.get('elements', (data) => {
            setElements(data.elements || []);
        });
    }, []);

    return (
        <div>
            <h1>Page Elements</h1>
            <pre>{JSON.stringify(elements, null, 2)}</pre>
        </div>
    );
};

export default App;