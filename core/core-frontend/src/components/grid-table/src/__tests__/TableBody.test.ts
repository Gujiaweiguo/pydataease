import { describe, it, expect } from 'vitest'
import TableBody from '../TableBody.vue'

describe('TableBody', () => {
  it('renders children when columns is empty', () => {
    const child1 = { props: { prop: 'name' } }
    const child2 = { props: { prop: 'age' } }
    const result = TableBody(
      { columns: [] },
      { slots: { default: () => [{ children: [child1, child2] }] } }
    )
    expect(result).toHaveLength(2)
  })

  it('filters children by columns prop', () => {
    const child1 = { props: { prop: 'name' } }
    const child2 = { props: { prop: 'age' } }
    const child3 = { props: { prop: 'email' } }

    const result = TableBody(
      { columns: ['name', 'age'] },
      { slots: { default: () => [{ children: [child1, child2, child3] }] } }
    )
    expect(result).toHaveLength(2)
  })

  it('includes children with type selection regardless of columns', () => {
    const child1 = { props: { prop: 'name' } }
    const child2 = { props: { type: 'selection' } }

    const result = TableBody(
      { columns: ['name'] },
      { slots: { default: () => [{ children: [child1, child2] }] } }
    )
    expect(result).toHaveLength(2)
  })

  it('includes children with key _operation regardless of columns', () => {
    const child1 = { props: { prop: 'name' } }
    const child2 = { props: { key: '_operation' } }

    const result = TableBody(
      { columns: ['name'] },
      { slots: { default: () => [{ children: [child1, child2] }] } }
    )
    expect(result).toHaveLength(2)
  })

  it('excludes children whose prop is not in columns', () => {
    const child1 = { props: { prop: 'name' } }
    const child2 = { props: { prop: 'excluded' } }

    const result = TableBody(
      { columns: ['name'] },
      { slots: { default: () => [{ children: [child1, child2] }] } }
    )
    expect(result).toHaveLength(1)
  })
})
