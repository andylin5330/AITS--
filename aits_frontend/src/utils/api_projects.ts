import request from './request'

// 获取项目列表
export function getProjects(params?: any) {
    return request({
        url: '/projects/',
        method: 'get',
        params
    })
}

// 创建项目
export function createProject(data: any) {
    return request({
        url: '/projects/',
        method: 'post',
        data
    })
}

// 获取项目详情
export function getProjectDetail(id: number) {
    return request({
        url: `/projects/${id}/`,
        method: 'get'
    })
}

// 更新项目
export function updateProject(id: number, data: any) {
    return request({
        url: `/projects/${id}/`,
        method: 'put',
        data
    })
}

// 删除项目
export function deleteProject(id: number) {
    return request({
        url: `/projects/${id}/`,
        method: 'delete'
    })
}
