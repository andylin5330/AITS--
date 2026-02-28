import request from './request'

// --- WebUITestCase ---
export function getWebUITestCases(params?: any) {
    return request({ url: '/web-cases/', method: 'get', params })
}
export function createWebUITestCase(data: any) {
    return request({ url: '/web-cases/', method: 'post', data })
}
export function updateWebUITestCase(id: number, data: any) {
    return request({ url: `/web-cases/${id}/`, method: 'put', data })
}
export function deleteWebUITestCase(id: number) {
    return request({ url: `/web-cases/${id}/`, method: 'delete' })
}

// --- WebUITestSuite ---
export function getWebUITestSuites(params?: any) {
    return request({ url: '/web-suites/', method: 'get', params })
}
export function createWebUITestSuite(data: any) {
    return request({ url: '/web-suites/', method: 'post', data })
}
export function deleteWebUITestSuite(id: number) {
    return request({ url: `/web-suites/${id}/`, method: 'delete' })
}

// --- WebUITestExecution ---
export function getWebUITestExecutions(params?: any) {
    return request({ url: '/web-executions/', method: 'get', params })
}
export function getMidSceneScript(caseId: number) {
    return request({ url: `/midscene-scripts/`, method: 'get', params: { case: caseId } })
}
export function saveMidSceneScript(data: any) {
    if (data.id) {
        return request({ url: `/midscene-scripts/${data.id}/`, method: 'put', data })
    }
    return request({ url: `/midscene-scripts/`, method: 'post', data })
}
