import { describe, it, expect } from 'vitest'
import type { DropdownProps } from '../types'

describe('types', () => {
  it('DropdownProps interface allows icon property', () => {
    const props: DropdownProps = { icon: 'edit' }
    expect(props.icon).toBe('edit')
  })

  it('DropdownProps interface allows disabled property', () => {
    const props: DropdownProps = { disabled: true }
    expect(props.disabled).toBe(true)
  })

  it('DropdownProps interface allows divided property', () => {
    const props: DropdownProps = { divided: true }
    expect(props.divided).toBe(true)
  })

  it('DropdownProps interface allows command property', () => {
    const props: DropdownProps = { command: 'edit' }
    expect(props.command).toBe('edit')
  })

  it('DropdownProps interface allows label property', () => {
    const props: DropdownProps = { label: 'Edit' }
    expect(props.label).toBe('Edit')
  })

  it('DropdownProps interface allows additional properties via index signature', () => {
    const props: DropdownProps = { icon: 'edit', customProp: 'value' }
    expect((props as any).customProp).toBe('value')
  })

  it('DropdownProps defaults to empty object', () => {
    const props: DropdownProps = {}
    expect(props.icon).toBeUndefined()
    expect(props.disabled).toBeUndefined()
  })
})
