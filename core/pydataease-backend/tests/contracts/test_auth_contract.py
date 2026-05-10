class TestLoginContract:
    def test_local_login_success_contract(self) -> None:
        """POST /de2api/login/localLogin should accept credential body and return ResultMessage with TokenVO data on success; no auth header required."""
        raise NotImplementedError

    def test_local_login_auth_failure_contract(self) -> None:
        """POST /de2api/login/localLogin should reject invalid credentials with non-zero ResultMessage.code and error msg."""
        raise NotImplementedError

    def test_refresh_success_contract(self) -> None:
        """GET /de2api/login/refresh should require X-DE-TOKEN and return refreshed TokenVO in ResultMessage.data."""
        raise NotImplementedError

    def test_refresh_missing_token_contract(self) -> None:
        """GET /de2api/login/refresh should fail when X-DE-TOKEN is missing, invalid, or expired."""
        raise NotImplementedError

    def test_logout_success_contract(self) -> None:
        """GET /de2api/logout should require X-DE-TOKEN and return success ResultMessage with empty data on logout."""
        raise NotImplementedError

    def test_logout_missing_token_contract(self) -> None:
        """GET /de2api/logout should fail when X-DE-TOKEN is missing, invalid, or expired."""
        raise NotImplementedError


class TestTokenSemanticsContract:
    def test_share_token_header_contract(self) -> None:
        """Protected share routes should accept X-DE-LINK-TOKEN as alternate auth header and resolve uid/oid/resourceId from JWT claims."""
        raise NotImplementedError

    def test_embedded_token_header_contract(self) -> None:
        """Embedded requests should support X-EMBEDDED-TOKEN header where frontend injects embedded session tokens."""
        raise NotImplementedError
