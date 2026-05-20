import { describe, expect, it } from 'vitest'

import type { BusiTreeNode, BusiTreeRequest } from '../tree/TreeNode'

describe('TreeNode types', () => {
  it('BusiTreeNode conforms to interface with required fields', () => {
    const node: BusiTreeNode = {
      id: '1',
      pid: '0',
      name: 'root',
      weight: 0,
      extraFlag: 0,
      extraFlag1: 0
    }
    expect(node).toHaveProperty('id')
    expect(node).toHaveProperty('pid')
    expect(node).toHaveProperty('name')
    expect(node).toHaveProperty('weight')
    expect(node).toHaveProperty('extraFlag')
    expect(node).toHaveProperty('extraFlag1')
  })

  it('BusiTreeNode accepts numeric id and pid', () => {
    const node: BusiTreeNode = {
      id: 123,
      pid: 0,
      name: 'folder',
      weight: 1,
      extraFlag: 1,
      extraFlag1: 0
    }
    expect(typeof node.id).toBe('number')
    expect(typeof node.pid).toBe('number')
  })

  it('BusiTreeNode supports optional fields', () => {
    const node: BusiTreeNode = {
      id: '1',
      pid: '0',
      name: 'leaf-node',
      weight: 2,
      extraFlag: 0,
      extraFlag1: 0,
      leaf: true,
      ext: 42
    }
    expect(node.leaf).toBe(true)
    expect(node.ext).toBe(42)
  })

  it('BusiTreeNode supports children recursively', () => {
    const child: BusiTreeNode = {
      id: '2',
      pid: '1',
      name: 'child',
      weight: 0,
      extraFlag: 0,
      extraFlag1: 0
    }
    const parent: BusiTreeNode = {
      id: '1',
      pid: '0',
      name: 'parent',
      weight: 0,
      extraFlag: 0,
      extraFlag1: 0,
      children: [child]
    }
    expect(parent.children).toHaveLength(1)
    expect(parent.children![0].name).toBe('child')
  })

  it('BusiTreeRequest conforms to interface with optional fields', () => {
    const req: BusiTreeRequest = {}
    expect(req).toEqual({})

    const fullReq: BusiTreeRequest = {
      busiFlag: 'panel',
      leaf: true,
      weight: 1,
      sortType: 'asc',
      resourceTable: 'chart'
    }
    expect(fullReq.busiFlag).toBe('panel')
    expect(fullReq.leaf).toBe(true)
    expect(fullReq.weight).toBe(1)
    expect(fullReq.sortType).toBe('asc')
    expect(fullReq.resourceTable).toBe('chart')
  })
})
