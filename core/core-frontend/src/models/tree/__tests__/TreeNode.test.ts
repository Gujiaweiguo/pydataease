import { describe, it, expect } from 'vitest'
import type { BusiTreeNode, BusiTreeRequest } from '../TreeNode'

describe('TreeNode types', () => {
  it('BusiTreeNode should accept valid data', () => {
    const node: BusiTreeNode = {
      id: '1',
      pid: '0',
      name: 'test',
      weight: 1,
      extraFlag: 0,
      extraFlag1: 0
    }
    expect(node.id).toBe('1')
    expect(node.name).toBe('test')
    expect(node.leaf).toBeUndefined()
    expect(node.children).toBeUndefined()
  })

  it('BusiTreeNode should accept optional fields', () => {
    const node: BusiTreeNode = {
      id: 1,
      pid: 0,
      name: 'test',
      leaf: true,
      weight: 1,
      ext: 5,
      extraFlag: 1,
      extraFlag1: 2,
      children: []
    }
    expect(node.leaf).toBe(true)
    expect(node.ext).toBe(5)
    expect(node.children).toEqual([])
  })

  it('BusiTreeNode should support number id and pid', () => {
    const node: BusiTreeNode = {
      id: 123,
      pid: 456,
      name: 'node',
      weight: 0,
      extraFlag: 0,
      extraFlag1: 0
    }
    expect(typeof node.id).toBe('number')
    expect(typeof node.pid).toBe('number')
  })

  it('BusiTreeRequest should accept valid data', () => {
    const request: BusiTreeRequest = {
      busiFlag: 'panel',
      leaf: true,
      weight: 1,
      sortType: 'asc',
      resourceTable: 'chart'
    }
    expect(request.busiFlag).toBe('panel')
    expect(request.leaf).toBe(true)
  })

  it('BusiTreeRequest should allow all optional fields', () => {
    const request: BusiTreeRequest = {}
    expect(request.busiFlag).toBeUndefined()
    expect(request.leaf).toBeUndefined()
  })
})
