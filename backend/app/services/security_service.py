import socket
import ipaddress
import logging
from urllib.parse import urlparse, urljoin
from fastapi import HTTPException, status

logger = logging.getLogger(__name__)

# All RFC-1918 private ranges, loopback, link-local (AWS/GCP/Azure metadata), and unspecified
_BLOCKED_NETWORKS = [
    ipaddress.ip_network("0.0.0.0/8"),        # "This" network
    ipaddress.ip_network("10.0.0.0/8"),        # RFC-1918 private
    ipaddress.ip_network("100.64.0.0/10"),     # Shared address space (RFC 6598)
    ipaddress.ip_network("127.0.0.0/8"),       # IPv4 loopback
    ipaddress.ip_network("169.254.0.0/16"),    # Link-local / cloud metadata endpoints
    ipaddress.ip_network("172.16.0.0/12"),     # RFC-1918 private
    ipaddress.ip_network("192.0.2.0/24"),      # TEST-NET-1 (RFC 5737)
    ipaddress.ip_network("192.168.0.0/16"),    # RFC-1918 private
    ipaddress.ip_network("198.18.0.0/15"),     # Benchmark testing (RFC 2544)
    ipaddress.ip_network("198.51.100.0/24"),   # TEST-NET-2 (RFC 5737)
    ipaddress.ip_network("203.0.113.0/24"),    # TEST-NET-3 (RFC 5737)
    ipaddress.ip_network("224.0.0.0/4"),       # Multicast
    ipaddress.ip_network("240.0.0.0/4"),       # Reserved
    ipaddress.ip_network("255.255.255.255/32"),# Broadcast
    # IPv6
    ipaddress.ip_network("::/128"),            # IPv6 unspecified
    ipaddress.ip_network("::1/128"),           # IPv6 loopback
    ipaddress.ip_network("::ffff:0:0/96"),     # IPv4-mapped IPv6
    ipaddress.ip_network("100::/64"),          # Discard-only prefix
    ipaddress.ip_network("2001:db8::/32"),     # Documentation
    ipaddress.ip_network("fc00::/7"),          # IPv6 Unique Local (ULA)
    ipaddress.ip_network("fe80::/10"),         # IPv6 link-local
    ipaddress.ip_network("ff00::/8"),          # IPv6 multicast
]

# Hostnames that must always be blocked regardless of DNS resolution
_BLOCKED_HOSTNAMES = {
    "localhost",
    "localhost.localdomain",
    "metadata.google.internal",   # GCP metadata
    "169.254.169.254",            # AWS/Azure/GCP metadata IP (string form)
    "fd00::ec2",                  # AWS IPv6 metadata
    "instance-data",              # AWS EC2 metadata legacy hostname
}

# Dangerous internal or non-HTTP ports to block against SSRF port scanning
_BLOCKED_PORTS = {
    21,    # FTP
    22,    # SSH
    23,    # Telnet
    25,    # SMTP
    53,    # DNS
    69,    # TFTP
    110,   # POP3
    135,   # RPC
    137, 138, 139, # NetBIOS
    445,   # SMB
    1433,  # MS SQL
    1521,  # Oracle
    3306,  # MySQL
    5432,  # PostgreSQL
    6379,  # Redis
    11211, # Memcached
    27017, # MongoDB
    28017, # MongoDB web
}


def validate_url_security(url: str) -> bool:
    """
    Validates a user-submitted URL against SSRF, unsafe schemes, private IPs,
    cloud metadata endpoints, and dangerous ports.

    Raises HTTPException 400 on any violation.
    Returns True if the URL passes all checks.
    """
    if not url or not isinstance(url, str):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="URL string is required.",
        )

    parsed = urlparse(url.strip())

    # 1. Scheme whitelist
    if parsed.scheme.lower() not in ("http", "https"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only HTTP and HTTPS URLs are allowed.",
        )

    hostname = parsed.hostname
    if not hostname:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="URL is missing a valid hostname.",
        )

    # 2. Blocked hostname strings (catches numeric IPs typed as hostnames too)
    hostname_clean = hostname.lower().strip()
    if hostname_clean in _BLOCKED_HOSTNAMES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Access to localhost or internal network endpoints is forbidden.",
        )

    # 3. Block sensitive/internal ports
    if parsed.port and parsed.port in _BLOCKED_PORTS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Access to port {parsed.port} is blocked for security reasons.",
        )

    # 4. Reject bare IP literals in private ranges before DNS resolution
    try:
        direct_ip = ipaddress.ip_address(hostname_clean)
        _assert_not_private(direct_ip)
    except ValueError:
        pass  # not a raw IP literal — continue to DNS resolution below

    # 5. DNS-resolve and check every returned IP address
    try:
        addr_infos = socket.getaddrinfo(hostname_clean, None)
        for info in addr_infos:
            ip_str = info[4][0]
            try:
                ip_obj = ipaddress.ip_address(ip_str)
                _assert_not_private(ip_obj)
            except ValueError:
                pass  # skip unparseable entries
    except socket.gaierror:
        # Unresolvable hostname — allow through; the scraper will fail gracefully
        logger.warning("SSRF check: could not resolve hostname '%s'; allowing through.", hostname_clean)

    return True


def validate_redirect_url(target_url: str, base_url: str) -> str:
    """
    Resolves relative redirect URLs against the base URL and verifies the destination.
    """
    resolved = urljoin(base_url, target_url)
    validate_url_security(resolved)
    return resolved


_NAT64_PREFIX = ipaddress.ip_network("64:ff9b::/96")


def _assert_not_private(ip: ipaddress.IPv4Address | ipaddress.IPv6Address) -> None:
    """
    Ensures an IP address is not private, loopback, link-local, multicast, or in blocked networks.
    Supports RFC-6052 NAT64 Well-Known Prefix (64:ff9b::/96) by validating embedded IPv4.
    """
    if ip.version == 6 and ip in _NAT64_PREFIX:
        embedded_ipv4 = ipaddress.IPv4Address(ip.packed[-4:])
        _assert_not_private(embedded_ipv4)
        return

    if (
        ip.is_private
        or ip.is_loopback
        or ip.is_link_local
        or ip.is_multicast
        or ip.is_reserved
        or ip.is_unspecified
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Access to private, loopback, or reserved IP address ({ip}) is forbidden.",
        )

    for network in _BLOCKED_NETWORKS:
        if ip in network:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Access to blocked network range ({ip}) is forbidden.",
            )
