import { describe, expect, it } from 'vitest'

import treeSort, { sortCircle, sortPer, treeParentWeight } from '../treeSortUtils'

const createTree = () => [
  {
    id: 1,
    name: 'Beta',
    weight: 10,
    children: [
      { id: 11, name: 'Delta', weight: 100, children: [] },
      { id: 12, name: 'Alpha', weight: 200, children: [] }
    ]
  },
  {
    id: 2,
    name: 'Alpha',
    weight: 20,
    children: [{ id: 21, name: 'Gamma', weight: 300, children: [] }]
  }
]

describe('treeSortUtils', () => {
  it('maps each node to its parent weight recursively', () => {
    expect(treeParentWeight(createTree() as any, 'root')).toEqual({
      1: 'root',
      2: 'root',
      11: 10,
      12: 10,
      21: 20
    })
  })

  it('returns an empty weight map for empty trees', () => {
    expect(treeParentWeight([], 'root')).toEqual({})
  })

  it('sorts a single level ascending by localized name', () => {
    const nodes = [
      { id: 1, name: '张三' },
      { id: 2, name: '李四' },
      { id: 3, name: '王五' }
    ] as any

    sortPer(nodes, 'name_asc')

    expect(nodes.map(node => node.name)).toEqual(['李四', '王五', '张三'])
  })

  it('sorts a single level descending and reverses for time_asc', () => {
    const descNodes = [
      { id: 1, name: 'A' },
      { id: 2, name: 'C' },
      { id: 3, name: 'B' }
    ] as any
    sortPer(descNodes, 'name_desc')
    expect(descNodes.map(node => node.name)).toEqual(['C', 'B', 'A'])

    const timeNodes = [
      { id: 1, name: 'A' },
      { id: 2, name: 'B' },
      { id: 3, name: 'C' }
    ] as any
    sortPer(timeNodes, 'time_asc')
    expect(timeNodes.map(node => node.name)).toEqual(['C', 'B', 'A'])
  })

  it('sorts nested children without mutating the original tree', () => {
    const source = createTree() as any
    const result = treeSort(source, 'name_asc') as any

    expect(result.map(node => node.name)).toEqual(['Alpha', 'Beta'])
    expect(result[1].children.map(node => node.name)).toEqual(['Alpha', 'Delta'])
    expect(source.map(node => node.name)).toEqual(['Beta', 'Alpha'])
    expect(source[0].children.map(node => node.name)).toEqual(['Delta', 'Alpha'])
  })

  it('leaves nodes untouched for unknown sort types while still recursing', () => {
    const source = createTree() as any

    sortCircle(source, 'unknown')

    expect(source.map(node => node.name)).toEqual(['Beta', 'Alpha'])
    expect(source[0].children.map(node => node.name)).toEqual(['Delta', 'Alpha'])
  })
})
