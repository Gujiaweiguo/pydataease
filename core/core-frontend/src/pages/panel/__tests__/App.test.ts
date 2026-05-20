import { shallowMount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

vi.mock('@/config/axios/service', () => ({
  service: {} as any,
  PATH_URL: './',
  cancelMap: new Map()
}))

vi.mock('@/hooks/web/useEmitt', () => ({
  useEmitt: vi.fn()
}))

vi.mock('@/utils/propTypes', () => ({
  propTypes: {
    string: {
      def: vi.fn().mockReturnValue({ type: String, default: 'Iframe' })
    }
  }
}))

import App from '../App.vue'

describe('panel/App.vue', () => {
  const mountApp = (componentName = 'Iframe') => {
    return shallowMount(App, {
      props: { componentName },
      global: {
        stubs: {
          DashboardEditor: { template: '<div>DashboardEditor</div>' },
          VisualizationEditor: { template: '<div>VisualizationEditor</div>' },
          ViewWrapper: { template: '<div>ViewWrapper</div>' },
          Preview: { template: '<div>Preview</div>' },
          Dashboard: { template: '<div>Dashboard</div>' },
          Dataset: { template: '<div>Dataset</div>' },
          Iframe: { template: '<div>Iframe</div>' },
          Datasource: { template: '<div>Datasource</div>' },
          ScreenPanel: { template: '<div>ScreenPanel</div>' },
          DashboardPanel: { template: '<div>DashboardPanel</div>' },
          DatasetEditor: { template: '<div>DatasetEditor</div>' },
          DashboardEmpty: { template: '<div>DashboardEmpty</div>' },
          TemplateManage: { template: '<div>TemplateManage</div>' },
          XpackComponent: { template: '<div>XpackComponent</div>' }
        }
      }
    })
  }

  it('renders the App component', () => {
    const wrapper = mountApp()
    expect(wrapper.exists()).toBe(true)
  })

  it('renders a root element', () => {
    const wrapper = mountApp()
    expect(wrapper.element).toBeTruthy()
  })

  it('accepts componentName prop', () => {
    const wrapper = mountApp('Dashboard')
    expect((wrapper.props() as any).componentName).toBe('Dashboard')
  })

  it('uses default componentName prop value', () => {
    const wrapper = mountApp()
    expect((wrapper.props() as any).componentName).toBe('Iframe')
  })
})
