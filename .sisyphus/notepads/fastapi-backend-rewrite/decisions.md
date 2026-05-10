## 2026-05-10 T01
- Freeze first delivery to standalone/community-oriented backend parity only; explicitly exclude desktop/H2 and distributed/Nacos runtime parity.
- Treat xpack and `de-xpack/` as enterprise boundary documentation only, not implementation scope.
- Preserve path compatibility, auth header semantics, and result-envelope behavior as higher priority than recreating Spring-internal structure.
- Classify WebSocket/STOMP notifications and sync-task runtime as deferred because they are not required to prove core BI CRUD/query/dashboard compatibility in first delivery.

## 2026-05-10 F4
- Scope fidelity verdict is blocked until compatibility leftovers are removed from Python backend: APISIX whitelist entry, xpack whitelist endpoints beyond `xpack_share`, and H2-labeled datasource test expectations.
