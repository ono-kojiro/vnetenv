; base zone file for example.com
$TTL 2d    ; default TTL for zone
$ORIGIN example.com. ; base domain-name
; Start of Authority RR defining the key characteristics of the zone (domain)
@         IN      SOA   router10 root (
                                2026021501 ; serial number
                                12h        ; refresh
                                15m        ; update retry
                                3w         ; expiry
                                2h         ; minimum
                                )
; name server RR for the domain
           IN      NS      router10.example.com.
router0    IN      A       172.16.10.1
router10   IN      A       172.16.10.99
router20   IN      A       172.16.20.99
router30   IN      A       172.16.30.99

