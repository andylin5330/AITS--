import request from './request'

// --- ScheduledTask ---
export function getScheduledTasks(params?: any) {
    return request({ url: '/scheduled-tasks/', method: 'get', params })
}
export function createScheduledTask(data: any) {
    return request({ url: '/scheduled-tasks/', method: 'post', data })
}
export function updateScheduledTask(id: number, data: any) {
    return request({ url: `/scheduled-tasks/${id}/`, method: 'put', data })
}
export function deleteScheduledTask(id: number) {
    return request({ url: `/scheduled-tasks/${id}/`, method: 'delete' })
}

// --- TaskExecutionLog ---
export function getTaskExecutionLogs(params?: any) {
    return request({ url: '/task-logs/', method: 'get', params })
}
