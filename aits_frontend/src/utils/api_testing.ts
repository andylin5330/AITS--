import request from './request'

// --- APISpecification ---
export function getAPISpecs(params?: any) {
    return request({ url: '/api-specifications/', method: 'get', params })
}
export function createAPISpec(data: any) {
    return request({ url: '/api-specifications/', method: 'post', data })
}
export function deleteAPISpec(id: number) {
    return request({ url: `/api-specifications/${id}/`, method: 'delete' })
}

// --- APITestCase ---
export function getAPITestCases(params?: any) {
    return request({ url: '/api-cases/', method: 'get', params })
}
export function createAPITestCase(data: any) {
    return request({ url: '/api-cases/', method: 'post', data })
}
export function updateAPITestCase(id: number, data: any) {
    return request({ url: `/api-cases/${id}/`, method: 'put', data })
}
export function deleteAPITestCase(id: number) {
    return request({ url: `/api-cases/${id}/`, method: 'delete' })
}

// --- APITestSuite ---
export function getAPITestSuites(params?: any) {
    return request({ url: '/api-suites/', method: 'get', params })
}
export function createAPITestSuite(data: any) {
    return request({ url: '/api-suites/', method: 'post', data })
}
export function deleteAPITestSuite(id: number) {
    return request({ url: `/api-suites/${id}/`, method: 'delete' })
}
export function executeAPITestSuite(id: number) {
    return request({ url: `/api-suites/${id}/execute/`, method: 'post' })
}

// --- APITestExecution ---
export function getAPITestExecutions(params?: any) {
    return request({ url: '/api-executions/', method: 'get', params })
}
