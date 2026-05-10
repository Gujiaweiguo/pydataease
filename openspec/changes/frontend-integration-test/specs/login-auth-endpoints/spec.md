## MODIFIED Requirements

### Requirement: RSA public key discovery SHALL support the existing login client
The FastAPI backend SHALL expose a `GET /de2api/dekey` endpoint that returns the RSA public key material required by the frontend before credential submission. The response format SHALL match the existing frontend encryption module's expectations.

#### Scenario: Login page requests the public key
- **WHEN** the frontend calls `GET /de2api/dekey`
- **THEN** the backend SHALL return a successful wrapped response containing the current RSA public key in the format expected by the existing client encryption logic

#### Scenario: Frontend encrypts password with returned key
- **WHEN** the frontend receives the RSA public key from `/dekey`
- **THEN** the frontend encryption module SHALL be able to encrypt a plaintext password using RSA-OAEP with SHA-256 and produce a ciphertext the backend can decrypt

#### Scenario: E2E login flow through Vite proxy
- **WHEN** the browser navigates to the login page and submits credentials
- **THEN** the full flow (GET /api/dekey → encrypt → POST /api/login/localLogin → JWT) SHALL complete successfully through the Vite dev proxy without modification to frontend code
