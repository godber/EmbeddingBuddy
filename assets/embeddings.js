// Text input embedding generation using Transformers.js
// This module runs entirely in the browser for privacy and performance

// Global flag to track initialization
window.transformersLoading = false;
window.transformersLoaded = false;

class TransformersEmbedder {
    constructor() {
        this.extractor = null;
        this.currentModel = null;
        this.modelCache = new Map();
        this.isLoading = false;
    }
    
    async initializeModel(modelName = 'Xenova/all-MiniLM-L6-v2') {
        try {
            if (this.modelCache.has(modelName)) {
                this.extractor = this.modelCache.get(modelName);
                this.currentModel = modelName;
                return { success: true, model: modelName };
            }
            
            if (this.isLoading) {
                return { success: false, error: 'Model loading already in progress' };
            }
            
            this.isLoading = true;
            
            // Use globally loaded Transformers.js pipeline
            if (!window.transformers) {
                if (!window.transformersPipeline) {
                    // Wait for the pipeline to load
                    let attempts = 0;
                    while (!window.transformersPipeline && attempts < 50) { // Wait up to 5 seconds
                        await new Promise(resolve => setTimeout(resolve, 100));
                        attempts++;
                    }
                    if (!window.transformersPipeline) {
                        throw new Error('Transformers.js pipeline not available. Please refresh the page.');
                    }
                }
                window.transformers = { pipeline: window.transformersPipeline };
                window.transformersLoaded = true;
                console.log('✅ Using globally loaded Transformers.js pipeline');
            }
            
            this.extractor = await window.transformers.pipeline('feature-extraction', modelName);

            this.modelCache.set(modelName, this.extractor);
            this.currentModel = modelName;
            this.isLoading = false;

            return { success: true, model: modelName };
        } catch (error) {
            this.isLoading = false;
            console.error('Model initialization error:', error);
            return { success: false, error: error.message };
        }
    }
    
    async generateEmbeddings(texts, options = {}) {
        if (!this.extractor) {
            throw new Error('Model not initialized. Call initializeModel() first.');
        }
        
        if (!texts || texts.length === 0) {
            throw new Error('No texts provided for embedding generation.');
        }
        
        const embeddings = [];
        const defaultOptions = { 
            pooling: 'mean', 
            normalize: true,
            ...options 
        };
        
        // Process in batches to avoid memory issues
        const batchSize = options.batchSize || 8;
        
        try {
            for (let i = 0; i < texts.length; i += batchSize) {
                const batch = texts.slice(i, i + batchSize);
                
                const batchResults = await Promise.all(
                    batch.map(text => {
                        if (!text || text.trim().length === 0) {
                            throw new Error('Empty text found in batch');
                        }
                        return this.extractor(text.trim(), defaultOptions);
                    })
                );
                
                // Convert tensor output to arrays
                batchResults.forEach((result, idx) => {
                    if (result && result.data) {
                        embeddings.push(Array.from(result.data));
                    } else {
                        throw new Error(`Invalid embedding result for text: ${batch[idx]}`);
                    }
                });
                
            }

            return embeddings;
        } catch (error) {
            console.error('Embedding generation error:', error);
            throw error;
        }
    }
}

// Global instance
window.transformersEmbedder = new TransformersEmbedder();
console.log('📦 TransformersEmbedder instance created');


// Dash clientside callback functions
window.dash_clientside = window.dash_clientside || {};
console.log('🔧 Setting up window.dash_clientside.transformers');
window.dash_clientside.transformers = {
    generateEmbeddings: async function(nClicks, textContent, modelName, tokenizationMethod, category, subcategory) {
        console.log('🚀 generateEmbeddings called with:', { nClicks, modelName, tokenizationMethod, textLength: textContent?.length });

        if (!nClicks || !textContent || textContent.trim().length === 0) {
            console.log('⚠️ Early return - missing required parameters');
            return window.dash_clientside.no_update;
        }

        try {
            // Initialize model if needed
            const initResult = await window.transformersEmbedder.initializeModel(modelName);
            if (!initResult.success) {
                return [
                    { error: `Model loading error: ${initResult.error}` },
                    false
                ];
            }

            // Tokenize text based on method
            let textChunks;
            const trimmedText = textContent.trim();

            switch (tokenizationMethod) {
                case 'sentence':
                    textChunks = trimmedText
                        .split(/[.!?]+/)
                        .map(s => s.trim())
                        .filter(s => s.length > 0);
                    break;
                case 'paragraph':
                    textChunks = trimmedText
                        .split(/\n\s*\n/)
                        .map(s => s.trim())
                        .filter(s => s.length > 0);
                    break;
                case 'manual':
                    textChunks = trimmedText
                        .split('\n')
                        .map(s => s.trim())
                        .filter(s => s.length > 0);
                    break;
                default:
                    textChunks = [trimmedText];
            }

            if (textChunks.length === 0) {
                return [
                    { error: 'No valid text chunks found after tokenization' },
                    false
                ];
            }

            // Generate embeddings
            const embeddings = await window.transformersEmbedder.generateEmbeddings(textChunks);

            if (!embeddings || embeddings.length !== textChunks.length) {
                return [
                    { error: 'Embedding generation failed' },
                    false
                ];
            }

            // Create documents structure
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
            console.error('Client-side embedding error:', error);
            return [
                { error: error.message },
                false
            ];
        }
    }
};


console.log('✅ Transformers.js client-side setup complete');
console.log('Available:', {
    transformersEmbedder: !!window.transformersEmbedder,
    dashClientside: !!window.dash_clientside,
    transformersModule: !!window.dash_clientside?.transformers,
    generateFunction: typeof window.dash_clientside?.transformers?.generateEmbeddings,
    processAsync: typeof window.processEmbeddingsAsync
});