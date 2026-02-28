import request from './request'

// --- LLMConfiguration ---
export function getLLMConfigs(params?: any) {
    return request({ url: '/llm-configs/', method: 'get', params })
}
export function createLLMConfig(data: any) {
    return request({ url: '/llm-configs/', method: 'post', data })
}
export function updateLLMConfig(id: number, data: any) {
    return request({ url: `/llm-configs/${id}/`, method: 'put', data })
}
export function deleteLLMConfig(id: number) {
    return request({ url: `/llm-configs/${id}/`, method: 'delete' })
}

// --- RAGConfiguration ---
export function getRAGConfigs(params?: any) {
    return request({ url: '/rag-configs/', method: 'get', params })
}
export function createRAGConfig(data: any) {
    return request({ url: '/rag-configs/', method: 'post', data })
}
export function updateRAGConfig(id: number, data: any) {
    return request({ url: `/rag-configs/${id}/`, method: 'put', data })
}
export function deleteRAGConfig(id: number) {
    return request({ url: `/rag-configs/${id}/`, method: 'delete' })
}

// --- MCPConfiguration ---
export function getMCPConfigs(params?: any) {
    return request({ url: '/mcp-configs/', method: 'get', params })
}
export function createMCPConfig(data: any) {
    return request({ url: '/mcp-configs/', method: 'post', data })
}
export function updateMCPConfig(id: number, data: any) {
    return request({ url: `/mcp-configs/${id}/`, method: 'put', data })
}
export function deleteMCPConfig(id: number) {
    return request({ url: `/mcp-configs/${id}/`, method: 'delete' })
}

// --- LLMUsageLog ---
export function getLLMUsageLogs(params?: any) {
    return request({ url: '/llm-usage-logs/', method: 'get', params })
}

// --- Agent Tasks ---
export function saveAgentCases(data: { project_id: number; content: string; name?: string }) {
    // Note: use exactly matching URL schema since request intercepter appends API_BASE_URL (/api/v1 by default locally). 
    // Here we need to circumvent /v1 appending if the backend is strictly 'api/ai-core' and not under v1 router. 
    // Instead of messing with axios instance, we just map it into backend root.
    return request({ url: '/../ai-core/agent/save-cases/', method: 'post', data })
}
