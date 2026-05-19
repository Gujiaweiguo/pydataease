import { beforeEach, describe, expect, it, vi } from 'vitest'

import { treeDraggble } from '../treeDraggble'

type TreeNode = {
  id: string
  name: string
  leaf: boolean
  children?: TreeNode[]
}

const createTree = (): TreeNode[] => [
  {
    id: 'folder-1',
    name: 'Folder 1',
    leaf: false,
    children: [
      { id: 'child-1', name: 'Child 1', leaf: true },
      { id: 'child-2', name: 'Child 2', leaf: true }
    ]
  },
  {
    id: 'folder-2',
    name: 'Folder 2',
    leaf: false,
    children: [{ id: 'child-3', name: 'Child 3', leaf: true }]
  }
]

describe('treeDraggble', () => {
  beforeEach(() => {
    vi.useRealTimers()
  })

  it('only allows dropping onto non-leaf nodes', () => {
    const state = { tree: createTree() }
    const draggable = treeDraggble(state, 'tree', vi.fn(), 'chart', { value: [] })

    expect(draggable.allowDrop(null, { data: { leaf: false } })).toBe(true)
    expect(draggable.allowDrop(null, { data: { leaf: true } })).toBe(false)
  })

  it('sends an inner move request and snapshots the updated tree on success', async () => {
    const state = { tree: createTree() }
    const originResourceTree = { value: [] as TreeNode[] }
    const req = vi.fn().mockResolvedValue(undefined)
    const draggable = treeDraggble(state, 'tree', req, 'chart', originResourceTree)
    const draggingNode = { data: state.tree[0].children?.[0] as TreeNode }

    draggable.handleDragStart(draggingNode)
    const movedNode = state.tree[0].children?.shift() as TreeNode
    state.tree[1].children?.push(movedNode)

    await draggable.handleDrop(draggingNode, { data: state.tree[1] }, 'inner')

    expect(req).toHaveBeenCalledWith({
      id: 'child-1',
      name: 'Child 1',
      nodeType: 'chart',
      pid: 'folder-2',
      action: 'move'
    })
    expect(originResourceTree.value).toEqual(state.tree)
    expect(originResourceTree.value).not.toBe(state.tree)
  })

  it('restores the original root order for same-level outer drops without calling req', async () => {
    vi.useFakeTimers()

    const state = {
      tree: [
        { id: 'node-a', name: 'Node A', leaf: true },
        { id: 'node-b', name: 'Node B', leaf: true }
      ]
    }
    const req = vi.fn()
    const draggable = treeDraggble(state, 'tree', req, 'chart', { value: [] })
    const draggingNode = { data: state.tree[0] }

    draggable.handleDragStart(draggingNode)
    state.tree = [state.tree[1], state.tree[0]]

    draggable.handleDrop(draggingNode, { data: state.tree[0] }, 'before')
    await vi.runAllTimersAsync()

    expect(req).not.toHaveBeenCalled()
    expect(state.tree.map(node => node.id)).toEqual(['node-a', 'node-b'])
  })

  it('computes the parent id for outer drops based on the current tree structure', async () => {
    const state = { tree: createTree() }
    const req = vi.fn().mockResolvedValue(undefined)
    const draggable = treeDraggble(state, 'tree', req, 'chart', { value: [] })
    const draggingNode = { data: state.tree[0].children?.[0] as TreeNode }
    const dropNode = { data: state.tree[1].children?.[0] as TreeNode }

    draggable.handleDragStart(draggingNode)
    const movedNode = state.tree[0].children?.shift() as TreeNode
    state.tree[1].children = [state.tree[1].children?.[0] as TreeNode, movedNode]

    await draggable.handleDrop(draggingNode, dropNode, 'after')

    expect(req).toHaveBeenCalledWith({
      id: 'child-1',
      name: 'Child 1',
      nodeType: 'chart',
      pid: 'folder-2',
      action: 'move'
    })
  })

  it('marks non-leaf drag nodes as folders in move requests', async () => {
    const state = { tree: createTree() }
    const req = vi.fn().mockResolvedValue(undefined)
    const draggable = treeDraggble(state, 'tree', req, 'chart', { value: [] })
    const draggingNode = { data: state.tree[0] }

    draggable.handleDragStart(draggingNode)
    state.tree = [state.tree[1], state.tree[0]]

    await draggable.handleDrop(draggingNode, { data: state.tree[0] }, 'inner')

    expect(req).toHaveBeenCalledWith({
      id: 'folder-1',
      name: 'Folder 1',
      nodeType: 'folder',
      pid: 'folder-2',
      action: 'move'
    })
  })
})
