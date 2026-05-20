class MockWorker {
  url: string
  constructor(url: string) {
    this.url = url
  }
  postMessage(_data?: unknown) {
    /* noop */
  }
  terminate() {
    /* noop */
  }
  addEventListener(_type?: string, _listener?: EventListener) {
    /* noop */
  }
  removeEventListener(_type?: string, _listener?: EventListener) {
    /* noop */
  }
}
;(globalThis as any).Worker = MockWorker
