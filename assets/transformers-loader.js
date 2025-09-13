// Simple script to load Transformers.js from CDN and initialize embedding functionality
// This approach uses traditional script loading instead of ES6 modules

console.log('🔧 Transformers.js loader starting...');

// Global state
window.transformersLibraryLoaded = false;
window.transformersLibraryLoading = false;

// Function to dynamically load a script
function loadScript(src) {
    return new Promise((resolve, reject) => {
        const script = document.createElement('script');
        script.src = src;
        script.type = 'module';
        script.onload = () => resolve();
        script.onerror = () => reject(new Error(`Failed to load script: ${src}`));
        document.head.appendChild(script);
    });
}

// Function to initialize Transformers.js
async function initializeTransformers() {
    if (window.transformersLibraryLoaded) {
        console.log('✅ Transformers.js already loaded');
        return true;
    }
    
    if (window.transformersLibraryLoading) {
        console.log('⏳ Transformers.js already loading, waiting...');
        // Wait for loading to complete
        while (window.transformersLibraryLoading) {
            await new Promise(resolve => setTimeout(resolve, 100));
        }
        return window.transformersLibraryLoaded;
    }
    
    window.transformersLibraryLoading = true;
    
    try {
        console.log('📦 Loading Transformers.js from CDN...');
        
        // Use dynamic import since this is more reliable with ES modules
        const transformers = await import('https://cdn.jsdelivr.net/npm/@huggingface/transformers@3.0.0');
        window.transformersLibrary = transformers;
        window.transformersLibraryLoaded = true;
        
        console.log('✅ Transformers.js loaded successfully');
        return true;
    } catch (error) {
        console.error('❌ Failed to load Transformers.js:', error);
        return false;
    } finally {
        window.transformersLibraryLoading = false;
    }
}

// Simple embeddings class
class SimpleEmbedder {
    constructor() {
        this.pipeline = null;
        this.modelCache = new Map();
    }
    
    async generateEmbeddings(texts, modelName = 'Xenova/all-MiniLM-L6-v2') {
        console.log('🔄 Generating embeddings for', texts.length, 'texts with model', modelName);
        
        // Ensure Transformers.js is loaded
        if (!window.transformersLibraryLoaded) {
            const loaded = await initializeTransformers();
            if (!loaded) {
                throw new Error('Failed to load Transformers.js');
            }
        }
        
        // Create pipeline if not cached
        if (!this.modelCache.has(modelName)) {
            console.log('🏗️ Creating pipeline for', modelName);
            const { pipeline } = window.transformersLibrary;
            this.pipeline = await pipeline('feature-extraction', modelName);
            this.modelCache.set(modelName, this.pipeline);
        } else {
            this.pipeline = this.modelCache.get(modelName);
        }
        
        // Generate embeddings
        const embeddings = [];
        for (let i = 0; i < texts.length; i++) {
            console.log(`Processing text ${i + 1}/${texts.length}...`);
            const result = await this.pipeline(texts[i], { pooling: 'mean', normalize: true });
            embeddings.push(Array.from(result.data));
        }
        
        console.log('✅ Generated', embeddings.length, 'embeddings');
        return embeddings;
    }
}

// Create global instance
window.simpleEmbedder = new SimpleEmbedder();

// Set up Dash clientside callbacks
window.dash_clientside = window.dash_clientside || {};
window.dash_clientside.transformers = {
    generateEmbeddings: async function(nClicks, textContent, modelName, tokenizationMethod, category, subcategory) {
        console.log('🚀 Client-side generateEmbeddings called');

        if (!nClicks || !textContent || textContent.trim().length === 0) {
            console.log('⚠️ Missing required parameters');
            return window.dash_clientside.no_update;
        }

        try {
            // Ensure Transformers.js is loaded
            if (!window.transformersLibraryLoaded) {
                const loaded = await initializeTransformers();
                if (!loaded) {
                    return [
                        { error: 'Failed to load Transformers.js' },
                        false
                    ];
                }
            }

            // Tokenize text
            let textChunks;
            const trimmedText = textContent.trim();

            switch (tokenizationMethod) {
                case 'sentence':
                    textChunks = trimmedText.split(/[.!?]+/).map(s => s.trim()).filter(s => s.length > 0);
                    break;
                case 'paragraph':
                    textChunks = trimmedText.split(/\n\s*\n/).map(s => s.trim()).filter(s => s.length > 0);
                    break;
                case 'manual':
                    textChunks = trimmedText.split('\n').map(s => s.trim()).filter(s => s.length > 0);
                    break;
                default:
                    textChunks = [trimmedText];
            }

            if (textChunks.length === 0) {
                return [
                    { error: 'No valid text chunks after tokenization' },
                    false
                ];
            }

            // Generate embeddings
            const embeddings = await window.simpleEmbedder.generateEmbeddings(textChunks, modelName);

            // Create documents
            const documents = textChunks.map((text, i) => ({
                id: `text_input_${Date.now()}_${i}`,
                text: text,
                embedding: embeddings[i],
                category: category || "Text Input",
                subcategory: subcategory || "Generated",
                tags: []
            }));

            // Return the successful embeddings data
            const embeddingsData = {
                documents: documents,
                embeddings: embeddings
            };

            console.log('✅ Embeddings generated successfully:', embeddingsData);

            return [
                embeddingsData,
                false
            ];

        } catch (error) {
            console.error('❌ Error generating embeddings:', error);
            return [
                { error: error.message },
                false
            ];
        }
    }
};


console.log('✅ Simple Transformers.js setup complete');
console.log('Available functions:', Object.keys(window.dash_clientside.transformers));