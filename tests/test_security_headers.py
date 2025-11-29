import pytest


def test_csp_header(client):
    """Verify that Content-Security-Policy header is correctly set with new directives."""
    response = client.get('/')
    assert 'Content-Security-Policy' in response.headers
    csp = response.headers['Content-Security-Policy']

    # Check for new directives
    # connect-src should contain cdn.jsdelivr.net
    assert "connect-src" in csp
    assert "https://cdn.jsdelivr.net" in csp

    # script-src should contain static.cloudflareinsights.com
    assert "script-src" in csp
    assert "https://static.cloudflareinsights.com" in csp


def test_security_headers(client):
    """Verify that all critical security headers are correctly set."""
    response = client.get('/')

    # Strict-Transport-Security (HSTS)
    assert 'Strict-Transport-Security' in response.headers
    hsts = response.headers['Strict-Transport-Security']
    assert 'max-age=31536000' in hsts
    assert 'includeSubDomains' in hsts

    # X-Frame-Options (Clickjacking Protection)
    assert 'X-Frame-Options' in response.headers
    assert response.headers['X-Frame-Options'] == 'SAMEORIGIN'

    # X-Content-Type-Options (MIME Sniffing Protection)
    assert 'X-Content-Type-Options' in response.headers
    assert response.headers['X-Content-Type-Options'] == 'nosniff'

    # Referrer-Policy
    assert 'Referrer-Policy' in response.headers
    assert response.headers['Referrer-Policy'] == 'strict-origin-when-cross-origin'

    # Permissions-Policy
    assert 'Permissions-Policy' in response.headers
    permissions = response.headers['Permissions-Policy']
    assert 'geolocation=()' in permissions
    assert 'microphone=()' in permissions
    assert 'camera=()' in permissions
